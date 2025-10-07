import { useState } from "react";
import { motion } from "framer-motion";
import Tilt from "react-parallax-tilt";
import { useTranslation } from "react-i18next"; // 1. Import the hook

type Project = {
  id: number;
  title: string;
  description: string;
  image?: string;
  live_link?: string;
  repo_link?: string;
  tech_stack?: string[] | string;
  featured?: boolean;
};

const ProjectCard = ({ project }: { project: Project }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { t } = useTranslation(); // 2. Get the translation function

  const charLimit = 150;
  const isLongDescription = project.description.length > charLimit;

  const toggleIsExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const getImageUrl = (imageUrl?: string) => {
    if (!imageUrl) return "/assets/default-project.png";
    if (imageUrl.startsWith("http") || imageUrl.startsWith("/"))
      return imageUrl;
    return `/media/${imageUrl}`;
  };

  return (
    <motion.div
      className="project-bg backdrop-blur-sm shadow-lg rounded-2xl overflow-hidden border flex flex-col h-full" // Added h-full
      whileHover={{ y: -5, scale: 1.03 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <img
        src={getImageUrl(project.image)}
        alt={project.title}
        className="w-full h-48 object-cover"
        onError={(e) => {
          const img = e.currentTarget as HTMLImageElement;
          img.onerror = null;
          img.src = "/assets/default-project.png";
        }}
      />
      <Tilt
        glareEnable={true}
        glareMaxOpacity={0.3}
        glareColor="#AAF0D1"
        glarePosition="all"
        tiltMaxAngleX={10}
        tiltMaxAngleY={10}
        scale={1.02}
        className="flex flex-col flex-grow"
      >
        <div className="p-4 flex flex-col flex-grow">
          <h2 className="text-xl font-semibold project-title mb-2">
            {project.title}
          </h2>
          <p className="project-text text-sm mb-4">
            {Array.isArray(project.tech_stack)
              ? project.tech_stack.join(", ")
              : project.tech_stack}
          </p>
          <div className="project-text mb-4 flex-grow">
            <p>
              {isLongDescription && !isExpanded
                ? `${project.description.substring(0, charLimit)}...`
                : project.description}
            </p>
            {isLongDescription && (
              <button
                onClick={toggleIsExpanded}
                className="font-bold text-primary-light dark:text-primary-dark hover:underline mt-2"
              >
                {/* 3. Replace static text */}
                {isExpanded ? t("projects.read_less") : t("projects.read_more")}
              </button>
            )}
          </div>
          <div className="flex gap-4 mt-auto">
            {project.live_link && (
              <a
                href={project.live_link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-lg project-link transition-colors duration-200"
              >
                {t("projects.live_link")}
              </a>
            )}
            {project.repo_link && (
              <a
                href={project.repo_link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-lg project-link transition-colors duration-200"
              >
                {t("projects.repo_link")}
              </a>
            )}
          </div>
        </div>
      </Tilt>
    </motion.div>
  );
};

export default ProjectCard;
