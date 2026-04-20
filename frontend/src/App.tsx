import { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Schema from "./components/Schema";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Contact from "./pages/Contact";
import Blog from "./pages/Blog";
import Services from "./pages/Services";
import Footer from "./components/Footer";
import ProjectInquiry from "./components/ProjectInquiry";
import ServiceDetailPage from "./pages/ServiceDetailPage";
import AnimatedBackground from "./components/AnimatedBackground";
import ProjectDetailPage from "./pages/ProjectDetailPage";
import ErrorPage from "./pages/ErrorPage";
import CookieConsent from "react-cookie-consent";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import CookiePolicy from "./pages/CookiePolicy";
import TermsOfUse from "./pages/TermsOfUse";
import BlogDetailPage from "./pages/BlogDetailPage";
import About from "./pages/About";
import ScrollToTopOnRouteChange from "./components/ScrollToTopOnRouteChange";
import BackToTopButton from "./components/BackToTopButton";
import SeoLandingPage from "./pages/SeoLandingPage";

function App() {
  // 1. Theme state is now managed here in the main App component
  const [isDark, setIsDark] = useState(false);
  const isClient = typeof window !== "undefined";

  useEffect(() => {
    const html = document.documentElement;
    const stored = localStorage.getItem("theme");
    // Initialize theme based on localStorage or system preference
    if (
      stored === "dark" ||
      (!stored && window.matchMedia("(prefers-color-scheme: dark)").matches)
    ) {
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
    <>
      <AnimatedBackground isDark={isDark} />
      <Schema />
      <ScrollToTopOnRouteChange />
      <Navbar isDark={isDark} setIsDark={setIsDark} />

      <main className="min-h-screen relative z-10">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/services" element={<Services />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/blog/:slug" element={<BlogDetailPage />} />
          <Route path="/quote" element={<ProjectInquiry />} />
          <Route path="/services/:slug" element={<ServiceDetailPage />} />
          <Route
            path="/custom-web-development-agency"
            element={<SeoLandingPage slug="custom-web-development-agency" />}
          />
          <Route
            path="/custom-web-developer-ireland"
            element={<SeoLandingPage slug="custom-web-developer-ireland" />}
          />
          <Route
            path="/web-development-agency-galway"
            element={<SeoLandingPage slug="web-development-agency-galway" />}
          />
          <Route
            path="/web-development-agency-dublin"
            element={<SeoLandingPage slug="web-development-agency-dublin" />}
          />
          <Route
            path="/django-react-developer"
            element={<SeoLandingPage slug="django-react-developer" />}
          />
          <Route
            path="/international-web-development"
            element={<SeoLandingPage slug="international-web-development" />}
          />
          <Route
            path="/web-developer-ireland"
            element={<Navigate to="/custom-web-developer-ireland" replace />}
          />
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
          <Route path="*" element={<ErrorPage code={404} />} />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
          <Route path="/cookie-policy" element={<CookiePolicy />} />
          <Route path="/terms-of-use" element={<TermsOfUse />} />
        </Routes>
      </main>

      {isClient && (
        <CookieConsent
          location="bottom"
          buttonText="I Accept"
          declineButtonText="Decline"
          cookieName="missbott-gdpr-consent"
          style={{ background: "#1f2937", color: "#ffffff" }} // Dark grey bg
          buttonStyle={{
            background: "#10b981",
            color: "#fff",
            fontSize: "13px",
            borderRadius: "4px",
          }} // Green button
          declineButtonStyle={{
            background: "#F4320B",
            color: "#000",
            fontSize: "13px",
            borderRadius: "4px",
          }}
          expires={150}
          enableDeclineButton
        >
          This website uses cookies to ensure you get the best experience.{" "}
          <a
            href="/cookie-policy"
            style={{ color: "#10b981", textDecoration: "underline" }}
          >
            Learn more
          </a>
        </CookieConsent>
      )}

      <BackToTopButton />
      <Footer isDark={isDark} />
    </>
  );
}

export default App;
