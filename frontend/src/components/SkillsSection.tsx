// src/components/SkillsSection.tsx

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

type Skill = {
  id: number;
  name: string;
  level: string;
};

const SkillsSection = () => {
  const [skills, setSkills] = useState<Skill[]>([]);

  useEffect(() => {
    const baseUrl =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
    fetch(`${baseUrl}/api/skills/`)
      .then((res) => res.json())
      .then(setSkills);
  }, []);

  return (
    <motion.section
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      viewport={{ once: true }}
      className="min-h-screen p-6"
    >
      <div className="bg-stone-light/90 dark:bg-earth-dark/90 backdrop-blur-sm rounded-lg shadow-xl max-w-6xl mx-auto px-6 py-12 border border-golden-light/20 dark:border-earth/20">
        <h2 className="text-3xl font-bold mb-8 text-golden-dark dark:text-leaf-light">
          Skills
        </h2>
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {skills.map((skill) => (
            <div
              key={skill.id}
              className="bg-stone-light/80 dark:bg-earth-dark/80 p-4 rounded-lg shadow-md border border-leaf-light/30 dark:border-earth/30"
            >
              <h3 className="text-lg font-semibold text-earth-dark dark:text-stone-light mb-2">
                {skill.name}
              </h3>
              <p className="text-earth dark:text-stone">Level: {skill.level}</p>
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  );
};

export default SkillsSection;
