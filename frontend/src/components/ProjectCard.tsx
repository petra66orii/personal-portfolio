import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { useTranslation } from "react-i18next";
import { getProjectTranslationKey } from "../utils/projects";

type Project = {
  id: number;
  title: string;
  image?: string;
  description?: string;
  client_challenge?: string;
};

interface ProjectCardProps {
  project: Project;
}

const getImageUrl = (imageUrl?: string) => {
  if (!imageUrl) return "/assets/default-project.png";
  if (imageUrl.startsWith("http") || imageUrl.startsWith("/")) {
    return imageUrl;
  }
  return `/media/${imageUrl}`;
};

const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  const { t } = useTranslation();
  const projectKey = getProjectTranslationKey(project);
  const cardLabel = projectKey
    ? t(`case_studies.${projectKey}.card_label`, { defaultValue: "" })
    : "";
  const cardSummary = projectKey
    ? t(`case_studies.${projectKey}.card_summary`, {
        defaultValue:
          project.client_challenge ||
          project.description ||
          t("project_card.fallback_description"),
      })
    : project.client_challenge ||
      project.description ||
      t("project_card.fallback_description");

  return (
    <div className="glassmorphism rounded-2xl overflow-hidden h-full flex flex-col group transition-all duration-300 hover:shadow-2xl hover:-translate-y-2">
      <img
        src={getImageUrl(project.image)}
        alt={t("project_card.alt_text", { title: project.title })}
        className="w-full h-40 sm:h-48 object-cover"
      />
      <div className="p-5 sm:p-6 flex flex-col flex-grow">
        {cardLabel && (
          <p className="text-xs uppercase tracking-[0.16em] text-secondary font-semibold mb-3">
            {cardLabel}
          </p>
        )}
        <h3 className="text-lg sm:text-xl font-semibold text-primary mb-3">
          {project.title}
        </h3>

        <p className="text-sm sm:text-base text-secondary leading-relaxed mb-5 sm:mb-6 flex-grow">
          {cardSummary}
        </p>

        <Link
          to={`/projects/${project.id}`}
          className="mt-auto inline-flex items-center text-primary font-semibold text-sm sm:text-base"
        >
          {t("project_card.link_text")}
          <ArrowRight
            size={16}
            className="ml-2 transition-transform group-hover:translate-x-1"
          />
        </Link>
      </div>
    </div>
  );
};

export default ProjectCard;
