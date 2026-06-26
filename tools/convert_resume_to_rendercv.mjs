import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve, dirname, relative } from "node:path";
import { pathToFileURL } from "node:url";
import YAML from "yaml";
import { convert as convertJsonResume } from "@jsonresume/jsonresume-to-rendercv/convert.js";
import { validateResumePipeline } from "./validate_resume.mjs";

const rootDir = resolve(process.cwd());
const variantsPath = resolve(rootDir, "cv/rendercv/variants.json");
const generatedDir = resolve(rootDir, "cv/generated");

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function deepMerge(target, source) {
  if (!isPlainObject(source)) {
    return source;
  }

  const result = isPlainObject(target) ? { ...target } : {};
  for (const [key, value] of Object.entries(source)) {
    if (isPlainObject(value) && isPlainObject(result[key])) {
      result[key] = deepMerge(result[key], value);
      continue;
    }

    result[key] = value;
  }

  return result;
}

async function readJson(filePath) {
  return JSON.parse(await readFile(filePath, "utf8"));
}

async function readYaml(filePath) {
  return YAML.parse(await readFile(filePath, "utf8"));
}

function clone(value) {
  return structuredClone(value);
}

function pickUsername(profile) {
  if (profile.username) {
    return profile.username;
  }

  if (profile.url) {
    try {
      const url = new URL(profile.url);
      return url.pathname.replace(/^\/+/, "");
    } catch {
      return profile.url;
    }
  }

  return "";
}

function formatLocation(location) {
  if (!location) {
    return "";
  }

  let country = location.countryCode || "";
  if (country && typeof Intl.DisplayNames === "function") {
    const regionNames = new Intl.DisplayNames(["en"], { type: "region" });
    country = regionNames.of(country) || country;
  }

  const region = location.region && location.region !== location.city ? location.region : "";
  const parts = [location.city, region, country].filter(Boolean);
  return parts.join(", ");
}

function toDateFields(startDate, endDate) {
  const date = {};
  if (startDate) {
    date.start_date = startDate;
  }
  if (endDate) {
    date.end_date = endDate;
  } else if (startDate) {
    date.end_date = "present";
  }
  return Object.keys(date).length > 0 ? date : undefined;
}

function withSummaryHighlights(summary, highlights) {
  const normalizedHighlights = Array.isArray(highlights) ? highlights.filter(Boolean) : [];
  if (normalizedHighlights.length > 0) {
    return normalizedHighlights;
  }
  return summary ? [summary] : [];
}

function applyProfileOverrides(resume, profile) {
  const nextResume = clone(resume);

  if (profile.summary) {
    nextResume.basics.summary = profile.summary;
  }

  const sectionConfig = profile.sections || {};
  for (const [sectionName, config] of Object.entries(sectionConfig)) {
    if (!isPlainObject(config)) {
      continue;
    }

    if (config.enabled === false) {
      nextResume[sectionName] = [];
      continue;
    }

    if (typeof config.limit === "number" && Array.isArray(nextResume[sectionName])) {
      nextResume[sectionName] = nextResume[sectionName].slice(0, config.limit);
    }
  }

  return nextResume;
}

function buildSections(resume) {
  const sections = {};

  if (resume.basics.summary) {
    sections.summary = [resume.basics.summary];
  }

  if (Array.isArray(resume.work) && resume.work.length > 0) {
    sections.experience = resume.work.map((item) => {
      const entry = {
        company: item.name,
        position: item.position,
        highlights: withSummaryHighlights(item.summary, item.highlights)
      };
      if (item.location) {
        entry.location = item.location;
      }
      if (item.summary) {
        entry.summary = item.summary;
      }
      const dates = toDateFields(item.startDate, item.endDate);
      if (dates) {
        Object.assign(entry, dates);
      }
      return entry;
    });
  }

  if (Array.isArray(resume.education) && resume.education.length > 0) {
    sections.education = resume.education.map((item) => {
      const entry = {
        institution: item.institution,
        area: item.area || "",
        degree: item.studyType || ""
      };
      if (item.location) {
        entry.location = item.location;
      }
      if (item.summary) {
        entry.summary = item.summary;
      }
      const dates = toDateFields(item.startDate, item.endDate);
      if (dates) {
        Object.assign(entry, dates);
      }
      return entry;
    });
  }

  if (Array.isArray(resume.skills) && resume.skills.length > 0) {
    sections.skills = resume.skills.map((item) => ({
      label: item.name,
      details: Array.isArray(item.keywords) ? item.keywords.join(", ") : ""
    }));
  }

  if (Array.isArray(resume.projects) && resume.projects.length > 0) {
    sections.projects = resume.projects.map((item) => {
      const entry = {
        name: item.name,
        highlights: withSummaryHighlights(item.description, item.highlights)
      };
      if (item.description) {
        entry.summary = item.description;
      }
      const dates = toDateFields(item.startDate, item.endDate);
      if (dates) {
        Object.assign(entry, dates);
      }
      return entry;
    });
  }

  if (Array.isArray(resume.certifications) && resume.certifications.length > 0) {
    sections.certifications = resume.certifications.map((item) => ({
      label: item.name,
      details: [item.issuer, item.date].filter(Boolean).join(" | ")
    }));
  }

  if (Array.isArray(resume.languages) && resume.languages.length > 0) {
    sections.languages = resume.languages.map((item) => ({
      label: item.language,
      details: item.fluency || ""
    }));
  }

  if (Array.isArray(resume.awards) && resume.awards.length > 0) {
    sections.awards = resume.awards.map((item) => ({
      bullet: [item.title, item.awarder].filter(Boolean).join(" | ")
    }));
  }

  return sections;
}

function buildRenderCvData(resume, convertedSeed, themeConfig, outputPath, pdfOutputPath) {
  const basics = resume.basics || {};
  const outputFolder = relative(dirname(outputPath), dirname(pdfOutputPath)) || ".";
  const pdfFilePath = relative(dirname(outputPath), pdfOutputPath);
  const typstFilePath = pdfFilePath.replace(/\.pdf$/i, ".typ");
  const cv = {
    ...(convertedSeed.cv || {}),
    name: basics.name,
    headline: basics.label || "",
    location: formatLocation(basics.location),
    email: basics.email || "",
    phone: basics.phone || "",
    website: basics.url || "",
    social_networks: (basics.profiles || []).map((profile) => ({
      network: profile.network,
      username: pickUsername(profile)
    })),
    sections: buildSections(resume)
  };

  return deepMerge(themeConfig, {
    cv,
    settings: {
      current_date: "today",
      render_command: {
        output_folder: outputFolder,
        pdf_path: pdfFilePath,
        typst_path: typstFilePath,
        dont_generate_markdown: true,
        dont_generate_html: true,
        dont_generate_png: true
      }
    }
  });
}

function parseArgs(argv) {
  const args = { variant: "default" };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--variant") {
      args.variant = argv[index + 1];
      index += 1;
    } else if (value === "--output") {
      args.output = argv[index + 1];
      index += 1;
    }
  }
  return args;
}

export async function generateRenderCvYaml({ variant = "default", output } = {}) {
  const { resume } = await validateResumePipeline();
  const variants = await readJson(variantsPath);
  const variantConfig = variants[variant];

  if (!variantConfig) {
    throw new Error(`Unknown resume variant "${variant}".`);
  }

  const profile = await readJson(resolve(rootDir, `cv/profiles/${variantConfig.profile}.json`));
  const baseConfig = await readYaml(resolve(rootDir, "cv/rendercv/base.yaml"));
  const themeConfig = await readYaml(resolve(rootDir, `cv/rendercv/themes/${variantConfig.theme}.yaml`));
  const themedConfig = deepMerge(baseConfig, themeConfig);

  const profiledResume = applyProfileOverrides(resume, profile);
  const convertedSeed = YAML.parse(await convertJsonResume(profiledResume));
  const outputPath = resolve(rootDir, output || `cv/generated/rendercv-${variant}.yaml`);
  const pdfOutputPath = resolve(rootDir, variantConfig.output);
  const renderCvData = buildRenderCvData(
    profiledResume,
    convertedSeed,
    themedConfig,
    outputPath,
    pdfOutputPath
  );

  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, YAML.stringify(renderCvData), "utf8");

  return {
    outputPath,
    profile: variantConfig.profile,
    theme: variantConfig.theme,
    pdfOutputPath
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const result = await generateRenderCvYaml(args);
  console.log(`Generated RenderCV input for variant "${args.variant}" at ${result.outputPath}`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
