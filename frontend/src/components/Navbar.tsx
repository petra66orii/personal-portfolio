import { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, X } from "lucide-react";
import NavItem from "./NavItem";
import ThemeToggleButton from "./ThemeToggleButton";
import LanguageSwitcher from "./LanguageSwitcher";
import { useTranslation } from "react-i18next";
import logoDark from "../assets/logos/mb-logo-dark.png";
import logoLight from "../assets/logos/mb-logo-light.png";

interface NavbarProps {
  isDark: boolean;
  setIsDark: React.Dispatch<React.SetStateAction<boolean>>;
}

const Navbar = ({ isDark, setIsDark }: NavbarProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const { t } = useTranslation();

  // --- SELECT LOGO BASED ON THEME ---
  const currentLogo = isDark ? logoDark : logoLight;

  return (
    <nav className="glassmorphism backdrop-blur-sm shadow-lg sticky top-0 z-50 border-b border-secondary/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* --- REPLACED THE TEXT SPAN WITH THE IMAGE TAG --- */}
          <Link to="/" className="flex items-center">
            <img
              src={currentLogo}
              alt="Miss Bott Logo"
              className="h-16 w-auto"
            />
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
            <div>
              <LanguageSwitcher />
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
