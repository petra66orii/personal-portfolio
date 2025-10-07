import { useTranslation } from "react-i18next";

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={() => changeLanguage("en")}
        className={`px-2 py-1 text-sm rounded-md ${
          i18n.language === "en" ? "font-bold text-primary" : "text-secondary"
        }`}
      >
        EN
      </button>
      <div className="w-px h-4 bg-secondary/50"></div>
      <button
        onClick={() => changeLanguage("ro")}
        className={`px-2 py-1 text-sm rounded-md ${
          i18n.language === "ro" ? "font-bold text-primary" : "text-secondary"
        }`}
      >
        RO
      </button>
    </div>
  );
};

export default LanguageSwitcher;
