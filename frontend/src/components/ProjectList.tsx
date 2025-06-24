// src/components/ProjectList.tsx

import { useEffect, useState } from 'react'

type Project = {
  id: number
  title: string
  description: string
  tech_stack: string
  repo_link?: string
  live_link?: string
  featured: boolean
}

const ProjectList = () => {
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    fetch('http://localhost:8000/api/projects/')
      .then(res => res.json())
      .then(data => setProjects(data))
      .catch(err => console.error(err))
  }, [])

  return (
    <section className="p-6">
      <h2 className="text-3xl font-bold mb-4">Projects</h2>
      <div className="grid gap-6 md:grid-cols-2">
        {projects.map(project => (
          <div key={project.id} className="p-4 border rounded-lg shadow hover:shadow-xl transition">
            <h3 className="text-xl font-semibold mb-2">{project.title}</h3>
            <p className="mb-2">{project.description}</p>
            <p className="text-sm text-gray-500 mb-2">{project.tech_stack}</p>
            <div className="flex gap-4 text-blue-600 text-sm">
              {project.repo_link && <a href={project.repo_link} target="_blank" rel="noreferrer">Repo</a>}
              {project.live_link && <a href={project.live_link} target="_blank" rel="noreferrer">Live</a>}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default ProjectList
