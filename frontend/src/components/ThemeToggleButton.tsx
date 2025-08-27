// src/components/ThemeToggleButton.tsx

import { motion } from "framer-motion";
import { Sun, Moon } from "lucide-react";

interface ThemeToggleButtonProps {
  isDark: boolean;
  setIsDark: (value: boolean | ((prev: boolean) => boolean)) => void;
}

const ThemeToggleButton: React.FC<ThemeToggleButtonProps> = ({
  isDark,
  setIsDark,
}) => {
  const spring = {
    type: "spring" as const,
    stiffness: 700,
    damping: 30,
  };

  return (
    <button
      onClick={() => setIsDark((prev: boolean) => !prev)}
      aria-label={isDark ? "Activate light mode" : "Activate dark mode"}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className={`relative flex items-center w-20 h-10 rounded-full p-1 transition-colors duration-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-light dark:focus:ring-primary-dark ${
        isDark ? "bg-surface-dark" : "bg-surface-light"
      }`}
    >
      {/* Background Scenes SVG */}
      <div className="absolute inset-0 w-full h-full overflow-hidden rounded-full">
        {/* Night Scene */}
        <motion.div
          className="absolute inset-0 w-full h-full"
          initial={{ opacity: 0 }}
          animate={{ opacity: isDark ? 1 : 0 }}
          transition={{ duration: 0.7 }}
        >
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 80 40"
            className="absolute inset-0"
          >
            <defs>
              <linearGradient
                id="nightGradient"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="100%"
              >
                <stop offset="0%" style={{ stopColor: "#0A0A0F" }} />
                <stop offset="100%" style={{ stopColor: "#1C1C24" }} />
              </linearGradient>
            </defs>
            <rect width="80" height="40" fill="url(#nightGradient)" />
            {/* --- NEW: Night mountains and moon --- */}
            <path d="M 0 40 Q 15 20 30 40 T 60 40" fill="#1C1C24" />
            <path
              d="M 20 40 Q 35 25 50 40 T 80 40"
              fill="#4B4B5A"
              opacity="0.6"
            />
            <path
              d="M 25 8 A 5 5 0 1 1 25 18 A 4 4 0 1 0 25 8 Z"
              fill="white"
              opacity="0.9"
            />

            {/* Stars */}
            <circle cx="20" cy="10" r="1.5" fill="white" opacity="0.8" />
            <circle cx="30" cy="20" r="1" fill="white" opacity="0.6" />
            <circle cx="15" cy="25" r="1" fill="white" opacity="0.7" />
          </svg>
        </motion.div>

        {/* Day Scene */}
        <motion.div
          className="absolute inset-0 w-full h-full"
          initial={{ opacity: 1 }}
          animate={{ opacity: isDark ? 0 : 1 }}
          transition={{ duration: 0.7 }}
        >
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 80 40"
            className="absolute inset-0"
          >
            <defs>
              <linearGradient
                id="dayGradient"
                x1="0%"
                y1="100%"
                x2="100%"
                y2="0%"
              >
                <stop offset="0%" style={{ stopColor: "#F15BB5" }} />
                <stop offset="100%" style={{ stopColor: "#AAF0D1" }} />
              </linearGradient>
            </defs>
            <rect width="80" height="40" fill="url(#dayGradient)" />
            {/* --- NEW: Day dunes --- */}
            <path
              d="M 40 40 Q 55 25 70 40 T 100 40"
              fill="#F15BB5"
              opacity="0.7"
            />
            <path
              d="M 50 40 Q 65 30 80 40 T 110 40"
              fill="#9B5DE5"
              opacity="0.5"
            />

            {/* Clouds */}
            <circle cx="60" cy="15" r="8" fill="white" opacity="0.7" />
            <circle cx="55" cy="12" r="10" fill="white" opacity="0.8" />
            <circle cx="50" cy="14" r="9" fill="white" opacity="0.7" />
          </svg>
        </motion.div>
      </div>

      {/* The moving thumb */}
      <motion.div
        className="relative z-10 w-8 h-8 bg-white/80 backdrop-blur-sm rounded-full shadow-md flex items-center justify-center"
        layout
        transition={spring}
        style={{ x: isDark ? "125%" : "0%" }}
      >
        {isDark ? (
          <Moon size={16} className="text-primary-dark" />
        ) : (
          <Sun size={16} className="text-yellow-500" />
        )}
      </motion.div>
    </button>
  );
};

export default ThemeToggleButton;
