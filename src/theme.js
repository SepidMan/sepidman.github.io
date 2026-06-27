const storageKey = "theme";
const themeModes = ["auto", "light", "dark"];
const themeIcons = {
  auto: "◐",
  light: "☀",
  dark: "☾"
};
const root = document.documentElement;
const button = document.querySelector("[data-theme-toggle]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const siteNav = document.querySelector("[data-site-nav]");
const downloadMenu = document.querySelector("[data-download-menu]");
const downloadMenuToggle = document.querySelector("[data-download-menu-toggle]");
const downloadMenuItems = document.querySelector("[data-download-menu-items]");

function preferredTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function normalizeThemeMode(theme) {
  return themeModes.includes(theme) ? theme : null;
}

function resolvedTheme(themeMode) {
  return themeMode === "auto" ? preferredTheme() : themeMode;
}

function nextThemeMode(themeMode) {
  const currentIndex = themeModes.indexOf(themeMode);
  return themeModes[(currentIndex + 1) % themeModes.length];
}

function formatThemeLabel(themeMode) {
  return themeMode.charAt(0).toUpperCase() + themeMode.slice(1);
}

function applyTheme(themeMode) {
  const activeThemeMode = normalizeThemeMode(themeMode) || "auto";
  const activeTheme = resolvedTheme(activeThemeMode);
  const upcomingThemeMode = nextThemeMode(activeThemeMode);

  root.setAttribute("data-theme", activeTheme);
  root.setAttribute("data-theme-mode", activeThemeMode);

  if (!button) {
    return;
  }

  button.setAttribute(
    "aria-label",
    `Theme: ${activeThemeMode}. Switch to ${upcomingThemeMode} theme.`
  );
  button.setAttribute("data-tip", `Theme: ${formatThemeLabel(activeThemeMode)}`);

  const label = button.querySelector(".theme-toggle-label");
  if (label) {
    label.textContent = formatThemeLabel(activeThemeMode);
  }

  const icon = button.querySelector(".theme-toggle-icon");
  if (icon) {
    icon.textContent = themeIcons[activeThemeMode];
  }
}

function storedTheme() {
  try {
    return normalizeThemeMode(localStorage.getItem(storageKey));
  } catch (error) {
    return null;
  }
}

function persistTheme(theme) {
  try {
    localStorage.setItem(storageKey, theme);
  } catch (error) {
    // Ignore storage access failures and keep the active session theme only.
  }
}

const initialThemeMode = storedTheme() || normalizeThemeMode(root.getAttribute("data-theme-mode")) || "auto";
applyTheme(initialThemeMode);

if (button) {
  button.addEventListener("click", () => {
    const currentThemeMode = normalizeThemeMode(root.getAttribute("data-theme-mode")) || "auto";
    const upcomingThemeMode = nextThemeMode(currentThemeMode);
    applyTheme(upcomingThemeMode);
    persistTheme(upcomingThemeMode);
  });
}

const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
mediaQuery.addEventListener("change", () => {
  const activeThemeMode = storedTheme() || normalizeThemeMode(root.getAttribute("data-theme-mode")) || "auto";
  if (activeThemeMode === "auto") {
    applyTheme("auto");
  }
});

function closeMenu() {
  if (!menuToggle || !siteNav) {
    return;
  }

  menuToggle.setAttribute("aria-expanded", "false");
  menuToggle.setAttribute("title", "Open menu");
  root.removeAttribute("data-menu-open");
}

function openMenu() {
  if (!menuToggle || !siteNav) {
    return;
  }

  menuToggle.setAttribute("aria-expanded", "true");
  menuToggle.setAttribute("title", "Close menu");
  root.setAttribute("data-menu-open", "true");
}

function syncMenuForViewport() {
  if (window.innerWidth > 700) {
    closeMenu();
  }
}

if (menuToggle && siteNav) {
  menuToggle.addEventListener("click", () => {
    const expanded = menuToggle.getAttribute("aria-expanded") === "true";
    if (expanded) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  siteNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth <= 700) {
        closeMenu();
      }
    });
  });

  window.addEventListener("resize", syncMenuForViewport);
  syncMenuForViewport();
}

function closeDownloadMenu() {
  if (!downloadMenu || !downloadMenuToggle || !downloadMenuItems) {
    return;
  }

  downloadMenu.removeAttribute("data-open");
  downloadMenuToggle.setAttribute("aria-expanded", "false");
  downloadMenuItems.hidden = true;
}

function openDownloadMenu() {
  if (!downloadMenu || !downloadMenuToggle || !downloadMenuItems) {
    return;
  }

  downloadMenu.setAttribute("data-open", "true");
  downloadMenuToggle.setAttribute("aria-expanded", "true");
  downloadMenuItems.hidden = false;
}

if (downloadMenu && downloadMenuToggle && downloadMenuItems) {
  downloadMenuToggle.addEventListener("click", () => {
    const expanded = downloadMenuToggle.getAttribute("aria-expanded") === "true";
    if (expanded) {
      closeDownloadMenu();
    } else {
      openDownloadMenu();
    }
  });

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Node) || downloadMenu.contains(event.target)) {
      return;
    }
    closeDownloadMenu();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeDownloadMenu();
    }
  });

  downloadMenuItems.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      closeDownloadMenu();
    });
  });
}

function animateHeroGraphic() {
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const graphic = document.querySelector(".hero-top-graphic");

  if (!graphic || prefersReducedMotion) {
    return;
  }

  const paths = graphic.querySelectorAll(".hero-top-graphic-line");
  paths.forEach((path) => {
    const length = path.getTotalLength();
    path.style.setProperty("--line-length", String(length));
  });

  window.requestAnimationFrame(() => {
    graphic.classList.add("is-animated");
  });
}

animateHeroGraphic();
