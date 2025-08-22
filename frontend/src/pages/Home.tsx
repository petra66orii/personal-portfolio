import { useEffect, useState } from "react";
import ProjectCard from "../components/ProjectCard";
import SEO from "../components/SEO";

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
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api";
    fetch(`${baseUrl}/projects/`)
      .then((res) => res.json())
      .then((data) => setProjects(data))
      .catch((err) => {
        console.error("Error fetching projects:", err);
        setProjects([]);
      });
  }, []);

  // Separate featured and non-featured projects
  const featuredProjects = projects.filter((project) => project.featured);
  const regularProjects = projects.filter((project) => !project.featured);

  return (
    <>
      <SEO
        title="Miss Bott - Full Stack Developer Portfolio"
        description="Full-stack developer specializing in React, TypeScript, Django, and PostgreSQL. Building modern web applications with clean code and user-focused design. Recent Code Institute graduate with Merit distinction."
        keywords="full stack developer, React developer, Django developer, TypeScript, portfolio, web development, Python, JavaScript, Code Institute, Merit graduate"
        type="website"
        image="/website-background.png"
      />
      <main className="min-h-screen p-6">
        <div className="project-bg backdrop-blur-sm rounded-lg shadow-xl max-w-6xl mx-auto px-6 py-12 border">
          <header className="mb-20">
            <h1 className="text-3xl sm:text-5xl font-bold mb-4 home-title">
              Miss Bott - Django + React Fullstack Developer
            </h1>
            <p className="text-lg home-text max-w-[790px] my-6">
              Full-stack developer proficient in modern tools like{" "}
              <strong>React</strong>, <strong>TypeScript</strong>,{" "}
              <strong>Tailwind CSS</strong>, <strong>Django</strong>, and{" "}
              <strong>PostgreSQL</strong>. I recently earned a Diploma in Full
              Stack Software Development from Code Institute with a Merit grade.
              Let's connect and build something great together!
            </p>
            <p className="text-lg home-text max-w-[790px] mb-6">
              I love building projects that solve real-world problems and make a
              difference in people's lives. I'm always looking for new
              challenges and opportunities to learn and grow as a developer.
            </p>
            <nav className="flex gap-4 mt-6" aria-label="Resume actions">
              <a
                href="/CV.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 rounded bg-gradient-to-r from-amber-700 via-amber-500 to-lime-500 text-white font-semibold hover:from-amber-900 hover:via-amber-700 hover:to-lime-700 transition"
                aria-label="View Miss Bott's CV in a new tab"
              >
                📄 View CV
              </a>

              <a
                href="/CV.pdf"
                download
                className="px-4 py-2 rounded btn-outline transition"
                aria-label="Download Miss Bott's CV as PDF"
              >
                Download CV
              </a>
            </nav>
            <p className="text-lg home-text max-w-[790px] my-3">
              🛠️ Currently working on: QR generator website, learning more about
              AI integrations, and exploring new technologies.
            </p>
          </header>

          {/* Services Preview Section */}
          <section className="mb-16 bg-gradient-to-br from-amber-50 to-orange-50 -mx-4 px-4 py-12 rounded-2xl">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold mb-4 home-title">
                Professional Services
              </h2>
              <p className="text-lg home-text max-w-3xl mx-auto">
                Ready to bring your ideas to life? I offer comprehensive web development 
                and maintenance services to help your business succeed online.
              </p>
            </div>
            
            <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-white text-xl">💻</span>
                </div>
                <h3 className="font-bold mb-2">Web Development</h3>
                <p className="text-sm text-gray-600">Custom websites with React & Django</p>
              </div>
              
              <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-white text-xl">🔧</span>
                </div>
                <h3 className="font-bold mb-2">Maintenance</h3>
                <p className="text-sm text-gray-600">Keep your site secure & updated</p>
              </div>
              
              <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-white text-xl">⚡</span>
                </div>
                <h3 className="font-bold mb-2">Optimization</h3>
                <p className="text-sm text-gray-600">Speed up your website performance</p>
              </div>
              
              <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-white text-xl">💡</span>
                </div>
                <h3 className="font-bold mb-2">Consultation</h3>
                <p className="text-sm text-gray-600">Expert technical guidance</p>
              </div>
            </div>
            
            <div className="text-center">
              <a 
                href="/services"
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                View All Services
                <span className="ml-2">→</span>
              </a>
            </div>
          </section>

          {/* Featured Projects Section */}
          {featuredProjects.length > 0 && (
            <section className="mb-16">
              <h2 className="text-2xl sm:text-4xl font-bold mb-8 home-title">
                Featured Projects
              </h2>
              <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                {featuredProjects.map((project: Project) => (
                  <ProjectCard key={project.id} project={project} />
                ))}
              </div>
            </section>
          )}

          {/* Regular Projects Section */}
          {regularProjects.length > 0 && (
            <section className="mb-16">
              <h2 className="text-2xl sm:text-3xl font-bold mb-8 home-title">
                Other Projects
              </h2>
              <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                {regularProjects.map((project: Project) => (
                  <ProjectCard key={project.id} project={project} />
                ))}
              </div>
            </section>
          )}

          {/* No Projects Message */}
          {projects.length === 0 && (
            <section className="text-center py-12">
              <p className="home-subtitle text-lg">
                No projects found. Make sure the backend server is running.
              </p>
              <p className="home-text text-sm mt-2">
                Backend URL:{" "}
                {import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}
                /api/projects/
              </p>
            </section>
          )}
        </div>
      </main>
    </>
  );
};

export default Home;
