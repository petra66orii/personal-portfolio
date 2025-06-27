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
    <nav className="bg-stone-light/98 dark:bg-stone-dark/98 backdrop-blur-sm shadow-lg sticky top-0 z-50 border-b border-golden-light/20 dark:border-leaf-dark/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link
            to="/"
            className="flex items-center gap-2 text-2xl font-bold text-golden-dark dark:text-leaf-light"
          >
            <span className="bg-gradient-to-r from-amber-700 via-amber-500 to-lime-500 bg-clip-text text-transparent">
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
              className="ml-2 px-3 py-2 text-sm border border-amber-300 dark:border-lime-600 rounded-lg bg-amber-100 dark:bg-lime-900 hover:bg-amber-200 dark:hover:bg-lime-800 text-amber-700 dark:text-lime-300 transition-all duration-200"
              title={`Switch to ${isDark ? "light" : "dark"} mode`}
            >
              {isDark ? "☀️ Light" : "🌙 Dark"}
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center gap-2">
            <button
              onClick={() => setIsDark((prev) => !prev)}
              className="px-2 py-1 text-sm border border-amber-300 dark:border-orange-600 rounded-lg bg-amber-100 dark:bg-orange-900 hover:bg-amber-200 dark:hover:bg-orange-800 text-amber-700 dark:text-lime-300 transition-all duration-200"
            >
              {isDark ? "☀️" : "🌙"}
            </button>
            <button
              onClick={() => setIsOpen((prev) => !prev)}
              className="text-amber-700 dark:text-lime-400 hover:text-amber-600 dark:hover:text-lime-300 transition-colors duration-200"
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
