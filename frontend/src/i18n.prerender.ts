import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import translationEN from "./locales/en.json";
import translationRO from "./locales/ro.json";
import translationES from "./locales/es.json";

if (!i18n.isInitialized) {
  void i18n.use(initReactI18next).init({
    lng: "en",
    fallbackLng: "en",
    interpolation: {
      escapeValue: false,
    },
    resources: {
      en: { translation: translationEN },
      ro: { translation: translationRO },
      es: { translation: translationES },
    },
  });
}

export default i18n;
