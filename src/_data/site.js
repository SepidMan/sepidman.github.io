const main = require("./main");
const resume = require("./resume");

function asArray(value) {
  return Array.isArray(value) ? value : [];
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

function resolveAction(action) {
  if (!action || typeof action !== "object") {
    return action;
  }

  if (typeof action.asset === "string") {
    const assetMap = {
      cvPdf: resume.cvPdfPath,
      resumePdf: resume.resumePdfPath,
      jsonResume: resume.jsonResumePath
    };

    return {
      ...action,
      url: assetMap[action.asset] || action.url || "#"
    };
  }

  return action;
}

const basics = main.basics || {};
const website = main.website || {};
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
  home: {
    ...(website.home || {}),
    ctaPrimary: resolveAction(website.home && website.home.ctaPrimary),
    ctaSecondary: resolveAction(website.home && website.home.ctaSecondary)
  },
  about: website.about || {},
  contact: {
    ...(website.contact || {}),
    resumePdf: resume.cvPdfPath
  },
  pages: {
    ...(website.pages || {}),
    home: {
      ...(website.pages && website.pages.home ? website.pages.home : {}),
      cta: {
        ...(website.pages && website.pages.home && website.pages.home.cta
          ? website.pages.home.cta
          : {}),
        primary: resolveAction(
          website.pages &&
            website.pages.home &&
            website.pages.home.cta &&
            website.pages.home.cta.primary
        ),
        secondary: resolveAction(
          website.pages &&
            website.pages.home &&
            website.pages.home.cta &&
            website.pages.home.cta.secondary
        )
      }
    }
  }
};
