---
name: docs-batch
description: Generate documentation for multiple pages from a list of URLs or a sitemap file.
---

# Batch Documentation Generator

**Goal:** Generate documentation for multiple pages in a single run, either from a list of URLs or by discovering routes from the codebase.

**Your Role:** You orchestrate multiple documentation generation runs, tracking progress and summarizing results.

---

## STEP 0: FIND AND LOAD CONFIGURATION

**CRITICAL:** Before doing anything else, locate and load the configuration file.

### 0.1 Search for Config File

Search for `aidocs-config.yml` in this order:
1. `docs/aidocs-config.yml` (default location)
2. `./aidocs-config.yml` (project root)

**Also check for old config format:**
If `docs/config.yml` exists but `aidocs-config.yml` doesn't:
```
⚠️  Found old config format: docs/config.yml

Please rename it to: docs/aidocs-config.yml
Then run this command again.
```

### 0.2 If Config Found

Load the config and extract:
- `docs_root` → Base directory for all documentation (default: `docs`)
- `urls.base` → Base URL for page navigation
- `auth.method` → How to authenticate
- `skip_pages` → Patterns to exclude from batch

### 0.3 If Config NOT Found

Display message and STOP:
```
⚠️  No aidocs-config.yml found.

This workflow requires a configuration file to run.

Would you like to create one now?
1. Yes - run /docs:init to set up configuration
2. No - I'll create docs/aidocs-config.yml manually
```

**IMPORTANT:** Do NOT proceed without config. Config is required.

---

## ARGUMENTS PARSING

Parse the arguments. Expected formats:
```
/docs:batch <urls-file> [--auth user:pass] [--output ./{docs_root}]
/docs:batch --discover [--base-url https://app.example.com] [--auth user:pass] [--output ./{docs_root}]
```

**Option 1: URLs file**
- File containing one URL per line
- Or comma-separated URLs in the argument

**Option 2: --discover mode**
- Scans codebase for routes
- Requires `--base-url` to construct full URLs

---

## STEP 1: MCP PREREQUISITE CHECK

Same as `/docs:generate` - verify Playwright MCP is available.

If not available, show installation instructions and stop.

---

## STEP 2: BUILD URL LIST

### From URLs file:
1. Read the file
2. Parse each line as a URL
3. Skip empty lines and comments (lines starting with #)
4. Validate each URL format

### From --discover mode:
1. Search codebase for route definitions:
   - Laravel: `routes/web.php`, `routes/api.php`
   - Next.js: `pages/**/*.tsx`, `app/**/page.tsx`
   - Nuxt: `pages/**/*.vue`
   - Express: `router.get/post/etc`

2. Extract route paths
3. Combine with `--base-url` to form full URLs
4. Filter out:
   - API-only routes (unless specifically requested)
   - Auth routes (login, logout, register)
   - Health check / status routes

Present the discovered URLs to user:
```
Found {count} pages to document:

1. https://app.example.com/dashboard
2. https://app.example.com/campaigns
3. https://app.example.com/users
...

Proceed with all? [Y/n] Or type numbers to select specific pages.
```

---

## STEP 3: AUTHENTICATE (if needed)

**Load credentials using same logic as /docs:generate:**

Check `auth.method` in config (loaded in Step 0):
1. **method: "file"** → Read from `{docs_root}/.auth`
2. **method: "env"** → Read from environment variables
3. **method: "manual"** → Require `--auth` flag
4. **--auth flag** always overrides stored credentials

If authentication is available:
1. Navigate to login page (from config `urls.login` or auto-detect)
2. Perform authentication once
3. Session will persist for all subsequent pages in batch

If auth required but no credentials available:
```
⚠️ Authentication required but no credentials found.

Options:
1. Run /docs:init to configure credentials
2. Pass --auth user:pass flag
3. Set DOCS_AUTH_USER and DOCS_AUTH_PASS environment variables
```

---

## STEP 4: PROCESS EACH PAGE

For each URL in the list:

1. **Show progress:**
   ```
   [2/15] Documenting: https://app.example.com/campaigns
   ```

2. **Execute single-page workflow:**
   - Navigate to URL
   - Capture screenshot
   - Analyze visually
   - Search codebase for related code
   - Generate markdown

3. **Track results:**
   - Success: file path created
   - Warning: partial success (e.g., no code found)
   - Error: failed (with reason)

4. **Continue to next page** (don't stop on single failures)

---

## STEP 5: GENERATE SUMMARY

After all pages processed, create summary:

### Console Output:
```
✅ Batch documentation complete!

📊 Results:
   ✓ {success_count} pages documented successfully
   ⚠ {warning_count} pages with warnings
   ✗ {error_count} pages failed

📁 Output directory: {docs_root}/

📄 Files created:
   - dashboard.md
   - campaigns.md
   - users.md
   ...

⚠️ Warnings:
   - campaigns.md: No backend code found

❌ Errors:
   - https://app.example.com/admin: 403 Forbidden

⏱️ Total time: {elapsed}
```

### Index File:
Create `{docs_root}/index.md` with links to all generated docs:

```markdown
# Documentation Index

Generated on {date}

## Pages

- [Dashboard](./dashboard.md)
- [Campaigns](./campaigns.md)
- [Users](./users.md)

## Statistics

- Total pages: {count}
- Successfully documented: {success_count}
- Warnings: {warning_count}
- Failed: {error_count}

---

*Generated by docs:batch*
```

---

## ERROR HANDLING

| Error | Behavior |
|-------|----------|
| Single page fails | Log error, continue to next |
| Auth fails | Stop batch (can't proceed) |
| All pages fail | Report and suggest troubleshooting |
| MCP missing | Stop before starting |

---

## TIPS

- Start with a small batch to verify setup
- Review generated docs before running full batch
- Use `--discover` to find all documentable pages
- Auth session persists across all pages in batch
