import ContactForm from "../components/ContactForm";
import SEO from "../components/SEO";

const Contact = () => {
  return (
    <>
      <SEO
        title="Contact Me - Let's Work Together"
        description="Get in touch with Miss Bott for web development projects, collaborations, or freelance opportunities. Specializing in React, Django, and full-stack development solutions."
        keywords="contact developer, hire React developer, Django freelancer, full stack developer contact, web development services"
        type="website"
      />
      <ContactForm />
    </>
  );
};

export default Contact;
