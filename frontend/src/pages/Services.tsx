import React from "react";
import ServicesSection from "../components/ServicesSection";
import SEO from "../components/SEO";

const Services: React.FC = () => {
  return (
    <>
      <SEO
        title="Professional Web Development Services | Miss Bott"
        description="Expert web development and maintenance services. Custom websites, performance optimization, and ongoing support for your business."
        keywords="web development services Ireland, custom React websites, Django backend development, website maintenance Dublin, SEO optimization services, web performance tuning, professional web developer Ireland"
      />
      <div className="min-h-screen">
        <ServicesSection />
      </div>
    </>
  );
};

export default Services;
