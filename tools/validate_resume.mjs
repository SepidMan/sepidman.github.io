import { access, readFile } from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import Ajv from "ajv";
import addFormats from "ajv-formats";

const rootDir = resolve(process.cwd());
const resumePath = resolve(rootDir, "cv/resume.json");
const resumeSchemaPath = resolve(rootDir, "cv/resume_schema.json");
const variantsPath = resolve(rootDir, "cv/rendercv/variants.json");
const renderCvBasePath = resolve(rootDir, "cv/rendercv/base.yaml");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function readJson(filePath) {
  return JSON.parse(await readFile(filePath, "utf8"));
}

async function ensureReadable(filePath, label) {
  try {
    await access(filePath, fsConstants.R_OK);
  } catch {
    throw new Error(`${label} is missing or unreadable: ${filePath}`);
  }
}

function validateVariantShape(name, config) {
  assert(config && typeof config === "object", `Variant "${name}" must be an object.`);
  assert(typeof config.profile === "string" && config.profile.length > 0, `Variant "${name}" must define a profile.`);
  assert(typeof config.theme === "string" && config.theme.length > 0, `Variant "${name}" must define a theme.`);
  assert(typeof config.output === "string" && config.output.length > 0, `Variant "${name}" must define an output path.`);
  assert(config.output.startsWith("build/assets/"), `Variant "${name}" output must live under build/assets/.`);
}

export async function validateResumePipeline() {
  await Promise.all([
    ensureReadable(resumePath, "Resume source"),
    ensureReadable(resumeSchemaPath, "Resume schema"),
    ensureReadable(variantsPath, "RenderCV variants config"),
    ensureReadable(renderCvBasePath, "RenderCV base config")
  ]);

  const [resume, schema, variants] = await Promise.all([
    readJson(resumePath),
    readJson(resumeSchemaPath),
    readJson(variantsPath)
  ]);

  const ajv = new Ajv({
    allErrors: true,
    strict: false
  });
  addFormats(ajv);

  const validate = ajv.compile(schema);
  const valid = validate(resume);
  if (!valid) {
    const messages = (validate.errors || [])
      .map((error) => `${error.instancePath || "/"} ${error.message}`)
      .join("\n");
    throw new Error(`cv/resume.json failed schema validation:\n${messages}`);
  }

  assert(variants && typeof variants === "object" && !Array.isArray(variants), "cv/rendercv/variants.json must be an object keyed by variant name.");

  const checks = [ensureReadable(resolve(rootDir, "cv/rendercv/themes/default.yaml"), "Default theme config")];
  for (const [name, config] of Object.entries(variants)) {
    validateVariantShape(name, config);
    checks.push(
      ensureReadable(resolve(rootDir, `cv/profiles/${config.profile}.json`), `Profile for variant "${name}"`),
      ensureReadable(resolve(rootDir, `cv/rendercv/themes/${config.theme}.yaml`), `Theme for variant "${name}"`)
    );
  }

  await Promise.all(checks);

  return {
    resume,
    variants
  };
}

async function main() {
  await validateResumePipeline();
  console.log("Resume source, schema, profiles, and RenderCV variant config are valid.");
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
