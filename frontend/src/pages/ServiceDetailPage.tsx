import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import SEO from "../components/SEO";
import {
  AlertTriangle,
  ArrowLeft,
  Check,
  CheckCircle,
  Clock3,
  Coins,
  Rocket,
} from "lucide-react";
import { useTranslation } from "react-i18next";

type Service = {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  description: string;
  starting_price: string;
  delivery_time: string;
  features_list: string[];
};

type ServiceDetailContent = {
  eyebrow: string;
  fit: string;
  includes_intro: string;
  solves: string[];
  process: Array<{
    title: string;
    body: string;
  }>;
  pricing_points: string[];
  support_price: string;
  cta_primary: string;
  cta_secondary: string;
};

type ServiceDetailCopy = {
  back_button: string;
  error_title: string;
  error_message: string;
  not_found: string;
  price_label_from: string;
  price_label_fixed: string;
  timeline_label: string;
  fit_label: string;
  includes_title: string;
  solves_title: string;
  process_title: string;
  pricing_title: string;
  support_label: string;
  pricing_scope_note: string;
  details_map: Record<string, ServiceDetailContent>;
};

const fallbackDetail: ServiceDetailContent = {
  eyebrow: "Service",
  fit: "Growing teams",
  includes_intro:
    "A scoped service focused on business outcomes, delivery clarity, and maintainable implementation.",
  solves: [
    "Unclear technical scope before implementation starts.",
    "Gaps between business requirements and delivery execution.",
    "Need for a maintainable system that can scale with the business.",
  ],
  process: [
    {
      title: "Discovery",
      body: "We align on goals, constraints, and technical boundaries.",
    },
    {
      title: "Scope",
      body: "You receive a structured plan with deliverables and timeline.",
    },
    {
      title: "Build",
      body: "Implementation follows the approved scope and priorities.",
    },
    {
      title: "Launch",
      body: "Delivery includes handover plus support recommendations.",
    },
  ],
  pricing_points: [
    "The final proposal is scoped around your exact requirements.",
    "Discovery keeps delivery focused and reduces expensive changes later.",
  ],
  support_price: "Scope dependent",
  cta_primary: "Start with Discovery",
  cta_secondary: "Back to Services",
};

const ServiceDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { i18n, t } = useTranslation();
  const copy = t("service_detail_page_v2", { returnObjects: true }) as ServiceDetailCopy;

  useEffect(() => {
    const fetchService = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/services/${slug}/`, {
          headers: {
            "Accept-Language": i18n.language,
          },
        });

        if (!response.ok) {
          throw new Error(`Service not found. Status: ${response.status}`);
        }

        const data = (await response.json()) as Service;
        setService(data);
      } catch (err) {
        setError(copy.error_message);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchService();
  }, [slug, i18n.language, copy.error_message]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary" />
      </div>
    );
  }

  if (error || !service) {
    return (
      <div className="text-center py-20">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-500" />
        <h2 className="mt-4 text-2xl font-bold text-primary">{copy.error_title}</h2>
        <p className="mt-2 text-secondary">{error || copy.not_found}</p>
        <Link to="/services" className="mt-6 inline-block text-primary hover:underline">
          &larr; {copy.back_button}
        </Link>
      </div>
    );
  }

  const serviceDetail = copy.details_map[service.slug] || fallbackDetail;
  const isDiscoveryService = service.slug === "strategic-discovery-session";

  return (
    <>
      <SEO title={`${service.name} | Miss Bott`} description={service.short_description} />

      <main className="min-h-screen p-4 sm:p-6">
        <div className="max-w-6xl mx-auto">
          <Link
            to="/services"
            className="inline-flex items-center gap-2 text-secondary hover:text-primary mb-8"
          >
            <ArrowLeft size={16} /> {copy.back_button}
          </Link>

          <section className="glassmorphism rounded-2xl p-6 sm:p-8 border border-secondary/20 mb-8 sm:mb-10">
            <p className="text-xs uppercase tracking-[0.18em] secondary font-semibold mb-3">
              {serviceDetail.eyebrow}
            </p>
            <h1 className="text-3xl sm:text-5xl font-bold mb-4 text-primary">{service.name}</h1>
            <p className="text-sm sm:text-lg text-secondary leading-relaxed max-w-4xl mb-6">
              {service.description}
            </p>

            <div className="grid sm:grid-cols-3 gap-3 sm:gap-4">
              <div className="rounded-xl border border-secondary/20 bg-primary/10 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {isDiscoveryService ? copy.price_label_fixed : copy.price_label_from}
                </p>
                <p className="text-base sm:text-lg font-semibold text-primary">
                  {service.starting_price}
                </p>
              </div>
              <div className="rounded-xl border border-secondary/20 bg-primary/10 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {copy.timeline_label}
                </p>
                <p className="text-base sm:text-lg font-semibold text-primary">
                  {service.delivery_time}
                </p>
              </div>
              <div className="rounded-xl border border-secondary/20 bg-primary/10 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {copy.fit_label}
                </p>
                <p className="text-sm sm:text-base font-semibold text-primary leading-snug">
                  {serviceDetail.fit}
                </p>
              </div>
            </div>
          </section>

          <div className="grid xl:grid-cols-[1.15fr_0.85fr] gap-6 sm:gap-8 items-start mb-8 sm:mb-10">
            <section className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
              <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-3">
                {copy.includes_title}
              </h2>
              <p className="text-sm sm:text-base text-secondary leading-relaxed mb-4">
                {serviceDetail.includes_intro}
              </p>
              <ul className="grid sm:grid-cols-2 gap-3">
                {service.features_list.map((feature) => (
                  <li key={feature} className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 mt-1 shrink-0 text-primary" />
                    <span className="text-sm text-secondary leading-relaxed">{feature}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
              <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-4">
                {copy.solves_title}
              </h2>
              <ul className="space-y-3">
                {serviceDetail.solves.map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <Check className="w-4 h-4 mt-1 shrink-0 text-primary" />
                    <span className="text-sm sm:text-base text-secondary leading-relaxed">
                      {item}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          </div>

          <section className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20 mb-8 sm:mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-5 flex items-center gap-2">
              <Rocket size={24} />
              {copy.process_title}
            </h2>
            <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
              {serviceDetail.process.map((step, index) => (
                <article
                  key={step.title}
                  className="group rounded-xl border border-secondary/20 p-4 transition-all duration-300 hover:border-primary/25"
                >
                  <div className="w-11 h-11 rounded-full bg-gradient-to-br from-primary/25 to-primary/10 border border-primary/30 text-primary text-base font-bold flex items-center justify-center mb-3 shadow-[0_10px_24px_-14px_var(--secondary-light)] dark:shadow-[0_10px_24px_-14px_var(--secondary-dark)] transition-transform duration-300 group-hover:scale-105">
                    {index + 1}
                  </div>
                  <h3 className="text-base font-semibold text-primary mb-2">{step.title}</h3>
                  <p className="text-sm text-secondary leading-relaxed">{step.body}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20 mb-8 sm:mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-5 flex items-center gap-2">
              <Coins size={24} />
              {copy.pricing_title}
            </h2>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div className="rounded-xl border border-secondary/20 p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {isDiscoveryService ? copy.price_label_fixed : copy.price_label_from}
                </p>
                <p className="text-lg font-semibold text-primary">{service.starting_price}</p>
              </div>
              <div className="rounded-xl border border-secondary/20 p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {copy.support_label}
                </p>
                <p className="text-lg font-semibold text-primary">{serviceDetail.support_price}</p>
              </div>
            </div>
            <ul className="space-y-2 mb-4">
              {serviceDetail.pricing_points.map((point) => (
                <li key={point} className="flex items-start gap-2">
                  <Clock3 className="w-4 h-4 mt-1 shrink-0 text-primary" />
                  <span className="text-sm text-secondary leading-relaxed">{point}</span>
                </li>
              ))}
            </ul>
            <p className="text-xs sm:text-sm text-secondary">{copy.pricing_scope_note}</p>
          </section>

          <section className="glassmorphism rounded-3xl p-6 sm:p-8 border border-secondary/20 text-center">
            <h2 className="text-2xl sm:text-4xl font-bold text-primary mb-4">
              {serviceDetail.cta_primary}
            </h2>
            <p className="text-sm sm:text-base text-secondary max-w-3xl mx-auto mb-6">
              {service.short_description}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4">
              <Link
                to="/quote"
                className="inline-flex items-center justify-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                {serviceDetail.cta_primary}
              </Link>
              <Link
                to="/services"
                className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
              >
                {serviceDetail.cta_secondary}
              </Link>
            </div>
          </section>
        </div>
      </main>
    </>
  );
};

export default ServiceDetailPage;
