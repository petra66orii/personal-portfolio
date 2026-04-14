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

const normalizeTitle = (title?: string) => (title || "").trim().toLowerCase();

export const isFlagshipProject = (project?: Pick<ProjectSummary, "title"> | null) =>
  FLAGSHIP_PROJECT_TITLES.has(normalizeTitle(project?.title));

export const sortProjectsWithFlagshipFirst = <T extends Pick<ProjectSummary, "title">>(
  projects: T[],
) =>
  [...projects].sort((left, right) => {
    const leftRank = isFlagshipProject(left) ? 0 : 1;
    const rightRank = isFlagshipProject(right) ? 0 : 1;

    if (leftRank !== rightRank) {
      return leftRank - rightRank;
    }

    return 0;
  });
