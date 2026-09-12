import { test, expect } from "@playwright/test";

test.describe("CodeSupply End-to-End User Journeys", () => {
  test("Landing page loads with core branding and ecosystem tags", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/CodeSupply/i);

    // Verify header and branding
    await expect(page.locator("h1")).toContainText(/Map every dependency/i);
    await expect(page.getByText("CodeSupply").first()).toBeVisible();

    // Verify ecosystem badges are rendered
    await expect(page.getByText("Python", { exact: false }).first()).toBeVisible();
    await expect(page.getByText("Node.js", { exact: false }).first()).toBeVisible();
    await expect(page.getByText("Rust", { exact: false }).first()).toBeVisible();
    await expect(page.getByText("Go", { exact: false }).first()).toBeVisible();
    await expect(page.getByText("Maven", { exact: false }).first()).toBeVisible();
  });

  test("Navigation across Scan History, Compare, and Settings pages", async ({ page }) => {
    // Navigate to Scan History
    await page.goto("/scans");
    await expect(page.locator("h1")).toContainText(/Scan History/i);

    // Navigate to Compare Scans
    await page.goto("/scans/compare");
    await expect(page.locator("h1")).toContainText(/Scan Comparison/i);

    // Navigate to Settings
    await page.goto("/settings");
    await expect(page.locator("h1")).toContainText(/System Settings/i);
    await expect(page.getByText("Vulnerability Intelligence Data Sources")).toBeVisible();
    await expect(page.getByText("Secure File Handling Guardrails")).toBeVisible();
  });

  test("Instant demo scan initiates and navigates to scan workspace", async ({ page }) => {
    await page.goto("/");
    const demoBtn = page.getByRole("button", { name: /Scan Demo Project/i }).first();
    await expect(demoBtn).toBeVisible();
    await demoBtn.click();

    // Expect client-side navigation to /scan/[id]
    await expect(page).toHaveURL(/\/scan\/[a-zA-Z0-9_-]+/, { timeout: 15000 });
  });
});
