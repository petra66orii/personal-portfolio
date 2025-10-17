import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import SEO from "../components/SEO";
import { CheckCircle } from "lucide-react";

// Define interfaces for form data and errors
interface FormData {
  name: string;
  email: string;
  company: string;
  phone: string;
  service: string;
  project_details: string;
  details: string;
  budget: string;
  timeline: string;
}

interface Errors {
  [key: string]: string | undefined;
}

interface Service {
  id: number;
  slug: string;
  name: string;
}

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

const ProjectInquiry = () => {
  const { t, i18n } = useTranslation();
  const [services, setServices] = useState<Service[]>([]);
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    company: "",
    phone: "",
    service: "",
    project_details: "",
    details: "",
    budget: "",
    timeline: "",
  });
  const [errors, setErrors] = useState<Errors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<"success" | "error" | null>(
    null
  );

  const totalSteps = 3;

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await fetch("/api/services/", {
          headers: { "Accept-Language": i18n.language },
        });
        const data = await response.json();
        setServices(data);
      } catch (error) {
        console.error("Failed to fetch services:", error);
      }
    };
    fetchServices();
  }, [i18n.language]);

  const validateStep = (step: number) => {
    const newErrors: Errors = {};
    if (step === 1) {
      if (!formData.name.trim()) newErrors.name = t("validation.name_required");
      if (!formData.email.trim()) {
        newErrors.email = t("validation.email_required");
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = t("validation.email_invalid");
      }
    }
    if (step === 2) {
      if (!formData.service)
        newErrors.service = t("project_inquiry.validation.service_required");
      if (!formData.project_details.trim()) {
        newErrors.project_details = t(
          "project_inquiry.validation.details_required"
        );
      } else if (formData.project_details.trim().length < 20) {
        newErrors.project_details = t("project_inquiry.validation.details_min");
      }
    }
    if (step === 3) {
      if (!formData.budget)
        newErrors.budget = t("project_inquiry.validation.budget_required");
      if (!formData.timeline)
        newErrors.timeline = t("project_inquiry.validation.timeline_required");
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    setErrors({});
    setCurrentStep((prev) => prev - 1);
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Also validate previous steps on final submission to be safe
    if (validateStep(1) && validateStep(2) && validateStep(3)) {
      setIsSubmitting(true);
      setSubmitStatus(null);
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
          const errorData = await response.json();
          // Throw an error with the specific message from the backend
          throw new Error(JSON.stringify(errorData) || "Submission failed");
        }

        setSubmitStatus("success");
      } catch (error) {
        console.error("Submission error:", error);
        setSubmitStatus("error");
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  if (submitStatus === "success") {
    return (
      <main className="min-h-screen p-6 flex items-center justify-center">
        <div className="text-center">
          <CheckCircle className="mx-auto h-16 w-16 text-green-500" />
          <h2 className="mt-4 text-3xl font-bold text-primary">
            {t("project_inquiry.success_title")}
          </h2>
          <p className="mt-2 text-secondary max-w-md mx-auto">
            {t("project_inquiry.success_message")}
          </p>
        </div>
      </main>
    );
  }

  const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;

  return (
    <>
      <SEO
        title={t("project_inquiry.seo_title")}
        description={t("project_inquiry.seo_description")}
      />
      <main className="min-h-screen p-6 flex items-center justify-center">
        <div className="glassmorphism w-full max-w-2xl p-8 rounded-2xl shadow-xl border">
          <h1 className="text-3xl font-bold text-center mb-2 text-primary">
            {t("project_inquiry.main_title")}
          </h1>
          <p className="text-center text-secondary mb-8">
            {t("project_inquiry.main_subtitle")}
          </p>

          <div className="mb-8">
            <div className="w-full bg-surface rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-secondary mt-2">
              <span className={currentStep >= 1 ? "text-primary" : ""}>
                {t("project_inquiry.step1_title")}
              </span>
              <span className={currentStep >= 2 ? "text-primary" : ""}>
                {t("project_inquiry.step2_title")}
              </span>
              <span className={currentStep >= 3 ? "text-primary" : ""}>
                {t("project_inquiry.step3_title")}
              </span>
            </div>
          </div>

          {currentStep === 1 && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleNext();
              }}
            >
              <h2 className="text-xl font-semibold mb-4">
                {t("project_inquiry.step1_title")}
              </h2>
              <div className="space-y-4">
                <div>
                  <input
                    type="text"
                    name="name"
                    placeholder={t("project_inquiry.placeholder_name")}
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full p-3 rounded-lg bg-surface border-2 border-transparent focus:border-primary focus:outline-none"
                  />
                  {errors.name && (
                    <p className="text-red-500 text-sm mt-1">{errors.name}</p>
                  )}
                </div>
                <div>
                  <input
                    type="email"
                    name="email"
                    placeholder={t("project_inquiry.placeholder_email")}
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full p-3 rounded-lg bg-surface border-2 border-transparent focus:border-primary focus:outline-none"
                  />
                  {errors.email && (
                    <p className="text-red-500 text-sm mt-1">{errors.email}</p>
                  )}
                </div>
              </div>
              <button
                type="submit"
                className="w-full mt-6 py-3 button-gradient text-white font-semibold rounded-lg"
              >
                {t("project_inquiry.button_next")}
              </button>
            </form>
          )}

          {currentStep === 2 && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleNext();
              }}
            >
              <h2 className="text-xl font-semibold mb-4">
                {t("project_inquiry.step2_title")}
              </h2>
              <div className="space-y-4">
                <div>
                  <select
                    name="service"
                    value={formData.service}
                    onChange={handleChange}
                    required
                    className="w-full p-3 rounded-lg bg-surface border-2 border-transparent focus:border-primary focus:outline-none"
                  >
                    <option value="" disabled>
                      {t("project_inquiry.select_service")}
                    </option>
                    {/* FIX 2: The value is now the service ID (a number) */}
                    {services.map((s) => (
                      <option key={s.slug} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                    <option value="other">
                      {t("project_inquiry.other_inquiry")}
                    </option>
                  </select>
                  {errors.service && (
                    <p className="text-red-500 text-sm mt-1">
                      {errors.service}
                    </p>
                  )}
                </div>
                <div>
                  {/* FIX 1: The name is now "project_details" */}
                  <textarea
                    name="project_details"
                    placeholder={t("project_inquiry.placeholder_details")}
                    value={formData.project_details}
                    onChange={handleChange}
                    required
                    maxLength={5000}
                    className="w-full p-3 h-40 rounded-lg bg-surface border-2 border-transparent focus:border-primary focus:outline-none resize-none"
                  />
                  <div className="text-right text-xs text-secondary mt-1">
                    {formData.project_details.length} / 5000
                  </div>
                  {errors.project_details && (
                    <p className="text-red-500 text-sm mt-1">
                      {errors.project_details}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex gap-4 mt-6">
                <button
                  type="button"
                  onClick={handlePrevious}
                  className="w-1/2 py-3 button-simple font-semibold rounded-lg"
                >
                  {t("project_inquiry.button_previous")}
                </button>
                <button
                  type="submit"
                  className="w-1/2 py-3 button-gradient text-white font-semibold rounded-lg"
                >
                  {t("project_inquiry.button_next")}
                </button>
              </div>
            </form>
          )}

          {currentStep === 3 && (
            <form onSubmit={handleSubmit}>
              <h2 className="text-xl font-semibold mb-4">
                {t("project_inquiry.step3_title")}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-secondary">
                    {t("project_inquiry.label_budget")}
                  </label>
                  <select
                    name="budget"
                    value={formData.budget}
                    onChange={handleChange}
                    className="w-full p-3 mt-1 rounded-lg bg-surface border-2 border-transparent focus:border-primary focus:outline-none"
                  >
                    <option value="" disabled>
                      {t("project_inquiry.select_budget")}
                    </option>
                    <option value="under_1k">
                      {t("project_inquiry.budgets.under_1k")}
                    </option>
                    <option value="1k_5k">
                      {t("project_inquiry.budgets.1k_5k")}
                    </option>
                    <option value="5k_10k">
                      {t("project_inquiry.budgets.5k_10k")}
                    </option>
                    <option value="10k_plus">
                      {t("project_inquiry.budgets.10k_plus")}
                    </option>
                    <option value="not_sure">
                      {t("project_inquiry.budgets.not_sure")}
                    </option>
                  </select>
                  {errors.budget && (
                    <p className="text-red-500 text-sm mt-1">{errors.budget}</p>
                  )}
                </div>
                <div>
                  <label className="text-sm font-medium text-secondary">
                    {t("project_inquiry.label_timeline")}
                  </label>
                  <select
                    name="timeline"
                    value={formData.timeline}
                    onChange={handleChange}
                    className="w-full p-3 mt-1 rounded-lg bg-surface border-2 border-transparent focus:border-primary focus:outline-none"
                  >
                    <option value="" disabled>
                      {t("project_inquiry.select_timeline")}
                    </option>
                    <option value="asap">
                      {t("project_inquiry.timelines.asap")}
                    </option>
                    <option value="1_month">
                      {t("project_inquiry.timelines.1_month")}
                    </option>
                    <option value="2_3_months">
                      {t("project_inquiry.timelines.2_3_months")}
                    </option>
                    <option value="flexible">
                      {t("project_inquiry.timelines.flexible")}
                    </option>
                  </select>
                  {errors.timeline && (
                    <p className="text-red-500 text-sm mt-1">
                      {errors.timeline}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex gap-4 mt-6">
                <button
                  type="button"
                  onClick={handlePrevious}
                  className="w-1/2 py-3 button-simple font-semibold rounded-lg"
                >
                  {t("project_inquiry.button_previous")}
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full sm:w-1/2 py-3 button-gradient text-white font-semibold rounded-lg disabled:opacity-50"
                >
                  {isSubmitting
                    ? t("project_inquiry.button_submitting")
                    : t("project_inquiry.button_submit")}
                </button>
              </div>
              {submitStatus === "error" && (
                <p className="text-red-500 text-center mt-4">
                  {t("project_inquiry.error_submit")}
                </p>
              )}
            </form>
          )}
        </div>
      </main>
    </>
  );
};

export default ProjectInquiry;
