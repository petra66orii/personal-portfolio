import { useEffect, useState } from "react";
import SEO from "../components/SEO";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { Clock, Feather, Mail } from "lucide-react";
import ScrollAnimator from "../components/ScrollAnimator";

interface BlogPost {
  id: number;
  title: string;
  excerpt: string;
  author: string;
  published_date: string;
  slug: string;
  featured_image?: string;
  read_time?: number;
}

const getImageUrl = (imageUrl?: string) => {
  if (!imageUrl) return "/assets/default-project.png";
  if (imageUrl.startsWith("http") || imageUrl.startsWith("/")) return imageUrl;
  return `/media/${imageUrl}`;
};

const formatDate = (dateString: string, locale: string) => {
  return new Date(dateString).toLocaleDateString(locale, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const Blog = () => {
  const { t, i18n } = useTranslation();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("Subscribing...");

    try {
      const response = await fetch("/api/newsletter-signup/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // If you use CSRF tokens, you'll need to include the header here
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Use the error message from the backend if available
        throw new Error(data.error || "Something went wrong.");
      }

      setMessage("Thank you for subscribing!");
      setEmail(""); // Clear the input on success
    } catch (err) {
      if (err instanceof Error) {
        setMessage(err.message);
      } else {
        setMessage("An unexpected error occurred.");
      }
    }
  };

  useEffect(() => {
    const fetchPosts = async () => {
      setLoading(true);
      try {
        const response = await fetch("/api/blog/", {
          headers: { "Accept-Language": i18n.language },
        });
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setPosts(data);
      } catch (err) {
        console.error("Error fetching blog posts:", err);
        setPosts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts(); // You were missing this call!
  }, [i18n.language]);

  const latestPost = posts[0];
  const otherPosts = posts.slice(1);

  if (loading) {
    return (
      <main className="min-h-screen p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-surface rounded w-1/3 mb-12 mx-auto"></div>
            <div className="space-y-8">
              {[1, 2, 3].map((i) => (
                <div key={i} className="glassmorphism rounded-lg p-6">
                  <div className="h-6 bg-surface rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-surface rounded w-1/2 mb-4"></div>
                  <div className="h-4 bg-surface rounded w-full mb-2"></div>
                  <div className="h-4 bg-surface rounded w-2/3"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <>
      <SEO
        title={t("blog.seo.title")}
        description={t("blog.seo.description")}
        keywords={t("blog.seo.keywords")}
        type="website"
      />
      <main className="min-h-screen p-6">
        <div className="max-w-6xl mx-auto">
          <header className="mb-12 text-center">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4 text-primary">
              {t("blog.title")}
            </h1>
            <p className="text-lg text-secondary max-w-2xl mx-auto">
              {t("blog.description")}
            </p>
          </header>

          {posts.length > 0 ? (
            <div className="space-y-16">
              {/* Featured Post Section */}
              {latestPost && <FeaturedPostCard post={latestPost} />}

              {/* Grid for Other Posts */}
              {otherPosts.length > 0 && (
                <div className="grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                  {otherPosts.map((post) => (
                    <PostCard key={post.id} post={post} />
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-20 glassmorphism rounded-2xl border border-secondary/20">
              <Feather className="mx-auto h-12 w-12 text-primary mb-4" />
              <h2 className="text-3xl font-bold mb-4 text-primary">
                Your Creative Business, Amplified.
              </h2>
              <p className="text-secondary max-w-xl mx-auto mb-8">
                The Insights Hub is coming soon. I'll be sharing practical tips
                on web design, online marketing, and technology to help you
                build your brand and thrive online.
              </p>
              <form
                onSubmit={handleNewsletterSubmit}
                className="flex justify-center"
              >
                <div className="relative w-full max-w-sm">
                  <Mail
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary"
                    size={20}
                  />
                  <input
                    type="email"
                    placeholder="Enter your email to be notified"
                    className="w-full pl-10 pr-32 py-3 rounded-xl border-2 border-primary/20 bg-surface focus:ring-2 focus:ring-primary focus:outline-none"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                  <button
                    type="submit"
                    className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 button-gradient text-white font-semibold rounded-lg"
                  >
                    Notify Me
                  </button>
                </div>
              </form>
              {/* Display success or error messages to the user */}
              {message && <p className="mt-4 text-secondary">{message}</p>}
            </div>
          )}
        </div>
      </main>
    </>
  );
};

// --- Child Components for Post Cards ---

const FeaturedPostCard: React.FC<{ post: BlogPost }> = ({ post }) => {
  const { t, i18n } = useTranslation();
  return (
    <ScrollAnimator>
      <Link to={`/blog/${post.slug}`} className="block group">
        <article className="glassmorphism rounded-2xl shadow-lg border border-secondary/20 p-6 flex flex-col md:flex-row gap-8 hover:shadow-xl transition-shadow duration-300">
          <div className="md:w-1/2">
            <img
              src={getImageUrl(post.featured_image)}
              alt={post.title}
              className="w-full h-64 md:h-full object-cover rounded-lg"
            />
          </div>
          <div className="md:w-1/2 flex flex-col">
            <p className="text-sm font-semibold text-primary mb-2">
              Latest Insight
            </p>
            <h2 className="text-3xl font-bold mb-4 text-primary group-hover:opacity-80 transition-opacity">
              {post.title}
            </h2>
            <p className="text-secondary mb-6 leading-relaxed flex-grow">
              {post.excerpt}
            </p>
            <div className="text-sm text-secondary flex items-center gap-4 mt-auto">
              <span>{formatDate(post.published_date, i18n.language)}</span>
              {post.read_time && (
                <span>
                  <Clock size={14} className="inline mr-1" />{" "}
                  {t("blog.read_time", { time: post.read_time })}
                </span>
              )}
            </div>
          </div>
        </article>
      </Link>
    </ScrollAnimator>
  );
};

const PostCard: React.FC<{ post: BlogPost }> = ({ post }) => {
  const { t, i18n } = useTranslation();
  return (
    <ScrollAnimator>
      <Link to={`/blog/${post.slug}`} className="block group h-full">
        <article className="glassmorphism rounded-2xl shadow-lg border border-secondary/20 p-6 h-full flex flex-col hover:shadow-xl transition-shadow duration-300">
          <img
            src={getImageUrl(post.featured_image)}
            alt={post.title}
            className="w-full h-40 object-cover rounded-lg mb-6"
          />
          <h2 className="text-xl font-bold mb-3 text-primary group-hover:opacity-80 transition-opacity">
            {post.title}
          </h2>
          <p className="text-secondary text-sm leading-relaxed flex-grow mb-4">
            {post.excerpt}
          </p>
          <div className="text-xs text-secondary flex items-center gap-3 mt-auto">
            <span>{formatDate(post.published_date, i18n.language)}</span>
            {post.read_time && (
              <span>
                <Clock size={12} className="inline mr-1" />{" "}
                {t("blog.read_time", { time: post.read_time })}
              </span>
            )}
          </div>
        </article>
      </Link>
    </ScrollAnimator>
  );
};

export default Blog;
