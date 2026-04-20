import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { resolvePrerenderRoutes } from "../prerender.routes.mjs";

const FRONTEND_ROOT = process.cwd();
const CLIENT_DIST_DIR = path.join(FRONTEND_ROOT, "dist");
const SSR_DIST_DIR = path.join(FRONTEND_ROOT, "dist-ssr");
const PRERENDER_ROOT = path.join(CLIENT_DIST_DIR, "prerender");

const ROOT_CONTAINER_PATTERN = /<div id="root"><\/div>/;
const TITLE_PATTERN = /<title>[\s\S]*?<\/title>/i;

function withHelmet(baseHtml, helmet) {
  const cleanedHtml = helmet.title ? baseHtml.replace(TITLE_PATTERN, "") : baseHtml;
  const helmetMarkup = [helmet.title, helmet.meta, helmet.link, helmet.script]
    .filter(Boolean)
    .join("\n");

  if (!helmetMarkup) {
    return cleanedHtml;
  }

  return cleanedHtml.replace("</head>", `${helmetMarkup}\n</head>`);
}

function withAppHtml(baseHtml, appHtml) {
  return baseHtml.replace(ROOT_CONTAINER_PATTERN, `<div id="root">${appHtml}</div>`);
}

function outputFileForRoute(route) {
  if (route === "/") {
    return path.join(PRERENDER_ROOT, "index.html");
  }

  const relativePath = route.replace(/^\/+/, "");
  return path.join(PRERENDER_ROOT, relativePath, "index.html");
}

async function resolveServerEntryFile() {
  const directCandidates = [
    path.join(SSR_DIST_DIR, "entry-server.js"),
    path.join(SSR_DIST_DIR, "assets", "index.js"),
  ];

  for (const candidate of directCandidates) {
    try {
      await fs.access(candidate);
      return candidate;
    } catch {
      // Continue searching.
    }
  }

  const assetsDir = path.join(SSR_DIST_DIR, "assets");
  try {
    const assetFiles = await fs.readdir(assetsDir);
    const jsAsset = assetFiles.find((file) => file.endsWith(".js"));
    if (jsAsset) {
      return path.join(assetsDir, jsAsset);
    }
  } catch {
    // Ignore and fall through to explicit error.
  }

  throw new Error("Unable to locate SSR entry module in dist-ssr output.");
}

async function main() {
  const routes = resolvePrerenderRoutes();
  const template = await fs.readFile(path.join(CLIENT_DIST_DIR, "index.html"), "utf8");
  const ssrEntryFile = await resolveServerEntryFile();
  const serverModule = await import(pathToFileURL(ssrEntryFile).href);

  if (typeof serverModule.render !== "function") {
    throw new Error("SSR prerender module is missing a render(url) export.");
  }

  for (const route of routes) {
    const { appHtml, helmet } = serverModule.render(route);
    let pageHtml = withAppHtml(template, appHtml);
    pageHtml = withHelmet(pageHtml, helmet);

    const outputFile = outputFileForRoute(route);
    await fs.mkdir(path.dirname(outputFile), { recursive: true });
    await fs.writeFile(outputFile, pageHtml, "utf8");
    console.log(`Prerendered ${route} -> ${path.relative(FRONTEND_ROOT, outputFile)}`);
  }

  await fs.rm(SSR_DIST_DIR, { recursive: true, force: true });
  console.log("Removed temporary SSR build output.");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
