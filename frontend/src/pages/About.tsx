import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import SEO from "../components/SEO";
import ScrollAnimator from "../components/ScrollAnimator";
import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  Cpu,
  Globe2,
  Handshake,
  MapPin,
  ShieldCheck,
} from "lucide-react";

type TrustCard = {
  icon: "location" | "years" | "stack" | "response" | "engagement" | "markets";
  label: string;
  value: string;
  sub: string;
};

type AboutCopy = {
  seo_title: string;
  seo_description: string;
  hero: {
    eyebrow: string;
    title: string;
    summary: string;
    fit_label: string;
    fit_points: string[];
  };
  mission: {
    eyebrow: string;
    title: string;
    body: string;
    side_intro: string;
    side_points: string[];
  };
  status: {
    live_label: string;
    response_label: string;
  };
  trust: {
    eyebrow: string;
    title: string;
    intro: string;
    cards: TrustCard[];
  };
  founder: {
    eyebrow: string;
    title: string;
    summary: string;
    points: Array<{
      title: string;
      body: string;
    }>;
  };
  qualifications: {
    eyebrow: string;
    title: string;
    provider: string;
    provider_sub: string;
    diploma: string;
    awarded: string;
    grade: string;
    credit: string;
    badge: string;
  };
  cta: {
    title: string;
    body: string;
    primary: string;
    secondary: string;
  };
};

const trustIconMap = {
  location: MapPin,
  years: ShieldCheck,
  stack: Cpu,
  response: Clock3,
  engagement: Handshake,
  markets: Globe2,
} as const;

const About = () => {
  const { t } = useTranslation();
  const copy = t("about_page", { returnObjects: true }) as AboutCopy;

  return (
    <>
      <SEO
        title={copy.seo_title}
        description={copy.seo_description}
        type="website"
      />

      <main className="min-h-screen p-3 sm:p-6">
        <div className="glassmorphism backdrop-blur-sm rounded-2xl shadow-xl max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-8 sm:py-12 border">
          <ScrollAnimator>
            <section className="mb-10 sm:mb-14">
              <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3">
                {copy.hero.eyebrow}
              </p>
              <div className="grid lg:grid-cols-[1.2fr_0.8fr] gap-6 sm:gap-8 items-start">
                <div>
                  <h1 className="text-3xl sm:text-5xl font-bold text-primary leading-tight mb-4">
                    {copy.hero.title}
                  </h1>
                  <p className="text-base sm:text-lg text-secondary leading-relaxed">
                    {copy.hero.summary}
                  </p>
                </div>
                <div className="glassmorphism rounded-2xl p-5 sm:p-6 border border-secondary/20">
                  <p className="text-xs uppercase tracking-[0.16em] text-secondary mb-3">
                    {copy.hero.fit_label}
                  </p>
                  <div className="space-y-3">
                    {copy.hero.fit_points.map((point) => (
                      <div key={point} className="flex items-start gap-2">
                        <CheckCircle2 className="text-primary mt-0.5 shrink-0" size={16} />
                        <p className="text-sm sm:text-base text-secondary leading-relaxed">
                          {point}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </ScrollAnimator>

          <ScrollAnimator delay={0.05}>
            <section className="mb-8 sm:mb-10 glassmorphism rounded-2xl p-5 sm:p-8 border border-secondary/20">
              <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3">
                {copy.mission.eyebrow}
              </p>
              <div className="grid lg:grid-cols-[1fr_auto_1fr] gap-5 sm:gap-8 items-start">
                <div>
                  <h2 className="text-2xl sm:text-4xl font-bold text-primary mb-4">
                    {copy.mission.title}
                  </h2>
                  <p className="text-sm sm:text-base text-secondary leading-relaxed">
                    {copy.mission.body}
                  </p>
                </div>
                <div className="hidden lg:block w-px self-stretch bg-secondary/20" />
                <div>
                  <p className="text-sm sm:text-base text-secondary leading-relaxed mb-3">
                    {copy.mission.side_intro}
                  </p>
                  <div className="space-y-2">
                    {copy.mission.side_points.map((point) => (
                      <p key={point} className="text-sm sm:text-base text-primary font-medium">
                        {point}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </ScrollAnimator>

          <ScrollAnimator delay={0.1}>
            <section className="mb-8 sm:mb-10 rounded-2xl bg-primary/10 border border-secondary/20 px-4 sm:px-6 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-primary shadow-[0_0_0_4px_rgba(155,93,229,0.2)]" />
                <p className="text-sm sm:text-base font-semibold text-primary">
                  {copy.status.live_label}
                </p>
              </div>
              <p className="text-xs sm:text-sm text-secondary">
                {copy.status.response_label}
              </p>
            </section>
          </ScrollAnimator>

          <ScrollAnimator delay={0.15}>
            <section className="mb-10 sm:mb-12">
              <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3 text-center">
                {copy.trust.eyebrow}
              </p>
              <h2 className="text-2xl sm:text-4xl font-bold text-primary mb-4 text-center">
                {copy.trust.title}
              </h2>
              <p className="text-sm sm:text-base text-secondary leading-relaxed text-center max-w-3xl mx-auto mb-6 sm:mb-8">
                {copy.trust.intro}
              </p>

              <div className="grid gap-4 sm:gap-5 md:grid-cols-2 xl:grid-cols-3">
                {copy.trust.cards.map((card) => {
                  const Icon = trustIconMap[card.icon];
                  return (
                    <article
                      key={`${card.label}-${card.value}`}
                      className="glassmorphism rounded-2xl p-5 border border-secondary/20"
                    >
                      <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                        <Icon className="text-primary" size={18} />
                      </div>
                      <p className="text-xs uppercase tracking-[0.16em] text-secondary mb-2">
                        {card.label}
                      </p>
                      <h3 className="text-base sm:text-lg font-semibold text-primary mb-2">
                        {card.value}
                      </h3>
                      <p className="text-sm text-secondary leading-relaxed">{card.sub}</p>
                    </article>
                  );
                })}
              </div>
            </section>
          </ScrollAnimator>

          <ScrollAnimator delay={0.2}>
            <section className="mb-10 sm:mb-12 py-8 border-t border-secondary/20">
              <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3">
                {copy.founder.eyebrow}
              </p>
              <h2 className="text-2xl sm:text-4xl font-bold text-primary mb-4">
                {copy.founder.title}
              </h2>
              <p className="text-sm sm:text-base text-secondary leading-relaxed max-w-4xl mb-6">
                {copy.founder.summary}
              </p>
              <div className="grid md:grid-cols-3 gap-4 sm:gap-5">
                {copy.founder.points.map((point) => (
                  <div
                    key={point.title}
                    className="glassmorphism rounded-2xl p-5 border border-secondary/20"
                  >
                    <h3 className="text-base sm:text-lg font-semibold text-primary mb-2">
                      {point.title}
                    </h3>
                    <p className="text-sm text-secondary leading-relaxed">{point.body}</p>
                  </div>
                ))}
              </div>
            </section>
          </ScrollAnimator>

          <ScrollAnimator delay={0.25}>
            <section className="mb-10 sm:mb-12 py-8 border-t border-secondary/20">
              <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3">
                {copy.qualifications.eyebrow}
              </p>
              <div className="glassmorphism rounded-2xl p-5 sm:p-7 border border-secondary/20">
                <h2 className="text-xl sm:text-2xl font-bold text-primary mb-4">
                  {copy.qualifications.title}
                </h2>
                <div className="flex flex-col lg:flex-row lg:items-center gap-5">
                  <div className="flex items-center gap-3 lg:pr-5 lg:border-r lg:border-secondary/20">
                    <div className="w-10 h-10 rounded-lg bg-primary text-white font-bold text-sm flex items-center justify-center">
                      CI
                    </div>
                    <div>
                      <p className="text-sm sm:text-base font-semibold text-primary">
                        {copy.qualifications.provider}
                      </p>
                      <p className="text-xs text-secondary">{copy.qualifications.provider_sub}</p>
                    </div>
                  </div>

                  <div className="flex-1">
                    <p className="text-sm sm:text-base font-semibold text-primary mb-2">
                      {copy.qualifications.diploma}
                    </p>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs sm:text-sm text-secondary">
                      <span>{copy.qualifications.awarded}</span>
                      <span>{copy.qualifications.grade}</span>
                      <span>{copy.qualifications.credit}</span>
                    </div>
                  </div>

                  <span className="inline-flex w-fit items-center rounded-full bg-primary/10 border border-secondary/20 px-3 py-1 text-xs font-semibold text-primary">
                    {copy.qualifications.badge}
                  </span>
                </div>
              </div>
            </section>
          </ScrollAnimator>

          <ScrollAnimator delay={0.3}>
            <section className="pt-6 border-t border-secondary/20">
              <div className="glassmorphism rounded-3xl p-5 sm:p-8 border border-secondary/20 text-center">
                <h2 className="text-2xl sm:text-4xl font-bold text-primary mb-4">
                  {copy.cta.title}
                </h2>
                <p className="text-sm sm:text-base text-secondary leading-relaxed max-w-3xl mx-auto mb-6">
                  {copy.cta.body}
                </p>
                <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4">
                  <Link
                    to="/quote"
                    className="inline-flex items-center justify-center px-5 sm:px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
                  >
                    {copy.cta.primary}
                    <ArrowRight size={16} className="ml-2" />
                  </Link>
                  <Link
                    to="/services"
                    className="inline-flex items-center justify-center px-5 sm:px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
                  >
                    {copy.cta.secondary}
                  </Link>
                </div>
              </div>
            </section>
          </ScrollAnimator>
        </div>
      </main>
    </>
  );
};

export default About;
