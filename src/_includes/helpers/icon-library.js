const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { icon } = require("@fortawesome/fontawesome-svg-core");
const brandIcons = require("@fortawesome/free-brands-svg-icons");
const regularIcons = require("@fortawesome/free-regular-svg-icons");
const solidIcons = require("@fortawesome/free-solid-svg-icons");
const customIconRoot = resolve(__dirname, "../../assets/icons/custom");
const customIconCache = new Map();

const faStyleLibraries = {
  brands: brandIcons,
  regular: regularIcons,
  solid: solidIcons
};

function toFontAwesomeExportName(name) {
  return `fa${String(name)
    .split(/[^a-zA-Z0-9]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join("")}`;
}

function renderFontAwesomeIcon(name, style) {
  const library = faStyleLibraries[style];
  if (!library || !name) {
    return null;
  }

  const definition = library[toFontAwesomeExportName(name)];
  if (!definition) {
    return null;
  }

  return icon(definition).html.join("");
}

function renderCustomIcon(name, family) {
  const key = `${family}:${name}`;
  if (customIconCache.has(key)) {
    return customIconCache.get(key);
  }

  const candidates = [
    resolve(customIconRoot, family, `${name}.svg`),
    resolve(customIconRoot, family, "fallback.svg"),
    resolve(customIconRoot, "social", "fallback.svg")
  ];

  const svg = candidates.find((candidate) => {
    try {
      customIconCache.set(candidate, readFileSync(candidate, "utf8"));
      return true;
    } catch {
      return false;
    }
  });

  const value = svg ? customIconCache.get(svg) : "";
  customIconCache.set(key, value);
  return value;
}

function renderIconDescriptor(kind, name, style, family = "social") {
  if (kind === "fontawesome") {
    return renderFontAwesomeIcon(name, style) || renderCustomIcon("fallback", family);
  }

  return renderCustomIcon(name, family);
}

module.exports = {
  renderIconDescriptor
};
