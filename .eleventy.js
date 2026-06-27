const { DateTime } = require("luxon");
const { renderIconDescriptor } = require("./src/_includes/helpers/icon-library");

function parseDate(value) {
  if (!value) {
    return null;
  }

  if (value instanceof Date) {
    return DateTime.fromJSDate(value, { zone: "utc" });
  }

  const parsed = DateTime.fromISO(value, { zone: "utc" });
  return parsed.isValid ? parsed : null;
}

module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/styles.css": "styles.css" });
  eleventyConfig.addPassthroughCopy({ "src/theme.js": "theme.js" });
  eleventyConfig.addPassthroughCopy("src/assets/**/*.{avif,gif,ico,jpg,jpeg,png,pdf,svg,webp}");
  eleventyConfig.ignores.add("src/assets/**/*.md");

  eleventyConfig.addCollection("projects", (collectionApi) => {
    return collectionApi.getFilteredByTag("projects").sort((a, b) => {
      return (
        (a.data.projectView && a.data.projectView.presentation
          ? a.data.projectView.presentation.order
          : 0) -
        (b.data.projectView && b.data.projectView.presentation
          ? b.data.projectView.presentation.order
          : 0)
      );
    });
  });

  eleventyConfig.addCollection("featuredProjects", (collectionApi) => {
    return collectionApi.getFilteredByTag("projects")
      .filter(
        (item) =>
          item.data.projectView &&
          item.data.projectView.presentation &&
          item.data.projectView.presentation.featured
      )
      .sort((a, b) => {
        return (
          (a.data.projectView && a.data.projectView.presentation
            ? a.data.projectView.presentation.order
            : 0) -
          (b.data.projectView && b.data.projectView.presentation
            ? b.data.projectView.presentation.order
            : 0)
        );
      });
  });

  eleventyConfig.addFilter("readableDate", (value, format = "LLLL d, yyyy") => {
    const parsed = parseDate(value);
    return parsed ? parsed.toFormat(format) : "";
  });

  eleventyConfig.addFilter("resumeDate", (value) => {
    const parsed = parseDate(value);
    return parsed ? parsed.toFormat("LLL yyyy") : "Present";
  });

  eleventyConfig.addFilter("yearRange", (start, end) => {
    const startDate = parseDate(start);
    const endDate = parseDate(end);
    const startLabel = startDate ? startDate.toFormat("yyyy") : "";
    const endLabel = endDate ? endDate.toFormat("yyyy") : "Present";

    if (!startLabel && !endLabel) {
      return "";
    }

    if (!startLabel) {
      return endLabel;
    }

    if (!endDate || startLabel !== endLabel) {
      return `${startLabel} - ${endLabel}`;
    }

    return startLabel;
  });

  eleventyConfig.addFilter("isoDate", (value) => {
    const parsed = parseDate(value);
    return parsed ? parsed.toISODate() : "";
  });

  eleventyConfig.addFilter("primaryProfile", (profiles, networkName) => {
    return (profiles || []).find((profile) => profile.network === networkName);
  });

  eleventyConfig.addFilter("renderIconFields", (iconName, iconKind, iconStyle, family = "social") => {
    return renderIconDescriptor(iconKind, iconName, iconStyle, family);
  });

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "build/website"
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
};
