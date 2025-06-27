import { useState } from "react";
import { motion } from "framer-motion";

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const baseUrl =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
    const res = await fetch(`${baseUrl}/api/contact/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (res.ok) {
      setSubmitted(true);
      setFormData({ name: "", email: "", message: "" });
    }
  };

  return (
    <section className="min-h-screen p-6">
      <motion.section
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        viewport={{ once: true }}
        className="bg-stone-light/90 dark:bg-earth-dark/90 backdrop-blur-sm rounded-lg shadow-xl max-w-2xl mx-auto px-6 py-12 border border-golden-light/20 dark:border-earth/20"
      >
        <h2 className="text-3xl font-bold mb-8 text-golden-dark dark:text-leaf-light">
          Contact Me
        </h2>
        {submitted ? (
          <p className="text-golden-dark dark:text-leaf-light text-lg">
            Thanks! Your message has been sent.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <input
              type="text"
              name="name"
              value={formData.name}
              placeholder="Your Name"
              onChange={handleChange}
              className="w-full p-3 border border-leaf-light/30 dark:border-earth/30 rounded-lg bg-stone-light/50 dark:bg-earth-dark/50 text-earth-dark dark:text-stone-light focus:outline-none focus:ring-2 focus:ring-leaf focus:border-transparent transition-all duration-200"
              required
            />
            <input
              type="email"
              name="email"
              value={formData.email}
              placeholder="Your Email"
              onChange={handleChange}
              className="w-full p-3 border border-leaf-light/30 dark:border-earth/30 rounded-lg bg-stone-light/50 dark:bg-earth-dark/50 text-earth-dark dark:text-stone-light focus:outline-none focus:ring-2 focus:ring-leaf focus:border-transparent transition-all duration-200"
              required
            />
            <textarea
              name="message"
              value={formData.message}
              placeholder="Your Message"
              onChange={handleChange}
              className="w-full p-3 border border-leaf-light/30 dark:border-earth/30 rounded-lg bg-stone-light/50 dark:bg-earth-dark/50 text-earth-dark dark:text-stone-light focus:outline-none focus:ring-2 focus:ring-leaf focus:border-transparent transition-all duration-200"
              rows={6}
              required
            />
            <button
              type="submit"
              className="w-full px-6 py-3 bg-leaf hover:bg-leaf-dark dark:bg-leaf-dark dark:hover:bg-leaf text-white rounded-lg font-semibold transition-colors duration-200"
            >
              Send Message
            </button>
          </form>
        )}
      </motion.section>
    </section>
  );
};

export default ContactForm;
