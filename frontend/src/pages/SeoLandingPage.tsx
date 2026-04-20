import { Link } from "react-router-dom";
import SEO from "../components/SEO";

export const SEO_LANDING_SLUGS = [
  "custom-web-development-agency",
  "custom-web-developer-ireland",
  "web-development-agency-galway",
  "web-development-agency-dublin",
  "django-react-developer",
  "international-web-development",
] as const;

export type SeoLandingSlug = (typeof SEO_LANDING_SLUGS)[number];

type LandingFaq = {
  question: string;
  answer: string;
};

type LandingPageConfig = {
  title: string;
  description: string;
  h1: string;
  intro: string;
  positioning: string[];
  credibilityTitle: string;
  credibilityPoints: string[];
  ctaTitle: string;
  ctaBody: string;
  faq: LandingFaq[];
};

const LANDING_PAGE_CONFIG: Record<SeoLandingSlug, LandingPageConfig> = {
  "custom-web-development-agency": {
    title: "Custom Web Development Agency | Miss Bott",
    description:
      "Miss Bott is a founder-led custom web development agency building high-performance websites and web applications for businesses that have outgrown template platforms.",
    h1: "Custom Web Development Agency for Growth-Stage Businesses",
    intro:
      "Miss Bott partners with businesses that need more than a theme refresh. We design and build custom web platforms with clear architecture, measurable performance, and conversion-focused user journeys.",
    positioning: [
      "Founder-led engagement with direct technical decision-making.",
      "Custom Django + React delivery instead of plugin patchwork.",
      "Scope-first process designed to protect delivery quality and budget.",
    ],
    credibilityTitle: "Why businesses move to custom development",
    credibilityPoints: [
      "Template platforms often slow down once operations, integrations, and content complexity increase.",
      "Custom architecture supports better performance, cleaner data flow, and long-term maintainability.",
      "You gain technical control without sacrificing UX, editorial flexibility, or growth planning.",
    ],
    ctaTitle: "Need software architecture, not plugin fixes?",
    ctaBody:
      "Start with a discovery session and get a scoped implementation roadmap before build starts.",
    faq: [
      {
        question: "What makes Miss Bott different from a general agency?",
        answer:
          "Miss Bott is founder-led and technical by default, so strategy and implementation stay connected from discovery through launch.",
      },
      {
        question: "Do you only build websites?",
        answer:
          "No. We also build custom web applications, including authenticated workflows, dashboards, and operational tooling.",
      },
    ],
  },
  "custom-web-developer-ireland": {
    title: "Custom Web Developer Ireland | Miss Bott",
    description:
      "Work with a custom web developer in Ireland for high-performance websites and custom web applications built with Django and React.",
    h1: "Custom Web Developer in Ireland for Serious Business Platforms",
    intro:
      "Based in Ireland, Miss Bott delivers custom websites and web applications for businesses that have outgrown WordPress, Wix, Squarespace, or off-the-shelf themes.",
    positioning: [
      "Ireland-based founder-led delivery with direct collaboration.",
      "Custom build process focused on scalability, speed, and maintainability.",
      "Ideal for businesses upgrading from brittle template stacks.",
    ],
    credibilityTitle: "Built for Irish businesses with growth priorities",
    credibilityPoints: [
      "Projects are scoped around business outcomes, not generic deliverables.",
      "Django and React architecture supports fast performance and flexible integration.",
      "Delivery works well for teams across Galway, Dublin, and Ireland-wide.",
    ],
    ctaTitle: "Planning a custom platform in Ireland?",
    ctaBody:
      "Book a discovery call to map the right architecture before committing to implementation.",
    faq: [
      {
        question: "Do you work with businesses outside Dublin?",
        answer:
          "Yes. Engagements are delivered remotely across Ireland, including Galway, Dublin, and nationwide teams.",
      },
      {
        question: "Is Django and React the default stack?",
        answer:
          "For most projects, yes. It provides strong foundations for performance, security, and long-term extensibility.",
      },
    ],
  },
  "web-development-agency-galway": {
    title: "Web Development Agency Galway | Miss Bott",
    description:
      "Miss Bott is a web development agency serving Galway businesses with custom websites and web applications built for long-term growth.",
    h1: "Web Development Agency in Galway for Custom Builds",
    intro:
      "Miss Bott supports Galway businesses that need custom digital platforms, not another template redesign. Every engagement is scoped around your commercial goals and delivery constraints.",
    positioning: [
      "Custom website and application delivery for Galway businesses.",
      "Strategic discovery before build to reduce scope risk.",
      "Conversion-focused UX with performance-first engineering.",
    ],
    credibilityTitle: "How Galway teams use custom builds",
    credibilityPoints: [
      "Upgrade legacy or template websites that can no longer support your growth plan.",
      "Launch new service, commerce, or application platforms with clear technical ownership.",
      "Improve lead quality with stronger architecture, messaging, and conversion flow.",
    ],
    ctaTitle: "Need a Galway web development partner?",
    ctaBody:
      "Start with discovery and receive a practical roadmap tailored to your business model.",
    faq: [
      {
        question: "Do you provide on-site workshops in Galway?",
        answer:
          "Most projects run remotely, but structured workshops can be arranged when needed.",
      },
      {
        question: "Do you replace existing WordPress or Wix sites?",
        answer:
          "Yes. A common project type is moving businesses from fragile template setups to a custom, maintainable platform.",
      },
    ],
  },
  "web-development-agency-dublin": {
    title: "Web Development Agency Dublin | Miss Bott",
    description:
      "Founder-led web development agency supporting Dublin businesses with custom websites and Django React web applications.",
    h1: "Web Development Agency in Dublin for Custom Platforms",
    intro:
      "Miss Bott helps Dublin teams build digital platforms that can support scaling operations, stronger conversion journeys, and complex workflows.",
    positioning: [
      "Dublin-focused delivery for businesses outgrowing template platforms.",
      "Custom architecture for service, commerce, and application needs.",
      "Clear communication, fixed-scope milestones, and practical execution.",
    ],
    credibilityTitle: "Built for teams with operational complexity",
    credibilityPoints: [
      "From lead-gen sites to authenticated applications, delivery is aligned to business process.",
      "Strong technical SEO and performance foundations are baked into implementation.",
      "Founder involvement keeps requirements, architecture, and build decisions aligned.",
    ],
    ctaTitle: "Building a platform in Dublin?",
    ctaBody:
      "Define architecture and scope in a discovery session before development starts.",
    faq: [
      {
        question: "Can you work with internal marketing and operations teams?",
        answer:
          "Yes. Collaboration with in-house teams is built into the process so product, content, and commercial goals stay aligned.",
      },
      {
        question: "Do you handle migration planning from existing systems?",
        answer:
          "Yes. Discovery includes migration and transition planning where legacy sites, CMSs, or workflows are involved.",
      },
    ],
  },
  "django-react-developer": {
    title: "Django React Developer | Miss Bott",
    description:
      "Hire a Django React developer to build high-performance custom websites and web applications with scalable architecture and clean delivery workflows.",
    h1: "Django React Developer for Custom Web Platforms",
    intro:
      "Miss Bott specialises in Django and React delivery for businesses that need maintainable full-stack systems, not template workarounds.",
    positioning: [
      "Django handles secure business logic, APIs, and data workflows.",
      "React delivers fast, modern interfaces for customer and internal users.",
      "Architecture decisions are aligned to business outcomes from day one.",
    ],
    credibilityTitle: "When Django + React is the right fit",
    credibilityPoints: [
      "You need role-based workflows, structured content, and reliable backend logic.",
      "You need performance and UX quality that default CMS templates cannot provide.",
      "You need a stack that supports both immediate launch goals and future product expansion.",
    ],
    ctaTitle: "Need a Django React build partner?",
    ctaBody:
      "Book discovery and get a delivery plan for your exact scope, integrations, and timeline.",
    faq: [
      {
        question: "Do you build API-first systems?",
        answer:
          "Yes. Django REST architecture is used where integrations, future clients, or workflow scaling require explicit service boundaries.",
      },
      {
        question: "Can you support ongoing improvements after launch?",
        answer:
          "Yes. Ongoing support and iterative delivery are available once the core platform is live.",
      },
    ],
  },
  "international-web-development": {
    title: "Remote Custom Web Development for USA Teams",
    description:
      "Founder-led remote custom web development for USA and international businesses that need Django React websites and web applications.",
    h1: "Remote Custom Web Development for USA and International Teams",
    intro:
      "Miss Bott is Ireland-based and works remotely with businesses across the USA and other international markets. Engagements are structured for clear communication, timezone-aware execution, and practical delivery cadence.",
    positioning: [
      "No fake local office claims. Delivery is remote, founder-led, and transparent.",
      "Projects are scoped around measurable outcomes and operational fit.",
      "Strong process for asynchronous collaboration with distributed teams.",
    ],
    credibilityTitle: "How remote delivery stays reliable",
    credibilityPoints: [
      "Discovery aligns scope, responsibilities, and decision points before build.",
      "Milestone delivery and structured updates keep progress visible.",
      "Architecture and documentation are designed for long-term internal adoption.",
    ],
    ctaTitle: "Need a custom web developer for a USA-based team?",
    ctaBody:
      "Schedule a discovery call to map requirements, timezone overlap, and a practical delivery plan.",
    faq: [
      {
        question: "Do you have a physical office in the United States?",
        answer: "No. Miss Bott is based in Ireland and works with USA teams remotely.",
      },
      {
        question: "Can remote delivery handle complex custom projects?",
        answer:
          "Yes. The process is built around scoped milestones, clear handoffs, and communication rhythms that support distributed teams.",
      },
    ],
  },
};

type SeoLandingPageProps = {
  slug: SeoLandingSlug;
};

const SeoLandingPage = ({ slug }: SeoLandingPageProps) => {
  const content = LANDING_PAGE_CONFIG[slug];

  return (
    <>
      <SEO
        title={content.title}
        description={content.description}
        type="website"
        image="/assets/logos/social-logo.png"
      />
      <main className="min-h-screen p-3 sm:p-6">
        <div className="glassmorphism backdrop-blur-sm rounded-2xl shadow-xl max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-8 sm:py-12 border">
          <section className="mb-8 sm:mb-10">
            <p className="text-xs sm:text-sm uppercase tracking-[0.2em] secondary font-semibold mb-3">
              Strategic Landing Page
            </p>
            <h1 className="text-3xl sm:text-5xl font-bold text-primary mb-4">
              {content.h1}
            </h1>
            <p className="text-base sm:text-lg text-secondary leading-relaxed max-w-4xl">
              {content.intro}
            </p>
            <div className="flex flex-col sm:flex-row gap-3 mt-6">
              <Link
                to="/contact"
                className="inline-flex items-center justify-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                Book Discovery
              </Link>
              <Link
                to="/services"
                className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
              >
                View Service Stacks
              </Link>
            </div>
          </section>

          <section className="mb-8 sm:mb-10 glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-4">
              Service positioning
            </h2>
            <ul className="space-y-3">
              {content.positioning.map((point) => (
                <li key={point} className="text-sm sm:text-base text-secondary leading-relaxed">
                  {point}
                </li>
              ))}
            </ul>
          </section>

          <section className="mb-8 sm:mb-10 glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-4">
              {content.credibilityTitle}
            </h2>
            <ul className="space-y-3">
              {content.credibilityPoints.map((point) => (
                <li key={point} className="text-sm sm:text-base text-secondary leading-relaxed">
                  {point}
                </li>
              ))}
            </ul>
          </section>

          <section className="mb-8 sm:mb-10 glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-4">
              Explore related pages
            </h2>
            <div className="grid sm:grid-cols-2 gap-3">
              <Link to="/services" className="text-primary hover:underline">
                Custom web development services
              </Link>
              <Link to="/blog" className="text-primary hover:underline">
                Insights on growth-stage web platforms
              </Link>
              <Link to="/django-react-developer" className="text-primary hover:underline">
                Django React developer expertise
              </Link>
              <Link to="/custom-web-development-agency" className="text-primary hover:underline">
                Agency engagement model
              </Link>
            </div>
          </section>

          <section className="mb-8 sm:mb-10 glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-4">
              Frequently asked questions
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {content.faq.map((item) => (
                <article key={item.question} className="rounded-xl border border-secondary/20 p-4">
                  <h3 className="text-base sm:text-lg font-semibold text-primary mb-2">
                    {item.question}
                  </h3>
                  <p className="text-sm sm:text-base text-secondary leading-relaxed">
                    {item.answer}
                  </p>
                </article>
              ))}
            </div>
          </section>

          <section className="glassmorphism rounded-3xl p-6 sm:p-8 border border-secondary/20 text-center">
            <h2 className="text-2xl sm:text-4xl font-bold text-primary mb-4">
              {content.ctaTitle}
            </h2>
            <p className="text-sm sm:text-base text-secondary leading-relaxed max-w-3xl mx-auto mb-6">
              {content.ctaBody}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4">
              <Link
                to="/contact"
                className="inline-flex items-center justify-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                Start Discovery
              </Link>
              <Link
                to="/services"
                className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
              >
                Compare Service Stacks
              </Link>
            </div>
          </section>
        </div>
      </main>
    </>
  );
};

export default SeoLandingPage;
