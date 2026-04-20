import { Helmet } from "react-helmet";
import { useLocation } from "react-router-dom";

interface SEOProps {
  title: string;
  description: string;
  image?: string;
  type?: string;
  canonicalPath?: string;
  robots?: string;
  ogTitle?: string;
  ogDescription?: string;
}

const SEO: React.FC<SEOProps> = ({
  title,
  description,
  image,
  type = "website",
  canonicalPath,
  robots = "index, follow",
  ogTitle,
  ogDescription,
}) => {
  const location = useLocation();
  const siteUrl = "https://missbott.online";
  const normalizedPath = (canonicalPath || location.pathname).replace(/\/+$/, "") || "/";
  const canonicalUrl = `${siteUrl}${normalizedPath}`;

  const imageUrl = image?.startsWith("http")
    ? image
    : `${siteUrl}${image || "/static/android-chrome-512x512.png"}`;

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="author" content="Miss Bott" />
      <meta name="robots" content={robots} />
      <link rel="canonical" href={canonicalUrl} />

      {/* Open Graph Meta Tags (for Facebook, LinkedIn, etc.) */}
      <meta property="og:title" content={ogTitle || title} />
      <meta property="og:description" content={ogDescription || description} />
      <meta property="og:image" content={imageUrl} />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:type" content={type} />
      <meta property="og:site_name" content="Miss Bott" />
      <meta property="og:locale" content="en_IE" />

      {/* Twitter Card Meta Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={ogTitle || title} />
      <meta name="twitter:description" content={ogDescription || description} />
      <meta name="twitter:image" content={imageUrl} />
      <meta name="twitter:creator" content="@missbott_dev" />
    </Helmet>
  );
};

export default SEO;
