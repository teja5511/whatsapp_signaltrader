import { test, expect } from "@playwright/test";

test.describe("Tauri Desktop Dashboard E2E Tests", () => {
  test("loads Overview page and verifies safety badges", async ({ page }) => {
    await page.goto("http://localhost:1420/");

    // Check title / topbar badges
    await expect(page.locator("text=DEMO ONLY (EXNESS MT5)")).toBeVisible();
    await expect(page.locator("text=REAL ACCOUNT BLOCKED")).toBeVisible();
  });

  test("verifies no token is present in browser localStorage", async ({ page }) => {
    await page.goto("http://localhost:1420/");
    const tokenInStorage = await page.evaluate(() => localStorage.getItem("LOCAL_API_TOKEN"));
    expect(tokenInStorage).toBeNull();
  });
});
