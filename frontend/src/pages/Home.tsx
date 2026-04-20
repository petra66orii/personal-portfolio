import { useEffect, useState } from "react";
import ProjectCard from "../components/ProjectCard";
import SEO from "../components/SEO";
import ScrollAnimator from "../components/ScrollAnimator";
import Testimonials from "../components/Testimonials";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { isFlagshipProject, type ProjectSummary } from "../utils/projects";

type Project = ProjectSummary & {
  featured: boolean;
};

type FlagshipFact = {
  label: string;
  value: string;
};

const CASE_STUDY_ORDER = ["Timeless Travel", "Honeypot", "CM Artistry"];

const getImageUrl = (imageUrl?: string) => {
  if (!imageUrl) return "/assets/default-project.png";
  if (imageUrl.startsWith("http") || imageUrl.startsWith("/")) return imageUrl;
  return `/media/${imageUrl}`;
};

const Home = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const { t, i18n } = useTranslation();
  const flagshipFacts = t("case_studies.openeire.hero.facts", {
    returnObjects: true,
  }) as FlagshipFact[];

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch("/api/projects/", {
          headers: {
            // Add this header to tell Django the user's language
            "Accept-Language": i18n.language,
          },
        });
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}.`);
        }
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          throw new TypeError(
            "Server did not send JSON. Check the backend URL and view.",
          );
        }
        const data: Project[] = await response.json();
        setProjects(data);
      } catch (err) {
        console.error("Error fetching projects:", err);
        setProjects([]);
      }
    };
    fetchProjects();
  }, [i18n.language]);

  const flagshipProject = projects.find(isFlagshipProject) ?? null;
  const selectedProjects = [...projects]
    .filter((project) => !isFlagshipProject(project))
    .sort((left, right) => {
      const leftIndex = CASE_STUDY_ORDER.indexOf(left.title);
      const rightIndex = CASE_STUDY_ORDER.indexOf(right.title);

      if (leftIndex === -1 && rightIndex === -1) {
        return left.title.localeCompare(right.title);
      }

      if (leftIndex === -1) return 1;
      if (rightIndex === -1) return -1;

      return leftIndex - rightIndex;
    });

  return (
    <>
      <SEO
        title={t("seo.home_title")}
        description={t("seo.home_description")}
        type="website"
        image="/assets/logos/social-logo.png"
      />
      <main className="min-h-screen p-3 sm:p-6">
        <div className="glassmorphism backdrop-blur-sm rounded-2xl shadow-xl max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-8 sm:py-12 border">
          <ScrollAnimator>
            <header className="mb-14 sm:mb-20 text-center">
              <h1 className="text-3xl sm:text-5xl font-bold mb-4 text-primary">
                {t("home.title")}
              </h1>
              <h2 className="text-xl sm:text-3xl text-primary font-semibold mb-4">
                {t("home.subtitle")}
              </h2>
              <p className="text-base sm:text-lg text-secondary max-w-[790px] my-5 sm:my-6 mx-auto">
                {t("home.description_p1")}
                <br />
                <br />
                {t("home.description_p2")}
              </p>

              <Link
                to="/quote"
                className="inline-block px-8 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                {t("home.call_to_action")}
              </Link>
            </header>
          </ScrollAnimator>

          <ScrollAnimator>
            <section className="mb-12 sm:mb-16 glassmorphism sm:mx-4 px-4 sm:px-6 py-8 sm:py-12 rounded-2xl">
              <div className="text-center mb-8 sm:mb-12">
                <h2 className="text-2xl sm:text-4xl text-primary font-bold mb-4 home-title break-words">
                  {t("problem.title")}
                </h2>
                <p className="text-base sm:text-lg text-secondary max-w-3xl mx-auto">
                  {t("problem.description1")}
                </p>
                <br />
                <p className="text-base sm:text-lg text-secondary max-w-3xl mx-auto">
                  {t("problem.description2")}
                </p>
                <br />
                <p className="text-base sm:text-lg text-secondary max-w-3xl mx-auto">
                  {t("problem.desciption3")}
                </p>
                <br />
                <p className="text-base sm:text-lg text-secondary max-w-3xl mx-auto">
                  {t("problem.description4")}
                </p>
              </div>
            </section>
          </ScrollAnimator>

          <ScrollAnimator>
            <section className="mb-12 sm:mb-16 glassmorphism sm:mx-4 px-4 sm:px-6 py-8 sm:py-12 rounded-2xl">
              <div className="text-center mb-8 sm:mb-12">
                <h2 className="text-2xl sm:text-4xl text-primary font-bold mb-4 home-title break-words">
                  {t("services1.title")}
                </h2>
                <p className="text-base sm:text-lg text-secondary max-w-3xl mx-auto">
                  {t("services1.description1")}
                </p>
                <br />
                <p className="text-base sm:text-lg text-secondary max-w-3xl mx-auto">
                  {t("services1.description2")}
                </p>
              </div>
              <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                <div className="glassmorphism p-5 sm:p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-4">
                    <span className="text-white text-xl">💻</span>
                  </div>
                  <h3 className="font-bold mb-2">
                    {t("services1.web_dev_title")}
                  </h3>
                  <p className="text-sm text-secondary">
                    {t("services1.web_dev_desc")}
                  </p>
                </div>
                <div className="glassmorphism p-5 sm:p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center mb-4">
                    <span className="text-white text-xl">🔧</span>
                  </div>
                  <h3 className="font-bold mb-2">
                    {t("services1.maintenance_title")}
                  </h3>
                  <p className="text-sm text-secondary">
                    {t("services1.maintenance_desc")}
                  </p>
                </div>
                <div className="glassmorphism p-5 sm:p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mb-4">
                    <span className="text-white text-xl">⚡</span>
                  </div>
                  <h3 className="font-bold mb-2">
                    {t("services1.optimization_title")}
                  </h3>
                  <p className="text-sm text-secondary">
                    {t("services1.optimization_desc")}
                  </p>
                </div>
                <div className="glassmorphism p-5 sm:p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg flex items-center justify-center mb-4">
                    <span className="text-white text-xl">💡</span>
                  </div>
                  <h3 className="font-bold mb-2">
                    {t("services1.consultation_title")}
                  </h3>
                  <p className="text-sm text-secondary">
                    {t("services1.consultation_desc")}
                  </p>
                </div>
              </div>
              <div className="text-center">
                <a
                  href="/services"
                  className="inline-flex items-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  {t("services1.view_all")}
                  <span className="ml-2">→</span>
                </a>
              </div>
            </section>
          </ScrollAnimator>

          <Testimonials />

          {flagshipProject && (
            <ScrollAnimator>
              <section className="mb-12 sm:mb-16 glassmorphism sm:mx-4 px-4 sm:px-6 py-8 sm:py-12 rounded-2xl">
                <div className="max-w-4xl mb-8 sm:mb-10">
                  <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3">
                    {t("projects.featured_title")}
                  </p>
                  <h2 className="text-2xl sm:text-4xl font-bold mb-4 home-title break-words">
                    {flagshipProject.title}
                  </h2>
                  <p className="text-base sm:text-lg text-secondary max-w-3xl">
                    {t("projects.featured_intro")}
                  </p>
                </div>

                <div className="grid gap-8 lg:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.82fr)] items-start">
                  <div className="space-y-5">
                    <div className="rounded-3xl overflow-hidden border border-secondary/20 shadow-xl bg-surface/40">
                      <img
                        src={getImageUrl(flagshipProject.image)}
                        alt={t("project_card.alt_text", {
                          title: flagshipProject.title,
                        })}
                        className="w-full aspect-[4/3] sm:aspect-[16/10] object-cover"
                      />
                    </div>

                    <div className="hidden lg:grid gap-4 lg:grid-cols-3">
                      {flagshipFacts.map((fact) => (
                        <div
                          key={fact.label}
                          className="glassmorphism rounded-2xl p-4 border border-secondary/20"
                        >
                          <p className="text-xs uppercase tracking-[0.16em] text-secondary mb-2">
                            {fact.label}
                          </p>
                          <p className="text-primary font-medium leading-relaxed text-sm">
                            {fact.value}
                          </p>
                        </div>
                      ))}
                    </div>

                    <div className="hidden lg:flex flex-wrap gap-2">
                      {flagshipProject.tech_stack.split(",").map((tech) => (
                        <span
                          key={tech}
                          className="px-3 py-1.5 rounded-full text-xs bg-primary/10 text-primary border border-secondary/20"
                        >
                          {tech.trim()}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="glassmorphism rounded-3xl p-5 sm:p-6 md:p-8 border border-secondary/20 shadow-lg flex flex-col">
                    <div>
                      <p className="text-base sm:text-lg text-secondary leading-relaxed mb-5 sm:mb-6">
                        {flagshipProject.description}
                      </p>
                    </div>

                    <div className="mt-4 pt-6 border-t border-secondary/20">
                      <p className="text-xs uppercase tracking-[0.16em] text-secondary mb-2">
                        {t("projects.featured_value_label")}
                      </p>
                      <p className="text-secondary leading-relaxed mb-6">
                        {flagshipProject.the_result}
                      </p>

                      <div className="flex flex-col gap-4">
                        <Link
                          to={`/projects/${flagshipProject.id}`}
                          className="inline-flex items-center justify-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
                        >
                          {t("project_card.link_text")}
                        </Link>
                        <Link
                          to="/quote"
                          className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-secondary/30 text-primary font-semibold hover:bg-surface transition-all duration-300"
                        >
                          {t("home.call_to_action")}
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-3 mt-8 lg:hidden">
                  {flagshipFacts.map((fact) => (
                    <div
                      key={fact.label}
                      className="glassmorphism rounded-2xl p-4 sm:p-5 border border-secondary/20"
                    >
                      <p className="text-xs uppercase tracking-[0.16em] text-secondary mb-2">
                        {fact.label}
                      </p>
                      <p className="text-primary font-medium leading-relaxed">
                        {fact.value}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="flex flex-wrap gap-2 mt-6 lg:hidden">
                  {flagshipProject.tech_stack.split(",").map((tech) => (
                    <span
                      key={tech}
                      className="px-3 py-1.5 rounded-full text-xs sm:text-sm bg-primary/10 text-primary border border-secondary/20"
                    >
                      {tech.trim()}
                    </span>
                  ))}
                </div>
              </section>
            </ScrollAnimator>
          )}

          {selectedProjects.length > 0 && (
            <ScrollAnimator>
              <section className="mb-12 sm:mb-16 glassmorphism sm:mx-4 px-4 sm:px-6 py-8 sm:py-12 rounded-2xl">
                <div className="max-w-4xl mb-8 sm:mb-10">
                  <p className="text-sm uppercase tracking-[0.18em] secondary font-semibold mb-3">
                    {t("projects.other_kicker")}
                  </p>
                  <h2 className="text-2xl sm:text-4xl font-bold mb-4 home-title break-words">
                    {t("projects.other_title")}
                  </h2>
                  <p className="text-base sm:text-lg text-secondary max-w-3xl">
                    {t("projects.other_intro")}
                  </p>
                </div>
                <div className="grid gap-6 sm:gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                  {selectedProjects.map((project: Project) => (
                    <ProjectCard key={project.id} project={project} />
                  ))}
                </div>
              </section>
            </ScrollAnimator>
          )}

          {projects.length === 0 && (
            <section className="text-center py-12">
              <p className="home-subtitle text-lg">
                {t("projects.none_found")}
              </p>
            </section>
          )}
          <section className="text-center py-12">
            <h2 className="text-2xl sm:text-3xl font-bold mb-4 home-title">
              {t("cta.title")}
            </h2>
            <p className="text-lg text-secondary max-w-3xl mx-auto mb-6">
              {t("cta.description")}
            </p>
            <Link
              to="/quote"
              className="inline-block px-8 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              {t("cta.button")}
            </Link>
          </section>
        </div>
      </main>
    </>
  );
};

export default Home;
