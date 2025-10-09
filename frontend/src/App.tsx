import { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
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

function App() {
  // 1. Theme state is now managed here in the main App component
  const [isDark, setIsDark] = useState(false);

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

      <Navbar isDark={isDark} setIsDark={setIsDark} />

      <main className="min-h-screen relative z-10">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/services" element={<Services />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/quote" element={<ProjectInquiry />} />
          <Route path="/services/:slug" element={<ServiceDetailPage />} />
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
          <Route path="*" element={<ErrorPage code={404} />} />
        </Routes>
      </main>
      <Footer />
    </>
  );
}

export default App;
