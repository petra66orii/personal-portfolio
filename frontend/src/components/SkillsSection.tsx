// src/components/SkillsSection.tsx

import { useEffect, useState } from 'react'

type Skill = {
  id: number
  name: string
  level: string
}

const SkillsSection = () => {
  const [skills, setSkills] = useState<Skill[]>([])

  useEffect(() => {
    fetch('http://localhost:8000/api/skills/')
      .then(res => res.json())
      .then(data => setSkills(data))
      .catch(err => console.error(err))
  }, [])

  return (
    <section className="p-6 bg-gray-100">
      <h2 className="text-3xl font-bold mb-4">Skills</h2>
      <ul className="grid gap-2 md:grid-cols-2">
        {skills.map(skill => (
          <li key={skill.id} className="p-3 bg-white rounded shadow">
            <span className="font-medium">{skill.name}</span> — {skill.level}
          </li>
        ))}
      </ul>
    </section>
  )
}

export default SkillsSection
