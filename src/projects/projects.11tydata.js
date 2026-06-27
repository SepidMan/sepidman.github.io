const main = require("../_data/main");
const projectView = require("../_data/project-view");
const { findProjectBySlug } = require("../_data/view-models");

function requireProject(data) {
  const slug = data.page.fileSlug;
  const project = findProjectBySlug(main, slug);

  if (!project) {
    throw new Error(`No project entry found in data/main.yaml for slug "${slug}".`);
  }

  return project;
}

function requireProjectView(data) {
  return projectView.build(requireProject(data));
}

module.exports = {
  layout: "layouts/project.njk",
  tags: ["projects"],
  eleventyComputed: {
    projectEntry: (data) => requireProject(data),
    projectView: (data) => requireProjectView(data),
    title: (data) => requireProjectView(data).title,
    description: (data) => requireProjectView(data).description,
    summary: (data) => requireProjectView(data).summary,
    role: (data) => requireProjectView(data).role,
    focus: (data) => requireProjectView(data).focus,
    timeline: (data) => requireProjectView(data).timeline,
    tools: (data) => requireProjectView(data).tools,
    coverTone: (data) => requireProjectView(data).presentation.coverTone,
    cardEyebrow: (data) => requireProjectView(data).presentation.cardEyebrow,
    featured: (data) => requireProjectView(data).presentation.featured,
    order: (data) => requireProjectView(data).presentation.order,
    permalink: (data) => requireProjectView(data).permalink
  }
};
