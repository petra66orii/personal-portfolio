from rest_framework.throttling import AnonRateThrottle


class ContactFormThrottle(AnonRateThrottle):
    scope = "contact_form"


class ServiceInquiryThrottle(AnonRateThrottle):
    scope = "service_inquiry"


class NewsletterSignupThrottle(AnonRateThrottle):
    scope = "newsletter_signup"
