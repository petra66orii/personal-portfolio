// src/i18n.ts
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

// Import your translation files
import translationEN from "./locales/en.json";
import translationRO from "./locales/ro.json";
import es from "./locales/es.json";

i18n
  // Detect user language
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next.
  .use(initReactI18next)
  // Init i18next
  .init({
    debug: true, // Set to false in production
    fallbackLng: "en", // Use English if detected language is not available
    interpolation: {
      escapeValue: false, // React already safes from xss
    },
    resources: {
      en: {
        translation: translationEN,
      },
      ro: {
        translation: translationRO,
      },
      es: { 
        translation: es 
      },
    },
  });

export default i18n;