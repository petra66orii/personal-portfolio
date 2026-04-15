import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import SEO from "../components/SEO";
import {
  ArrowLeft,
  ExternalLink,
  Github,
  Target,
  Code,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import OpenEireCaseStudy from "../components/OpenEireCaseStudy";
import {
  getProjectTranslationKey,
  isFlagshipProject,
  type ProjectSummary,
} from "../utils/projects";

// The full project type including our new case study fields
type Project = ProjectSummary;
type SupportingCaseStudyCopy = {
  seo: {
    title: string;
    description: string;
    keywords: string;
  };
  hero_eyebrow: string;
  summary: string;
  challenge: string;
  solution: string;
  result: string;
  snapshot: {
    title: string;
    items: Array<{
      label: string;
      value: string;
    }>;
  };
  demonstrates: {
    eyebrow: string;
    title: string;
    intro: string;
    items: Array<{
      title: string;
      body: string;
    }>;
  };
};

const getImageUrl = (imageUrl?: string) => {
  if (!imageUrl) return "/assets/default-project.png";
  if (imageUrl.startsWith("http") || imageUrl.startsWith("/")) return imageUrl;
  return `/media/${imageUrl}`;
};

const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { t, i18n } = useTranslation();

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const response = await fetch(`/api/projects/${id}/`, {
          headers: { "Accept-Language": i18n.language }, // <-- Make fetch language-aware
        });
        if (!response.ok) {
          throw new Error(`Project not found. Status: ${response.status}`);
        }
        const data: Project = await response.json();
        setProject(data);
      } catch (err) {
        setError(t("project_detail_page.error_message"));
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProject();
  }, [id, i18n.language, t]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="text-center py-20">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-500" />
        <h2 className="mt-4 text-2xl font-bold text-primary">
          {t("project_detail_page.error_title")}
        </h2>
        <p className="mt-2 text-secondary">
          {error || t("project_detail_page.not_found")}
        </p>
        <Link to="/" className="mt-6 inline-block text-primary hover:underline">
          &larr; {t("project_detail_page.back_button")}
        </Link>
      </div>
    );
  }

  if (isFlagshipProject(project)) {
    return <OpenEireCaseStudy project={project} />;
  }

  const translationKey = getProjectTranslationKey(project);
  const supportingCopy = translationKey
    ? (t(`case_studies.${translationKey}`, {
        returnObjects: true,
      }) as SupportingCaseStudyCopy)
    : null;

  return (
    <>
      <SEO
        title={
          supportingCopy?.seo.title ||
          `${project.title} - ${t("project_detail_page.case_study_title")}`
        }
        description={
          supportingCopy?.seo.description ||
          project.client_challenge ||
          project.description
        }
        keywords={supportingCopy?.seo.keywords || project.tech_stack}
        type="article"
        image={project.image}
      />
      <main className="min-h-screen p-6">
        <div className="max-w-6xl mx-auto">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-secondary hover:text-primary mb-8"
          >
            <ArrowLeft size={16} /> {t("project_detail_page.back_button")}
          </Link>

          <div className="glassmorphism backdrop-blur-sm rounded-lg shadow-xl p-6 md:p-12 border">
            <div className="grid lg:grid-cols-[minmax(0,1.15fr)_320px] gap-10 items-start">
              <div>
                {supportingCopy?.hero_eyebrow && (
                  <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3">
                    {supportingCopy.hero_eyebrow}
                  </p>
                )}
                <h1 className="text-3xl sm:text-5xl font-bold mb-4 text-primary">
                  {project.title}
                </h1>
                <p className="text-xl text-secondary leading-relaxed mb-5">
                  {supportingCopy?.summary || project.description}
                </p>
                {supportingCopy?.summary && (
                  <p className="text-secondary leading-relaxed mb-8">
                    {project.description}
                  </p>
                )}
                <img
                  src={getImageUrl(project.image)}
                  alt={`${project.title} main screenshot`}
                  className="w-full rounded-3xl shadow-lg"
                />
              </div>

              <div className="space-y-6">
                {supportingCopy?.snapshot && (
                  <div className="glassmorphism p-6 rounded-2xl border">
                    <h2 className="text-xl font-semibold mb-5 text-primary">
                      {supportingCopy.snapshot.title}
                    </h2>
                    <dl className="space-y-4">
                      {supportingCopy.snapshot.items.map((item) => (
                        <div
                          key={item.label}
                          className="border-b border-secondary/15 pb-4 last:border-b-0 last:pb-0"
                        >
                          <dt className="text-xs uppercase tracking-[0.16em] text-secondary mb-1">
                            {item.label}
                          </dt>
                          <dd className="text-primary font-medium leading-relaxed">
                            {item.value}
                          </dd>
                        </div>
                      ))}
                    </dl>
                  </div>
                )}

                <div className="glassmorphism p-6 rounded-2xl border">
                  <h3 className="text-xl font-semibold mb-4 text-primary">
                    {t("project_detail_page.tech_stack_title")}
                  </h3>
                  <div className="flex flex-wrap gap-2 mb-6">
                    {project.tech_stack.split(",").map((tech) => (
                      <span
                        key={tech}
                        className="bg-primary/10 text-primary text-xs font-medium px-2.5 py-1 rounded-full"
                      >
                        {tech.trim()}
                      </span>
                    ))}
                  </div>

                  <h3 className="text-xl font-semibold mb-4 mt-8 text-primary">
                    {t("project_detail_page.links_title")}
                  </h3>
                  <div className="space-y-4">
                    {project.live_link && (
                      <a
                        href={project.live_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-secondary hover:text-primary"
                      >
                        <ExternalLink size={16} />{" "}
                        {t("project_detail_page.live_link")}
                      </a>
                    )}
                    {project.repo_link && (
                      <a
                        href={project.repo_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-secondary hover:text-primary"
                      >
                        <Github size={16} />{" "}
                        {t("project_detail_page.repo_link")}
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="grid gap-6 mt-12">
                <CaseStudySection
                  icon={Target}
                  title={t("project_detail_page.challenge_title")}
                  text={supportingCopy?.challenge || project.client_challenge}
                />
                <CaseStudySection
                  icon={Code}
                  title={t("project_detail_page.solution_title")}
                  text={supportingCopy?.solution || project.my_solution}
                />
                <CaseStudySection
                  icon={TrendingUp}
                  title={t("project_detail_page.result_title")}
                  text={supportingCopy?.result || project.the_result}
                />
            </div>

            {supportingCopy?.demonstrates && (
              <section className="mt-12 pt-12 border-t border-secondary/20">
                <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3 text-center">
                  {supportingCopy.demonstrates.eyebrow}
                </p>
                <h2 className="text-3xl font-bold text-primary mb-4 text-center">
                  {supportingCopy.demonstrates.title}
                </h2>
                <p className="text-secondary leading-relaxed max-w-3xl mx-auto text-center mb-10">
                  {supportingCopy.demonstrates.intro}
                </p>

                <div className="grid md:grid-cols-3 gap-6">
                  {supportingCopy.demonstrates.items.map((item) => (
                    <div
                      key={item.title}
                      className="glassmorphism rounded-2xl p-6 border border-secondary/20"
                    >
                      <h3 className="text-xl font-semibold text-primary mb-3">
                        {item.title}
                      </h3>
                      <p className="text-secondary leading-relaxed">
                        {item.body}
                      </p>
                    </div>
                  ))}
                  </div>
              </section>
            )}
          </div>
        </div>
      </main>
    </>
  );
};

// Helper component for consistent section styling
interface CaseStudySectionProps {
  icon: React.ElementType;
  title: string;
  text?: string;
}

const CaseStudySection: React.FC<CaseStudySectionProps> = ({
  icon: Icon,
  title,
  text,
}) => (
  <div className="glassmorphism rounded-2xl p-6 md:p-8 border border-secondary/20">
    <div className="flex items-center gap-3 mb-4">
      <Icon className="text-primary" size={24} />
      <h2 className="text-2xl font-bold text-primary">{title}</h2>
    </div>
    <p className="text-secondary text-lg leading-relaxed">
      {text || "Details for this section are coming soon."}
    </p>
  </div>
);

export default ProjectDetailPage;
