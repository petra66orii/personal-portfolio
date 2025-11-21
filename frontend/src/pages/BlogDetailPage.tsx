import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ArrowLeft, Calendar, Clock, User, Share2 } from "lucide-react";
import SEO from "../components/SEO";
import ScrollAnimator from "../components/ScrollAnimator";

interface BlogPost {
  id: number;
  title: string;
  content: string;
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

const BlogDetailPage = () => {
  const { slug } = useParams<{ slug: string }>();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();

  const [post, setPost] = useState<BlogPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchPost = async () => {
      setLoading(true);
      try {
        // Assuming your Django URL structure matches this.
        // If it fails, check if your backend expects /api/blog/?slug=...
        const response = await fetch(`/api/blog/${slug}/`, {
          headers: { "Accept-Language": i18n.language },
        });

        if (!response.ok) {
          throw new Error("Post not found");
        }

        const data = await response.json();
        setPost(data);
      } catch (err) {
        console.error("Error fetching blog post:", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    if (slug) {
      fetchPost();
    }
  }, [slug, i18n.language]);

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: post?.title,
          text: post?.excerpt,
          url: window.location.href,
        });
      } catch (err) {
        console.log("Error sharing:", err);
      }
    } else {
      // Fallback: Copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      alert(t("blog.share_copied", "Link copied to clipboard!"));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-8 bg-surface w-64 rounded mb-4"></div>
          <div className="h-4 bg-surface w-48 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen flex flex-col justify-center items-center text-center p-6">
        <h1 className="text-4xl font-bold text-primary mb-4">Post Not Found</h1>
        <p className="text-secondary mb-8">
          The article you are looking for doesn't exist or has been moved.
        </p>
        <button
          onClick={() => navigate("/blog")}
          className="px-6 py-3 button-gradient text-white rounded-lg font-semibold"
        >
          Back to Blog
        </button>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={`${post.title} | Miss Bott`}
        description={post.excerpt}
        keywords={t("blog.seo.keywords")} // You can also add dynamic tags from the post here
        type="article"
        image={getImageUrl(post.featured_image)}
      />

      <article className="min-h-screen pt-12 pb-20 px-4 sm:px-6">
        {/* --- Navigation Bar --- */}
        <div className="max-w-4xl mx-auto mb-8">
          <Link
            to="/blog"
            className="inline-flex items-center text-secondary hover:text-primary transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            {t("blog.back_to_blog")}
          </Link>
        </div>

        <div className="max-w-4xl mx-auto">
          <ScrollAnimator>
            {/* --- Header Section --- */}
            <header className="mb-12 text-center md:text-left">
              <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-primary mb-6 leading-tight">
                {post.title}
              </h1>

              <div className="flex flex-wrap justify-center md:justify-start gap-4 sm:gap-8 text-sm sm:text-base text-secondary">
                <div className="flex items-center">
                  <Calendar size={16} className="mr-2 text-primary" />
                  {formatDate(post.published_date, i18n.language)}
                </div>
                {post.read_time && (
                  <div className="flex items-center">
                    <Clock size={16} className="mr-2 text-primary" />
                    {post.read_time}
                    {t("blog.min_read")}
                  </div>
                )}
                <div className="flex items-center">
                  <User size={16} className="mr-2 text-primary" />
                  {post.author}
                </div>
              </div>
            </header>

            {/* --- Featured Image --- */}
            {post.featured_image && (
              <div className="mb-12 rounded-2xl overflow-hidden shadow-2xl border border-secondary/20">
                <img
                  src={getImageUrl(post.featured_image)}
                  alt={post.title}
                  className="w-full h-auto object-cover max-h-[600px]"
                />
              </div>
            )}

            {/* --- Main Content (Summernote HTML) --- */}
            {/* We use a specific class 'rich-text-content' to style the inner HTML */}
            <div className="glassmorphism rounded-3xl p-6 sm:p-10 md:p-12 border border-secondary/20 shadow-xl">
              <div
                className="rich-text-content"
                dangerouslySetInnerHTML={{ __html: post.content }}
              />
            </div>

            {/* --- Footer / Share --- */}
            <div className="mt-12 flex justify-between items-center border-t border-secondary/20 pt-8">
              <p className="text-secondary italic">
                {t("blog.thanks_reading")}
              </p>
              <button
                onClick={handleShare}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border border-secondary/30 text-primary hover:bg-surface transition-all"
              >
                <Share2 size={18} />
                <span>{t("blog.share")}</span>
              </button>
            </div>
          </ScrollAnimator>
        </div>
      </article>
    </>
  );
};

export default BlogDetailPage;
