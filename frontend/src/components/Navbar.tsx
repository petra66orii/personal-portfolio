import { Link, NavLink } from 'react-router-dom'

const Navbar = () => {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    isActive
      ? 'text-blue-600 font-bold underline'
      : 'hover:text-blue-600'

  return (
    <nav className="flex justify-between items-center p-4 shadow-md">
      <Link to="/" className="text-2xl font-bold">Petra's Portfolio</Link>
      <div className="flex gap-6">
        <NavLink to="/" className={linkClass}>Home</NavLink>
        <NavLink to="/skills" className={linkClass}>Skills</NavLink>
        <NavLink to="/contact" className={linkClass}>Contact</NavLink>
      </div>
    </nav>
  )
}

export default Navbar
