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

// The full project type including our new case study fields
type Project = {
  id: number;
  title: string;
  description: string;
  image?: string;
  tech_stack: string;
  repo_link?: string;
  live_link?: string;
  client_challenge?: string;
  my_solution?: string;
  the_result?: string;
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

  return (
    <>
      <SEO
        title={`${project.title} - ${t(
          "project_detail_page.case_study_title"
        )}`}
        description={project.client_challenge || project.description}
        keywords={project.tech_stack}
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
            <h1 className="text-3xl sm:text-5xl font-bold mb-4 text-primary">
              {project.title}
            </h1>
            <p className="text-lg text-secondary mb-8">{project.description}</p>
            <img
              src={getImageUrl(project.image)}
              alt={`${project.title} main screenshot`}
              className="w-full rounded-lg shadow-lg mb-12"
            />

            <div className="grid md:grid-cols-3 gap-12">
              <div className="md:col-span-2 space-y-12">
                <CaseStudySection
                  icon={Target}
                  title={t("project_detail_page.challenge_title")}
                  text={project.client_challenge}
                />
                <CaseStudySection
                  icon={Code}
                  title={t("project_detail_page.solution_title")}
                  text={project.my_solution}
                />
                <CaseStudySection
                  icon={TrendingUp}
                  title={t("project_detail_page.result_title")}
                  text={project.the_result}
                />
              </div>

              <div className="md:col-span-1">
                <div className="glassmorphism p-6 rounded-xl border">
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
  <div>
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
