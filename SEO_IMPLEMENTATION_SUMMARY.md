# React-First SEO Architecture Summary

## 1. Final Architecture (React-first)
- Public marketing pages are React-owned and served through the SPA routing flow.
- Django remains backend/API/admin and infrastructure host for:
  - `/robots.txt`
  - `/sitemap.xml` and sitemap section endpoints
  - API data for services/blog/projects
- Django catch-all now serves:
  - prerendered React HTML when a route snapshot exists
  - otherwise the React SPA entry (`index.html`)
- Canonical host and redirect hygiene remain in middleware (`CanonicalUrlMiddleware`) and continue to apply safely with React routes.

## 2. What Was Rolled Back From Django Templates
- Removed Django public page ownership for marketing routes (`/`, `/about`, `/services`, `/services/<slug>`, `/blog`, `/blog/<slug>`, `/contact`, SEO landing routes).
- Removed SEO-only Django rendering layer and templates:
  - `portfolio/site_views.py`
  - `templates/seo/*`
  - `portfolio/static/portfolio/seo.css`
- Updated URL routing in `backend/urls.py` to stop dispatching public pages to Django template views.
- Kept `web-developer-ireland` as a simple permanent redirect alias to `/custom-web-developer-ireland`.

## 3. Prerendering Approach Chosen (and why)
- Chosen approach: Vite SSR-based prerender snapshots generated at build time, then served by Django when available.
- Why this approach:
  - Low disruption to current stack (no Next.js migration required now).
  - Keeps React Router and existing frontend UX/components.
  - Avoids duplicate page implementations in Django.
  - Produces route-specific HTML with React Helmet metadata at build time.

### Implemented prerender flow
1. Build client bundle (`frontend/dist`).
2. Build SSR render entry (`frontend/src/prerender/entry-server.tsx`) to temporary `dist-ssr`.
3. Generate route snapshots via `frontend/scripts/prerender-routes.mjs` into:
   - `frontend/dist/prerender/index.html`
   - `frontend/dist/prerender/<route>/index.html`
4. Django view `backend/views.py::react_frontend_entry` serves prerender snapshot if it exists, otherwise serves `index.html`.

### Priority routes prerendered
- `/`
- `/about`
- `/services`
- `/blog`
- `/contact`
- `/custom-web-development-agency`
- `/custom-web-developer-ireland`
- `/web-development-agency-galway`
- `/web-development-agency-dublin`
- `/django-react-developer`
- `/international-web-development`

### Optional selected blog prerender
- Supported via environment variable:
  - `PRERENDER_BLOG_SLUGS=slug-one,slug-two`
- These are appended to prerender routes as `/blog/<slug>`.

## 4. Limitations Still Remaining
- Dynamic detail pages (`/services/<slug>`, `/blog/<slug>`) depend on API data at runtime; they are not universally prerendered by default.
- Optional blog detail prerender can be enabled only when specific slugs are provided.
- Current React schema implementation is still mostly global (organization-level) rather than deeply route-specific for every page type.
- Full SSR request-time rendering is not implemented; this is build-time prerender plus SPA fallback.

## 5. Migration Path to Next.js (if needed later)
1. Introduce Next.js App Router for public marketing/blog/service routes.
2. Keep Django as API/admin backend (headless contract).
3. Move page metadata/schema from React Helmet to Next metadata APIs.
4. Replace build-time snapshots with request-time SSR/ISR where needed.
5. Preserve route parity and canonical URLs during migration, then retire Django SPA catch-all for migrated routes.

## Source of Truth Notes
- `robots.txt`: Django route in `backend/urls.py`.
- Sitemaps: Django sitemaps in `portfolio/sitemaps.py` exposed by `backend/urls.py`.
- Canonical redirect enforcement: `portfolio/middleware.py` (`CanonicalUrlMiddleware`).
- React prerender serving: `backend/views.py` (`react_frontend_entry`) + snapshots in `frontend/dist/prerender`.
