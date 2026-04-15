import React, { useEffect, useState } from "react";
import {
  AppWindow,
  ArrowRight,
  Check,
  LayoutTemplate,
  Search,
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
  service_type: string;
  short_description: string;
  description: string;
  features_list: string[];
  starting_price: string;
  delivery_time: string;
  icon: string;
  featured: boolean;
  active: boolean;
  order: number;
}

interface StackOverrideCopy {
  tier: string;
  hook: string;
  ideal: string;
  support_price: string;
  badge?: string;
}

interface ServicesCopy {
  hero: {
    eyebrow: string;
    title: string;
    summary: string;
  };
  discovery: {
    eyebrow: string;
    required_badge: string;
    summary: string;
    price_label: string;
    credit_note: string;
    cta: string;
  };
  stacks: {
    eyebrow: string;
    title: string;
    intro: string;
    scope_note: string;
    timeline_label: string;
    from_price_label: string;
    fixed_price_label: string;
    support_from_label: string;
    includes_label: string;
    ideal_for_label: string;
    detail_cta: string;
    featured_badge: string;
  };
  stack_overrides: Record<string, StackOverrideCopy>;
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
    description: string;
    primary: string;
    secondary: string;
  };
}

const iconMap = {
  search: Search,
  layout: LayoutTemplate,
  "shopping-cart": ShoppingCart,
  server: AppWindow,
};

const ServicesSection: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const { t, i18n } = useTranslation();

  const copy = t("services_page_v2", { returnObjects: true }) as ServicesCopy;

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

  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName as keyof typeof iconMap] || LayoutTemplate;
    return IconComponent;
  };

  const discoveryService = services.find(
    (service) => service.slug === "strategic-discovery-session",
  );
  const stackServices = services.filter(
    (service) => service.slug !== "strategic-discovery-session",
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-400 dark:border-purple-600" />
      </div>
    );
  }

  return (
    <section className="py-16 sm:py-20 glassmorphism">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10 sm:space-y-12">
        <ScrollAnimator>
          <div className="text-center max-w-4xl mx-auto">
            <p className="text-xs sm:text-sm uppercase tracking-[0.2em] secondary font-semibold mb-3">
              {copy.hero.eyebrow}
            </p>
            <h1 className="text-3xl sm:text-5xl font-bold text-primary mb-4">
              {copy.hero.title}
            </h1>
            <p className="text-base sm:text-lg text-secondary leading-relaxed">
              {copy.hero.summary}
            </p>
          </div>
        </ScrollAnimator>

        {discoveryService && (
          <ScrollAnimator delay={0.05}>
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
                    {discoveryService.name}
                  </h2>
                  <p className="text-sm sm:text-base text-secondary leading-relaxed mb-4">
                    {copy.discovery.summary}
                  </p>
                  <ul className="grid sm:grid-cols-2 gap-3">
                    {discoveryService.features_list.slice(0, 4).map((feature) => (
                      <li key={feature} className="flex items-start gap-2">
                        <Check className="w-4 h-4 text-primary mt-1 shrink-0" />
                        <span className="text-sm text-secondary leading-relaxed">
                          {feature}
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
                    {discoveryService.starting_price}
                  </p>
                  <p className="text-sm text-secondary mb-5">{copy.discovery.credit_note}</p>
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
        )}

        <ScrollAnimator delay={0.1}>
          <section>
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
              {copy.stacks.scope_note}
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6">
              {stackServices.map((service) => {
                const IconComponent = getIcon(service.icon);
                const serviceCopy = copy.stack_overrides[service.slug];
                const isFeatured = Boolean(serviceCopy?.badge);

                return (
                  <article
                    key={service.id}
                    className="relative glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20 flex flex-col"
                  >
                    {isFeatured && (
                      <span className="absolute top-4 right-4 text-xs font-semibold rounded-full px-3 py-1 bg-primary/10 border border-secondary/20 text-primary">
                        {serviceCopy.badge || copy.stacks.featured_badge}
                      </span>
                    )}

                    <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                      <IconComponent className="w-5 h-5 text-primary" />
                    </div>

                    <p className="text-xs uppercase tracking-[0.16em] secondary font-semibold mb-2">
                      {serviceCopy?.tier || service.name}
                    </p>
                    <h3 className="text-xl font-bold text-primary mb-2">{service.name}</h3>
                    <p className="text-sm text-secondary leading-relaxed mb-4">
                      {serviceCopy?.hook || service.short_description}
                    </p>

                    <div className="rounded-xl border border-secondary/20 bg-primary/5 p-4 mb-4">
                      <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                        {copy.stacks.from_price_label}
                      </p>
                      <p className="text-2xl font-bold text-primary mb-3">{service.starting_price}</p>
                      <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                        {copy.stacks.support_from_label}
                      </p>
                      <p className="text-sm font-semibold text-primary">
                        {serviceCopy?.support_price || "-"}
                      </p>
                      <p className="text-xs text-secondary mt-3">
                        {copy.stacks.timeline_label}: {service.delivery_time}
                      </p>
                    </div>

                    <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-2">
                      {copy.stacks.includes_label}
                    </p>
                    <ul className="space-y-2 mb-4">
                      {service.features_list.slice(0, 6).map((feature) => (
                        <li key={feature} className="flex items-start gap-2">
                          <Check className="w-4 h-4 text-primary mt-1 shrink-0" />
                          <span className="text-sm text-secondary leading-relaxed">{feature}</span>
                        </li>
                      ))}
                    </ul>

                    <div className="rounded-xl border border-secondary/20 bg-surface/40 p-3 mb-5">
                      <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                        {copy.stacks.ideal_for_label}
                      </p>
                      <p className="text-sm text-secondary leading-relaxed">
                        {serviceCopy?.ideal || service.short_description}
                      </p>
                    </div>

                    <Link
                      to={`/services/${service.slug}`}
                      className="mt-auto w-full inline-flex items-center justify-center px-5 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
                    >
                      {copy.stacks.detail_cta}
                      <ArrowRight size={16} className="ml-2" />
                    </Link>
                  </article>
                );
              })}
            </div>
          </section>
        </ScrollAnimator>

        <ScrollAnimator delay={0.15}>
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
                  <h4 className="text-base font-semibold text-primary mb-2">{step.title}</h4>
                  <p className="text-sm text-secondary leading-relaxed">{step.body}</p>
                </article>
              ))}
            </div>
          </section>
        </ScrollAnimator>

        <ScrollAnimator delay={0.2}>
          <section className="glassmorphism rounded-3xl p-6 sm:p-10 border border-secondary/20 text-center">
            <h3 className="text-2xl sm:text-4xl font-bold text-primary mb-4">
              {copy.cta.title}
            </h3>
            <p className="text-sm sm:text-base text-secondary leading-relaxed max-w-3xl mx-auto mb-6">
              {copy.cta.description}
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
