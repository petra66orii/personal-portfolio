import React, { useEffect, useState } from "react";
import {
  AppWindow,
  ArrowRight,
  Check,
  LayoutTemplate,
  ShieldCheck,
  ShoppingCart,
} from "lucide-react";
import ScrollAnimator from "../components/ScrollAnimator";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

interface Service {
  id: number;
  name: string;
  slug: string;
}

type StackSlug = "foundation-stack" | "commerce-stack" | "application-stack";

type StackCardContent = {
  eyebrow: string;
  title: string;
  description: string;
  price: string;
  support: string;
  timeline: string;
  includes: string[];
  bestFit: string;
  cta: string;
  badge?: string;
};

type ServicesPageCopy = {
  hero: {
    eyebrow: string;
    title_line_1: string;
    title_line_2: string;
    body: string;
    body_support: string;
    primary_cta: string;
    secondary_cta: string;
  };
  pain: {
    title: string;
    items: string[];
    lead_line: string;
    line_1: string;
    line_2: string;
    line_3: string;
  };
  discovery: {
    eyebrow: string;
    required_badge: string;
    title: string;
    intro: string;
    leave_with_label: string;
    outcomes: string[];
    sales_line_1: string;
    sales_line_2: string;
    deliverables: string[];
    price_label: string;
    price_value: string;
    price_note: string;
    cta: string;
  };
  stacks: {
    eyebrow: string;
    title: string;
    intro: string;
    pricing_note: string;
    includes_label: string;
    best_fit_label: string;
    cards: Record<StackSlug, StackCardContent>;
  };
  why_custom: {
    eyebrow: string;
    title: string;
    lead: string;
    intro: string;
    items: string[];
    turning_point: string;
    pressure_line: string;
    design_line: string;
    summary_line: string;
  };
  process: {
    eyebrow: string;
    title: string;
    steps: Array<{
      title: string;
      body: string;
    }>;
  };
  cta: {
    title: string;
    line_1: string;
    body: string;
    primary: string;
    secondary: string;
  };
};

const STACK_ORDER: StackSlug[] = [
  "foundation-stack",
  "commerce-stack",
  "application-stack",
];

const iconMap = {
  layout: LayoutTemplate,
  "shopping-cart": ShoppingCart,
  server: AppWindow,
} as const;

const stackIconBySlug: Record<StackSlug, keyof typeof iconMap> = {
  "foundation-stack": "layout",
  "commerce-stack": "shopping-cart",
  "application-stack": "server",
};

const ServicesSection: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const { t, i18n } = useTranslation();
  const copy = t("services_page_v2", { returnObjects: true }) as ServicesPageCopy;

  useEffect(() => {
    const fetchServices = async () => {
      setLoading(true);
      try {
        const response = await fetch("/api/services/", {
          headers: {
            "Accept-Language": i18n.language,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = (await response.json()) as Service[];
        setServices(data);
      } catch (error) {
        console.error("Error fetching services:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, [i18n.language]);

  const availableSlugSet = new Set(services.map((service) => service.slug));
  const showAllStacks = loading || availableSlugSet.size === 0;
  const visibleStacks = STACK_ORDER.filter(
    (slug) => showAllStacks || availableSlugSet.has(slug),
  );

  return (
    <section className="py-16 sm:py-20 glassmorphism">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10 sm:space-y-12">
        <ScrollAnimator>
          <div className="text-center max-w-4xl mx-auto">
            <p className="text-xs sm:text-sm uppercase tracking-[0.2em] secondary font-semibold mb-3">
              {copy.hero.eyebrow}
            </p>
            <h1 className="text-3xl sm:text-5xl font-bold text-primary mb-4">
              {copy.hero.title_line_1}
              <br className="hidden sm:block" /> {copy.hero.title_line_2}
            </h1>
            <p className="text-base sm:text-lg text-secondary leading-relaxed">
              {copy.hero.body}
            </p>
            <p className="text-base sm:text-lg text-secondary leading-relaxed mt-3">
              {copy.hero.body_support}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4 mt-7">
              <a
                href="#service-stacks"
                className="inline-flex items-center justify-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                {copy.hero.primary_cta}
                <ArrowRight size={16} className="ml-2" />
              </a>
              <Link
                to="/quote"
                className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
              >
                {copy.hero.secondary_cta}
              </Link>
            </div>
          </div>
        </ScrollAnimator>

        <ScrollAnimator delay={0.05}>
          <section className="glassmorphism rounded-2xl p-5 sm:p-8 border border-secondary/20">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-5">
              {copy.pain.title}
            </h2>
            <ul className="space-y-3 mb-5">
              {copy.pain.items.map((point, index) => (
                <li key={`pain-${index}`} className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-primary mt-1 shrink-0" />
                  <span className="text-sm sm:text-base text-secondary leading-relaxed">
                    {point}
                  </span>
                </li>
              ))}
            </ul>
            <p className="text-sm sm:text-base text-primary font-semibold">
              {copy.pain.lead_line}
            </p>
            <p className="text-sm sm:text-base text-primary font-semibold mt-2">
              {copy.pain.line_1}
            </p>
            <p className="text-sm sm:text-base text-primary font-semibold mt-2">
              {copy.pain.line_2}
            </p>
            <p className="text-sm sm:text-base text-primary font-semibold mt-2">
              {copy.pain.line_3}
            </p>
          </section>
        </ScrollAnimator>

        <ScrollAnimator delay={0.1}>
          <section className="glassmorphism rounded-2xl p-5 sm:p-8 border border-secondary/20">
            <div className="grid lg:grid-cols-[1.35fr_0.65fr] gap-6 sm:gap-8 items-start">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-primary font-semibold mb-3">
                  {copy.discovery.eyebrow}
                </p>
                <span className="inline-flex items-center rounded-full border border-secondary/20 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary mb-4">
                  {copy.discovery.required_badge}
                </span>
                <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-3">
                  {copy.discovery.title}
                </h2>
                <p className="text-sm sm:text-base text-secondary leading-relaxed mb-3">
                  {copy.discovery.intro}
                </p>
                <p className="text-sm sm:text-base text-secondary leading-relaxed mb-4">
                  {copy.discovery.leave_with_label}
                </p>
                <ul className="space-y-2 mb-5">
                  {copy.discovery.outcomes.map((item, index) => (
                    <li key={`outcome-${index}`} className="flex items-start gap-2">
                      <Check className="w-4 h-4 text-primary mt-1 shrink-0" />
                      <span className="text-sm text-secondary leading-relaxed">
                        {item}
                      </span>
                    </li>
                  ))}
                </ul>
                <p className="text-sm sm:text-base text-secondary leading-relaxed mb-4">
                  {copy.discovery.sales_line_1}
                </p>
                <p className="text-sm sm:text-base text-secondary leading-relaxed mb-4">
                  {copy.discovery.sales_line_2}
                </p>
                <ul className="grid sm:grid-cols-2 gap-3">
                  {copy.discovery.deliverables.map((item, index) => (
                    <li key={`deliverable-${index}`} className="flex items-start gap-2">
                      <Check className="w-4 h-4 text-primary mt-1 shrink-0" />
                      <span className="text-sm text-secondary leading-relaxed">
                        {item}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
                <p className="text-xs uppercase tracking-[0.16em] text-secondary mb-1">
                  {copy.discovery.price_label}
                </p>
                <p className="text-3xl font-bold text-primary mb-2">
                  {copy.discovery.price_value}
                </p>
                <p className="text-sm text-secondary mb-5">
                  {copy.discovery.price_note}
                </p>
                <Link
                  to="/quote"
                  className="w-full inline-flex items-center justify-center px-5 py-3 rounded-xl button-gradient text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  {copy.discovery.cta}
                  <ArrowRight size={16} className="ml-2" />
                </Link>
              </div>
            </div>
          </section>
        </ScrollAnimator>

        <ScrollAnimator delay={0.15}>
          <section id="service-stacks">
            <p className="text-xs sm:text-sm uppercase tracking-[0.2em] secondary font-semibold mb-3 text-center">
              {copy.stacks.eyebrow}
            </p>
            <h2 className="text-2xl sm:text-4xl font-bold text-primary text-center mb-3">
              {copy.stacks.title}
            </h2>
            <p className="text-sm sm:text-base text-secondary leading-relaxed text-center max-w-3xl mx-auto mb-3">
              {copy.stacks.intro}
            </p>
            <p className="text-xs sm:text-sm text-secondary/90 text-center max-w-3xl mx-auto mb-6 sm:mb-8">
              {copy.stacks.pricing_note}
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6">
              {visibleStacks.map((slug) => {
                const stack = copy.stacks.cards[slug];
                const IconComponent = iconMap[stackIconBySlug[slug]];

                return (
                  <article
                    key={slug}
                    className="relative glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20 flex flex-col"
                  >
                    {stack.badge && (
                      <span className="absolute top-4 right-4 text-xs font-semibold rounded-full px-3 py-1 bg-primary/10 border border-secondary/20 text-primary">
                        {stack.badge}
                      </span>
                    )}

                    <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                      <IconComponent className="w-5 h-5 text-primary" />
                    </div>

                    <p className="text-xs uppercase tracking-[0.16em] secondary font-semibold mb-2">
                      {stack.eyebrow}
                    </p>
                    <h3 className="text-xl font-bold text-primary mb-2">
                      {stack.title}
                    </h3>
                    <p className="text-sm text-secondary leading-relaxed mb-4">
                      {stack.description}
                    </p>

                    <div className="rounded-xl border border-secondary/20 bg-primary/5 p-4 mb-4">
                      <p className="text-sm font-semibold text-primary mb-2">
                        {stack.price}
                      </p>
                      <p className="text-xs text-secondary mb-2">
                        {stack.support}
                      </p>
                      <p className="text-xs text-secondary">{stack.timeline}</p>
                    </div>

                    <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-2">
                      {copy.stacks.includes_label}
                    </p>
                    <ul className="space-y-2 mb-4">
                      {stack.includes.map((feature, index) => (
                        <li key={`${slug}-feature-${index}`} className="flex items-start gap-2">
                          <Check className="w-4 h-4 text-primary mt-1 shrink-0" />
                          <span className="text-sm text-secondary leading-relaxed">
                            {feature}
                          </span>
                        </li>
                      ))}
                    </ul>

                    <div className="rounded-xl border border-secondary/20 bg-surface/40 p-3 mb-5">
                      <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                        {copy.stacks.best_fit_label}
                      </p>
                      <p className="text-sm text-secondary leading-relaxed">
                        {stack.bestFit}
                      </p>
                    </div>

                    <Link
                      to={`/services/${slug}`}
                      className="mt-auto w-full inline-flex items-center justify-center px-5 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
                    >
                      {stack.cta}
                      <ArrowRight size={16} className="ml-2" />
                    </Link>
                  </article>
                );
              })}
            </div>
          </section>
        </ScrollAnimator>

        <ScrollAnimator delay={0.2}>
          <section className="glassmorphism rounded-2xl p-5 sm:p-8 border border-secondary/20">
            <p className="text-xs uppercase tracking-[0.18em] secondary font-semibold mb-3 text-center">
              {copy.why_custom.eyebrow}
            </p>
            <h3 className="text-2xl sm:text-3xl font-bold text-primary text-center mb-5">
              {copy.why_custom.title}
            </h3>
            <p className="text-sm sm:text-base text-secondary leading-relaxed text-center max-w-3xl mx-auto mb-5">
              {copy.why_custom.lead}
            </p>
            <p className="text-sm sm:text-base text-secondary leading-relaxed text-center max-w-3xl mx-auto mb-3">
              {copy.why_custom.intro}
            </p>
            <ul className="space-y-2 w-fit mx-auto mb-6 text-left">
              {copy.why_custom.items.map((item, index) => (
                <li key={`why-custom-${index}`} className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-primary mt-1 shrink-0" />
                  <span className="text-sm sm:text-base text-secondary leading-relaxed">
                    {item}
                  </span>
                </li>
              ))}
            </ul>
            <p className="text-sm sm:text-base text-primary font-semibold text-center mb-2">
              {copy.why_custom.turning_point}
            </p>
            <p className="text-sm sm:text-base text-secondary leading-relaxed text-center max-w-3xl mx-auto mb-2">
              {copy.why_custom.pressure_line}
            </p>
            <p className="text-sm sm:text-base text-secondary leading-relaxed text-center max-w-3xl mx-auto mb-2">
              {copy.why_custom.design_line}
            </p>
            <p className="text-sm sm:text-base text-secondary leading-relaxed text-center max-w-3xl mx-auto">
              {copy.why_custom.summary_line}
            </p>
          </section>
        </ScrollAnimator>

        <ScrollAnimator delay={0.25}>
          <section className="glassmorphism rounded-2xl p-5 sm:p-8 border border-secondary/20">
            <p className="text-xs uppercase tracking-[0.18em] secondary font-semibold mb-3 text-center">
              {copy.process.eyebrow}
            </p>
            <h3 className="text-2xl sm:text-3xl font-bold text-primary text-center mb-6">
              {copy.process.title}
            </h3>
            <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
              {copy.process.steps.map((step, index) => (
                <article
                  key={step.title}
                  className="group rounded-xl border border-secondary/20 p-4 bg-surface/40 transition-all duration-300 hover:border-primary/25"
                >
                  <div className="w-11 h-11 rounded-full bg-gradient-to-br from-primary/25 to-primary/10 border border-primary/30 text-primary text-base font-bold flex items-center justify-center mb-3 shadow-[0_10px_24px_-14px_var(--secondary-light)] dark:shadow-[0_10px_24px_-14px_var(--secondary-dark)] transition-transform duration-300 group-hover:scale-105">
                    {index + 1}
                  </div>
                  <h4 className="text-base font-semibold text-primary mb-2">
                    {step.title}
                  </h4>
                  <p className="text-sm text-secondary leading-relaxed">
                    {step.body}
                  </p>
                </article>
              ))}
            </div>
          </section>
        </ScrollAnimator>

        <ScrollAnimator delay={0.3}>
          <section className="glassmorphism rounded-3xl p-6 sm:p-10 border border-secondary/20 text-center">
            <h3 className="text-2xl sm:text-4xl font-bold text-primary mb-4">
              {copy.cta.title}
            </h3>
            <p className="text-sm sm:text-base text-secondary leading-relaxed max-w-3xl mx-auto mb-2">
              {copy.cta.line_1}
            </p>
            <p className="text-sm sm:text-base text-secondary leading-relaxed max-w-3xl mx-auto mb-6">
              {copy.cta.body}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4">
              <Link
                to="/quote"
                className="inline-flex items-center justify-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                {copy.cta.primary}
                <ArrowRight size={16} className="ml-2" />
              </Link>
              <Link
                to="/contact"
                className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
              >
                <ShieldCheck size={16} className="mr-2" />
                {copy.cta.secondary}
              </Link>
            </div>
          </section>
        </ScrollAnimator>
      </div>
    </section>
  );
};

export default ServicesSection;

