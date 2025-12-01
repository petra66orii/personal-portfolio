import json
import logging
import os
from django.conf import settings
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() 

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the client
client = OpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)

def analyze_lead(inquiry_instance):
    """
    Takes a ProjectInquiry instance, sends it to GPT-4o for analysis,
    and updates the instance with a score, summary, and red flags.
    """
    
    # 1. Construct the "Gatekeeper" Persona
    system_prompt = """
    You are 'Miss Bott', a premium technical consultant specializing in custom React, Django, and Headless Commerce architectures.
    
    Task 1: Evaluate the lead (Score 1-10).
    Task 2: Write a HYPER-PERSONALIZED email draft to the client.
    Task 3: Identify any red flags.
    
    Scoring Criteria (1-10):
    - 8-10 (Ideal): Budget > €6,000, specifically asks for React/Django/API work, clearly defined business goal (B2B/SaaS/E-commerce).
    - 5-7 (Maybe): Budget unclear but project sounds complex/interesting. Good technical literacy.
    - 1-4 (Avoid): Budget < €3,000, asking for Wordpress/Wix, vague "I need a website" requests, poor spelling/effort.

    Email Draft Instructions:
    - Tone: Professional, authoritative, yet warm.
    - If Score > 6: Write an invitation. Reference their SPECIFIC project details (e.g., "I saw you are migrating a FinTech app..."). Prove you read it.
    - If Score < 6: Write a polite decline (fully booked).
    - Do NOT include the Calendly link or sign-off (The system adds these). Just the body.

    Output JSON:
        {
            "summary": "Executive summary...",
            "score": integer,
            "red_flags": [],
            "recommended_action": "APPROVE" or "REJECT",
            "email_draft": "Hi [Name], \n\n[Body text here referencing their specific project needs...]"
        }
    """

    # 2. Format the Client Data
    # Adjust field names (e.g., .budget, .message) to match your actual model
    user_message = f"""
        Analyze this lead:
        Name: {inquiry_instance.name}
        Email: {inquiry_instance.email}
        Company: {inquiry_instance.company}
        Budget: {inquiry_instance.get_budget_range_display()}
        Timeline: {inquiry_instance.get_timeline_display()}
        Service Interest: {inquiry_instance.service.name if inquiry_instance.service else 'General'}
        Project Details: {inquiry_instance.project_details}
        """

    try:
        # 3. Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        data = json.loads(response.choices[0].message.content)

        # 4. Update Model
        inquiry_instance.ai_summary = data.get('summary', '')
        inquiry_instance.lead_score = data.get('score', 0)
        inquiry_instance.ai_email_draft = data.get('email_draft', '') # <--- Capture Draft
        
        flags = data.get('red_flags', [])
        action = data.get('recommended_action', 'MANUAL_REVIEW')
        
        inquiry_instance.ai_analysis_raw = f"Action: {action}\nFlags: {', '.join(flags)}"
        inquiry_instance.status = 'analyzed' 
        
        inquiry_instance.save()
        return True

    except Exception as e:
        logger.error(f"AI Analysis Failed: {str(e)}")
        return False