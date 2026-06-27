Dev container for sepidman.github.io

This devcontainer provides a reproducible development environment for this Eleventy site.

Included tools:
- Node 20 and npm (via the base devcontainer image)
- pixi for Python environment management
- git
- Git LFS (`git-lfs`)
- GitHub CLI (`gh`)
- build tools: `build-essential`, `python3`, `make`, etc.
- utilities: `curl`, `ripgrep`, `jq`, `tree`, `less`, `zip`, `unzip`
- scripting and lint helpers: `shellcheck`, `sqlite3`
- asset tooling: `imagemagick`
- terminal editors: `nano`, `vim`

How to use
1. Install Docker Desktop on Windows and ensure it is running.
2. Open this repository in VS Code.
3. Run the command: **Dev Containers: Reopen in Container** (Command Palette).

What happens when the container is created
- The Dockerfile installs the system tools above.
- The container runs as the built-in `node` user from the official Node devcontainer image.
- `postCreateCommand` in `.devcontainer/devcontainer.json` runs `npm install && ~/.pixi/bin/pixi install --all` so the Node toolchain plus the `resume`, `rendercv`, and `lint` pixi environments are ready.

After the container starts
- Start the live preview server: `npx task dev`.
- Build the default paper-native resume PDF: `npx task build:resume`.
- Build the full site plus default PDF: `npx task build`.
- Open the forwarded port `8080` when VS Code prompts you. The devcontainer is configured to open this as a preview automatically.
- Verify the production build too: `npx task build`.
- If `package-lock.json` was created, commit it so CI can use `npm ci`.

Commit example after container run:

```bash
git add package-lock.json
git commit -m "chore: add package-lock.json (generated in devcontainer)"
git push origin main
```
