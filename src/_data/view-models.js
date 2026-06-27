function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function asObject(value) {
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}

function cleanDateParts(value) {
  if (!value) {
    return null;
  }

  const parts = String(value).split("-");
  const [year, month = "01", day = "01"] = parts;
  return `${year}-${month}-${day}`;
}

function buildHighlights(item) {
  const highlights = asArray(item && item.highlights);
  if (highlights.length > 0) {
    return highlights;
  }

  return item && item.summary ? [item.summary] : [];
}

function slugifyName(value) {
  const slug = String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

  return slug || "resume";
}

function formatLocation(location) {
  if (!location || typeof location !== "object") {
    return "";
  }

  const city = typeof location.city === "string" ? location.city : "";
  const region = typeof location.region === "string" ? location.region : "";
  const countryCode =
    typeof location.countryCode === "string" ? location.countryCode : "";
  const parts = [city];

  if (region && region !== city) {
    parts.push(region);
  }

  if (countryCode) {
    parts.push(countryCode);
  }

  return parts.filter(Boolean).join(", ");
}

function normalizeIcon(icon) {
  if (typeof icon === "string" && icon) {
    return {
      icon,
      iconKind: "custom",
      iconName: icon,
      iconStyle: null,
      iconToken: icon
    };
  }

  if (icon && typeof icon === "object") {
    const kind = typeof icon.kind === "string" ? icon.kind : "custom";
    const name = typeof icon.name === "string" ? icon.name : "";
    const style = typeof icon.style === "string" ? icon.style : null;

    return {
      icon,
      iconKind: kind,
      iconName: name,
      iconStyle: style,
      iconToken: name || null
    };
  }

  return {
    icon: null,
    iconKind: null,
    iconName: "",
    iconStyle: null,
    iconToken: null
  };
}

function withIcon(item, fallbackIcon) {
  return {
    ...item,
    ...normalizeIcon(item.icon || fallbackIcon || null)
  };
}

function buildResumeDownloads(source) {
  const basics = asObject(source && source.basics);
  const website = asObject(source && source.website);
  const pages = asObject(website.pages);
  const pageResume = asObject(pages.resume);
  const contact = asObject(pageResume.contact);
  const labels = asObject(contact.downloads);
  const assetSlug = slugifyName(basics.name);

  const downloads = {
    resumePdf: {
      href: `/assets/${assetSlug}-resume.pdf`,
      label: labels.resumePdf || "Resume (PDF)"
    },
    cvPdf: {
      href: `/assets/${assetSlug}-cv.pdf`,
      label: labels.cvPdf || "CV (PDF)"
    },
    jsonResume: {
      href: `/assets/${assetSlug}-jsonresume.json`,
      label: labels.jsonResume || "CV (JSON Resume)"
    }
  };

  return {
    downloads,
    downloadOptions: [
      downloads.resumePdf,
      downloads.cvPdf,
      downloads.jsonResume
    ],
    resumePdfPath: downloads.resumePdf.href,
    cvPdfPath: downloads.cvPdf.href,
    jsonResumePath: downloads.jsonResume.href
  };
}

function resolveAction(action, assets) {
  if (!action || typeof action !== "object") {
    return action;
  }

  if (typeof action.asset === "string") {
    const assetMap = {
      cvPdf: assets.cvPdfPath,
      resumePdf: assets.resumePdfPath,
      jsonResume: assets.jsonResumePath
    };

    return {
      ...action,
      url: assetMap[action.asset] || action.url || "#"
    };
  }

  return action;
}

function resolveActionGroup(group, assets) {
  if (!group || typeof group !== "object") {
    return group;
  }

  return {
    ...group,
    primary: resolveAction(group.primary, assets),
    secondary: resolveAction(group.secondary, assets)
  };
}

function getProjectEntries(main) {
  return asArray(main && main.projects);
}

function getProjectPresentation(project) {
  return asObject(project && project.presentation);
}

function getProjectSlug(project) {
  return getProjectPresentation(project).slug || "";
}

function getPrimaryRole(project) {
  const roles = asArray(project && project.roles);
  return roles[0] || "";
}

function getTimeline(project) {
  const start = project && project.startDate ? String(project.startDate) : "";
  const end = project && project.endDate ? String(project.endDate) : "";

  if (start && end && start !== end) {
    return `${start} - ${end}`;
  }

  return start || end || "";
}

function buildProjectView(project, projectsPage) {
  const presentation = getProjectPresentation(project);
  const listing = asObject(presentation.listing);
  const cover = asObject(presentation.cover);
  const meta = asObject(presentation.meta);
  const seo = asObject(presentation.seo);
  const page = asObject(projectsPage);
  const labels = asObject(page.meta);

  return {
    title: project.name || "",
    summary: project.description || "",
    description: seo.description || project.description || "",
    permalink: `/work/${getProjectSlug(project)}/index.html`,
    role: getPrimaryRole(project),
    timeline: getTimeline(project),
    tools: asArray(project.keywords),
    focus: meta.focus || "",
    presentation: {
      slug: getProjectSlug(project),
      featured: Boolean(listing.featured),
      order: typeof listing.order === "number" ? listing.order : 0,
      label: listing.label || null,
      coverTone: cover.tone || "sage"
    },
    labels: {
      role: labels.roleLabel || "Role",
      timeline: labels.timelineLabel || "Timeline",
      tools: labels.toolsLabel || "Tools",
      focus: labels.focusLabel || "Focus"
    }
  };
}

function findProjectBySlug(main, slug) {
  return getProjectEntries(main).find((project) => getProjectSlug(project) === slug);
}

module.exports = {
  asArray,
  asObject,
  buildHighlights,
  buildProjectView,
  buildResumeDownloads,
  cleanDateParts,
  findProjectBySlug,
  formatLocation,
  resolveAction,
  resolveActionGroup,
  withIcon
};
