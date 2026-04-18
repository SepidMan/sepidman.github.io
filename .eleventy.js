const { DateTime } = require("luxon");

module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/styles.css": "styles.css" });

  eleventyConfig.addFilter("readableDate", dateObj => {
    return DateTime.fromJSDate(dateObj, { zone: "utc" }).toFormat("LLLL d, yyyy");
  });

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "docs"
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
};
