import { useState, useEffect } from "react";
import SEO from "../components/SEO";

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
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api";
    fetch(`${baseUrl}/blog/`)
      .then((res) => res.json())
      .then((data) => {
        setPosts(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching blog posts:", err);
        // Fallback to mock data if API fails
        const mockPosts: BlogPost[] = [
          {
            id: 1,
            title: "Building Modern Web Applications with React and Django",
            excerpt:
              "Exploring the powerful combination of React frontend with Django backend for full-stack development. Learn about API integration, state management, and deployment strategies.",
            content: "",
            author: "Miss Bott",
            published_date: "2025-01-15",
            tags: ["React", "Django", "Full Stack", "API"],
            slug: "react-django-modern-web-apps",
            featured_image: "/project1.png",
            read_time: 8,
          },
          {
            id: 2,
            title: "TypeScript Best Practices for React Developers",
            excerpt:
              "Discover essential TypeScript patterns and practices that will make your React applications more robust, maintainable, and developer-friendly.",
            content: "",
            author: "Miss Bott",
            published_date: "2025-01-10",
            tags: ["TypeScript", "React", "Best Practices", "Development"],
            slug: "typescript-react-best-practices",
            featured_image: "/project2.png",
            read_time: 6,
          },
          {
            id: 3,
            title: "Deploying Full-Stack Applications to the Cloud",
            excerpt:
              "A comprehensive guide to deploying React and Django applications using modern cloud platforms. From development to production with CI/CD pipelines.",
            content: "",
            author: "Miss Bott",
            published_date: "2025-01-05",
            tags: ["Deployment", "Cloud", "DevOps", "CI/CD"],
            slug: "deploying-fullstack-apps-cloud",
            featured_image: "/project3.png",
            read_time: 12,
          },
        ];
        setPosts(mockPosts);
        setLoading(false);
      });
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
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
            <div className="h-8 bg-gray-300 rounded w-1/3 mb-4"></div>
            <div className="space-y-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="border rounded-lg p-6">
                  <div className="h-6 bg-gray-300 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-300 rounded w-1/2 mb-4"></div>
                  <div className="h-4 bg-gray-300 rounded w-full mb-2"></div>
                  <div className="h-4 bg-gray-300 rounded w-2/3"></div>
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
        title="Tech Blog - Web Development Insights"
        description="Read the latest insights, tutorials, and experiences from a full-stack developer. Covering React, Django, TypeScript, and modern web development practices with practical examples."
        keywords="tech blog, web development blog, React tutorials, Django guides, TypeScript tips, full stack development, programming blog"
        type="website"
      />
      <main className="min-h-screen p-6">
        <div className="max-w-6xl mx-auto">
          <header className="mb-12 text-center">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4 home-title">
              Tech Blog
            </h1>
            <p className="text-lg home-text max-w-2xl mx-auto">
              Sharing insights, tutorials, and experiences from my journey as a
              full-stack developer. Covering React, Django, TypeScript, and
              modern web development practices.
            </p>
          </header>

          <section className="space-y-8">
            {posts.map((post) => (
              <article
                key={post.id}
                className="bg-stone-light/50 dark:bg-stone-dark/50 backdrop-blur-sm rounded-lg shadow-lg border border-golden-light/20 dark:border-leaf-dark/20 p-6 hover:shadow-xl transition-shadow duration-300"
              >
                <div className="flex flex-col lg:flex-row gap-6">
                  {post.featured_image && (
                    <div className="lg:w-1/3">
                      <img
                        src={post.featured_image}
                        alt={post.title}
                        className="w-full h-48 lg:h-32 object-cover rounded-lg"
                        loading="lazy"
                      />
                    </div>
                  )}

                  <div className="lg:w-2/3 flex-1">
                    <header className="mb-4">
                      <h2 className="text-2xl font-bold mb-2 home-title hover:opacity-80 transition-opacity">
                        <a
                          href={`/blog/${post.slug}`}
                          className="hover:underline"
                        >
                          {post.title}
                        </a>
                      </h2>

                      <div className="flex flex-wrap items-center gap-4 text-sm home-text">
                        <span>By {post.author}</span>
                        <span>•</span>
                        <time dateTime={post.published_date}>
                          {formatDate(post.published_date)}
                        </time>
                        {post.read_time && (
                          <>
                            <span>•</span>
                            <span>{post.read_time} min read</span>
                          </>
                        )}
                      </div>
                    </header>

                    <p className="home-text mb-4 leading-relaxed">
                      {post.excerpt}
                    </p>

                    <footer className="flex flex-wrap justify-between items-center gap-4">
                      <div className="flex flex-wrap gap-2">
                        {post.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-3 py-1 bg-golden-light/20 dark:bg-leaf-dark/20 home-text text-xs rounded-full"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>

                      <a
                        href={`/blog/${post.slug}`}
                        className="text-golden-light dark:text-leaf-light hover:underline font-medium"
                      >
                        Read more →
                      </a>
                    </footer>
                  </div>
                </div>
              </article>
            ))}
          </section>

          {posts.length === 0 && !loading && (
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4 home-title">
                Coming Soon!
              </h2>
              <p className="home-text">
                I'm working on some exciting blog posts about web development.
                Check back soon!
              </p>
            </div>
          )}
        </div>
      </main>
    </>
  );
};

export default Blog;
