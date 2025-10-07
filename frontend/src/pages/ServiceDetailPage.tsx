import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Check,
  ArrowRight,
  Code,
  Wrench,
  Zap,
  Users,
  AlertTriangle,
} from "lucide-react";
import SEO from "../components/SEO";
import ScrollAnimator from "../components/ScrollAnimator";

interface Service {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  description: string;
  features_list: string[];
  starting_price: string;
  delivery_time: string;
  icon: string;
}

const iconMap: { [key: string]: React.ElementType } = {
  code: Code,
  wrench: Wrench,
  zap: Zap,
  users: Users,
};

const ServiceDetailPage = () => {
  const { slug } = useParams<{ slug: string }>();
  const { t, i18n } = useTranslation(); // 1. Get translation functions
  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchServiceDetail = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/services/${slug}/`, {
          // 2. Send current language to the backend
          headers: { "Accept-Language": i18n.language },
        });

        if (!response.ok) {
          throw new Error(`Service not found. Status: ${response.status}`);
        }

        const data: Service = await response.json();
        setService(data);
      } catch (err) {
        console.error("Error fetching service details:", err);
        setError(t("service_detail.error_load"));
      } finally {
        setLoading(false);
      }
    };

    if (slug) {
      fetchServiceDetail();
    }
  }, [slug, i18n.language, t]); // Add 't' to dependency array

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary"></div>
      </div>
    );
  }

  if (error || !service) {
    return (
      <div className="min-h-screen p-6 flex items-center justify-center">
        <div className="glassmorphism text-center p-8 rounded-lg">
          <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h2 className="text-2xl font-bold text-primary mb-2">
            {t("service_detail.error_title")}
          </h2>
          <p className="text-secondary">
            {error || t("service_detail.error_not_exist")}
          </p>
          <Link to="/services" className="button-gradient mt-6 inline-block">
            {t("service_detail.back_button")}
          </Link>
        </div>
      </div>
    );
  }

  const IconComponent = iconMap[service.icon] || Code;

  return (
    <>
      <SEO
        title={`${service.name} | ${t("service_detail.seo_title")}`}
        description={service.short_description}
        keywords={`${service.name}, ${t("service_detail.seo_keywords")}`}
      />
      <main className="min-h-screen p-6">
        <ScrollAnimator>
          <div className="glassmorphism max-w-5xl mx-auto rounded-2xl shadow-xl overflow-hidden">
            <div className="p-8 md:p-12">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-primary/20 to-secondary/20 rounded-xl flex items-center justify-center">
                  <IconComponent className="w-8 h-8 text-primary" />
                </div>
                <div>
                  <h1 className="text-4xl md:text-5xl font-bold text-primary">
                    {service.name}
                  </h1>
                  <p className="text-lg text-secondary mt-1">
                    {service.short_description}
                  </p>
                </div>
              </div>

              {/* Use dangerouslySetInnerHTML for rich text from backend */}
              <div
                className="prose prose-lg text-secondary max-w-none mb-8"
                dangerouslySetInnerHTML={{ __html: service.description }}
              />

              <div className="bg-surface/50 rounded-lg p-6 mb-8">
                <h3 className="text-2xl font-semibold text-primary mb-4">
                  {t("service_detail.whats_included")}
                </h3>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
                  {service.features_list.map((feature, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <Check className="w-6 h-6 mt-1 flex-shrink-0 text-green-500" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex flex-col md:flex-row justify-between items-center bg-primary/10 p-6 rounded-lg">
                <div>
                  <p className="text-secondary">
                    {t("service_detail.starting_from")}
                  </p>
                  <p className="text-4xl font-bold text-primary">
                    {service.starting_price}
                  </p>
                  <p className="text-secondary">{service.delivery_time}</p>
                </div>
                <Link to="/quote" className="button-gradient mt-4 md:mt-0">
                  {t("service_detail.get_quote_button")}{" "}
                  <ArrowRight className="inline ml-2" />
                </Link>
              </div>
            </div>
          </div>
        </ScrollAnimator>
      </main>
    </>
  );
};

export default ServiceDetailPage;
