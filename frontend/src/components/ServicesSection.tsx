import React, { useState, useEffect } from 'react';
import { Code, Wrench, Zap, Users, ArrowRight, Check } from 'lucide-react';

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
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const response = await fetch('/api/services/');
      const data = await response.json();
      setServices(data);
    } catch (error) {
      console.error('Error fetching services:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName as keyof typeof iconMap] || Code;
    return IconComponent;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 via-white to-amber-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Professional
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-600 to-orange-600 ml-3">
              Web Services
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            From custom web development to ongoing maintenance, I deliver modern, 
            high-performance solutions tailored to your business needs.
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
                className={`group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 border border-gray-100 ${
                  service.featured ? 'ring-2 ring-amber-400 ring-opacity-50' : ''
                }`}
                onMouseEnter={() => setHoveredCard(service.id)}
                onMouseLeave={() => setHoveredCard(null)}
              >
                {/* Featured Badge */}
                {service.featured && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                )}

                {/* Icon */}
                <div className={`inline-flex items-center justify-center w-16 h-16 rounded-xl mb-6 transition-all duration-300 ${
                  isHovered 
                    ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white scale-110' 
                    : 'bg-gradient-to-r from-amber-100 to-orange-100 text-amber-600'
                }`}>
                  <IconComponent className="w-8 h-8" />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold text-gray-900 mb-4 group-hover:text-amber-600 transition-colors">
                  {service.name}
                </h3>
                
                <p className="text-gray-600 mb-6 leading-relaxed">
                  {service.short_description}
                </p>

                {/* Features */}
                <ul className="space-y-3 mb-8">
                  {service.features_list.slice(0, 3).map((feature, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <Check className={`w-5 h-5 mt-0.5 flex-shrink-0 transition-colors ${
                        isHovered ? 'text-amber-500' : 'text-green-500'
                      }`} />
                      <span className="text-gray-700 text-sm">{feature}</span>
                    </li>
                  ))}
                  {service.features_list.length > 3 && (
                    <li className="text-amber-600 text-sm font-medium">
                      +{service.features_list.length - 3} more features
                    </li>
                  )}
                </ul>

                {/* Pricing and CTA */}
                <div className="border-t border-gray-100 pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="text-2xl font-bold text-gray-900">
                        {service.starting_price || 'Custom Quote'}
                      </p>
                      {service.delivery_time && (
                        <p className="text-sm text-gray-500">{service.delivery_time}</p>
                      )}
                    </div>
                  </div>
                  
                  <button className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center space-x-2 ${
                    service.featured
                      ? 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg hover:shadow-xl'
                      : 'bg-gray-900 hover:bg-amber-600 text-white'
                  }`}>
                    <span>Get Quote</span>
                    <ArrowRight className={`w-4 h-4 transition-transform ${isHovered ? 'translate-x-1' : ''}`} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-8 md:p-12">
            <h3 className="text-3xl font-bold text-white mb-4">
              Ready to Start Your Project?
            </h3>
            <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
              Let's discuss your requirements and create something amazing together. 
              Get a free consultation and personalized quote.
            </p>
            <button className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-semibold py-4 px-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
              Schedule Free Consultation
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;
