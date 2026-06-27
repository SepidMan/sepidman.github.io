const main = require("./main");
const resume = require("./resume");
const {
  asArray,
  asObject,
  formatLocation,
  resolveAction,
  resolveActionGroup,
  withIcon
} = require("./view-models");

const basics = main.basics || {};
const website = main.website || {};
const pages = asObject(website.pages);
const homePage = asObject(pages.home);
const homeHero = asObject(homePage.hero);
const projectsPage = asObject(pages.projects);
const social = asArray(basics.profiles).map((item) =>
  withIcon(
    {
      name: item.network,
      url: item.url,
      username: item.username,
      icon: item.icon
    },
    item.network ? String(item.network).toLowerCase() : null
  )
);
const extraConnections = asArray(basics.connections).map((item) =>
  withIcon({
    name: item.label,
    url: item.url || null,
    icon: item.icon
  })
);

module.exports = {
  title: basics.name || "",
  tagline: basics.label || "",
  description: website.description || "",
  url: website.baseUrl || basics.url || "",
  author: {
    name: basics.name || "",
    shortName: basics.shortName || basics.name || "",
    title: basics.label || "",
    location: formatLocation(basics.location),
    email: basics.email || "",
    brandImage: basics.image
      ? basics.image.replace(/^https?:\/\/[^/]+/, "")
      : ""
  },
  navigation: asArray(website.navigation).map((item) => withIcon(item)),
  social,
  headerSocial: [...social, ...extraConnections],
  pages: {
    ...pages,
    home: {
      ...homePage,
      hero: {
        ...homeHero,
        primaryAction: resolveAction(homeHero.primaryAction, resume),
        secondaryAction: resolveAction(homeHero.secondaryAction, resume)
      },
      callToAction: resolveActionGroup(homePage.callToAction, resume)
    },
    projects: {
      ...projectsPage,
      callToAction: resolveActionGroup(projectsPage.callToAction, resume)
    },
    contact: {
      ...asObject(pages.contact),
      resumePdf: resume.cvPdfPath
    }
  }
};
