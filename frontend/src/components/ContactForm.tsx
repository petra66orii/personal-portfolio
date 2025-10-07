import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  FaUser,
  FaEnvelope,
  FaComment,
  FaPaperPlane,
  FaCheck,
  FaExclamationTriangle,
  FaConciergeBell,
} from "react-icons/fa";
import { useTranslation } from "react-i18next"; // 1. Import hook

// --- CSRF HELPER FUNCTION ---
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

interface FormData {
  name: string;
  email: string;
  service: string;
  message: string;
}

interface FormErrors {
  name?: string;
  email?: string;
  message?: string;
  general?: string;
}

interface Service {
  id: number;
  name: string;
}

const ContactForm = () => {
  const { t, i18n } = useTranslation(); // 2. Get translation function and i18n instance
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    message: "",
    service: "",
  });
  const [services, setServices] = useState<Service[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isDark, setIsDark] = useState(false);

  // Theme detection effect
  useEffect(() => {
    const html = document.documentElement;
    const observer = new MutationObserver(() => {
      setIsDark(html.classList.contains("dark"));
    });
    setIsDark(html.classList.contains("dark"));
    observer.observe(html, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);

  // 3. Update fetch to be language-aware
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const res = await fetch("/api/services/", {
          headers: {
            "Accept-Language": i18n.language,
          },
        });
        if (res.ok) {
          const data = await res.json();
          setServices(data);
        }
      } catch (error) {
        console.error("Failed to fetch services:", error);
      }
    };
    fetchServices();
  }, [i18n.language]); // Re-fetch when language changes

  // 4. Translate validation messages
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = t("contact.validation.name_required");
    } else if (formData.name.trim().length < 2) {
      newErrors.name = t("contact.validation.name_min");
    }

    if (!formData.email.trim()) {
      newErrors.email = t("contact.validation.email_required");
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = t("contact.validation.email_invalid");
    }

    if (!formData.message.trim()) {
      newErrors.message = t("contact.validation.message_required");
    } else if (formData.message.trim().length < 10) {
      newErrors.message = t("contact.validation.message_min");
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    if (errors[name as keyof FormErrors]) {
      setErrors({ ...errors, [name]: undefined });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setErrors({});

    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api";
      const csrfToken = getCookie("csrftoken");

      const res = await fetch(`${baseUrl}/contact/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
        },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setSubmitted(true);
        setFormData({ name: "", email: "", message: "", service: "" });
      } else {
        const errorData = await res.json().catch(() => ({}));
        setErrors({
          general: errorData.detail || t("contact.error.general_submit"),
        });
      }
    } catch (error) {
      console.error("Contact form error:", error);
      setErrors({
        general: t("contact.error.network"),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSendAnother = () => {
    setSubmitted(false);
    setErrors({});
  };

  return (
    <section className="min-h-screen p-6">
      <motion.section
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        viewport={{ once: true }}
        className="glassmorphism backdrop-blur-sm rounded-2xl shadow-xl max-w-2xl mx-auto px-8 py-12 border"
      >
        <motion.h2
          className="text-4xl font-bold mb-8 text-primary text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          {t("contact.title")}
        </motion.h2>

        {submitted ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="text-center py-8"
          >
            <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <FaCheck className="text-3xl text-green-500" />
            </div>
            <h3 className="text-2xl font-semibold home-subtitle mb-4">
              {t("contact.success.title")}
            </h3>
            <p className="home-text text-lg mb-6">
              {t("contact.success.message")}
            </p>
            <motion.button
              onClick={handleSendAnother}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-3 button-simple text-secondary rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              {t("contact.success.button_send_another")}
            </motion.button>
          </motion.div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {errors.general && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center gap-3 text-red-500"
              >
                <FaExclamationTriangle className="flex-shrink-0" />
                <span>{errors.general}</span>
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="space-y-2"
            >
              <label className="block text-sm font-medium">
                <FaUser className="inline mr-2" />
                {t("contact.form.label_name")}
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                placeholder={t("contact.form.placeholder_name")}
                onChange={handleChange}
                className={`w-full p-4 border rounded-lg glassmorphism focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200 ${
                  isDark ? "placeholder-gray-300" : "placeholder-emerald-950"
                } ${
                  errors.name
                    ? "border-red-400 dark:border-red-600 focus:ring-red-500"
                    : "border-leaf-light/30 dark:border-earth/30 focus:ring-leaf dark:focus:ring-leaf-dark"
                }`}
                required
              />
              {errors.name && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-red-500 text-sm flex items-center gap-1"
                >
                  <FaExclamationTriangle className="text-xs" />
                  {errors.name}
                </motion.p>
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="space-y-2"
            >
              <label className="block text-sm font-medium home-subtitle">
                <FaEnvelope className="inline mr-2" />
                {t("contact.form.label_email")}
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                placeholder={t("contact.form.placeholder_email")}
                onChange={handleChange}
                className={`w-full p-4 border rounded-lg glassmorphism focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200 ${
                  isDark ? "placeholder-gray-300" : "placeholder-emerald-950"
                } ${
                  errors.email
                    ? "border-red-400 dark:border-red-600 focus:ring-red-500"
                    : "border-leaf-light/30 dark:border-earth/30 focus:ring-leaf dark:focus:ring-leaf-dark"
                }`}
                required
              />
              {errors.email && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-red-500 text-sm flex items-center gap-1"
                >
                  <FaExclamationTriangle className="text-xs" />
                  {errors.email}
                </motion.p>
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="space-y-2"
            >
              <label className="block text-sm font-medium home-subtitle">
                <FaConciergeBell className="inline mr-2" />
                {t("contact.form.label_service")}
              </label>
              <select
                name="service"
                value={formData.service}
                onChange={handleChange}
                className={`w-full p-4 border rounded-lg glassmorphism focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200 ${
                  isDark ? "placeholder-gray-300" : "placeholder-emerald-950"
                } border-leaf-light/30 dark:border-earth/30 focus:ring-leaf dark:focus:ring-leaf-dark`}
              >
                <option value="" disabled>
                  {t("contact.form.placeholder_service")}
                </option>
                {services.map((service) => (
                  <option key={service.id} value={service.name}>
                    {service.name}
                  </option>
                ))}
                <option value="Other">{t("contact.form.service_other")}</option>
              </select>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              className="space-y-2"
            >
              <label className="block text-sm font-medium home-subtitle">
                <FaComment className="inline mr-2" />
                {t("contact.form.label_message")}
              </label>
              <textarea
                name="message"
                value={formData.message}
                placeholder={t("contact.form.placeholder_message")}
                onChange={handleChange}
                className={`w-full p-4 border rounded-lg glassmorphism focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200 resize-vertical ${
                  isDark ? "placeholder-gray-300" : "placeholder-emerald-950"
                } ${
                  errors.message
                    ? "border-red-400 dark:border-red-600 focus:ring-red-500"
                    : "border-leaf-light/30 dark:border-earth/30 focus:ring-leaf dark:focus:ring-leaf-dark"
                }`}
                rows={6}
                required
              />
              {errors.message && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-red-500 text-sm flex items-center gap-1"
                >
                  <FaExclamationTriangle className="text-xs" />
                  {errors.message}
                </motion.p>
              )}
            </motion.div>

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: loading ? 1 : 1.05 }}
              whileTap={{ scale: loading ? 1 : 0.95 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
              className={`w-full px-6 py-4 rounded-lg font-semibold transition-all duration-200 shadow-lg flex items-center justify-center gap-3 ${
                loading
                  ? "bg-stone dark:bg-stone-dark text-stone-light cursor-not-allowed"
                  : isDark
                  ? "button-simple text-primary hover:shadow-xl"
                  : "button-simple text-primary hover:shadow-xl"
              }`}
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  {t("contact.form.button_sending")}
                </>
              ) : (
                <>
                  <FaPaperPlane />
                  {t("contact.form.button_send")}
                </>
              )}
            </motion.button>
          </form>
        )}
      </motion.section>
    </section>
  );
};

export default ContactForm;
