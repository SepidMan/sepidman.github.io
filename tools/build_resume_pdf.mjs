import { access, mkdir } from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import { resolve } from "node:path";
import { spawn } from "node:child_process";
import { pathToFileURL } from "node:url";
import { generateRenderCvYaml } from "./convert_resume_to_rendercv.mjs";
import { validateResumePipeline } from "./validate_resume.mjs";

const rootDir = resolve(process.cwd());
const pixiBinary = resolve(process.env.HOME || "", ".pixi/bin/pixi");

function parseArgs(argv) {
  const args = {
    variant: "default",
    all: false
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--variant") {
      args.variant = argv[index + 1];
      index += 1;
    } else if (value === "--all") {
      args.all = true;
    }
  }

  return args;
}

async function ensurePixi() {
  try {
    await access(pixiBinary, fsConstants.X_OK);
  } catch {
    throw new Error(`Pixi is not installed at ${pixiBinary}. Install it first or reopen the devcontainer.`);
  }
}

function run(command, args) {
  return new Promise((resolveRun, rejectRun) => {
    const child = spawn(command, args, {
      cwd: rootDir,
      stdio: "inherit"
    });

    child.on("exit", (code) => {
      if (code === 0) {
        resolveRun();
        return;
      }
      rejectRun(new Error(`Command failed: ${command} ${args.join(" ")}`));
    });
    child.on("error", rejectRun);
  });
}

async function buildVariant(variant) {
  const { outputPath, pdfOutputPath } = await generateRenderCvYaml({ variant });
  await mkdir(resolve(rootDir, "build/assets"), { recursive: true });
  await run(pixiBinary, ["run", "rendercv", "render", outputPath]);
  await access(pdfOutputPath, fsConstants.R_OK);
  return pdfOutputPath;
}

export async function buildResumePdf({ variant = "default", all = false } = {}) {
  await ensurePixi();
  const { variants } = await validateResumePipeline();
  const names = all ? Object.keys(variants) : [variant];

  const outputs = [];
  for (const name of names) {
    outputs.push(await buildVariant(name));
  }
  return outputs;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const outputs = await buildResumePdf(args);
  for (const output of outputs) {
    console.log(`Built RenderCV PDF: ${output}`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
