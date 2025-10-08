import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

type Project = {
  id: number;
  title: string;
  image?: string;
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
  return (
    <div className="glassmorphism rounded-2xl overflow-hidden h-full flex flex-col group transition-all duration-300 hover:shadow-2xl hover:-translate-y-2">
      <img
        src={getImageUrl(project.image)}
        alt={`${project.title} screenshot`}
        className="w-full h-48 object-cover"
      />
      <div className="p-6 flex flex-col flex-grow">
        <h3 className="text-xl font-semibold text-primary mb-3">
          {project.title}
        </h3>

        {/* We now show the challenge instead of a generic description */}
        <p className="text-secondary mb-6 flex-grow">
          {project.client_challenge ||
            "A featured project showcasing modern web development."}
        </p>

        {/* This button links to the full case study page */}
        <Link
          to={`/projects/${project.id}`} // Or a slug if you have one
          className="mt-auto inline-flex items-center text-primary font-semibold"
        >
          View Case Study
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
