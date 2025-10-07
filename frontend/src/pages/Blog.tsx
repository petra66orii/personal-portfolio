import { useEffect, useState } from "react";
import SEO from "../components/SEO";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

interface BlogPost {
  id: number;
  title: string;
  excerpt: string;
  content: string;
  author: string;
  published_date: string;
  tags: string[];
  slug: string;
  featured_image?: string;
  read_time?: number;
}

const Blog = () => {
  const { t, i18n } = useTranslation();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPosts = async () => {
      setLoading(true);
      try {
        const response = await fetch("/api/blog/", {
          headers: {
            "Accept-Language": i18n.language,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          throw new TypeError("Server did not send JSON for blog posts.");
        }

        const data = await response.json();
        setPosts(data);
      } catch (err) {
        console.error("Error fetching blog posts:", err);
        setPosts([]); // Clear posts on error
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [i18n.language]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(i18n.language, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

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

          <section className="space-y-8">
            {posts.map((post) => (
              <article
                key={post.id}
                className="glassmorphism rounded-lg shadow-lg border border-secondary/20 p-6 hover:shadow-xl transition-shadow duration-300"
              >
                <div className="flex flex-col lg:flex-row gap-6">
                  {post.featured_image && (
                    <div className="lg:w-1/3">
                      <img
                        src={post.featured_image}
                        alt={post.title}
                        className="w-full h-48 lg:h-full object-cover rounded-lg"
                        loading="lazy"
                      />
                    </div>
                  )}

                  <div className="lg:w-2/3 flex-1 flex flex-col">
                    <header className="mb-4">
                      <h2 className="text-2xl font-bold mb-2 text-primary hover:opacity-80 transition-opacity">
                        <Link
                          to={`/blog/${post.slug}`}
                          className="hover:underline"
                        >
                          {post.title}
                        </Link>
                      </h2>

                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-secondary">
                        <span>
                          {t("blog.author_prefix")} {post.author}
                        </span>
                        <span>•</span>
                        <time dateTime={post.published_date}>
                          {formatDate(post.published_date)}
                        </time>
                        {post.read_time && (
                          <>
                            <span>•</span>
                            <span>
                              {t("blog.read_time", { time: post.read_time })}
                            </span>
                          </>
                        )}
                      </div>
                    </header>

                    <p className="text-secondary mb-4 leading-relaxed flex-grow">
                      {post.excerpt}
                    </p>

                    <footer className="flex flex-wrap justify-between items-center gap-4 mt-auto">
                      <div className="flex flex-wrap gap-2">
                        {post.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-3 py-1 bg-surface text-secondary text-xs rounded-full"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>

                      <Link
                        to={`/blog/${post.slug}`}
                        className="text-primary hover:underline font-medium"
                      >
                        {t("blog.read_more")} →
                      </Link>
                    </footer>
                  </div>
                </div>
              </article>
            ))}
          </section>

          {posts.length === 0 && !loading && (
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4 text-primary">
                {t("blog.coming_soon.title")}
              </h2>
              <p className="text-secondary">{t("blog.coming_soon.message")}</p>
            </div>
          )}
        </div>
      </main>
    </>
  );
};

export default Blog;
