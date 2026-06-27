const resume = require("./resume");

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

const navigation = [
  {
    label: "Work",
    url: "/work/",
    icon: "work"
  },
  {
    label: "Resume",
    url: "/resume/",
    icon: "resume"
  },
  {
    label: "About",
    url: "/about/",
    icon: "about"
  },
  {
    label: "Contact",
    url: "/contact/",
    icon: "contact"
  }
].map((item) => withIcon(item));

const social = [
  {
    name: "LinkedIn",
    url: "https://www.linkedin.com/in/sepid-mans/",
    icon: "linkedin"
  },
  {
    name: "GitHub",
    url: "https://github.com/SepidMans",
    icon: "github"
  },
  {
    name: "Instagram",
    url: "https://www.instagram.com/_seraphim___/",
    icon: "instagram"
  }
].map((item) => withIcon(item));

const headerSocial = [
  {
    name: "LinkedIn",
    url: "https://www.linkedin.com/in/sepid-mans/",
    icon: "linkedin"
  },
  {
    name: "GitHub",
    url: "https://github.com/SepidMans",
    icon: "github"
  },
  {
    name: "Instagram",
    url: "https://www.instagram.com/_seraphim___/",
    icon: "instagram"
  },
  {
    name: "Email",
    url: "mailto:sepideh.mansouri85@gmail.com",
    icon: "email"
  }
].map((item) => withIcon(item));

module.exports = {
  title: "Sepideh Mansouri",
  tagline: "UI/UX Designer",
  description:
    "Portfolio website for Sepideh Mansouri, a UI/UX designer focused on calm interfaces, thoughtful systems, and human-centered digital experiences.",
  url: "https://sepidman.github.io",
  author: {
    name: "Sepideh Mansouri",
    shortName: "Sepideh",
    title: "UI/UX Designer",
    location: "Berlin, Germany",
    email: "sepideh.mansouri85@gmail.com",
    brandImage: "/assets/images/profile/headshot.jpg"
  },
  navigation,
  social,
  headerSocial,
  home: {
    eyebrow: "UI/UX designer based in Berlin",
    headline:
      "I design digital products that feel clear, calm, and genuinely human.",
    intro:
      "My work blends UX thinking, content clarity, and visual sensitivity to create interfaces that help people feel capable from the first screen to the final decision.",
    highlights: [
      "Mobile-first product thinking",
      "Clear flows and information architecture",
      "Warm, professional interface design"
    ],
    ctaPrimary: {
      label: "View selected work",
      url: "/work/"
    },
    ctaSecondary: {
      label: "Download CV",
      url: resume.cvPdfPath
    },
    stats: [
      {
        label: "Focus",
        value: "UX strategy",
        detail: "User flows, clarity, and design systems"
      },
      {
        label: "Approach",
        value: "Calm UI",
        detail: "Strong hierarchy with expressive restraint"
      },
      {
        label: "Based in",
        value: "Berlin",
        detail: "Open to junior and internship opportunities"
      }
    ]
  },
  about: {
    summary: [
      "I am a UI/UX designer with a background in content management and customer-facing work, now focused on designing digital experiences that are both usable and emotionally aware.",
      "I care about information architecture, tone of voice, and visual rhythm because the best interfaces do more than function well. They help people feel oriented, respected, and confident."
    ],
    principles: [
      "Start from real user intent",
      "Reduce friction before adding flourish",
      "Design systems that stay coherent as products grow",
      "Give every interface a clear point of view"
    ]
  },
  contact: {
    intro:
      "If you would like to talk about a role, collaboration, or portfolio feedback, I would love to hear from you.",
    availability:
      "Currently open to junior UI/UX roles, internships, and collaborative product design opportunities.",
    resumePdf: resume.cvPdfPath
  }
};
