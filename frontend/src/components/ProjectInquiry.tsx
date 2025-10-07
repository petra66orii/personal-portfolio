import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import {
  ArrowRight,
  Check,
  Loader,
  AlertTriangle,
  Building,
  Calendar,
  Phone,
  Link as LinkIcon,
  User,
  Mail,
  MessageSquare,
} from "lucide-react";
import SEO from "../components/SEO";
import { FaEuroSign, FaConciergeBell } from "react-icons/fa";

// Helper function to get CSRF token from cookies
function getCookie(name: string): string | null {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

interface Service {
  id: number;
  name: string;
}

const ProjectInquiry = () => {
  const { t, i18n } = useTranslation();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    service: "",
    name: "",
    email: "",
    company: "",
    project_details: "",
    budget_range: "",
    timeline: "",
    phone: "",
    website_url: "",
  });
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await fetch("/api/services/", {
          headers: { "Accept-Language": i18n.language },
        });
        if (!response.ok) throw new Error("Failed to fetch services");
        const data = await response.json();
        setServices(data);
      } catch (error) {
        console.error("Error fetching services:", error);
      }
    };
    fetchServices();
  }, [i18n.language]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleNext = () => setStep((prev) => prev + 1);
  const handlePrev = () => setStep((prev) => prev - 1);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const csrfToken = getCookie("csrftoken");
      const response = await fetch("/api/service-inquiry/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || t("project_inquiry.error_submit"));
      }

      setSuccess(true);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || t("project_inquiry.error_unexpected"));
      } else {
        setError(t("project_inquiry.error_unexpected"));
      }
    } finally {
      setLoading(false);
    }
  };

  const budgetRanges = [
    { value: "under_1k", label: t("project_inquiry.budgets.under_1k") },
    { value: "1k_5k", label: t("project_inquiry.budgets.1k_5k") },
    { value: "5k_10k", label: t("project_inquiry.budgets.5k_10k") },
    { value: "10k_plus", label: t("project_inquiry.budgets.10k_plus") },
    { value: "not_sure", label: t("project_inquiry.budgets.not_sure") },
  ];

  const timelines = [
    { value: "asap", label: t("project_inquiry.timelines.asap") },
    { value: "1_month", label: t("project_inquiry.timelines.1_month") },
    { value: "2_3_months", label: t("project_inquiry.timelines.2_3_months") },
    { value: "flexible", label: t("project_inquiry.timelines.flexible") },
  ];

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center glassmorphism p-12 rounded-2xl max-w-lg mx-auto"
        >
          <Check size={64} className="mx-auto text-green-500 mb-4" />
          <h2 className="text-3xl font-bold text-primary mb-4">
            {t("project_inquiry.success_title")}
          </h2>
          <p className="text-secondary">
            {t("project_inquiry.success_message")}
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={t("project_inquiry.seo_title")}
        description={t("project_inquiry.seo_description")}
      />
      <div className="min-h-screen p-6 flex items-center justify-center">
        <div className="glassmorphism rounded-2xl shadow-xl max-w-2xl w-full mx-auto px-8 py-12 border">
          <h2 className="text-4xl font-bold mb-2 text-primary text-center">
            {t("project_inquiry.main_title")}
          </h2>
          <p className="text-center text-secondary mb-8">
            {t("project_inquiry.main_subtitle")}
          </p>

          {/* Progress Bar */}
          <div className="w-full bg-surface rounded-full h-2.5 mb-8">
            <motion.div
              className="bg-primary h-2.5 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${(step / 3) * 100}%` }}
            />
          </div>

          <form onSubmit={handleSubmit}>
            <AnimatePresence mode="wait">
              {step === 1 && (
                <motion.div
                  key="step1"
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 50 }}
                >
                  <h3 className="text-2xl font-semibold mb-6 text-primary">
                    {t("project_inquiry.step1_title")}
                  </h3>
                  <div className="space-y-4">
                    {/* Name, Email, Company, Phone */}
                    <InputField
                      icon={User}
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder={t("project_inquiry.placeholder_name")}
                      required
                    />
                    <InputField
                      icon={Mail}
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder={t("project_inquiry.placeholder_email")}
                      required
                    />
                    <InputField
                      icon={Building}
                      name="company"
                      value={formData.company}
                      onChange={handleChange}
                      placeholder={t("project_inquiry.placeholder_company")}
                    />
                    <InputField
                      icon={Phone}
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder={t("project_inquiry.placeholder_phone")}
                    />
                  </div>
                  <div className="mt-8 flex justify-end">
                    <button
                      type="button"
                      onClick={handleNext}
                      className="px-6 py-2 button-gradient text-white font-semibold rounded-lg flex items-center gap-2"
                    >
                      {t("project_inquiry.button_next")}{" "}
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </motion.div>
              )}

              {step === 2 && (
                <motion.div
                  key="step2"
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 50 }}
                >
                  <h3 className="text-2xl font-semibold mb-6 text-primary">
                    {t("project_inquiry.step2_title")}
                  </h3>
                  <div className="space-y-4">
                    {/* Service, Details, Website URL */}
                    <SelectField
                      label={t("project_inquiry.select_service")}
                      name="service"
                      value={formData.service}
                      icon={FaConciergeBell}
                      onChange={handleChange}
                    >
                      {services.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                      <option value="Other">
                        {t("project_inquiry.other_inquiry")}
                      </option>
                    </SelectField>
                    <TextareaField
                      icon={MessageSquare}
                      name="project_details"
                      value={formData.project_details}
                      onChange={handleChange}
                      placeholder={t("project_inquiry.placeholder_details")}
                      required
                    />
                    <InputField
                      icon={LinkIcon}
                      name="website_url"
                      value={formData.website_url}
                      onChange={handleChange}
                      placeholder={t("project_inquiry.placeholder_website")}
                    />
                  </div>
                  <div className="mt-8 flex justify-between">
                    <button
                      type="button"
                      onClick={handlePrev}
                      className="px-6 py-2 button-simple text-secondary font-semibold rounded-lg"
                    >
                      {t("project_inquiry.button_previous")}
                    </button>
                    <button
                      type="button"
                      onClick={handleNext}
                      className="px-6 py-2 button-gradient text-white font-semibold rounded-lg flex items-center gap-2"
                    >
                      {t("project_inquiry.button_next")}{" "}
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </motion.div>
              )}

              {step === 3 && (
                <motion.div
                  key="step3"
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 50 }}
                >
                  <h3 className="text-2xl font-semibold mb-6 text-primary">
                    {t("project_inquiry.step3_title")}
                  </h3>
                  <div className="space-y-4">
                    {/* Budget and Timeline */}
                    <SelectField
                      icon={FaEuroSign}
                      name="budget_range"
                      value={formData.budget_range}
                      onChange={handleChange}
                      label={t("project_inquiry.label_budget")}
                    >
                      <option value="" disabled>
                        {t("project_inquiry.select_budget")}
                      </option>
                      {budgetRanges.map((b) => (
                        <option key={b.value} value={b.value}>
                          {b.label}
                        </option>
                      ))}
                    </SelectField>
                    <SelectField
                      icon={Calendar}
                      name="timeline"
                      value={formData.timeline}
                      onChange={handleChange}
                      label={t("project_inquiry.label_timeline")}
                    >
                      <option value="" disabled>
                        {t("project_inquiry.select_timeline")}
                      </option>
                      {timelines.map((t) => (
                        <option key={t.value} value={t.value}>
                          {t.label}
                        </option>
                      ))}
                    </SelectField>
                  </div>

                  {error && (
                    <div className="mt-4 text-red-500 flex items-center gap-2">
                      <AlertTriangle size={16} /> {error}
                    </div>
                  )}

                  <div className="mt-8 flex justify-between">
                    <button
                      type="button"
                      onClick={handlePrev}
                      className="px-6 py-2 button-simple text-secondary font-semibold rounded-lg"
                    >
                      {t("project_inquiry.button_previous")}
                    </button>
                    <button
                      type="submit"
                      disabled={loading}
                      className="px-6 py-2 button-gradient text-white font-semibold rounded-lg flex items-center gap-2"
                    >
                      {loading ? (
                        <>
                          <Loader size={16} className="animate-spin" />{" "}
                          {t("project_inquiry.button_submitting")}
                        </>
                      ) : (
                        t("project_inquiry.button_submit")
                      )}
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </form>
        </div>
      </div>
    </>
  );
};

// Reusable input components for consistent styling
const InputField: React.FC<
  {
    icon: React.ComponentType<{ size: number }>;
  } & React.InputHTMLAttributes<HTMLInputElement>
> = ({ icon: Icon, ...props }) => (
  <div className="relative">
    <div className="absolute top-1/2 left-4 -translate-y-1/2 text-secondary">
      <Icon size={20} />
    </div>
    <input
      {...props}
      className="w-full p-4 pl-12 border rounded-lg glassmorphism focus:outline-none focus:ring-2 focus:border-transparent ring-primary"
    />
  </div>
);

const TextareaField: React.FC<
  {
    icon: React.ComponentType<{ size: number }>;
  } & React.TextareaHTMLAttributes<HTMLTextAreaElement>
> = ({ icon: Icon, ...props }) => (
  <div className="relative">
    <div className="absolute top-7 left-4 -translate-y-1/2 text-secondary">
      <Icon size={20} />
    </div>
    <textarea
      {...props}
      rows={5}
      className="w-full p-4 pl-12 border rounded-lg glassmorphism focus:outline-none focus:ring-2 focus:border-transparent ring-primary resize-vertical"
    />
  </div>
);

const SelectField: React.FC<
  {
    icon: React.ComponentType<{ size: number }>;
    label?: string;
    children: React.ReactNode;
  } & React.SelectHTMLAttributes<HTMLSelectElement>
> = ({ icon: Icon, label, children, ...props }) => (
  <div className="relative">
    {label && (
      <label className="block text-sm font-medium text-secondary mb-2">
        {label}
      </label>
    )}
    <div className="absolute top-12 bottom-0 my-auto left-4 text-secondary">
      <Icon size={20} />
    </div>
    <select
      {...props}
      className="w-full p-4 pl-12 border rounded-lg glassmorphism focus:outline-none focus:ring-2 focus:border-transparent ring-primary appearance-none"
    >
      {children}
    </select>
    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-secondary">
      <svg
        className="fill-current h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
      >
        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
      </svg>
    </div>
  </div>
);

export default ProjectInquiry;
