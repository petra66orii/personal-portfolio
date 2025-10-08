import { Star } from "lucide-react";
import ScrollAnimator from "./ScrollAnimator";

// We'll use static data for now. You can fetch this from your API later.
const testimonials = [
  {
    id: 1,
    quote:
      "Petra translated our artistic vision into a website that was more beautiful and functional than we ever imagined. The entire process was seamless.",
    name: "OpenEire Studios",
    company: "Drone Videography Business",
  },
  {
    id: 2,
    quote:
      "Working with Miss Bott was a game-changer. Our new portfolio site has already led to two major commissions. Truly a professional and intuitive partner.",
    name: "CMD Artistry",
    company: "Mural Painter",
  },
  // Add a third one if you have it
];

const Testimonials: React.FC = () => {
  return (
    <ScrollAnimator>
      <section className="mb-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl text-primary font-bold mb-4">
            What My Clients Say
          </h2>
          <p className="text-lg text-secondary max-w-2xl mx-auto">
            I'm proud to partner with creatives to build a digital presence they
            love.
          </p>
        </div>
        <div className="grid gap-8 grid-cols-1 md:grid-cols-2">
          {testimonials.map((testimonial) => (
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
                <p className="font-semibold text-primary">{testimonial.name}</p>
                <p className="text-sm text-secondary">{testimonial.company}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </ScrollAnimator>
  );
};

export default Testimonials;
