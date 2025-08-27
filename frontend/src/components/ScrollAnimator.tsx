import { motion, useInView, useAnimation } from "framer-motion";
import { useEffect, useRef } from "react";

interface ScrollAnimatorProps {
  children: React.ReactNode;
  delay?: number; // Optional delay for staggered animations
}

const ScrollAnimator = ({ children, delay = 0 }: ScrollAnimatorProps) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true }); // `once: true` makes it animate only once
  const mainControls = useAnimation();

  useEffect(() => {
    if (isInView) {
      mainControls.start("visible");
    }
  }, [isInView, mainControls]);

  return (
    <div ref={ref} style={{ position: "relative", overflow: "hidden" }}>
      <motion.div
        variants={{
          hidden: { opacity: 0, y: 75 }, // Start hidden, 75px down
          visible: { opacity: 1, y: 0 }, // Animate to visible, original position
        }}
        initial="hidden"
        animate={mainControls}
        transition={{ duration: 0.5, delay: delay }}
      >
        {children}
      </motion.div>
    </div>
  );
};

export default ScrollAnimator;
