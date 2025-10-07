import { useTranslation } from "react-i18next";
import { SiLinkedin, SiInstagram, SiX } from "react-icons/si";

const Footer = () => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="text-primary backdrop-blur-sm border-t border-secondary/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-3 flex items-center justify-between">
          <p className="text-xs text-secondary">
            {t("footer.copyright", { year: currentYear })}
          </p>
          <div className="flex items-center space-x-3">
            <a
              className="text-primary transition-colors duration-200 hover:text-secondary"
              href="https://www.linkedin.com/in/petra-bot-a552601a4/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="LinkedIn Profile"
            >
              <SiLinkedin className="w-4 h-4" />
            </a>
            <a
              className="text-primary transition-colors duration-200 hover:text-secondary"
              href="https://www.instagram.com/missbott_dev/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Instagram Profile"
            >
              <SiInstagram className="w-4 h-4" />
            </a>
            <a
              className="text-primary transition-colors duration-200 hover:text-secondary"
              href="https://twitter.com/missbott_dev"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="X (formerly Twitter) Profile"
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
