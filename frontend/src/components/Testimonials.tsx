import { Star } from "lucide-react";
import ScrollAnimator from "./ScrollAnimator";
import { useTranslation } from "react-i18next";

// Define the type for a single testimonial
interface Testimonial {
  id: number;
  quote: string;
  name: string;
  company: string;
}

const Testimonials: React.FC = () => {
  const { t } = useTranslation();

  // --- Fetch the testimonials list from your JSON file ---
  const testimonials =
    (t("testimonials.list", { returnObjects: true }) as Testimonial[]) || [];

  return (
    <ScrollAnimator>
      <section className="mb-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl text-primary font-bold mb-4">
            {t("testimonials.title")}
          </h2>
          <p className="text-lg text-secondary max-w-2xl mx-auto">
            {t("testimonials.subtitle")}
          </p>
        </div>
        <div className="grid gap-8 grid-cols-1 md:grid-cols-2">
          {Array.isArray(testimonials) &&
            testimonials.map((testimonial) => (
              <div
                key={testimonial.id}
                className="glassmorphism p-8 rounded-2xl flex flex-col"
              >
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className="text-yellow-400 fill-yellow-400"
                      size={20}
                    />
                  ))}
                </div>
                <p className="text-secondary mb-6 flex-grow">
                  "{testimonial.quote}"
                </p>
                <div>
                  <p className="font-semibold text-primary">
                    {testimonial.name}
                  </p>
                  <p className="text-sm text-secondary">
                    {testimonial.company}
                  </p>
                </div>
              </div>
            ))}
        </div>
      </section>
    </ScrollAnimator>
  );
};

export default Testimonials;
