export const prerenderRoutes = [
  "/",
  "/about",
  "/services",
  "/blog",
  "/contact",
  "/custom-web-development-agency",
  "/custom-web-developer-ireland",
  "/web-development-agency-galway",
  "/web-development-agency-dublin",
  "/django-react-developer",
  "/international-web-development",
];

export function resolvePrerenderRoutes() {
  const extraBlogSlugs = (process.env.PRERENDER_BLOG_SLUGS || "")
    .split(",")
    .map((slug) => slug.trim())
    .filter(Boolean)
    .map((slug) => `/blog/${slug}`);

  return [...new Set([...prerenderRoutes, ...extraBlogSlugs])];
}
