const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const YAML = require("yaml");

const mainPath = resolve(__dirname, "../../data/main.yaml");

module.exports = YAML.parse(readFileSync(mainPath, "utf8"));
