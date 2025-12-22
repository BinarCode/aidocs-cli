/**
 * UI Highlight Utilities for Documentation Screenshots
 *
 * Use these functions with Playwright's browser_evaluate or browser_run_code
 * to highlight important UI elements before taking documentation screenshots.
 *
 * RECOMMENDED APPROACH: Spotlight/Overlay effect that darkens the page
 * except for the highlighted element.
 */

// ============================================================================
// RECOMMENDED: SPOTLIGHT/OVERLAY APPROACH
// ============================================================================

/**
 * Creates a spotlight effect that darkens the entire page except for
 * the target element. Uses a large box-shadow to create the dark overlay
 * with a "cutout" around the element.
 *
 * Usage with browser_run_code (RECOMMENDED):
 * ```js
 * async (page) => {
 *   // Clear existing highlights
 *   await page.evaluate(() => {
 *     document.querySelectorAll('[data-doc-highlight]').forEach(el => el.remove());
 *   });
 *
 *   // Get element by role/name
 *   const element = page.getByRole('button', { name: 'Submit' });
 *   const box = await element.boundingBox();
 *
 *   // Apply spotlight
 *   await page.evaluate((rect) => {
 *     const spotlight = document.createElement('div');
 *     spotlight.setAttribute('data-doc-highlight', 'true');
 *     spotlight.style.cssText = `
 *       position: fixed;
 *       left: ${rect.x - 8}px;
 *       top: ${rect.y - 8}px;
 *       width: ${rect.width + 16}px;
 *       height: ${rect.height + 16}px;
 *       border-radius: 8px;
 *       z-index: 999999;
 *       pointer-events: none;
 *       box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.6);
 *     `;
 *
 *     const glow = document.createElement('div');
 *     glow.setAttribute('data-doc-highlight', 'true');
 *     glow.style.cssText = `
 *       position: fixed;
 *       left: ${rect.x - 4}px;
 *       top: ${rect.y - 4}px;
 *       width: ${rect.width + 8}px;
 *       height: ${rect.height + 8}px;
 *       border-radius: 6px;
 *       border: 3px solid rgba(255, 255, 255, 0.9);
 *       z-index: 1000000;
 *       pointer-events: none;
 *       box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
 *     `;
 *
 *     document.body.appendChild(spotlight);
 *     document.body.appendChild(glow);
 *   }, box);
 *
 *   return 'Spotlight applied';
 * }
 * ```
 */


// ============================================================================
// COPY-PASTE TEMPLATES FOR PLAYWRIGHT MCP
// ============================================================================

/*
TEMPLATE 1: Spotlight on a single element (using browser_run_code)
------------------------------------------------------------------
async (page) => {
  // Clear existing highlights
  await page.evaluate(() => {
    document.querySelectorAll('[data-doc-highlight]').forEach(el => el.remove());
  });

  // Get element - use appropriate selector
  const element = page.getByRole('button', { name: 'YOUR_BUTTON_NAME' });
  // Or: page.getByRole('textbox', { name: 'Field Name' });
  // Or: page.locator('selector');

  const box = await element.boundingBox();
  if (!box) return 'Element not found';

  // Apply spotlight effect
  await page.evaluate((rect) => {
    const spotlight = document.createElement('div');
    spotlight.setAttribute('data-doc-highlight', 'true');
    spotlight.style.cssText = `
      position: fixed;
      left: ${rect.x - 8}px;
      top: ${rect.y - 8}px;
      width: ${rect.width + 16}px;
      height: ${rect.height + 16}px;
      border-radius: 8px;
      z-index: 999999;
      pointer-events: none;
      box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.6);
    `;

    const glow = document.createElement('div');
    glow.setAttribute('data-doc-highlight', 'true');
    glow.style.cssText = `
      position: fixed;
      left: ${rect.x - 4}px;
      top: ${rect.y - 4}px;
      width: ${rect.width + 8}px;
      height: ${rect.height + 8}px;
      border-radius: 6px;
      border: 3px solid rgba(255, 255, 255, 0.9);
      z-index: 1000000;
      pointer-events: none;
      box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
    `;

    document.body.appendChild(spotlight);
    document.body.appendChild(glow);
  }, box);

  return 'Done';
}


TEMPLATE 2: Clear all highlights
--------------------------------
() => {
  document.querySelectorAll('[data-doc-highlight]').forEach(el => el.remove());
  return 'Cleared';
}


TEMPLATE 3: Spotlight using browser_evaluate (simpler but limited)
------------------------------------------------------------------
() => {
  // Clear existing
  document.querySelectorAll('[data-doc-highlight]').forEach(el => el.remove());

  // Find element
  const element = document.querySelector('YOUR_SELECTOR');
  if (!element) return 'Element not found';

  const rect = element.getBoundingClientRect();

  // Spotlight
  const spotlight = document.createElement('div');
  spotlight.setAttribute('data-doc-highlight', 'true');
  spotlight.style.cssText = `
    position: fixed;
    left: ${rect.left - 8}px;
    top: ${rect.top - 8}px;
    width: ${rect.width + 16}px;
    height: ${rect.height + 16}px;
    border-radius: 8px;
    z-index: 999999;
    pointer-events: none;
    box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.6);
  `;

  // Glow border
  const glow = document.createElement('div');
  glow.setAttribute('data-doc-highlight', 'true');
  glow.style.cssText = `
    position: fixed;
    left: ${rect.left - 4}px;
    top: ${rect.top - 4}px;
    width: ${rect.width + 8}px;
    height: ${rect.height + 8}px;
    border-radius: 6px;
    border: 3px solid rgba(255, 255, 255, 0.9);
    z-index: 1000000;
    pointer-events: none;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
  `;

  document.body.appendChild(spotlight);
  document.body.appendChild(glow);

  return 'Done';
}

*/


// ============================================================================
// CUSTOMIZATION OPTIONS
// ============================================================================

/*
Overlay darkness levels:
- Light:    rgba(0, 0, 0, 0.3)
- Medium:   rgba(0, 0, 0, 0.5)  (recommended)
- Dark:     rgba(0, 0, 0, 0.75)

Glow border colors:
- White (default):  rgba(255, 255, 255, 0.9)
- Blue:             rgba(59, 130, 246, 0.9)
- Green:            rgba(34, 197, 94, 0.9)
- Red:              rgba(239, 68, 68, 0.9)

Padding around element:
- Tight:   4px
- Normal:  8px (recommended)
- Loose:   12px
*/
