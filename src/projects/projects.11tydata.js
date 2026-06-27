const main = require("../_data/main");

function getProjectEntries() {
  return Array.isArray(main.projects) ? main.projects : [];
}

function getProjectWebsite(project) {
  return project && typeof project.website === "object" ? project.website : {};
}

function findProjectBySlug(slug) {
  return getProjectEntries().find((project) => {
    const website = getProjectWebsite(project);
    return website.slug === slug;
  });
}

function requireProject(data) {
  const slug = data.page.fileSlug;
  const project = findProjectBySlug(slug);

  if (!project) {
    throw new Error(`No project entry found in data/main.yaml for slug "${slug}".`);
  }

  return project;
}

function getRole(project) {
  const roles = Array.isArray(project.roles) ? project.roles : [];
  return roles[0] || "";
}

function getTimeline(project) {
  const start = project.startDate ? String(project.startDate) : "";
  const end = project.endDate ? String(project.endDate) : "";

  if (start && end && start !== end) {
    return `${start} - ${end}`;
  }

  return start || end || "";
}

module.exports = {
  layout: "layouts/project.njk",
  tags: ["projects"],
  eleventyComputed: {
    projectEntry: (data) => requireProject(data),
    title: (data) => requireProject(data).name,
    description: (data) => {
      const project = requireProject(data);
      return project.website.seoDescription || project.description;
    },
    summary: (data) => requireProject(data).description,
    role: (data) => getRole(requireProject(data)),
    focus: (data) => requireProject(data).website.focus || "",
    timeline: (data) => getTimeline(requireProject(data)),
    tools: (data) => requireProject(data).keywords || [],
    coverTone: (data) => requireProject(data).website.coverTone || "sage",
    cardEyebrow: (data) => requireProject(data).website.cardEyebrow,
    featured: (data) => Boolean(requireProject(data).website.featured),
    order: (data) => requireProject(data).website.order || 0,
    permalink: (data) => `/work/${data.page.fileSlug}/index.html`
  }
};
