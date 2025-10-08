// src/pages/ServiceDetailPage.tsx

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import SEO from "../components/SEO";
import {
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  UserCheck,
  Package,
  Rocket,
} from "lucide-react";
import { useTranslation } from "react-i18next";

// The full service type
type Service = {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  description: string;
  features_list: string[];
  icon: string;
};

const ServiceDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { t } = useTranslation();

  useEffect(() => {
    const fetchService = async () => {
      try {
        const response = await fetch(`/api/services/${slug}/`);
        if (!response.ok) {
          throw new Error(`Service not found. Status: ${response.status}`);
        }
        const data: Service = await response.json();
        setService(data);
      } catch (err) {
        setError("Failed to fetch service details. Please try again later.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchService();
  }, [slug]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !service) {
    return (
      <div className="text-center py-20">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-500" />
        <h2 className="mt-4 text-2xl font-bold text-primary">Error</h2>
        <p className="mt-2 text-secondary">
          {error || "The service could not be found."}
        </p>
        <Link
          to="/services"
          className="mt-6 inline-block text-primary hover:underline"
        >
          &larr; Back to Solutions
        </Link>
      </div>
    );
  }

  const whoIsItForList =
    t(`service_detail_page.who_is_it_for_map.${service.slug}`, {
      returnObjects: true,
    }) || [];

  return (
    <>
      <SEO
        title={`${service.name} | Miss Bott`}
        description={service.short_description}
      />
      <main className="min-h-screen p-6">
        <div className="max-w-5xl mx-auto">
          <Link
            to="/services"
            className="inline-flex items-center gap-2 text-secondary hover:text-primary mb-8"
          >
            <ArrowLeft size={16} /> {t("service_detail_page.back_button")}
          </Link>

          {/* --- Hero Section --- */}
          <section className="text-center mb-20">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 text-primary">
              {service.name}
            </h1>
            <p className="text-xl text-secondary max-w-3xl mx-auto leading-relaxed">
              {service.description}
            </p>
          </section>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="md:col-span-2">
              {/* --- What's Included Section --- */}
              <section className="mb-16">
                <h2 className="text-3xl font-bold text-primary mb-6 flex items-center gap-3">
                  <Package /> {t("service_detail_page.whats_included")}
                </h2>
                <ul className="grid sm:grid-cols-2 gap-4">
                  {service.features_list.map((feature, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 mt-1 flex-shrink-0 text-green-500" />
                      <span className="text-secondary">{feature}</span>
                    </li>
                  ))}
                </ul>
              </section>

              {/* --- Our Process Section --- */}
              <section>
                <h2 className="text-3xl font-bold text-primary mb-6 flex items-center gap-3">
                  <Rocket /> {t("service_detail_page.our_process")}
                </h2>
                <ol className="space-y-4">
                  <li className="flex items-center gap-4">
                    <strong className="text-primary text-2xl">1.</strong>
                    <span className="text-secondary">
                      <strong>
                        {t("service_detail_page.process_step1_title")}
                      </strong>{" "}
                      {t("service_detail_page.process_step1_desc")}
                    </span>
                  </li>
                  <li className="flex items-center gap-4">
                    <strong className="text-primary text-2xl">2.</strong>
                    <span className="text-secondary">
                      <strong>
                        {t("service_detail_page.process_step2_title")}
                      </strong>{" "}
                      {t("service_detail_page.process_step2_desc")}
                    </span>
                  </li>
                  <li className="flex items-center gap-4">
                    <strong className="text-primary text-2xl">3.</strong>
                    <span className="text-secondary">
                      <strong>
                        {t("service_detail_page.process_step3_title")}
                      </strong>{" "}
                      {t("service_detail_page.process_step3_desc")}
                    </span>
                  </li>
                </ol>
              </section>
            </div>

            {/* --- Sidebar --- */}
            <div className="md:col-span-1">
              <div className="glassmorphism p-6 rounded-xl border sticky top-24">
                <h3 className="text-xl font-semibold mb-4 text-primary flex items-center gap-2">
                  <UserCheck /> {t("service_detail_page.who_is_it_for")}
                </h3>
                <ul className="space-y-2 mb-8">
                  {Array.isArray(whoIsItForList) &&
                    whoIsItForList.map((item) => (
                      <li
                        key={item}
                        className="flex items-start space-x-2 text-secondary text-sm"
                      >
                        <span>✓</span>
                        <span>{item}</span>
                      </li>
                    ))}
                </ul>
                <Link
                  to="/quote"
                  className="w-full inline-block text-center px-6 py-3 button-gradient text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  {t("service_detail_page.cta_button")}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
};

export default ServiceDetailPage;
