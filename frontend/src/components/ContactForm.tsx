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

// --- ADD THE CSRF HELPER FUNCTION ---
// This function reads the CSRF token from the browser's cookies.
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
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    message: "",
    service: "",
  });
  const [services, setServices] = useState<Service[]>([]); // State for services
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

  // Effect to fetch services for the dropdown
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const res = await fetch("/api/services/");
        if (res.ok) {
          const data = await res.json();
          setServices(data);
        }
      } catch (error) {
        console.error("Failed to fetch services:", error);
      }
    };
    fetchServices();
  }, []);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    } else if (formData.name.trim().length < 2) {
      newErrors.name = "Name must be at least 2 characters";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.message.trim()) {
      newErrors.message = "Message is required";
    } else if (formData.message.trim().length < 10) {
      newErrors.message = "Message must be at least 10 characters";
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

  // --- UPDATE THE SUBMIT HANDLER ---
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setErrors({});

    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api";
      const csrfToken = getCookie("csrftoken"); // Get the token

      const res = await fetch(`${baseUrl}/contact/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "", // Add token to headers
        },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setSubmitted(true);
        setFormData({ name: "", email: "", message: "", service: "" });
      } else {
        const errorData = await res.json().catch(() => ({}));
        setErrors({
          general:
            errorData.detail || "Failed to send message. Please try again.",
        });
      }
    } catch (error) {
      console.error("Contact form error:", error);
      setErrors({
        general: "Network error. Please check your connection and try again.",
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
          Get In Touch
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
              Message Sent Successfully!
            </h3>
            <p className="home-text text-lg mb-6">
              Thank you for reaching out. I'll get back to you as soon as
              possible.
            </p>
            <motion.button
              onClick={handleSendAnother}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-3 button-simple text-secondary rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Send Another Message
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
                Your Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                placeholder="Enter your full name"
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
                Your Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                placeholder="Enter your email address"
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
                Service of Interest
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
                  Select a service...
                </option>
                {services.map((service) => (
                  <option key={service.id} value={service.name}>
                    {service.name}
                  </option>
                ))}
                <option value="Other">Other / General Inquiry</option>
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
                Your Message
              </label>
              <textarea
                name="message"
                value={formData.message}
                placeholder="Tell me about your project or question you might have"
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
                  Sending...
                </>
              ) : (
                <>
                  <FaPaperPlane />
                  Send Message
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
