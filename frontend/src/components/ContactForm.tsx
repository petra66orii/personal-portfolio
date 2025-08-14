import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  FaUser,
  FaEnvelope,
  FaComment,
  FaPaperPlane,
  FaCheck,
  FaExclamationTriangle,
} from "react-icons/fa";

interface FormErrors {
  name?: string;
  email?: string;
  message?: string;
  general?: string;
}

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isDark, setIsDark] = useState(false);

  // Theme detection effect
  useEffect(() => {
    const html = document.documentElement;
    const stored = localStorage.getItem("theme");
    if (stored === "dark") {
      setIsDark(true);
    }

    // Listen for theme changes
    const observer = new MutationObserver(() => {
      setIsDark(html.classList.contains("dark"));
    });

    observer.observe(html, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
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
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    // Clear error for this field when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors({ ...errors, [name]: undefined });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const baseUrl = "/api";
      const res = await fetch(`${baseUrl}/contact/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setSubmitted(true);
        setFormData({ name: "", email: "", message: "" });
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
        className="project-bg backdrop-blur-sm rounded-2xl shadow-xl max-w-2xl mx-auto px-8 py-12 border"
      >
        <motion.h2
          className="text-4xl font-bold mb-8 home-title text-center"
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
            <div className="w-20 h-20 bg-leaf/20 dark:bg-leaf-dark/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <FaCheck className="text-3xl text-leaf dark:text-leaf-light" />
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
              className={
                isDark
                  ? "px-6 py-3 bg-lime-500 hover:bg-lime-600 text-white rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl"
                  : "px-6 py-3 bg-amber-500 hover:bg-amber-600 text-white rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl"
              }
            >
              Send Another Message
            </motion.button>
          </motion.div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* General Error Message */}
            {errors.general && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center gap-3"
              >
                <FaExclamationTriangle className="text-red-500 flex-shrink-0" />
                <span className="text-red-700 dark:text-red-300">
                  {errors.general}
                </span>
              </motion.div>
            )}

            {/* Name Field */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="space-y-2"
            >
              <label className="block text-sm font-medium home-subtitle">
                <FaUser className="inline mr-2" />
                Your Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                placeholder="Enter your full name"
                onChange={handleChange}
                className={`w-full p-4 border rounded-lg bg-stone-light/50 dark:bg-earth-dark/50 home-text focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200 ${
                  isDark ? "placeholder-gray-300" : "placeholder-amber-950"
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

            {/* Email Field */}
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
                className={`w-full p-4 border rounded-lg bg-stone-light/50 dark:bg-earth-dark/50 home-text focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200 ${
                  isDark ? "placeholder-gray-300" : "placeholder-amber-950"
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

            {/* Message Field */}
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
                className={`w-full p-4 border rounded-lg bg-stone-light/50 dark:bg-earth-dark/50 home-text focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200 resize-vertical ${
                  isDark ? "placeholder-gray-300" : "placeholder-amber-950"
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

            {/* Submit Button */}
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
                  ? "bg-lime-500 hover:bg-lime-600 text-white hover:shadow-xl"
                  : "bg-amber-500 hover:bg-amber-600 text-white hover:shadow-xl"
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
