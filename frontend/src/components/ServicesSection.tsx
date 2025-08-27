import React, { useState, useEffect } from "react";
import { Code, Wrench, Zap, Users, ArrowRight, Check } from "lucide-react";
import ScrollAnimator from "../components/ScrollAnimator";
import { Link } from "react-router-dom";

interface Service {
  id: number;
  name: string;
  slug: string;
  service_type: string;
  short_description: string;
  description: string;
  features_list: string[];
  starting_price: string;
  delivery_time: string;
  icon: string;
  featured: boolean;
  active: boolean;
  order: number;
}

const iconMap = {
  code: Code,
  wrench: Wrench,
  zap: Zap,
  users: Users,
};

const ServicesSection: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await fetch("/api/services/");

        // Check for HTTP errors (like 404 Not Found)
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Check if the server sent JSON
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          throw new TypeError(
            "Server did not send JSON. Check the /api/services/ endpoint in your Django backend."
          );
        }

        const data = await response.json();
        setServices(data);
      } catch (error) {
        console.error("Error fetching services:", error);
        setServices([]); // Clear services on error
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, []);

  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName as keyof typeof iconMap] || Code;
    return IconComponent;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-400 dark:border-purple-600"></div>
      </div>
    );
  }

  return (
    <ScrollAnimator>
      <section className="py-20 glassmorphism">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-primary mb-6">
              Professional
              <span className="text-transparent bg-clip-text bg-gradient-to-r logo-gradient ml-3">
                Web Services
              </span>
            </h2>
            <p className="text-xl text-secondary max-w-3xl mx-auto leading-relaxed">
              From custom web development to ongoing maintenance, I deliver
              modern, high-performance solutions tailored to your business
              needs.
            </p>
          </div>

          {/* Services Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            {services.map((service) => {
              const IconComponent = getIcon(service.icon);
              const isHovered = hoveredCard === service.id;

              return (
                <div
                  key={service.id}
                  className={`group relative rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 border border-gray-100 glassmorphism ${
                    service.featured ? "ring-4 ring-color ring-opacity-50" : ""
                  }`}
                  onMouseEnter={() => setHoveredCard(service.id)}
                  onMouseLeave={() => setHoveredCard(null)}
                >
                  {/* Featured Badge */}
                  {service.featured && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <span className="bg-gradient-to-r logo-gradient text-primary px-4 py-1 rounded-full text-sm font-semibold">
                        Most Popular
                      </span>
                    </div>
                  )}

                  {/* Icon */}
                  <div
                    className={`inline-flex items-center justify-center w-16 h-16 rounded-xl mb-6 transition-all duration-300 ${
                      isHovered
                        ? "logo-gradient text-primary scale-110"
                        : "services-icon text-icon"
                    }`}
                  >
                    <IconComponent className="w-8 h-8" />
                  </div>

                  {/* Content */}
                  <h3 className="text-2xl font-bold title-text-primary mb-4 transition-colors">
                    {service.name}
                  </h3>

                  <p className="text-secondary mb-6 leading-relaxed">
                    {service.short_description}
                  </p>

                  {/* Features */}
                  <ul className="space-y-3 mb-8">
                    {service.features_list.slice(0, 3).map((feature, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <Check
                          className={`w-5 h-5 mt-0.5 flex-shrink-0 transition-colors ${
                            isHovered ? "secondary" : "text-green-500"
                          }`}
                        />
                        <span className="text-secondary text-sm">
                          {feature}
                        </span>
                      </li>
                    ))}
                    {service.features_list.length > 3 && (
                      <li className="secondary text-sm font-medium">
                        +{service.features_list.length - 3} more features
                      </li>
                    )}
                  </ul>

                  {/* Pricing and CTA */}
                  <div className="border-t border-gray-100 pt-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <p className="text-2xl font-bold text-primary">
                          {service.starting_price || "Custom Quote"}
                        </p>
                        {service.delivery_time && (
                          <p className="text-sm text-secondary">
                            {service.delivery_time}
                          </p>
                        )}
                      </div>
                    </div>

                    <button
                      className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center space-x-2 ${
                        service.featured
                          ? "bg-gradient-to-r button-gradient text-primary shadow-lg hover:shadow-xl"
                          : "button-simple"
                      }`}
                    >
                      <span>Get Quote</span>
                      <ArrowRight
                        className={`w-4 h-4 transition-transform ${
                          isHovered ? "translate-x-1" : ""
                        }`}
                      />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* CTA Section */}
          <ScrollAnimator>
            <div className="text-center glassmorphism">
              <div className="glassmorphism rounded-2xl p-8 md:p-12">
                <h3 className="text-3xl font-bold text-primary mb-4">
                  Ready to Start Your Project?
                </h3>
                <p className="text-secondary mb-8 max-w-2xl mx-auto">
                  Let's discuss your requirements and create something amazing
                  together. Get a free consultation and personalized quote.
                </p>
                <Link
                  to="/contact"
                  className="bg-gradient-to-r button-gradient text-white font-semibold py-4 px-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                >
                  Schedule Free Consultation
                </Link>
              </div>
            </div>
          </ScrollAnimator>
        </div>
      </section>
    </ScrollAnimator>
  );
};

export default ServicesSection;
