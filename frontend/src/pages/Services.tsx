import React from "react";
import ServicesSection from "../components/ServicesSection";
import SEO from "../components/SEO";
import { useTranslation } from "react-i18next";

const Services: React.FC = () => {
  const { t } = useTranslation();

  return (
    <>
      <SEO
        title={t("services_page_v2.seo_title")}
        description={t("services_page_v2.seo_description")}
        keywords={t("services_page_v2.seo_keywords")}
      />
      <div className="min-h-screen">
        <ServicesSection />
      </div>
    </>
  );
};

export default Services;
