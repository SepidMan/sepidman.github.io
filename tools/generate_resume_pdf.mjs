import { createReadStream, existsSync, mkdirSync, statSync } from "node:fs";
import { resolve, join, extname } from "node:path";
import { createServer } from "node:http";
import { chromium } from "playwright";

// Legacy fallback: this prints the resume HTML page to PDF via Chromium.
// The dedicated RenderCV pipeline is now the preferred path for paper-native PDFs.
const rootDir = resolve(process.cwd(), "build");
const outputDir = join(rootDir, "assets");
const outputFile = join(outputDir, "sepideh-mansouri-resume.pdf");
const mimeTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".pdf": "application/pdf",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".webp": "image/webp"
};

function safePath(urlPath) {
  const cleanPath = urlPath === "/" ? "/index.html" : urlPath;
  const candidate = resolve(rootDir, `.${cleanPath}`);
  if (!candidate.startsWith(rootDir)) {
    return null;
  }

  if (existsSync(candidate) && statSync(candidate).isDirectory()) {
    return join(candidate, "index.html");
  }

  return candidate;
}

function startStaticServer() {
  const server = createServer((request, response) => {
    const requestUrl = new URL(request.url, "http://127.0.0.1");
    const filePath = safePath(requestUrl.pathname);

    if (!filePath || !existsSync(filePath)) {
      response.writeHead(404);
      response.end("Not found");
      return;
    }

    const extension = extname(filePath);
    response.setHeader("Content-Type", mimeTypes[extension] || "application/octet-stream");
    createReadStream(filePath).pipe(response);
  });

  return new Promise((resolveServer) => {
    server.listen(0, "127.0.0.1", () => resolveServer(server));
  });
}

async function generate() {
  if (!existsSync(rootDir)) {
    throw new Error("The build directory does not exist. Run the site build before generating the PDF.");
  }

  mkdirSync(outputDir, { recursive: true });

  const server = await startStaticServer();
  const address = server.address();
  const port = typeof address === "object" && address ? address.port : 4173;
  const browser = await chromium.launch({ headless: true });

  try {
    const page = await browser.newPage();
    await page.goto(`http://127.0.0.1:${port}/resume/print/`, { waitUntil: "networkidle" });
    await page.emulateMedia({ media: "print" });
    await page.pdf({
      path: outputFile,
      format: "A4",
      printBackground: true,
      margin: {
        top: "14mm",
        right: "14mm",
        bottom: "14mm",
        left: "14mm"
      }
    });
    console.log(`Saved PDF to ${outputFile}`);
  } finally {
    await browser.close();
    await new Promise((resolveClose) => server.close(resolveClose));
  }
}

generate().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
