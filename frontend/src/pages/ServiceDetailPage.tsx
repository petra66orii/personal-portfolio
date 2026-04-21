import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import SEO from "../components/SEO";
import {
  AlertTriangle,
  ArrowLeft,
  Check,
  CheckCircle,
  Coins,
  Rocket,
} from "lucide-react";
import { useTranslation } from "react-i18next";

type Service = {
  id: number;
  slug: string;
};

type StackSlug = "foundation-stack" | "commerce-stack" | "application-stack";

type StackDetailContent = {
  eyebrow: string;
  heroTitle: string;
  heroBody: string;
  heroBodySupport: string;
  summaryPrice: string;
  summaryTimeline: string;
  summaryFit: string;
  includesIntro: string;
  includesItems: string[];
  solvesItems: string[];
  whoFor: string[];
  notFor: string[];
  process: Array<{
    title: string;
    body: string;
  }>;
  pricingStart: string;
  pricingSupport: string;
  pricingNote: string;
  ctaHeading: string;
  ctaSubtext: string;
  ctaPrimary: string;
  ctaSecondary: string;
};

type ServiceDetailCopy = {
  seo_title_suffix: string;
  back_button: string;
  error_title: string;
  error_message: string;
  not_found: string;
  summary_labels: {
    pricing: string;
    timeline: string;
    best_fit: string;
  };
  sections: {
    includes_title: string;
    solves_title: string;
    fit_title: string;
    who_for_title: string;
    not_for_title: string;
    process_title: string;
    pricing_title: string;
    pricing_start_label: string;
    pricing_support_label: string;
  };
  fallback: StackDetailContent;
  stacks: Record<StackSlug, StackDetailContent>;
};

const ServiceDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const { t, i18n } = useTranslation();
  const copy = t("service_detail_page_v2", {
    returnObjects: true,
  }) as ServiceDetailCopy;

  useEffect(() => {
    const fetchService = async () => {
      setLoading(true);
      setHasError(false);

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
        setHasError(true);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchService();
  }, [slug, i18n.language]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary" />
      </div>
    );
  }

  if (hasError || !service) {
    return (
      <div className="text-center py-20">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-500" />
        <h2 className="mt-4 text-2xl font-bold text-primary">{copy.error_title}</h2>
        <p className="mt-2 text-secondary">{copy.not_found}</p>
        <Link
          to="/services"
          className="mt-6 inline-block text-primary hover:underline"
        >
          &larr; {copy.back_button}
        </Link>
      </div>
    );
  }

  const detail =
    slug && slug in copy.stacks
      ? copy.stacks[slug as StackSlug]
      : copy.fallback;

  const seoTitle = `${detail.heroTitle}${copy.seo_title_suffix}`;
  const seoDescription = `${detail.heroBody} ${detail.heroBodySupport}`;

  return (
    <>
      <SEO title={seoTitle} description={seoDescription} />

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
              {detail.eyebrow}
            </p>
            <h1 className="text-3xl sm:text-5xl font-bold mb-4 text-primary">
              {detail.heroTitle}
            </h1>
            <p className="text-sm sm:text-lg text-secondary leading-relaxed max-w-4xl mb-3">
              {detail.heroBody}
            </p>
            <p className="text-sm sm:text-lg text-secondary leading-relaxed max-w-4xl mb-6">
              {detail.heroBodySupport}
            </p>

            <div className="grid sm:grid-cols-3 gap-3 sm:gap-4">
              <div className="rounded-xl border border-secondary/20 bg-primary/10 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {copy.summary_labels.pricing}
                </p>
                <p className="text-sm sm:text-base font-semibold text-primary">
                  {detail.summaryPrice}
                </p>
              </div>
              <div className="rounded-xl border border-secondary/20 bg-primary/10 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {copy.summary_labels.timeline}
                </p>
                <p className="text-sm sm:text-base font-semibold text-primary">
                  {detail.summaryTimeline}
                </p>
              </div>
              <div className="rounded-xl border border-secondary/20 bg-primary/10 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {copy.summary_labels.best_fit}
                </p>
                <p className="text-sm font-semibold text-primary leading-snug">
                  {detail.summaryFit}
                </p>
              </div>
            </div>
          </section>

          <div className="grid xl:grid-cols-[1.15fr_0.85fr] gap-6 sm:gap-8 items-start mb-8 sm:mb-10">
            <section className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
              <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-3">
                {copy.sections.includes_title}
              </h2>
              <p className="text-sm sm:text-base text-secondary leading-relaxed mb-4">
                {detail.includesIntro}
              </p>
              <ul className="grid sm:grid-cols-2 gap-3">
                {detail.includesItems.map((feature, index) => (
                  <li key={`includes-${index}`} className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 mt-1 shrink-0 text-primary" />
                    <span className="text-sm text-secondary leading-relaxed">
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
              <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-4">
                {copy.sections.solves_title}
              </h2>
              <ul className="space-y-3">
                {detail.solvesItems.map((item, index) => (
                  <li key={`solves-${index}`} className="flex items-start gap-2">
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
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-5">
              {copy.sections.fit_title}
            </h2>
            <div className="grid md:grid-cols-2 gap-5">
              <article className="rounded-xl border border-secondary/20 p-4 bg-surface/40">
                <h3 className="text-base sm:text-lg font-semibold text-primary mb-3">
                  {copy.sections.who_for_title}
                </h3>
                <ul className="space-y-2">
                  {detail.whoFor.map((item, index) => (
                    <li key={`who-for-${index}`} className="flex items-start gap-2">
                      <Check className="w-4 h-4 mt-1 shrink-0 text-primary" />
                      <span className="text-sm text-secondary leading-relaxed">
                        {item}
                      </span>
                    </li>
                  ))}
                </ul>
              </article>
              <article className="rounded-xl border border-secondary/20 p-4 bg-surface/40">
                <h3 className="text-base sm:text-lg font-semibold text-primary mb-3">
                  {copy.sections.not_for_title}
                </h3>
                <ul className="space-y-2">
                  {detail.notFor.map((item, index) => (
                    <li key={`not-for-${index}`} className="flex items-start gap-2">
                      <Check className="w-4 h-4 mt-1 shrink-0 text-primary" />
                      <span className="text-sm text-secondary leading-relaxed">
                        {item}
                      </span>
                    </li>
                  ))}
                </ul>
              </article>
            </div>
          </section>

          <section className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20 mb-8 sm:mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-5 flex items-center gap-2">
              <Rocket size={24} />
              {copy.sections.process_title}
            </h2>
            <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
              {detail.process.map((step, index) => (
                <article
                  key={`${step.title}-${index}`}
                  className="group rounded-xl border border-secondary/20 p-4 transition-all duration-300 hover:border-primary/25"
                >
                  <div className="w-11 h-11 rounded-full bg-gradient-to-br from-primary/25 to-primary/10 border border-primary/30 text-primary text-base font-bold flex items-center justify-center mb-3 shadow-[0_10px_24px_-14px_var(--secondary-light)] dark:shadow-[0_10px_24px_-14px_var(--secondary-dark)] transition-transform duration-300 group-hover:scale-105">
                    {index + 1}
                  </div>
                  <h3 className="text-base font-semibold text-primary mb-2">
                    {step.title}
                  </h3>
                  <p className="text-sm text-secondary leading-relaxed">
                    {step.body}
                  </p>
                </article>
              ))}
            </div>
          </section>

          <section className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20 mb-8 sm:mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-5 flex items-center gap-2">
              <Coins size={24} />
              {copy.sections.pricing_title}
            </h2>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div className="rounded-xl border border-secondary/20 p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {copy.sections.pricing_start_label}
                </p>
                <p className="text-lg font-semibold text-primary">
                  {detail.pricingStart}
                </p>
              </div>
              <div className="rounded-xl border border-secondary/20 p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-secondary mb-1">
                  {copy.sections.pricing_support_label}
                </p>
                <p className="text-lg font-semibold text-primary">
                  {detail.pricingSupport}
                </p>
              </div>
            </div>
            <p className="text-xs sm:text-sm text-secondary">{detail.pricingNote}</p>
          </section>

          <section className="glassmorphism rounded-3xl p-6 sm:p-8 border border-secondary/20 text-center">
            <h2 className="text-2xl sm:text-4xl font-bold text-primary mb-4">
              {detail.ctaHeading}
            </h2>
            <p className="text-sm sm:text-base text-secondary max-w-3xl mx-auto mb-6">
              {detail.ctaSubtext}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4">
              <Link
                to="/quote"
                className="inline-flex items-center justify-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                {detail.ctaPrimary}
              </Link>
              <Link
                to="/services"
                className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
              >
                {detail.ctaSecondary}
              </Link>
            </div>
          </section>
        </div>
      </main>
    </>
  );
};

export default ServiceDetailPage;
