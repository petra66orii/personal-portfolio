import { useEffect, useRef } from "react";

// TypeScript interface for a star object for type safety
interface Star {
  x: number;
  y: number;
  radius: number;
  alpha: number;
  alphaChange: number;
}

// Props interface for the component
interface AnimatedBackgroundProps {
  isDark: boolean;
}

const AnimatedBackground = ({ isDark }: AnimatedBackgroundProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);
    let stars: Star[] = [];
    const starCount = 200;
    let time = 0;

    const resizeHandler = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      stars = createStars(starCount);
    };

    window.addEventListener("resize", resizeHandler);

    function createStar(): Star {
      return {
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 1.5 + 0.5,
        alpha: Math.random(),
        alphaChange: Math.random() * 0.02 - 0.01,
      };
    }

    function createStars(count: number): Star[] {
      const newStars: Star[] = [];
      for (let i = 0; i < count; i++) {
        newStars.push(createStar());
      }
      return newStars;
    }

    stars = createStars(starCount);

    function draw() {
      if (!ctx) return;
      ctx.clearRect(0, 0, width, height);

      // --- Theme-Aware Nebula Gradients ---
      const gradient1 = ctx.createRadialGradient(
        width * 0.25 + Math.sin(time * 0.0001) * 100,
        height * 0.25 + Math.cos(time * 0.0001) * 100,
        0,
        width * 0.5,
        height * 0.5,
        width
      );
      // Use dark or light theme colors based on the isDark prop
      gradient1.addColorStop(
        0,
        isDark ? "rgba(155, 93, 229, 0.1)" : "rgba(170, 240, 209, 0.2)"
      );
      gradient1.addColorStop(
        1,
        isDark ? "rgba(155, 93, 229, 0)" : "rgba(170, 240, 209, 0)"
      );

      const gradient2 = ctx.createRadialGradient(
        width * 0.75 + Math.cos(time * 0.00015) * 100,
        height * 0.75 + Math.sin(time * 0.00015) * 100,
        0,
        width * 0.5,
        height * 0.5,
        width
      );
      gradient2.addColorStop(
        0,
        isDark ? "rgba(241, 91, 181, 0.1)" : "rgba(108, 99, 255, 0.2)"
      );
      gradient2.addColorStop(
        1,
        isDark ? "rgba(241, 91, 181, 0)" : "rgba(108, 99, 255, 0)"
      );

      ctx.fillStyle = gradient1;
      ctx.fillRect(0, 0, width, height);
      ctx.fillStyle = gradient2;
      ctx.fillRect(0, 0, width, height);

      // --- Theme-Aware Stars ---
      stars.forEach((star) => {
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);

        // White for dark mode, and a subtle dark gray for light mode.
        ctx.fillStyle = isDark
          ? `rgba(255, 255, 255, ${star.alpha})`
          : `rgba(10, 10, 15, ${star.alpha * 0.7})`;

        ctx.fill();

        star.alpha += star.alphaChange;
        if (star.alpha <= 0 || star.alpha >= 1) {
          star.alphaChange *= -1;
        }
      });

      time++;
      requestAnimationFrame(draw);
    }

    const animationFrameId = requestAnimationFrame(draw);

    // Cleanup function to remove the event listener and stop the animation
    return () => {
      window.removeEventListener("resize", resizeHandler);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isDark]); // Re-run the effect when isDark changes

  return <canvas ref={canvasRef} id="background-canvas" />;
};

export default AnimatedBackground;
