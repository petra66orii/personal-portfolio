import type { ElementType } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  ArrowLeft,
  ArrowRight,
  Bot,
  CheckCircle2,
  Database,
  ExternalLink,
  FileText,
  Github,
  Images,
  Lock,
  Printer,
  Server,
  ShieldCheck,
  ShoppingCart,
  Workflow,
} from "lucide-react";
import SEO from "./SEO";
import ScrollAnimator from "./ScrollAnimator";
import type { ProjectSummary } from "../utils/projects";

interface CaseStudyFact {
  label: string;
  value: string;
}

interface CaseStudyItem {
  title: string;
  body: string;
}

interface HighlightItem extends CaseStudyItem {
  tags?: string[];
}

interface CallToAction {
  title: string;
  body: string;
  primary: string;
  secondary: string;
}

interface SeoCopy {
  title: string;
  description: string;
  keywords: string;
}

interface OpenEireCopy {
  seo: SeoCopy;
  hero: {
    eyebrow: string;
    title: string;
    summary: string;
    facts: CaseStudyFact[];
    primaryCta: string;
    secondaryCta: string;
  };
  overview: {
    label: string;
    title: string;
    paragraphs: string[];
    statCards: CaseStudyFact[];
  };
  challenge: {
    label: string;
    title: string;
    intro: string;
    items: CaseStudyItem[];
  };
  solution: {
    label: string;
    title: string;
    intro: string;
    items: CaseStudyItem[];
  };
  highlights: {
    label: string;
    title: string;
    intro: string;
    items: HighlightItem[];
  };
  technical_snapshot: {
    label: string;
    title: string;
    intro: string;
    cards: CaseStudyItem[];
  };
  client_value: {
    label: string;
    title: string;
    intro: string;
    items: CaseStudyItem[];
  };
  cta: CallToAction;
}

const challengeIcons = [Lock, Images, Printer, Workflow];
const solutionIcons = [Server, ShieldCheck, ShoppingCart, Bot];
const highlightIcons = [FileText, Images, Printer, Bot];
const technicalIcons = [Server, Database, ShieldCheck, Workflow];

const getImageUrl = (imageUrl?: string) => {
  if (!imageUrl) {
    return "/assets/default-project.png";
  }
  if (imageUrl.startsWith("http") || imageUrl.startsWith("/")) {
    return imageUrl;
  }
  return `/media/${imageUrl}`;
};

const OpenEireCaseStudy = ({ project }: { project: ProjectSummary }) => {
  const { t } = useTranslation();
  const copy = t("case_studies.openeire", {
    returnObjects: true,
  }) as OpenEireCopy;

  const stackItems = project.tech_stack
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return (
    <>
      <SEO
        title={copy.seo.title}
        description={copy.seo.description}
        keywords={copy.seo.keywords}
        type="article"
        image={getImageUrl(project.image)}
      />

      <main className="min-h-screen p-6">
        <div className="max-w-6xl mx-auto">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-secondary hover:text-primary mb-8"
          >
            <ArrowLeft size={16} /> {t("project_detail_page.back_button")}
          </Link>

          <div className="glassmorphism backdrop-blur-sm rounded-lg shadow-xl p-6 md:p-12 border overflow-hidden">
            <ScrollAnimator>
              <section className="pb-12 border-b border-secondary/20">
                <p className="text-sm uppercase tracking-[0.2em] secondary font-semibold mb-4">
                  {copy.hero.eyebrow}
                </p>
                <div className="grid lg:grid-cols-[1.5fr_0.9fr] gap-10 items-start">
                  <div>
                    <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-primary leading-tight mb-6">
                      {copy.hero.title}
                    </h1>
                    <p className="text-lg text-secondary max-w-3xl leading-relaxed mb-8">
                      {copy.hero.summary}
                    </p>

                    <div className="flex flex-wrap gap-3 mb-8">
                      {stackItems.map((item) => (
                        <span
                          key={item}
                          className="px-3 py-1.5 rounded-full text-sm bg-primary/10 text-primary border border-secondary/20"
                        >
                          {item}
                        </span>
                      ))}
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4">
                      <Link
                        to="/quote"
                        className="inline-flex items-center justify-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
                      >
                        {copy.hero.primaryCta}
                        <ArrowRight size={16} className="ml-2" />
                      </Link>
                      <Link
                        to="/services"
                        className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
                      >
                        {copy.hero.secondaryCta}
                      </Link>
                    </div>
                  </div>

                  <div className="glassmorphism rounded-2xl p-6 border border-secondary/20 shadow-lg">
                    <h2 className="text-xl font-semibold text-primary mb-5">
                      {project.title}
                    </h2>
                    <dl className="space-y-4">
                      {copy.hero.facts.map((fact) => (
                        <div key={fact.label} className="border-b border-secondary/15 pb-4 last:border-b-0 last:pb-0">
                          <dt className="text-xs uppercase tracking-[0.16em] text-secondary mb-1">
                            {fact.label}
                          </dt>
                          <dd className="text-primary font-medium">{fact.value}</dd>
                        </div>
                      ))}
                    </dl>
                  </div>
                </div>
              </section>
            </ScrollAnimator>

            <ScrollAnimator delay={0.05}>
              <section className="py-12 border-b border-secondary/20">
                <div className="grid lg:grid-cols-[1.2fr_0.8fr] gap-10">
                  <div>
                    <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3">
                      {copy.overview.label}
                    </p>
                    <h2 className="text-3xl sm:text-4xl font-bold text-primary mb-5">
                      {copy.overview.title}
                    </h2>
                    <p className="text-lg text-secondary leading-relaxed mb-4">
                      {project.description}
                    </p>
                    {copy.overview.paragraphs.map((paragraph) => (
                      <p
                        key={paragraph}
                        className="text-secondary leading-relaxed mb-4 last:mb-0"
                      >
                        {paragraph}
                      </p>
                    ))}
                  </div>

                  <div className="grid gap-4">
                    {copy.overview.statCards.map((card) => (
                      <div
                        key={card.label}
                        className="glassmorphism rounded-2xl p-5 border border-secondary/20"
                      >
                        <p className="text-xs uppercase tracking-[0.16em] text-secondary mb-2">
                          {card.label}
                        </p>
                        <p className="text-primary text-lg font-semibold leading-snug">
                          {card.value}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            </ScrollAnimator>

            <ScrollAnimator delay={0.1}>
              <section className="py-12 border-b border-secondary/20">
                <div className="grid lg:grid-cols-2 gap-8">
                  <SectionCard
                    eyebrow={copy.challenge.label}
                    title={copy.challenge.title}
                    intro={project.client_challenge || copy.challenge.intro}
                    items={copy.challenge.items}
                    icons={challengeIcons}
                  />
                  <SectionCard
                    eyebrow={copy.solution.label}
                    title={copy.solution.title}
                    intro={project.my_solution || copy.solution.intro}
                    items={copy.solution.items}
                    icons={solutionIcons}
                  />
                </div>
              </section>
            </ScrollAnimator>

            <ScrollAnimator delay={0.15}>
              <section className="py-12 border-b border-secondary/20">
                <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3 text-center">
                  {copy.highlights.label}
                </p>
                <h2 className="text-3xl sm:text-4xl font-bold text-primary mb-4 text-center">
                  {copy.highlights.title}
                </h2>
                <p className="text-secondary text-center max-w-3xl mx-auto mb-10 leading-relaxed">
                  {copy.highlights.intro}
                </p>

                <div className="grid md:grid-cols-2 gap-6">
                  {copy.highlights.items.map((item, index) => {
                    const Icon = highlightIcons[index % highlightIcons.length];
                    return (
                      <div
                        key={item.title}
                        className="glassmorphism rounded-2xl p-6 border border-secondary/20 shadow-lg"
                      >
                        <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                          <Icon className="text-primary" size={22} />
                        </div>
                        <h3 className="text-xl font-semibold text-primary mb-3">
                          {item.title}
                        </h3>
                        <p className="text-secondary leading-relaxed mb-4">
                          {item.body}
                        </p>
                        {item.tags && item.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {item.tags.map((tag) => (
                              <span
                                key={tag}
                                className="px-2.5 py-1 rounded-full text-xs bg-surface border border-secondary/20 text-secondary"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </section>
            </ScrollAnimator>

            <ScrollAnimator delay={0.2}>
              <section className="py-12 border-b border-secondary/20">
                <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3 text-center">
                  {copy.technical_snapshot.label}
                </p>
                <h2 className="text-3xl sm:text-4xl font-bold text-primary mb-4 text-center">
                  {copy.technical_snapshot.title}
                </h2>
                <p className="text-secondary text-center max-w-3xl mx-auto mb-10 leading-relaxed">
                  {copy.technical_snapshot.intro}
                </p>

                <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-5">
                  {copy.technical_snapshot.cards.map((card, index) => {
                    const Icon = technicalIcons[index % technicalIcons.length];
                    return (
                      <div
                        key={card.title}
                        className="rounded-2xl border border-secondary/20 bg-surface/60 p-5"
                      >
                        <Icon className="text-primary mb-4" size={22} />
                        <h3 className="text-lg font-semibold text-primary mb-2">
                          {card.title}
                        </h3>
                        <p className="text-sm text-secondary leading-relaxed">
                          {card.body}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </section>
            </ScrollAnimator>

            <ScrollAnimator delay={0.25}>
              <section className="py-12 border-b border-secondary/20">
                <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3 text-center">
                  {copy.client_value.label}
                </p>
                <h2 className="text-3xl sm:text-4xl font-bold text-primary mb-4 text-center">
                  {copy.client_value.title}
                </h2>
                <p className="text-secondary text-center max-w-3xl mx-auto mb-10 leading-relaxed">
                  {project.the_result || copy.client_value.intro}
                </p>

                <div className="grid md:grid-cols-3 gap-6">
                  {copy.client_value.items.map((item) => (
                    <div
                      key={item.title}
                      className="glassmorphism rounded-2xl p-6 border border-secondary/20"
                    >
                      <CheckCircle2 className="text-primary mb-4" size={22} />
                      <h3 className="text-xl font-semibold text-primary mb-3">
                        {item.title}
                      </h3>
                      <p className="text-secondary leading-relaxed">{item.body}</p>
                    </div>
                  ))}
                </div>
              </section>
            </ScrollAnimator>

            <ScrollAnimator delay={0.3}>
              <section className="pt-12">
                <div className="glassmorphism rounded-3xl p-8 md:p-10 border border-secondary/20 text-center">
                  <h2 className="text-3xl sm:text-4xl font-bold text-primary mb-4">
                    {copy.cta.title}
                  </h2>
                  <p className="text-secondary text-lg leading-relaxed max-w-3xl mx-auto mb-8">
                    {copy.cta.body}
                  </p>

                  <div className="flex flex-col sm:flex-row justify-center gap-4">
                    <Link
                      to="/quote"
                      className="inline-flex items-center justify-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
                    >
                      {copy.cta.primary}
                      <ArrowRight size={16} className="ml-2" />
                    </Link>
                    <Link
                      to="/services"
                      className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
                    >
                      {copy.cta.secondary}
                    </Link>
                    {project.live_link && (
                      <a
                        href={project.live_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
                      >
                        <ExternalLink size={16} className="mr-2" />
                        {t("project_detail_page.live_link")}
                      </a>
                    )}
                    {project.repo_link && (
                      <a
                        href={project.repo_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
                      >
                        <Github size={16} className="mr-2" />
                        {t("project_detail_page.repo_link")}
                      </a>
                    )}
                  </div>
                </div>
              </section>
            </ScrollAnimator>
          </div>
        </div>
      </main>
    </>
  );
};

interface SectionCardProps {
  eyebrow: string;
  title: string;
  intro: string;
  items: CaseStudyItem[];
  icons: ElementType[];
}

const SectionCard = ({
  eyebrow,
  title,
  intro,
  items,
  icons,
}: SectionCardProps) => (
  <div className="glassmorphism rounded-3xl p-6 md:p-8 border border-secondary/20">
    <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3">
      {eyebrow}
    </p>
    <h2 className="text-3xl font-bold text-primary mb-4">{title}</h2>
    <p className="text-secondary leading-relaxed mb-8">{intro}</p>

    <div className="space-y-5">
      {items.map((item, index) => {
        const Icon = icons[index % icons.length];
        return (
          <div key={item.title} className="flex gap-4 items-start">
            <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
              <Icon className="text-primary" size={20} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary mb-1.5">
                {item.title}
              </h3>
              <p className="text-secondary leading-relaxed">{item.body}</p>
            </div>
          </div>
        );
      })}
    </div>
  </div>
);

export default OpenEireCaseStudy;
