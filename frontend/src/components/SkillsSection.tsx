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
import { FaWindows, FaCode } from "react-icons/fa";
import Tilt from "react-parallax-tilt";

type Skill = {
  id: number;
  name: string;
  level: string;
};

const SkillsSection = () => {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [isDark, setIsDark] = useState(false);

  // This effect correctly observes theme changes for standalone use.
  useEffect(() => {
    const html = document.documentElement;
    const observer = new MutationObserver(() => {
      setIsDark(html.classList.contains("dark"));
    });
    // Set initial state on mount
    setIsDark(html.classList.contains("dark"));
    observer.observe(html, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);

  // This useEffect hook is now updated with the robust async/await logic
  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const response = await fetch("/api/skills/");

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          throw new TypeError(
            "Server did not send JSON. Check the /api/skills/ endpoint in your Django backend."
          );
        }

        const data: Skill[] = await response.json();
        setSkills(data);
      } catch (err) {
        console.error("Error fetching skills:", err);
        setSkills([]);
      }
    };

    fetchSkills();
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

  // Function to get skill icon based on name
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
      Vercel: <SiVercel {...iconProps} className="text-primary" />,
      Vite: <SiVite {...iconProps} className="text-purple-500" />,
      Webpack: <SiWebpack {...iconProps} className="text-blue-400" />,
      Figma: <SiFigma {...iconProps} className="text-purple-500" />,
      VSCode: <VscVscode {...iconProps} className="text-blue-500" />,
      Linux: <SiLinux {...iconProps} className="text-yellow-500" />,
      Windows: <FaWindows {...iconProps} className="text-blue-500" />,
      macOS: <SiMacos {...iconProps} className="text-gray-600" />,
      jQuery: <SiJquery {...iconProps} className="text-blue-600" />,
      GitHub: <SiGithub {...iconProps} className="text-primary" />,
    };

    return (
      iconMap[skillName] || <FaCode {...iconProps} className="text-gray-500" />
    );
  };

  // Function to categorize skills
  const getSkillCategory = (skillName: string): string => {
    const categoryMap: { [key: string]: string } = {
      JavaScript: "Frontend",
      TypeScript: "Frontend",
      React: "Frontend",
      HTML5: "Frontend",
      CSS3: "Frontend",
      TailwindCSS: "Frontend",
      Bootstrap: "Frontend",
      Vite: "Frontend",
      Webpack: "Frontend",
      jQuery: "Frontend",
      Python: "Backend",
      Django: "Backend",
      "Node.js": "Backend",
      Express: "Backend",
      PostgreSQL: "Database",
      MongoDB: "Database",
      MySQL: "Database",
      Git: "Tools",
      Docker: "Tools",
      VSCode: "Tools",
      Figma: "Tools",
      Linux: "Tools",
      Windows: "Tools",
      macOS: "Tools",
      GitHub: "Tools",
      AWS: "Cloud",
      Heroku: "Cloud",
      Vercel: "Cloud",
    };
    return categoryMap[skillName] || "Other";
  };

  // Get unique categories from the fetched skills
  const categories = [
    "All",
    ...Array.from(new Set(skills.map((skill) => getSkillCategory(skill.name)))),
  ];

  // Filter skills by the selected category
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
      <div className="backdrop-blur-sm rounded-lg shadow-xl max-w-6xl mx-auto px-6 py-12 border glassmorphism">
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
                    ? "bg-primary text-primary" // Using theme colors
                    : "bg-primary text-primary"
                  : isDark
                  ? "bg-surface text-secondary hover:bg-opacity-80"
                  : "bg-surface text-secondary hover:bg-opacity-80"
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
            <Tilt
              glareEnable={true}
              glareMaxOpacity={0.3}
              glareColor="#AAF0D1"
              glarePosition="all"
              tiltMaxAngleX={10}
              tiltMaxAngleY={10}
              scale={1.02}
            >
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
                  delay: index * 0.05, // Slightly faster stagger
                }}
                className="p-6 rounded-lg shadow-md border cursor-pointer group relative overflow-hidden glassmorphism"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-surface rounded-lg shadow-lg">
                    {getSkillIcon(skill.name)}
                  </div>
                  <h3 className="text-lg font-semibold transition-colors title-text-primary">
                    {skill.name}
                  </h3>
                </div>

                <div className="mb-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium home-text">
                      {skill.level}
                    </span>
                    <span className="text-sm home-text opacity-75">
                      {getProgressPercentage(skill.level)}%
                    </span>
                  </div>
                  <div className="w-full rounded-full h-2 bg-surface">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{
                        width: `${getProgressPercentage(skill.level)}%`,
                      }}
                      transition={{ duration: 1, delay: index * 0.1 }}
                      className="h-2 rounded-full bg-secondary"
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-surface text-secondary">
                    {getSkillCategory(skill.name)}
                  </span>
                </div>

                <div className="absolute inset-0 bg-gradient-to-r from-primary-light/10 to-secondary-light/10 dark:from-primary-dark/10 dark:to-secondary-dark/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg" />
              </motion.div>
            </Tilt>
          ))}
        </motion.div>

        {filteredSkills.length === 0 && skills.length > 0 && (
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
