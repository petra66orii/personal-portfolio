// src/pages/ErrorPage.tsx

import { Link } from "react-router-dom";
import { AlertTriangle, ServerCrash, Lock, Home } from "lucide-react";
import SEO from "../components/SEO";
import { useTranslation } from "react-i18next";

interface ErrorPageProps {
  code: number;
}

interface ErrorDetails {
  seo_title: string;
  seo_desc: string;
  title: string;
  message: string;
}

// Keep the icon map separate as it's not translatable
const iconMap = {
  404: AlertTriangle,
  403: Lock,
  500: ServerCrash,
};

const ErrorPage: React.FC<ErrorPageProps> = ({ code }) => {
  const { t } = useTranslation();

  // Fetch the details object from the translation file
  const details = t(`error_page.${code}`, { returnObjects: true });
  const fallbackDetails = t("error_page.500", {
    returnObjects: true,
  }) as ErrorDetails;

  // Determine which details to use
  const currentDetails =
    typeof details === "object" && details !== null
      ? (details as ErrorDetails)
      : fallbackDetails;

  const Icon = iconMap[code as keyof typeof iconMap] || ServerCrash;

  return (
    <>
      <SEO
        title={currentDetails.seo_title}
        description={currentDetails.seo_desc}
      />
      <main className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center">
          <Icon className="mx-auto h-16 w-16 text-primary mb-4" />
          <h1 className="text-6xl font-bold text-primary">{code}</h1>
          <h2 className="text-2xl font-semibold text-primary mt-4 mb-2">
            {currentDetails.title}
          </h2>
          <p className="text-secondary max-w-sm mx-auto mb-8">
            {currentDetails.message}
          </p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
          >
            <Home size={18} /> {t("error_page.go_home_button")}
          </Link>
        </div>
      </main>
    </>
  );
};

export default ErrorPage;
