import { Helmet } from "react-helmet";

interface SEOProps {
  title: string;
  description: string;
  keywords?: string;
  image?: string;
  url?: string;
  type?: string;
  author?: string;
}

const SEO = ({
  title,
  description,
  keywords = "portfolio, web developer, full stack developer, React, TypeScript, Python, Django",
  image = "/website-background.png",
  url = "https://missbott.online",
  type = "website",
  author = "Miss Bott",
}: SEOProps) => {
  const fullTitle = title.includes("Miss Bott")
    ? title
    : `${title} | Miss Bott - Fullstack Developer Ireland`;

  const fullUrl = `https://missbott.online${window.location.pathname}`;

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content={author} />
      <meta name="robots" content="index, follow" />

      {/* Open Graph Meta Tags */}
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:url" content={fullUrl} />
      <meta property="og:type" content={type} />
      <meta property="og:site_name" content="Miss Bott Portfolio" />

      {/* Twitter Card Meta Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />
      <meta name="twitter:creator" content="@missbott_dev" />

      <link rel="canonical" href={fullUrl} />

      {/* --- UPDATED: Structured Data with Location and Education --- */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "Person",
          name: "Miss Bott",
          jobTitle: "Full Stack Developer",
          url: url,
          image: image,
          sameAs: [
            "https://github.com/petra66orii",
            "https://www.linkedin.com/in/petra-bot-a552601a4/",
            "https://www.instagram.com/missbott_dev/",
          ],
          // NEW: Adds location for local SEO
          address: {
            "@type": "PostalAddress",
            addressLocality: "Galway",
            addressCountry: "IE",
          },
          // NEW: Formalizes your education
          alumniOf: {
            "@type": "CollegeOrUniversity",
            name: "Code Institute",
          },
          knowsAbout: [
            "React.js",
            "TypeScript",
            "Python",
            "Django REST framework",
            "PostgreSQL",
            "Full Stack Web Development",
            "API Development",
            "Tailwind CSS",
          ],
          description:
            "Full-stack developer based in Galway, Ireland, specializing in building modern web applications with React and Django.",
        })}
      </script>
    </Helmet>
  );
};

export default SEO;
