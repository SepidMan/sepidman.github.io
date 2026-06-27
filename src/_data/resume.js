const source = require("./main");
const {
  asArray,
  buildHighlights,
  buildResumeDownloads,
  cleanDateParts
} = require("./view-models");

const resumeAssets = buildResumeDownloads(source);

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
  downloads: resumeAssets.downloads,
  downloadOptions: resumeAssets.downloadOptions,
  resumePdfPath: resumeAssets.resumePdfPath,
  cvPdfPath: resumeAssets.cvPdfPath,
  jsonResumePath: resumeAssets.jsonResumePath
};
