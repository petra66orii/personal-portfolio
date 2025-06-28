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
  // Helper function to get the correct image URL
  const getImageUrl = (imageUrl?: string) => {
    console.log("🖼️ Original image URL:", imageUrl);

    if (!imageUrl) {
      console.log("🖼️ No image URL, using default");
      return "/default-project.png";
    }

    // If it's already a full URL (from Django API), use it as is
    if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) {
      console.log("🖼️ Full URL detected:", imageUrl);
      return imageUrl;
    }

    const baseUrl =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
    console.log("🖼️ Base URL:", baseUrl);

    let finalUrl = "";

    // If it starts with "media/" (without slash), add the base URL and leading slash
    if (imageUrl.startsWith("media/")) {
      finalUrl = `${baseUrl}/${imageUrl}`;
    }
    // If it's a relative path from Django, prefix with backend URL
    else if (imageUrl.startsWith("/media/")) {
      finalUrl = `${baseUrl}${imageUrl}`;
    }
    // If it's just the filename, add the full path
    else if (!imageUrl.startsWith("/")) {
      finalUrl = `${baseUrl}/media/${imageUrl}`;
    }
    // Fallback for other cases - assume it needs /media/ prefix
    else {
      finalUrl = `${baseUrl}/media${imageUrl}`;
    }

    console.log("🖼️ Final image URL:", finalUrl);
    return finalUrl;
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
          console.error("🚨 Image failed to load:", e.currentTarget.src);
          console.log("🔄 Falling back to default image");
          e.currentTarget.src = "/default-project.png";
        }}
        onLoad={(e) => {
          console.log("✅ Image loaded successfully:", e.currentTarget.src);
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
