import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: "systems-engineering-pages.spec.ts",
  outputDir: "/private/tmp/become-engineer-systems-playwright-results",
  fullyParallel: true,
  retries: 0,
  reporter: "line",
  use: {
    baseURL: "http://127.0.0.1:8008/become_engineer/",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "../../../../.venv/bin/mkdocs serve -f ../../../../mkdocs.yml -a 127.0.0.1:8008",
    url: "http://127.0.0.1:8008/become_engineer/learning-paths/systems-engineering/",
    reuseExistingServer: false,
    timeout: 120000,
  },
  projects: [
    {
      name: "desktop-light",
      use: { ...devices["Desktop Chrome"], colorScheme: "light" },
    },
    {
      name: "mobile-dark-reduced",
      use: {
        viewport: { width: 390, height: 844 },
        colorScheme: "dark",
        reducedMotion: "reduce",
      },
    },
    {
      name: "no-javascript",
      use: { ...devices["Desktop Chrome"], javaScriptEnabled: false },
    },
  ],
});
