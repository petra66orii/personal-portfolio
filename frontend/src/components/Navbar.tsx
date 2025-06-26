import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Menu, X } from "lucide-react";
import NavItem from "./NavItem";
import UnicornIcon from "./UnicornIcon";

const Navbar = () => {
  const [isDark, setIsDark] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const html = document.documentElement;
    const stored = localStorage.getItem("theme");
    if (stored === "dark") {
      html.classList.add("dark");
      setIsDark(true);
    }
  }, []);

  useEffect(() => {
    const html = document.documentElement;
    if (isDark) {
      html.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      html.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDark]);

  return (
    <nav className="bg-white dark:bg-gray-900 shadow sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link
            to="/"
            className="flex items-center gap-2 text-2xl font-bold text-gray-900 dark:text-white"
          >
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-700 via-violet-800 to-rose-600 dark:from-pink-500 dark:via-yellow-500 dark:to-green-500">
              Petra.dev
            </span>
            <UnicornIcon />
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex space-x-6 items-center">
            <NavItem to="/" label="Home" onClick={() => setIsOpen(false)} />
            <NavItem
              to="/skills"
              label="Skills"
              onClick={() => setIsOpen(false)}
            />
            <NavItem
              to="/contact"
              label="Contact"
              onClick={() => setIsOpen(false)}
            />
            <button
              onClick={() => setIsDark((prev) => !prev)}
              className="ml-2 px-2 py-1 text-sm border border-gray-400 rounded hover:bg-gray-100 dark:hover:bg-gray-800 dark:text-white"
            >
              {isDark ? "☀️" : "🌙"}
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center gap-2">
            <button
              onClick={() => setIsDark((prev) => !prev)}
              className="px-2 py-1 text-sm border border-gray-400 rounded hover:bg-gray-100 dark:hover:bg-gray-800 dark:text-white"
            >
              {isDark ? "☀️" : "🌙"}
            </button>
            <button
              onClick={() => setIsOpen((prev) => !prev)}
              className="text-gray-700 dark:text-gray-200"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile dropdown */}
        {isOpen && (
          <div className="md:hidden mt-2 pb-4 space-y-2 flex flex-col">
            <NavItem to="/" label="Home" onClick={() => setIsOpen(false)} />
            <NavItem
              to="/skills"
              label="Skills"
              onClick={() => setIsOpen(false)}
            />
            <NavItem
              to="/contact"
              label="Contact"
              onClick={() => setIsOpen(false)}
            />
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
