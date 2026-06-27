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
    projectView: (data) => requireProjectView(data),
    title: (data) => requireProjectView(data).title,
    description: (data) => requireProjectView(data).description,
    permalink: (data) => requireProjectView(data).permalink
  }
};
