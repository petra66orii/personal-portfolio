import { createLucideIcon } from "lucide-react";
import { unicornHead } from "@lucide/lab";
import { motion } from "framer-motion";

const Unicorn = createLucideIcon("Unicorn", unicornHead);

const UnicornIcon = () => (
  <motion.div
    className="relative w-8 h-8 flex items-center justify-center"
    whileHover={{
      scale: 1.15,
      rotate: [0, -5, 5, 0],
      filter: "drop-shadow(0 0 10px rgba(255, 255, 255, 0.6))",
    }}
    transition={{ type: "spring", stiffness: 300, damping: 12 }}
  >
    {/* Animated sparkles */}
    <div className="absolute w-full h-full animate-ping rounded-full bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 opacity-20 blur-lg dark:from-yellow-300 dark:via-pink-500 dark:to-green-400" />

    {/* Twinkle 1 */}
    <motion.div
      className="absolute w-2 h-2 rounded-full bg-white dark:bg-yellow-300 opacity-0 blur-sm"
      initial={{ opacity: 0 }}
      whileHover={{
        opacity: [0, 1, 0],
        x: [-5, 0, 5],
        y: [5, 0, -5],
        scale: [0.8, 1.3, 0.8],
      }}
      transition={{
        duration: 0.8,
        repeat: Infinity,
        repeatType: "loop",
        ease: "easeInOut",
      }}
    />
    {/* Twinkle 2 */}
    <motion.div
      className="absolute w-1.5 h-1.5 rounded-full bg-pink-400 dark:bg-green-400 opacity-0 blur-sm"
      initial={{ opacity: 0 }}
      whileHover={{
        opacity: [0, 1, 0],
        x: [5, 0, -5],
        y: [-5, 0, 5],
        scale: [1, 1.5, 1],
      }}
      transition={{
        duration: 1,
        delay: 0.2,
        repeat: Infinity,
        repeatType: "loop",
        ease: "easeInOut",
      }}
    />

    {/* Unicorn SVG with dual gradient */}
    <svg
      viewBox="0 0 24 24"
      className="w-7 h-7 z-10"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
    >
      <defs>
        <linearGradient id="gradient-light" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#965E14" />
          <stop offset="50%" stopColor="#EE9B0C" />
          <stop offset="100%" stopColor="#AFDC0F" />
        </linearGradient>
        <linearGradient id="gradient-dark" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#965E14" />
          <stop offset="50%" stopColor="#EE9B0C" />
          <stop offset="100%" stopColor="#AFDC0F" />
        </linearGradient>
      </defs>

      {/* Twin unicorns for light/dark */}
      <g className="dark:hidden">
        <Unicorn stroke="url(#gradient-light)" strokeWidth="1.5" />
      </g>
      <g className="hidden dark:block">
        <Unicorn stroke="url(#gradient-dark)" strokeWidth="1.5" />
      </g>
    </svg>
  </motion.div>
);

export default UnicornIcon;
