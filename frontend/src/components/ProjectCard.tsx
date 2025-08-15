// src/components/ProjectCard.tsx
import { motion } from "framer-motion";

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
  // Improved image URL handler
  const getImageUrl = (imageUrl?: string) => {
    // No image provided -> prefer default bundled with the frontend (served from /assets/)
    if (!imageUrl) return "/assets/default-project.png";

    // If it's a full URL or absolute path, return as-is
    if (imageUrl.startsWith("http") || imageUrl.startsWith("/"))
      return imageUrl;

    // Otherwise assume it's a filename stored in MEDIA_ROOT
    return `/media/${imageUrl}`;
  };

  return (
    <motion.div
      className="project-bg backdrop-blur-sm shadow-lg rounded-2xl overflow-hidden border"
      whileHover={{ y: -5, scale: 1.03 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <img
        src={getImageUrl(project.image)}
        alt={project.title}
        className="w-full h-48 object-cover"
        onError={(e) => {
          // Prevent an endless retry loop: if the image is already the fallback,
          // disable further onError handling and stop.
          const img = e.currentTarget as HTMLImageElement;
          const fallbackAssets = "/assets/default-project.png";
          const fallbackMedia = "/media/default-project.png";
          if (
            img.src &&
            (img.src.endsWith(fallbackAssets) ||
              img.src.endsWith(fallbackMedia))
          ) {
            img.onerror = null;
            return;
          }
          img.onerror = null; // clear handler so setting src won't re-trigger this
          // Try the asset-bundled default first (should exist when collectstatic included frontend assets)
          img.src = fallbackAssets;
        }}
      />
      <div className="p-4">
        <h2 className="text-xl font-semibold project-title mb-2">
          {project.title}
        </h2>
        <p className="project-text mb-4">
          {Array.isArray(project.tech_stack)
            ? project.tech_stack.join(", ")
            : project.tech_stack}
        </p>
        <p className="project-text mb-4">{project.description}</p>
        <div className="flex gap-4">
          {project.live_link && (
            <a
              href={project.live_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-lg project-link transition-colors duration-200"
            >
              Live Link
            </a>
          )}
          {project.repo_link && (
            <a
              href={project.repo_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-lg project-link transition-colors duration-200"
            >
              Link to Repository
            </a>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ProjectCard;
