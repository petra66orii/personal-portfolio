import React from "react";
import ServicesSection from "../components/ServicesSection";
import SEO from "../components/SEO";

const Services: React.FC = () => {
  return (
    <>
      <SEO
        title="Solutions for Creatives: Web Design & E-Commerce | Miss Bott"
        description="Specialized web design and development solutions for artists, photographers, and creative professionals. Discover packages for digital portfolios, e-commerce, and more."
        keywords="web design for artists, photographer portfolio websites, e-commerce for creatives, custom websites Ireland, portfolio websites for designers, web developer for artists"
      />
      <div className="min-h-screen">
        <ServicesSection />
      </div>
    </>
  );
};

export default Services;
