import { Helmet } from "react-helmet";

// Define a type for your schema data for better type-checking
interface SchemaData {
  "@context": string;
  "@type": string;
  name: string;
  url: string;
  logo: string;
  contactPoint?: {
    "@type": string;
    telephone: string;
    contactType: string;
  };
  sameAs?: string[];
}

const Schema: React.FC = () => {
  const siteUrl = "https://missbott.online";

  // Define the structured data for your business
  const schemaData: SchemaData = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService", // This type is perfect for a consultant/developer
    name: "Miss Bott",
    url: siteUrl,
    logo: `${siteUrl}/assets/logos/social-logo.png`,
    // Add links to your professional profiles
    sameAs: [
      "https://www.linkedin.com/in/petra-bot-a552601a4/",
      "https://github.com/petra66orii",
      "https://x.com/missbott_dev",
      "https://www.instagram.com/missbott_dev/",
    ],
  };

  return (
    <Helmet>
      <script type="application/ld+json">{JSON.stringify(schemaData)}</script>
    </Helmet>
  );
};

export default Schema;
