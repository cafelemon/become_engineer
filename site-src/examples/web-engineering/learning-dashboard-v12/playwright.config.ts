import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  outputDir: "/private/tmp/become-engineer-playwright-results",
  fullyParallel: true,
  retries: 0,
  reporter: "line",
  use: { baseURL: "http://127.0.0.1:8008/become_engineer/", trace: "retain-on-failure" },
  webServer: [
    {
      command: "../../../../.venv/bin/mkdocs serve -f ../../../../mkdocs.yml -a 127.0.0.1:8008",
      url: "http://127.0.0.1:8008/become_engineer/learning-paths/web-fullstack/web-engineering/",
      reuseExistingServer: false,
      timeout: 120000
    },
    {
      command: "../../../../.venv/bin/uvicorn e2e_app:app --host 127.0.0.1 --port 8792",
      url: "http://127.0.0.1:8792/",
      reuseExistingServer: false,
      timeout: 120000,
      env: { WEB_ENGINEERING_DATABASE_URL: "postgresql+psycopg://dashboard:dashboard@127.0.0.1:55439/dashboard" }
    }
  ],
  projects: [
    { name: "desktop-light", use: { ...devices["Desktop Chrome"], colorScheme: "light" } },
    { name: "mobile-dark-reduced", use: { viewport: { width: 390, height: 844 }, colorScheme: "dark", reducedMotion: "reduce" } },
    { name: "no-javascript", use: { ...devices["Desktop Chrome"], javaScriptEnabled: false } }
  ]
});
