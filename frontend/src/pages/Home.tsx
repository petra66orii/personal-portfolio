import { useEffect, useState } from "react";
import ProjectCard from "../components/ProjectCard";
import SEO from "../components/SEO";
import ScrollAnimator from "../components/ScrollAnimator";
import Credentials from "../components/Credentials";
import { useTranslation } from "react-i18next";
import useMediaQuery from "../hooks/useMediaQuery";

// --- IMPORT SWIPER COMPONENTS AND STYLES ---
import { Swiper, SwiperSlide } from "swiper/react";
import { EffectCoverflow, Pagination, Autoplay } from "swiper/modules";

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
  const { t, i18n } = useTranslation();
  const isMobile = useMediaQuery("(max-width: 767px)"); // Check for mobile screen size

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
            "Server did not send JSON. Check the backend URL and view."
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

  const featuredProjects = projects.filter((project) => project.featured);
  const regularProjects = projects.filter((project) => !project.featured);

  // Determine whether to show the carousel or a static grid
  const showCarousel = isMobile || featuredProjects.length > 3;

  return (
    <>
      <SEO
        title={t("seo.home_title")}
        description={t("seo.home_description")}
        keywords={t("seo.home_keywords")}
        type="website"
        image="/website-background.png"
      />
      <main className="min-h-screen p-6">
        <div className="glassmorphism backdrop-blur-sm rounded-lg shadow-xl max-w-6xl mx-auto px-6 py-12 border">
          <ScrollAnimator>
            <header className="mb-20">
              <h1 className="text-3xl sm:text-5xl font-bold mb-4 text-primary">
                {t("home.title")}
              </h1>
              <p className="text-lg text-secondary max-w-[790px] my-6">
                {t("home.description_p1")}{" "}
                <strong className="text-primary">React</strong>,{" "}
                <strong className="text-primary">TypeScript</strong>,{" "}
                <strong className="text-primary">Tailwind CSS</strong>,{" "}
                <strong className="text-primary">Django</strong>,{" "}
                {t("common.and")}{" "}
                <strong className="text-primary">PostgreSQL</strong>.{" "}
                {t("home.description_p2")}
              </p>
              <p className="text-lg text-secondary max-w-[790px] mb-6">
                {t("home.description_p3")}
              </p>
              <p className="text-lg text-secondary max-w-[790px] my-3">
                {t("home.currently_working")}
              </p>
              <p className="text-lg text-secondary max-w-[790px] mb-6">
                {t("home.currently_learning")}
              </p>
              <p className="text-lg text-secondary max-w-[790px] mb-6">
                {t("home.call_to_action")}
              </p>
            </header>
          </ScrollAnimator>

          <ScrollAnimator>
            <section className="mb-16 glassmorphism mx-4 px-4 py-12 rounded-2xl">
              <div className="text-center mb-12">
                <h2 className="text-3xl sm:text-4xl text-primary font-bold mb-4 home-title">
                  {t("services1.title")}
                </h2>
                <p className="text-lg text-secondary max-w-3xl mx-auto">
                  {t("services1.description")}
                </p>
              </div>
              <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                <div className="glassmorphism p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
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
                <div className="glassmorphism p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
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
                <div className="glassmorphism p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
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
                <div className="glassmorphism p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
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

          <Credentials />

          {featuredProjects.length > 0 && (
            <ScrollAnimator>
              <section className="mb-16">
                <h2 className="text-2xl sm:text-4xl font-bold mb-8 home-title text-center">
                  {t("projects.featured_title")}
                </h2>
                {showCarousel ? (
                  <Swiper
                    modules={[EffectCoverflow, Pagination, Autoplay]}
                    effect={"coverflow"}
                    grabCursor={true}
                    centeredSlides={true}
                    loop={featuredProjects.length > 3}
                    coverflowEffect={{
                      rotate: 50,
                      stretch: 0,
                      depth: 100,
                      modifier: 1,
                      slideShadows: true,
                    }}
                    autoplay={{ delay: 3500, disableOnInteraction: false }}
                    pagination={{ clickable: true }}
                    breakpoints={{
                      320: { slidesPerView: 1, spaceBetween: 20 },
                      768: { slidesPerView: 2, spaceBetween: 30 },
                      1024: { slidesPerView: 3, spaceBetween: 40 },
                    }}
                    className="py-8 px-4"
                  >
                    {featuredProjects.map((project: Project) => (
                      <SwiperSlide key={project.id} className="h-auto">
                        <ProjectCard project={project} />
                      </SwiperSlide>
                    ))}
                  </Swiper>
                ) : (
                  <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                    {featuredProjects.map((project: Project) => (
                      <ProjectCard key={project.id} project={project} />
                    ))}
                  </div>
                )}
              </section>
            </ScrollAnimator>
          )}

          {regularProjects.length > 0 && (
            <ScrollAnimator>
              <section className="mb-16">
                <h2 className="text-2xl sm:text-3xl font-bold mb-8 home-title">
                  {t("projects.other_title")}
                </h2>
                <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                  {regularProjects.map((project: Project) => (
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
        </div>
      </main>
    </>
  );
};

export default Home;
