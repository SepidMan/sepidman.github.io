const source = require("./main");

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function cleanDateParts(value) {
  if (!value) {
    return null;
  }

  const parts = String(value).split("-");
  const [year, month = "01", day = "01"] = parts;
  return `${year}-${month}-${day}`;
}

function buildHighlights(workItem) {
  const highlights = asArray(workItem.highlights);
  if (highlights.length > 0) {
    return highlights;
  }
  return workItem.summary ? [workItem.summary] : [];
}

function slugifyName(value) {
  const slug = String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

  return slug || "resume";
}

const assetSlug = slugifyName(source.basics && source.basics.name);
const downloads = {
  resumePdf: {
    href: `/assets/${assetSlug}-resume.pdf`,
    label: "Resume (PDF)"
  },
  cvPdf: {
    href: `/assets/${assetSlug}-cv.pdf`,
    label: "CV (PDF)"
  },
  jsonResume: {
    href: `/assets/${assetSlug}-jsonresume.json`,
    label: "CV (JSON Resume)"
  }
};

module.exports = {
  ...source,
  basics: {
    ...source.basics,
    profiles: asArray(source.basics && source.basics.profiles)
  },
  work: asArray(source.work).map((item) => ({
    ...item,
    startDateRaw: item.startDate || null,
    endDateRaw: item.endDate || null,
    startDate: cleanDateParts(item.startDate),
    endDate: cleanDateParts(item.endDate),
    highlights: buildHighlights(item)
  })),
  education: asArray(source.education).map((item) => ({
    ...item,
    startDateRaw: item.startDate || null,
    endDateRaw: item.endDate || null,
    startDate: cleanDateParts(item.startDate),
    endDate: cleanDateParts(item.endDate)
  })),
  awards: asArray(source.awards).map((item) => ({
    ...item,
    dateRaw: item.date || null,
    date: cleanDateParts(item.date)
  })),
  certificates: asArray(source.certificates),
  skills: asArray(source.skills),
  languages: asArray(source.languages),
  interests: asArray(source.interests),
  projects: asArray(source.projects),
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
