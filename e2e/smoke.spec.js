import { test, expect } from '@playwright/test';

test.describe('Public app smoke', () => {
  test('home page loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/UNTOLD/i);
  });

  test('studio login route is reachable', async ({ page }) => {
    await page.goto('/studio/login');
    await expect(page.getByRole('heading', { name: /welcome back/i })).toBeVisible();
  });
});
