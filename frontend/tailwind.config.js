/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Dark Mode: "Cyber Violet"
        'primary-dark': '#9B5DE5',      // Cyber Violet
        'secondary-dark': '#F15BB5',    // Hot Pink
        'background-dark': '#0A0A0F',   // Near Black
        'surface-dark': '#1C1C24',      // Dark Gray
        'text-dark-primary': '#FFFFFF',
        'text-dark-secondary': '#B3B3C9',

        // Light Mode: "Neo Mint"
        'primary-light': '#AAF0D1',     // Neo Mint
        'secondary-light': '#6C63FF',   // Electric Indigo
        'background-light': '#FFFFFF',  // Pure White
        'surface-light': '#F5F7FA',     // Soft Gray-Blue
        'text-light-primary': '#0A0A0F',
        'text-light-secondary': '#4B4B5A',
      },
      backgroundImage: {
        'highlight-dark': 'linear-gradient(to right, #9B5DE5, #F15BB5)',
        'highlight-light': 'linear-gradient(to right, #AAF0D1, #6C63FF)',
      },
    },
  },
};
