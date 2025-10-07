import { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, X } from "lucide-react";
import NavItem from "./NavItem";
import ThemeToggleButton from "./ThemeToggleButton";
import LanguageSwitcher from "./LanguageSwitcher";
import { useTranslation } from "react-i18next";

interface NavbarProps {
  isDark: boolean;
  setIsDark: React.Dispatch<React.SetStateAction<boolean>>;
}

const Navbar = ({ isDark, setIsDark }: NavbarProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const { t } = useTranslation();

  return (
    <nav className="glassmorphism backdrop-blur-sm shadow-lg sticky top-0 z-50 border-b border-secondary/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-2 text-2xl font-bold">
            <span className="logo-gradient bg-clip-text text-transparent">
              Miss Bott
            </span>
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex space-x-6 items-center text-navbar">
            <NavItem
              to="/"
              label={t("navbar.about")}
              onClick={() => setIsOpen(false)}
            />
            <NavItem
              to="/services"
              label={t("navbar.services")}
              onClick={() => setIsOpen(false)}
            />
            <NavItem
              to="/blog"
              label={t("navbar.blog")}
              onClick={() => setIsOpen(false)}
            />
            <NavItem
              to="/contact"
              label={t("navbar.contact")}
              onClick={() => setIsOpen(false)}
            />
            <div className="ml-4">
              <ThemeToggleButton isDark={isDark} setIsDark={setIsDark} />
            </div>
            <div className="ml-4">
              <LanguageSwitcher />
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center gap-4">
            {/* --- REPLACED THE OLD BUTTON WITH THE NEW COMPONENT --- */}
            <ThemeToggleButton isDark={isDark} setIsDark={setIsDark} />
            <button
              onClick={() => setIsOpen((prev) => !prev)}
              className="text-secondary"
              aria-label="Toggle mobile menu"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile dropdown */}
        {isOpen && (
          <div className="md:hidden mt-2 pb-4 space-y-2 flex flex-col">
            <NavItem to="/" label="About Me" onClick={() => setIsOpen(false)} />
            <NavItem
              to="/skills"
              label="Skills"
              onClick={() => setIsOpen(false)}
            />
            <NavItem
              to="/services"
              label="Services"
              onClick={() => setIsOpen(false)}
            />
            <NavItem to="/blog" label="Blog" onClick={() => setIsOpen(false)} />
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
