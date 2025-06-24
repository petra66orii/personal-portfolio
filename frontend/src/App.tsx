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

function App() {
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    fetch('http://localhost:8000/api/projects/')
      .then(res => res.json())
      .then(data => setProjects(data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">My Projects</h1>
      <ul className="space-y-4">
        {projects.map(p => (
          <li key={p.id} className="p-4 border rounded shadow">
            <h2 className="text-xl font-semibold">{p.title}</h2>
            <p>{p.description}</p>
            <p className="text-sm text-gray-500">{p.tech_stack}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default App
