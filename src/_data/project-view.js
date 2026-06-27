const main = require("./main");
const { asObject, buildProjectView } = require("./view-models");

const website = asObject(main.website);
const pages = asObject(website.pages);
const projectsPage = asObject(pages.projects);

module.exports = {
  build(project) {
    return buildProjectView(project, projectsPage);
  }
};
