import React from 'react';
import ServicesSection from '../components/ServicesSection';
import SEO from '../components/SEO';

const Services: React.FC = () => {
  return (
    <>
      <SEO 
        title="Professional Web Development Services | Miss Bott"
        description="Expert web development and maintenance services. Custom websites, performance optimization, and ongoing support for your business."
        keywords="web development services, website maintenance, custom websites, React development, Django development"
      />
      <div className="min-h-screen">
        <ServicesSection />
      </div>
    </>
  );
};

export default Services;
