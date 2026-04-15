import { useTranslation } from "react-i18next";
import { SiLinkedin, SiInstagram, SiX } from "react-icons/si";
import { Link } from "react-router-dom";
import { ArrowRight, Mail } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";
import logoDark from "../assets/logos/mb-logo-dark.png";
import logoLight from "../assets/logos/mb-logo-light.png";

interface FooterProps {
  isDark: boolean;
}

const Footer = ({ isDark }: FooterProps) => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();
  const [email, setEmail] = useState("");
  const [newsletterMessage, setNewsletterMessage] = useState("");
  const [isSubmittingNewsletter, setIsSubmittingNewsletter] = useState(false);
  const currentLogo = isDark ? logoDark : logoLight;

  const siteLinks = [
    { to: "/", label: t("navbar.home") },
    { to: "/about", label: t("navbar.about") },
    { to: "/services", label: t("navbar.services") },
    { to: "/blog", label: t("navbar.blog") },
    { to: "/contact", label: t("navbar.contact") },
  ];

  const legalLinks = [
    { to: "/privacy-policy", label: t("footer.privacy_policy") },
    { to: "/cookie-policy", label: t("footer.cookies_policy") },
    { to: "/terms-of-use", label: t("footer.terms_of_use") },
  ];

  const handleNewsletterSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (isSubmittingNewsletter) return;

    setIsSubmittingNewsletter(true);
    setNewsletterMessage(t("newsletter.subscribing"));

    try {
      const response = await fetch("/api/newsletter-signup/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || t("newsletter.error_generic"));
      }

      setNewsletterMessage(t("newsletter.success"));
      setEmail("");
    } catch (err) {
      if (err instanceof Error) {
        setNewsletterMessage(err.message);
      } else {
        setNewsletterMessage(t("newsletter.error_unexpected"));
      }
    } finally {
      setIsSubmittingNewsletter(false);
    }
  };

  return (
    <footer className="text-primary border-t border-secondary/20 bg-gradient-to-b from-transparent to-primary/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-10 grid gap-8 md:grid-cols-[1.1fr_0.9fr_0.9fr]">
          <div className="space-y-4">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 border border-secondary/20 px-2.5 py-1 text-[11px] font-semibold secondary leading-none w-fit">
              <img
                src={currentLogo}
                alt={t("footer.logo_alt")}
                className="h-3.5 w-auto"
              />
              {t("footer.trust_badge")}
            </span>
            <p className="text-sm sm:text-base text-secondary leading-relaxed max-w-md">
              {t("footer.tagline")}
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <a
                href="mailto:contact@missbott.online"
                className="inline-flex items-center gap-2 text-sm text-primary hover:secondary transition-colors"
              >
                <Mail size={14} />
                <span>{t("footer.email_label")}</span>
              </a>
              <Link
                to="/quote"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl button-gradient text-white text-sm font-semibold transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                {t("footer.discovery_cta")}
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>

          <div>
            <h3 className="text-xs uppercase tracking-[0.18em] secondary font-semibold mb-3">
              {t("footer.navigation_title")}
            </h3>
            <ul className="space-y-2">
              {siteLinks.map((link) => (
                <li key={link.to}>
                  <Link
                    to={link.to}
                    className="text-sm text-secondary hover:text-primary transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-xs uppercase tracking-[0.18em] secondary font-semibold mb-3">
              {t("footer.legal_title")}
            </h3>
            <ul className="space-y-2 mb-5">
              {legalLinks.map((link) => (
                <li key={link.to}>
                  <Link
                    to={link.to}
                    className="text-sm text-secondary hover:text-primary transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>

            <h3 className="text-xs uppercase tracking-[0.18em] secondary font-semibold mb-3">
              {t("footer.social_title")}
            </h3>
            <div className="flex items-center gap-2">
              <a
                className="w-8 h-8 rounded-full border border-secondary/20 bg-surface/50 flex items-center justify-center text-primary transition-all duration-200 hover:-translate-y-0.5 hover:text-secondary hover:border-secondary/40"
                href="https://www.linkedin.com/in/petra-bot-a552601a4/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="LinkedIn Profile"
              >
                <SiLinkedin className="w-3.5 h-3.5" />
              </a>
              <a
                className="w-8 h-8 rounded-full border border-secondary/20 bg-surface/50 flex items-center justify-center text-primary transition-all duration-200 hover:-translate-y-0.5 hover:text-secondary hover:border-secondary/40"
                href="https://www.instagram.com/missbott_dev/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Instagram Profile"
              >
                <SiInstagram className="w-3.5 h-3.5" />
              </a>
              <a
                className="w-8 h-8 rounded-full border border-secondary/20 bg-surface/50 flex items-center justify-center text-primary transition-all duration-200 hover:-translate-y-0.5 hover:text-secondary hover:border-secondary/40"
                href="https://twitter.com/missbott_dev"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="X (formerly Twitter) Profile"
              >
                <SiX className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>

        <section className="mb-6 rounded-2xl border border-secondary/20 bg-surface/30 px-4 py-4 sm:px-5 sm:py-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h3 className="text-sm font-semibold text-primary">
                {t("footer.newsletter_title")}
              </h3>
              <p className="text-xs text-secondary mt-1">
                {t("footer.newsletter_subtitle")}
              </p>
            </div>
            <form
              onSubmit={handleNewsletterSubmit}
              className="flex flex-col sm:flex-row gap-2 w-full md:w-auto md:min-w-[420px]"
            >
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t("footer.newsletter_placeholder")}
                required
                disabled={isSubmittingNewsletter}
                className="min-w-0 flex-1 rounded-xl border border-secondary/30 bg-surface/70 px-3 py-2 text-sm text-primary placeholder:text-secondary/70 focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-70"
              />
              <button
                type="submit"
                disabled={isSubmittingNewsletter}
                className="rounded-xl button-gradient px-4 py-2 text-sm font-semibold text-white transition-all duration-200 disabled:opacity-70"
              >
                {isSubmittingNewsletter
                  ? t("footer.newsletter_button_loading")
                  : t("footer.newsletter_button")}
              </button>
            </form>
          </div>
          {newsletterMessage && (
            <p className="mt-2 text-xs text-secondary">{newsletterMessage}</p>
          )}
        </section>

        <div className="py-4 border-t border-secondary/20 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <p className="text-xs text-secondary">
            {t("footer.copyright", { year: currentYear })}
          </p>
          <p className="text-xs text-secondary/80">{t("footer.impressum")}</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
