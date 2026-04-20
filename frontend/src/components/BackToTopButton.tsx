import { useEffect, useState } from "react";
import { ArrowUp } from "lucide-react";

const VISIBILITY_THRESHOLD = 320;

const BackToTopButton = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsVisible(window.scrollY > VISIBILITY_THRESHOLD);
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleClick = () => {
    window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label="Back to top"
      title="Back to top"
      className={[
        "fixed right-4 z-40 rounded-full border border-secondary/30",
        "bg-surface/85 p-3 text-primary shadow-lg backdrop-blur-md",
        "transition-all duration-300 hover:-translate-y-1 hover:text-secondary",
        "focus:outline-none focus:ring-2 focus:ring-secondary/50",
        "sm:right-6",
        "bottom-24 sm:bottom-28",
        isVisible
          ? "pointer-events-auto translate-y-0 opacity-100"
          : "pointer-events-none translate-y-3 opacity-0",
      ].join(" ")}
    >
      <ArrowUp size={18} />
    </button>
  );
};

export default BackToTopButton;
