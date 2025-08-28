// src/components/CredentialsSection.tsx

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Award, ExternalLink, AlertTriangle } from "lucide-react";
import ScrollAnimator from "./ScrollAnimator";

// 1. UPDATED: Interface now matches your Django model's field names
interface Credential {
  id: number;
  name: string; // Was 'title'
  issuing_organization: string;
  issue_date: string; // Was 'date_issued'
  credential_url: string;
  image: string; // Assumes you have an 'image' field in your model/serializer
}

const Credentials: React.FC = () => {
  const [credentials, setCredentials] = useState<Credential[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCredentials = async () => {
      try {
        const response = await fetch("/api/credentials/");

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          throw new TypeError(
            "Server did not send JSON. Check the /api/credentials/ endpoint."
          );
        }

        const data: Credential[] = await response.json();
        setCredentials(data);
      } catch (err: unknown) {
        console.error("Error fetching credentials:", err);
        const message =
          err instanceof Error ? err.message : "Failed to load credentials.";
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    fetchCredentials();
  }, []);

  // --- THE FIX: This helper function is now more robust ---
  // It checks if the image URL is already a full path before adding a prefix.
  const getImageUrl = (imageUrl?: string) => {
    if (!imageUrl) return "/assets/default-project.png"; // Fallback if no image
    // If it's already a full URL (from backend) or an absolute path, use it directly
    if (imageUrl.startsWith("http") || imageUrl.startsWith("/")) {
      return imageUrl;
    }
    // Otherwise, assume it's just a filename and prepend the media path
    return `/media/${imageUrl}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-light dark:border-primary-dark"></div>
      </div>
    );
  }

  if (error) {
    return (
      <section className="max-w-6xl mx-auto px-6 py-12 text-center">
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center justify-center gap-3 text-red-500">
          <AlertTriangle className="flex-shrink-0" />
          <span>{error}</span>
        </div>
      </section>
    );
  }

  return (
    <ScrollAnimator>
      <section className="mb-16">
        <h2 className="text-3xl sm:text-4xl font-bold mb-8 text-primary text-center">
          Credentials & Certifications
        </h2>
        <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {credentials.map((cred, index) => (
            <motion.a
              key={cred.id}
              href={cred.credential_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block group"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="glassmorphism rounded-2xl overflow-hidden h-full flex flex-col transition-all duration-300 group-hover:shadow-2xl group-hover:-translate-y-2">
                <img
                  src={getImageUrl(cred.image)}
                  alt={`${cred.name} certificate`}
                  className="w-full h-48 object-cover"
                  onError={(e) => {
                    const img = e.currentTarget as HTMLImageElement;
                    img.onerror = null;
                    img.src = "/assets/default-project.png"; // Fallback image
                  }}
                />
                <div className="p-6 flex flex-col flex-grow">
                  <p className="text-sm text-secondary mb-2 flex items-center">
                    <Award size={14} className="mr-2" />
                    {cred.issuing_organization}
                  </p>
                  <h3 className="text-xl font-semibold text-primary mb-4 flex-grow">
                    {cred.name}
                  </h3>
                  <div className="mt-auto text-xs text-secondary flex justify-between items-center">
                    <span>
                      Issued: {new Date(cred.issue_date).toLocaleDateString()}
                    </span>
                    <span className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      View Certificate <ExternalLink size={12} />
                    </span>
                  </div>
                </div>
              </div>
            </motion.a>
          ))}
        </div>
      </section>
    </ScrollAnimator>
  );
};

export default Credentials;
