const path = require("path");
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: "visual-qa.spec.js",
  timeout: 60_000,
  workers: 1,
  reporter: "line",
  outputDir: path.join("/tmp", "ninad-phase-b-playwright-results"),
  use: {
    baseURL: "http://127.0.0.1:8765",
    browserName: "chromium",
    channel: "chrome",
    colorScheme: "light",
  },
  projects: [
    {
      name: "desktop",
      use: {
        viewport: { width: 1440, height: 1200 },
      },
    },
    {
      name: "mobile",
      use: {
        browserName: "chromium",
        channel: "chrome",
        viewport: { width: 390, height: 844 },
        userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
      },
    },
  ],
});
