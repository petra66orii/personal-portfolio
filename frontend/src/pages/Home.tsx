import { useEffect, useState } from "react";
import ProjectCard from "../components/ProjectCard";

type Project = {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
  repo_link?: string;
  live_link?: string;
  featured: boolean;
  image?: string;
};

const Home = () => {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    const baseUrl = "/api";
    fetch(`${baseUrl}/projects/`)
      .then((res) => {
        console.log("Response status:", res.status);
        return res.json();
      })
      .then((data) => {
        console.log("Projects data:", data);
        setProjects(data);
      })
      .catch((err) => {
        console.error("Error fetching projects:", err);
        setProjects([]);
      });
  }, []);

  // Separate featured and non-featured projects
  const featuredProjects = projects.filter((project) => project.featured);
  const regularProjects = projects.filter((project) => !project.featured);

  return (
    <section className="min-h-screen p-6">
      <div className="project-bg backdrop-blur-sm rounded-lg shadow-xl max-w-6xl mx-auto px-6 py-12 border">
        <div className="mb-20">
          <h1 className="text-3xl sm:text-5xl font-bold mb-4 home-title">
            Hi, I'm Miss Bott - Django + React Fullstack Developer
          </h1>
          <p className="text-lg home-text max-w-[790px] my-6">
            Full-stack developer with a strong focus on writing clean,
            maintainable code and crafting responsive, accessible user
            experiences. Proficient in modern tools like <strong>React</strong>,{" "}
            <strong>TypeScript</strong>, <strong>Tailwind CSS</strong>,{" "}
            <strong>Django</strong>, and <strong>PostgreSQL</strong>. I recently
            earned a Diploma in Full Stack Software Development from Code
            Institute with a Merit grade.
          </p>
          <p className="text-lg home-text max-w-[790px] mb-6">
            I love building projects that solve real-world problems and make a
            difference in people's lives. I'm always looking for new challenges
            and opportunities to learn.
          </p>
          <div className="flex gap-4 mt-6">
            <a
              href="/CV.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 rounded bg-gradient-to-r from-amber-700 via-amber-500 to-lime-500 text-white font-semibold hover:from-amber-900 hover:via-amber-700 hover:to-lime-700 transition"
            >
              📄 View CV
            </a>

            <a
              href="/CV.pdf"
              download
              className="px-4 py-2 rounded btn-outline transition"
            >
              Download CV
            </a>
          </div>
          <p className="text-lg home-text max-w-[790px] my-3">
            🛠️ Currently working on: building this portfolio site using React,
            Tailwind CSS, and Django — experimenting with motion, dark mode,
            golden ratio layout, and a natural-inspired design.
          </p>
        </div>

        {/* Featured Projects Section */}
        {featuredProjects.length > 0 && (
          <div className="mb-16">
            <h2 className="text-2xl sm:text-4xl font-bold mb-8 home-title">
              Featured Projects
            </h2>
            <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
              {featuredProjects.map((project: Project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </div>
        )}

        {/* Regular Projects Section */}
        {regularProjects.length > 0 && (
          <div className="mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold mb-8 home-title">
              Other Projects
            </h2>
            <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
              {regularProjects.map((project: Project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </div>
        )}

        {/* No Projects Message */}
        {projects.length === 0 && (
          <div className="text-center py-12">
            <p className="home-subtitle text-lg">
              No projects found. Make sure the backend server is running.
            </p>
            <p className="home-text text-sm mt-2">
              Backend URL:{" "}
              {import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}
              /api/projects/
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default Home;
