export interface ProjectSummary {
  id: number;
  title: string;
  description: string;
  tech_stack: string;
  repo_link?: string;
  live_link?: string;
  featured?: boolean;
  image?: string;
  client_challenge?: string;
  my_solution?: string;
  the_result?: string;
}

const FLAGSHIP_PROJECT_TITLES = new Set(["openeire studios"]);
const PROJECT_TRANSLATION_KEYS = new Map([
  ["openeire studios", "openeire"],
  ["timeless travel", "timeless_travel"],
  ["honeypot", "honeypot"],
  ["cm artistry", "cm_artistry"],
]);

const normalizeTitle = (title?: string) => (title || "").trim().toLowerCase();

export const isFlagshipProject = (project?: Pick<ProjectSummary, "title"> | null) =>
  FLAGSHIP_PROJECT_TITLES.has(normalizeTitle(project?.title));

export const getProjectTranslationKey = (
  project?: Pick<ProjectSummary, "title"> | null,
) => PROJECT_TRANSLATION_KEYS.get(normalizeTitle(project?.title)) ?? null;
