import { useEffect, useState } from "react";
import { SiGithub, SiLinkedin, SiInstagram, SiX } from "react-icons/si";

const Footer = () => {
  const [isDark, setIsDark] = useState(false);

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
    <footer className="text-primary backdrop-blur-sm border-t border-golden-light/20 dark:border-leaf-dark/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-3 flex items-center justify-between">
          <p className="text-xs text-stone-50-dark dark:text-stone-100-light">
            &copy; {new Date().getFullYear()} Miss Bott. All rights reserved.
          </p>
          <div className="flex items-center space-x-3">
            <a
              className="text-primary transition-colors duration-200"
              href="https://github.com/petra66orii"
              target="_blank"
              rel="noopener noreferrer"
            >
              <SiGithub className="w-4 h-4" />
            </a>
            <a
              className="text-primary transition-colors duration-200"
              href="https://www.linkedin.com/in/petra-bot-a552601a4/"
              target="_blank"
              rel="noopener noreferrer"
            >
              <SiLinkedin className="w-4 h-4" />
            </a>
            <a
              className="text-primary transition-colors duration-200"
              href="https://www.instagram.com/missbott_dev/"
              target="_blank"
              rel="noopener noreferrer"
            >
              <SiInstagram className="w-4 h-4" />
            </a>
            <a
              className="text-primary transition-colors duration-200"
              href="https://twitter.com/missbott_dev"
              target="_blank"
              rel="noopener noreferrer"
            >
              <SiX className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
