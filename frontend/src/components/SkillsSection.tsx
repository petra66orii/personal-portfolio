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
    fetch("http://localhost:8000/api/skills/")
      .then((res) => res.json())
      .then(setSkills);
  }, []);

  return (
    <motion.section
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      viewport={{ once: true }}
      className="p-6"
    >
      <h2 className="text-3xl font-bold mb-4">Skills</h2>
      {/* your list */}
    </motion.section>
  );
};

export default SkillsSection;
