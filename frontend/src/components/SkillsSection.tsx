// src/components/SkillsSection.tsx

import { useEffect, useState } from "react";
import type { JSX } from "react";
import { motion } from "framer-motion";
import {
  SiJavascript,
  SiTypescript,
  SiReact,
  SiPython,
  SiDjango,
  SiHtml5,
  SiCss3,
  SiPostgresql,
  SiGit,
  SiNodedotjs,
  SiTailwindcss,
  SiMongodb,
  SiExpress,
  SiBootstrap,
  SiMysql,
  SiDocker,
  SiAmazonwebservices,
  SiHeroku,
  SiVercel,
  SiVite,
  SiWebpack,
  SiFigma,
  SiLinux,
  SiMacos,
  SiJquery,
  SiGithub,
} from "react-icons/si";
import { VscVscode } from "react-icons/vsc";
import { FaWindows } from "react-icons/fa";
import { FaCode } from "react-icons/fa";

type Skill = {
  id: number;
  name: string;
  level: string;
};

const SkillsSection = () => {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [isDark, setIsDark] = useState(false);

  // Theme detection effect
  useEffect(() => {
    const html = document.documentElement;
    const stored = localStorage.getItem("theme");
    if (stored === "dark") {
      setIsDark(true);
    }

    // Listen for theme changes
    const observer = new MutationObserver(() => {
      setIsDark(html.classList.contains("dark"));
    });

    observer.observe(html, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const baseUrl =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
    console.log("Fetching skills from:", `${baseUrl}/api/skills/`);
    fetch(`${baseUrl}/api/skills/`)
      .then((res) => {
        console.log("Skills API response status:", res.status);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log("Skills data received:", data);
        setSkills(data);
      })
      .catch((err) => {
        console.error("Error fetching skills:", err);
        setSkills([]);
      });
  }, []);

  // Function to get progress percentage from level
  const getProgressPercentage = (level: string): number => {
    const levelMap: { [key: string]: number } = {
      Beginner: 25,
      Intermediate: 50,
      Advanced: 75,
      Expert: 100,
    };
    return levelMap[level] || 50;
  };

  // Function to get skill icon based on name (official icons)
  const getSkillIcon = (skillName: string): JSX.Element => {
    const iconProps = { size: 32, className: "text-current" };

    const iconMap: { [key: string]: JSX.Element } = {
      JavaScript: <SiJavascript {...iconProps} className="text-yellow-500" />,
      TypeScript: <SiTypescript {...iconProps} className="text-blue-600" />,
      React: <SiReact {...iconProps} className="text-cyan-500" />,
      Python: <SiPython {...iconProps} className="text-blue-500" />,
      Django: <SiDjango {...iconProps} className="text-green-600" />,
      HTML5: <SiHtml5 {...iconProps} className="text-orange-600" />,
      CSS3: <SiCss3 {...iconProps} className="text-blue-500" />,
      PostgreSQL: <SiPostgresql {...iconProps} className="text-blue-700" />,
      Git: <SiGit {...iconProps} className="text-orange-600" />,
      "Node.js": <SiNodedotjs {...iconProps} className="text-green-600" />,
      TailwindCSS: <SiTailwindcss {...iconProps} className="text-cyan-500" />,
      MongoDB: <SiMongodb {...iconProps} className="text-green-500" />,
      Express: <SiExpress {...iconProps} className="text-gray-600" />,
      Bootstrap: <SiBootstrap {...iconProps} className="text-purple-600" />,
      MySQL: <SiMysql {...iconProps} className="text-blue-600" />,
      Docker: <SiDocker {...iconProps} className="text-blue-500" />,
      AWS: <SiAmazonwebservices {...iconProps} className="text-orange-500" />,
      Heroku: <SiHeroku {...iconProps} className="text-purple-600" />,
      Vercel: (
        <SiVercel {...iconProps} className="text-black dark:text-white" />
      ),
      Vite: <SiVite {...iconProps} className="text-purple-500" />,
      Webpack: <SiWebpack {...iconProps} className="text-blue-400" />,
      Figma: <SiFigma {...iconProps} className="text-purple-500" />,
      VSCode: <VscVscode {...iconProps} className="text-blue-500" />,
      Linux: <SiLinux {...iconProps} className="text-yellow-500" />,
      Windows: <FaWindows {...iconProps} className="text-blue-500" />,
      macOS: <SiMacos {...iconProps} className="text-gray-600" />,
      jQuery: <SiJquery {...iconProps} className="text-blue-600" />,
      GitHub: <SiGithub {...iconProps} className="text-white" />,
    };

    return (
      iconMap[skillName] || <FaCode {...iconProps} className="text-gray-500" />
    );
  };

  // Function to categorize skills (expanded categories)
  const getSkillCategory = (skillName: string): string => {
    const categoryMap: { [key: string]: string } = {
      JavaScript: "Frontend",
      TypeScript: "Frontend",
      React: "Frontend",
      HTML: "Frontend",
      CSS: "Frontend",
      TailwindCSS: "Frontend",
      Bootstrap: "Frontend",
      Vite: "Frontend",
      Webpack: "Frontend",
      Python: "Backend",
      Django: "Backend",
      "Node.js": "Backend",
      Express: "Backend",
      PostgreSQL: "Database",
      MongoDB: "Database",
      MySQL: "Database",
      Git: "Tools",
      Docker: "Tools",
      "VS Code": "Tools",
      Figma: "Tools",
      Linux: "Tools",
      Windows: "Tools",
      macOS: "Tools",
      AWS: "Cloud",
      Heroku: "Cloud",
      Vercel: "Cloud",
    };
    return categoryMap[skillName] || "Other";
  };

  // Get unique categories
  const categories = [
    "All",
    ...new Set(skills.map((skill) => getSkillCategory(skill.name))),
  ];

  // Filter skills by category
  const filteredSkills =
    selectedCategory === "All"
      ? skills
      : skills.filter(
          (skill) => getSkillCategory(skill.name) === selectedCategory
        );

  return (
    <motion.section
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      viewport={{ once: true }}
      className="min-h-screen p-6"
    >
      <div className="project-bg backdrop-blur-sm rounded-lg shadow-xl max-w-6xl mx-auto px-6 py-12 border">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-3xl font-bold mb-8 home-title text-center"
        >
          Skills & Technologies
        </motion.h2>

        {/* Category Filter */}
        <div className="flex flex-wrap justify-center gap-3 mb-8">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                selectedCategory === category
                  ? isDark
                    ? "bg-lime-600 text-white hover:bg-lime-700"
                    : "bg-amber-500 text-white hover:bg-amber-600"
                  : isDark
                  ? "bg-lime-900 text-lime-200 hover:bg-lime-800"
                  : "bg-amber-100 text-amber-800 hover:bg-amber-200"
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* Skills Grid */}
        <motion.div
          layout
          className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
        >
          {filteredSkills.map((skill, index) => (
            <motion.div
              key={skill.id}
              layout
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              whileHover={{
                scale: 1.05,
                boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
              }}
              transition={{
                duration: 0.3,
                delay: index * 0.1,
              }}
              className="project-bg p-6 rounded-lg shadow-md border cursor-pointer group relative overflow-hidden"
            >
              {/* Skill Icon & Name */}
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                  {getSkillIcon(skill.name)}
                </div>
                <h3
                  className={`text-lg font-semibold home-title transition-colors ${
                    isDark
                      ? "group-hover:text-lime-400"
                      : "group-hover:text-amber-600"
                  }`}
                >
                  {skill.name}
                </h3>
              </div>

              {/* Level & Progress Bar */}
              <div className="mb-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium home-text">
                    {skill.level}
                  </span>
                  <span className="text-sm home-text opacity-75">
                    {getProgressPercentage(skill.level)}%
                  </span>
                </div>

                {/* Progress Bar */}
                <div
                  className={`w-full rounded-full h-2 ${
                    isDark ? "bg-lime-900" : "bg-amber-200"
                  }`}
                >
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{
                      width: `${getProgressPercentage(skill.level)}%`,
                    }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className={`h-2 rounded-full ${
                      isDark ? "bg-lime-500" : "bg-amber-500"
                    }`}
                  />
                </div>
              </div>

              {/* Category Badge */}
              <div className="flex justify-end">
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full ${
                    isDark
                      ? "bg-lime-800 text-lime-200"
                      : "bg-amber-100 text-amber-700"
                  }`}
                >
                  {getSkillCategory(skill.name)}
                </span>
              </div>

              {/* Hover Effect Overlay */}
              <div className="absolute inset-0 bg-gradient-to-r from-amber-500/10 to-lime-500/10 dark:from-lime-500/10 dark:to-amber-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg" />
            </motion.div>
          ))}
        </motion.div>

        {/* Empty State */}
        {filteredSkills.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <p className="home-text text-lg">
              No skills found in this category.
            </p>
          </motion.div>
        )}
      </div>
    </motion.section>
  );
};

export default SkillsSection;
