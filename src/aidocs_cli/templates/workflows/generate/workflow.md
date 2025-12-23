---
name: docs-generate
description: Generate documentation for a web page using Playwright MCP for browser automation and Claude vision for page comprehension.
---

# Documentation Generator Workflow

**Goal:** Generate comprehensive, user-focused documentation for a web page by first understanding the codebase, then navigating to capture screenshots with full context.

**Your Role:** You are a documentation specialist. You will FIRST analyze the codebase to understand what the page does, THEN navigate to capture screenshots knowing exactly what to look for.

**CRITICAL - CODEBASE BEFORE UI:**
Understanding the code FIRST ensures:
- You know what fields/forms exist (even hidden/conditional ones)
- You understand validation rules and can capture error states
- You know relationships to other modules
- Screenshots are comprehensive and accurate

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

Load the config and extract these values:
- `docs_root` → Base directory for all documentation (default: `docs`)
- `project.name` → Use in documentation headers
- `style.tone` → Apply to writing style
- `stack.frontend.path` → Default codebase path
- `urls.base` → Can construct full URLs if only path provided
- `content.sections` → Which sections to include
- `content.exclude` → What to filter out
- `auth.method` → How to get credentials
- `auth.env_user` / `auth.env_pass` → Environment variable names if method is "env"

### 0.3 If Config NOT Found

Display message and STOP:
```
⚠️  No aidocs-config.yml found.

This workflow requires a configuration file to run.

Would you like to create one now?
1. Yes - run /docs:init to set up configuration
2. No - I'll create docs/aidocs-config.yml manually
```

**If user chooses "Yes":** Execute the `/docs:init` workflow to walk through setup.
**If user chooses "No":** Stop and provide this minimal config template:

```yaml
# Minimal aidocs-config.yml
docs_root: docs
urls:
  base: "https://your-app.com"
auth:
  required: false
```

**IMPORTANT:** Do NOT proceed without config. Config is required.

### 0.4 Resolve Paths

Once config is loaded, set these path variables:
- `{docs_root}` → Use for all output paths (from config, default: `docs`)
- `{docs_root}/.auth` → Credentials file location
- `{docs_root}/{module}/` → Module documentation folder
- `{docs_root}/{module}/images/` → Screenshots folder

---

## LOAD CREDENTIALS

**If authentication is needed** (page requires login or `--auth` flag provided):

Check `auth.method` in config:

1. **method: "file"** → Read from `{docs_root}/.auth`:
   ```yaml
   username: "user@example.com"
   password: "secretpassword"
   ```

2. **method: "env"** → Read from environment variables:
   - Username from `$DOCS_AUTH_USER` (or custom var from config)
   - Password from `$DOCS_AUTH_PASS` (or custom var from config)

3. **method: "manual"** → Require `--auth` flag:
   - If not provided, prompt: "This page requires authentication. Use --auth user:pass"

4. **--auth flag always overrides** stored credentials

**Priority order:**
1. `--auth` flag (highest)
2. `{docs_root}/.auth` file
3. Environment variables
4. Prompt user (lowest)

---

## ARGUMENTS PARSING

Parse the arguments passed to this workflow. Expected format:
```
/docs:generate <url-or-module> [--auth user:pass] [--output ./docs] [--codebase ./src] [--skip-flows] [--flow "flow name"]
```

Extract:
- `url` (required) - The URL or module name to document (can be full URL, path, or module name)
- `auth` (optional) - Credentials in user:pass format for authenticated pages
- `output` (optional) - Base output directory (default from config `docs_root`)
- `codebase` (optional) - Path to codebase (default from config or .)
- `skip-flows` (optional) - Skip interactive flow detection, just capture page
- `flow` (optional) - Automatically document a specific flow (e.g., --flow "create campaign")

If URL is missing, ask the user: "Please provide the URL or module name to document."

**URL/Module Resolution:**
- If full URL provided: use as-is, extract module from path
- If path provided (e.g., `/campaigns`): combine with `urls.base` from config
- If module name provided (e.g., `projects`): search routes for matching URL
- If no base URL in config and path provided: ask for full URL

**Module Name Detection:**
If input looks like a module name (no `/` prefix, no `http`):
1. Search `routes/web.php` or `routes/api.php` for matching route
2. Search for controller with matching name (e.g., `ProjectsController`)
3. If found, construct URL from base URL + route path
4. If not found, ask user for the full URL

---

## OUTPUT STRUCTURE

**Output is organized by module name within `{docs_root}`:**

```
{docs_root}/
├── {module}/
│   ├── index.md          # Main page documentation
│   └── images/
│       ├── {module}.png  # Main screenshot
│       └── {module}-flow-step-1.png  # Flow screenshots
```

**Examples (assuming `docs_root: docs`):**
- `/docs:generate /projects` → `{docs_root}/projects/index.md`
- `/docs:generate /users/settings` → `{docs_root}/users-settings/index.md`
- `/docs:generate campaigns` → `{docs_root}/campaigns/index.md`

**Module name extraction:**
- From URL path: `/projects` → `projects`
- From URL path: `/users/settings` → `users-settings`
- From full URL: `https://app.com/campaigns` → `campaigns`
- From module name: `projects` → `projects`

---

## STEP 1: MCP PREREQUISITE CHECK

**CRITICAL:** Before proceeding, verify Playwright MCP is available.

Check if you have access to Playwright MCP tools by looking for these capabilities:
- `mcp__playwright__browser_navigate` or similar navigation tool
- `mcp__playwright__browser_screenshot` or similar screenshot tool

**If Playwright MCP is NOT available:**

Display this message and STOP:

```
⚠️  Playwright MCP Required

This workflow requires Playwright MCP for browser automation.

To install it, add this to your ~/.claude.json or project .mcp.json:

{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic/mcp-playwright"]
    }
  }
}

Then restart Claude Code and run this command again.

Alternatively, you can use the Playwright MCP from:
https://github.com/anthropics/mcp-playwright
```

**If Playwright MCP IS available:** Proceed to Step 2.

---

## STEP 2: AUTHENTICATE (if needed)

**IMPORTANT:** Before navigating to the target URL, check if authentication is required.

### 2.1 Load Credentials

Check for credentials in this priority order:

1. **`--auth` flag** (highest priority): Parse `user:pass` format
2. **`{docs_root}/.auth` file**: Read YAML credentials
3. **Environment variables**: Check `$DOCS_AUTH_USER` and `$DOCS_AUTH_PASS`

**Read `{docs_root}/.auth` if it exists:**

```yaml
# {docs_root}/.auth format:
username: "user@example.com"
password: "secretpassword"
login_url: "/login"  # optional, defaults to /login
```

### 2.2 Perform Login

If credentials are found (from any source):

1. Get base URL from config → `urls.base`
2. Navigate to login URL: `{base_url}/login` (or custom `login_url` from `.auth`)
3. Wait for login form to load
4. Fill username field (look for: `input[type="email"]`, `input[name="email"]`, `#email`, `input[name="username"]`)
5. Fill password field (look for: `input[type="password"]`, `input[name="password"]`, `#password`)
6. Click submit button (look for: `button[type="submit"]`, `input[type="submit"]`, button containing "Login"/"Sign in")
7. Wait for redirect/navigation to complete
8. Verify login succeeded (check for dashboard, user menu, or absence of login form)

```
🔐 Authenticating...
   Reading credentials from {docs_root}/.auth
   Navigating to: https://app.example.com/login
   Filling login form...
   ✓ Logged in successfully
```

**If login fails:**
```
⚠️ Authentication failed - check credentials in {docs_root}/.auth
   Continuing without authentication (page may show login screen)
```

---

## STEP 3: ANALYZE CODEBASE FIRST

**CRITICAL:** Before navigating to the UI, analyze the codebase to understand what you're documenting.

### 3.1 Why Codebase First?

Understanding the code BEFORE capturing screenshots ensures:
- You know what fields/forms exist (even hidden/conditional ones)
- You understand validation rules and error states to capture
- You know relationships between modules
- You can identify all UI states worth documenting
- Screenshots are more accurate and complete

### 3.2 Extract Resource from URL

From the URL/module name, identify what to search for:
- `/campaigns` → search for "campaigns", "Campaign"
- `/users/settings` → search for "users", "settings", "UserSettings"

### 3.3 Search for Backend Code

Look for route definitions and controllers:

```
🔍 Analyzing codebase for: campaigns

[1/4] Scanning routes...
   ✓ Found: GET /campaigns (index)
   ✓ Found: GET /campaigns/create (create form)
   ✓ Found: POST /campaigns (store)
   ✓ Found: GET /campaigns/{id} (show)
   ✓ Found: GET /campaigns/{id}/edit (edit form)
   ✓ Found: PUT /campaigns/{id} (update)
   ✓ Found: DELETE /campaigns/{id} (destroy)

[2/4] Scanning controllers...
   ✓ Found: CampaignController
   ✓ Methods: index, create, store, show, edit, update, destroy
```

### 3.4 Search for Frontend Components

Look for UI components matching the resource:

```
[3/4] Scanning frontend components...
   ✓ Found: resources/js/Pages/Campaigns/Index.vue
   ✓ Found: resources/js/Pages/Campaigns/Create.vue
   ✓ Found: resources/js/Pages/Campaigns/Edit.vue
   ✓ Found: resources/js/Pages/Campaigns/Show.vue
```

### 3.5 Extract Form Fields and Validation

From Request classes and frontend forms:

```
[4/4] Extracting form fields and validation...

Create form fields:
  • name (text, required, max:255)
  • description (textarea, nullable)
  • start_date (date, required, after:today)
  • end_date (date, nullable, after:start_date)
  • budget (number, required, min:0)
  • status (select: draft|active|paused)

Validation rules to capture:
  • name required error
  • start_date must be in future
  • end_date must be after start_date
```

### 3.6 Identify Relationships

Find related modules and navigation:

```
Relationships found:
  • Campaign belongsTo User (creator)
  • Campaign hasMany Orders
  • Campaign hasMany Analytics

Related pages to link:
  • /users (creator)
  • /orders (campaign orders)
```

### 3.7 Build Screenshot Plan

Based on code analysis, plan what to capture:

```
📸 Screenshot Plan (from code analysis):

1. List page (/campaigns)
   - Table with: name, status, budget, dates columns
   - Action buttons: Create, Edit, Delete

2. Create form (/campaigns/create)
   - 6 fields identified
   - Capture empty state

3. Validation states
   - Required field errors
   - Date validation errors

4. Edit form (/campaigns/{id}/edit)
   - Populated with data

5. Delete confirmation
   - Modal or confirmation dialog
```

**If codebase not found or no relevant code:**
Log: "No codebase analysis available - will analyze visually"

---

## STEP 4: NAVIGATE TO URL

Now navigate to the UI, knowing exactly what to look for from code analysis.

Use Playwright MCP to:
1. Launch browser (headless) - or reuse from auth step
2. Navigate to the provided URL
3. Wait for page to load (networkidle)

**On navigation failure:** Report the error with suggestions:
- Check if URL is correct
- Check network connectivity
- Check if authentication is required (suggest adding credentials to `{docs_root}/.auth`)

---

## STEP 5: CAPTURE AND ANALYZE PAGE (with Context)

Using the knowledge from Step 3, capture comprehensive screenshots:

### 5.1 Extract module name
From URL (e.g., `/projects` → `projects`)

### 5.2 Capture main screenshot
Using Playwright MCP:
- Create `{docs_root}/{module}/images/` directory if it doesn't exist
- Save as `{docs_root}/{module}/images/{module}.png`
- Store the relative path for markdown: `./images/{module}.png`

### 5.3 Analyze page with codebase context

Compare what you see against what the code told you:

```
📊 Page Analysis (visual + code):

Page Title: [extracted title]
Page Purpose: [what this page is for]

Expected from code    | Found in UI
----------------------|------------------
6 table columns       | ✓ All 6 visible
Create button         | ✓ Found top-right
Edit/Delete actions   | ✓ Found per row
Status filter         | ✓ Found in header

Main Sections: [list of identified sections]
Key UI Elements: [buttons, forms, important interactive elements]
Data Displayed: [tables, metrics, lists]
Navigation: [links to other pages]
Screenshot saved: [path to saved screenshot]
```

### 5.4 Capture additional states (from code analysis)

If code analysis identified important states:

```
📸 Capturing additional states from code analysis:

[1/3] Create form (empty)
   Navigating to /campaigns/create
   📸 Saved: campaigns-create.png

[2/3] Validation errors
   Submitting empty form
   📸 Saved: campaigns-validation.png

[3/3] Edit form (populated)
   Navigating to /campaigns/1/edit
   📸 Saved: campaigns-edit.png
```

**Merge findings:**
- Code behavior takes precedence over visual assumptions
- Note any conflicts between what's visible and what code shows

---

## STEP 6: GENERATE DOCUMENTATION (using Code + UI)

Create a markdown file with the following structure:

```markdown
# [Page Title]

![Page Screenshot](./images/{kebab-case-title}.png)

## Overview

[1-2 sentence description of what this page is for - generic, not runtime-specific]

## Features

- [What users can DO on this page]
- [List capabilities, not implementation details]

## Key Actions

### [Action Name]
[Description of what happens when user takes this action]

## Data Display

[If page has tables/lists, describe the columns/fields shown - without specific counts]

## Related Pages

- [Link to related page 1]
- [Link to related page 2]

---

*Documentation generated by docs:generate*
```

**Screenshot placement options** (based on config `content.screenshot_position`):
- `top` (default): Screenshot appears right after the H1 title
- `overview`: Screenshot appears within the Overview section
- `bottom`: Screenshot appears at the end before the footer
- `none`: No screenshot in markdown (still saved to images folder)

**Important guidelines:**
- Write for the audience specified in config (default: end users)
- Apply the tone from config:
  - **friendly**: "Click the big blue button to get started!"
  - **professional**: "Select the Submit button to proceed."
  - **technical**: "Invoke the submit handler via the primary CTA."
  - **minimal**: "Click Submit."
- Remove runtime data (counts, specific IDs, timestamps)
- Describe WHAT users can do, not HOW it's implemented
- Keep it concise and scannable
- Save as `{docs_root}/{module}/index.md` (e.g., `{docs_root}/projects/index.md`)
- Include project name from config in header if available

---

## STEP 7: DETECT INTERACTIVE OPPORTUNITIES

**Skip this step if:**
- `--skip-flows` flag was provided
- Running in batch mode (`/docs:batch`)
- Config has `content.interactive_flows: false`

**Auto-execute specific flow if:**
- `--flow "flow name"` was provided → Find matching action and execute it

After initial analysis, identify actionable elements on the page:

### 6.1 Detect Forms
Look for:
- `<form>` elements
- Input fields, textareas, selects
- Submit buttons

If forms found, note:
- Form purpose (login, create, edit, search, filter)
- Required fields
- Field types (text, email, date, select, etc.)

### 6.2 Detect Clickable Actions
Look for:
- Buttons that trigger actions (Create, Edit, Delete, Save)
- Links to related pages (View details, Edit item)
- Tabs or toggles that reveal content
- Modal triggers

### 6.3 Build Action Menu
Create a list of possible documentation enhancements:

```
📋 I detected these interactive elements on the page:

Forms:
  [F1] Create Campaign form (5 fields)
  [F2] Search/filter form (2 fields)

Actions:
  [A1] "Create Campaign" button → likely opens modal or navigates
  [A2] "Edit" links on each row → edit flow
  [A3] "Delete" buttons → deletion confirmation
  [A4] Status filter tabs → shows filtered results

Would you like me to document any of these flows?

Options:
  1. Fill form with sample data and document the submission flow
  2. Click an action and document what happens
  3. Document a complete user flow (e.g., "Create a new campaign")
  4. Skip - just save the current documentation

Enter choice (or type a custom flow to document):
```

---

## STEP 8: INTERACTIVE FLOW DOCUMENTATION (if user chooses)

### 7.1 Form Documentation Flow

If user selects a form:

1. **Ask for sample data** (or generate realistic fake data):
   ```
   I'll fill the "Create Campaign" form. What sample data should I use?

   - Campaign Name: [suggest: "Summer Sale 2024"]
   - Start Date: [suggest: tomorrow's date]
   - Budget: [suggest: "5000"]

   Press Enter to use suggestions, or type custom values.
   ```

2. **Fill the form** using Playwright:
   - Use `fill()` for text inputs
   - Use `selectOption()` for dropdowns
   - Use `check()` for checkboxes
   - Capture screenshot of filled form

3. **Document validation** (if any):
   - Try submitting with invalid data first
   - Capture validation error messages
   - Screenshot the error state

4. **Submit the form** (with user confirmation):
   ```
   ⚠️  Ready to submit the form. This may create real data.

   1. Submit and document the result
   2. Just document the filled form (don't submit)
   3. Cancel
   ```

5. **Capture the result**:
   - Screenshot after submission
   - Document success/error messages
   - Note any redirects

### 7.2 Action Flow Documentation

If user selects an action (button/link):

1. **Confirm the action**:
   ```
   I'll click "{action_name}" and document what happens.

   This might:
   - Open a modal
   - Navigate to a new page
   - Trigger an API call
   - Show a confirmation dialog

   Proceed? [Y/n]
   ```

2. **Perform the action** using Playwright:
   - Click the element
   - Wait for response (modal, navigation, or content change)
   - Capture screenshot of result

3. **Document the outcome**:
   - What changed on screen
   - Any new forms or inputs
   - Success/error states

4. **Chain actions** (optional):
   ```
   Action completed. The page now shows [description].

   Would you like to:
   1. Continue documenting this flow (e.g., fill the modal form)
   2. Go back and document another action
   3. Finish and save all documentation
   ```

### 7.3 Complete User Flow Documentation

If user requests a complete flow (e.g., "Create a new campaign"):

1. **Plan the flow**:
   ```
   To document "Create a new campaign", I'll:

   1. Click "Create Campaign" button
   2. Fill the form with sample data
   3. Submit the form
   4. Document the success state

   This will create {count} screenshots showing each step.

   Proceed? [Y/n]
   ```

2. **Execute step by step**:
   - Perform each action
   - Capture screenshot after each step
   - Note what changed

3. **Generate flow documentation**:
   Add a "How to" section to the markdown:

   ```markdown
   ## How to: Create a New Campaign

   ### Step 1: Open the form
   Click the "Create Campaign" button in the top right.

   ![Step 1](./images/campaigns-flow-step-1.png)

   ### Step 2: Fill in the details
   Enter the campaign information:
   - **Name**: Your campaign name
   - **Start Date**: When the campaign begins
   - **Budget**: Campaign budget in dollars

   ![Step 2](./images/campaigns-flow-step-2.png)

   ### Step 3: Submit
   Click "Save" to create the campaign.

   ![Step 3](./images/campaigns-flow-step-3.png)

   ### Result
   You'll see a success message and the new campaign in the list.

   ![Result](./images/campaigns-flow-result.png)
   ```

---

## STEP 9: SAVE AND REPORT

1. **Extract module name** from URL:
   - `/projects` → `projects`
   - `/users/settings` → `users-settings`
   - `https://app.com/campaigns` → `campaigns`

2. **Create module directory** `{docs_root}/{module}/` if it doesn't exist

3. **Create images subdirectory** `{docs_root}/{module}/images/` if it doesn't exist

4. **Save all screenshots**:
   - Main page: `{docs_root}/{module}/images/{module}.png`
   - Flow steps: `{docs_root}/{module}/images/{module}-flow-step-{n}.png`
   - Form states: `{docs_root}/{module}/images/{module}-form-{state}.png`

5. **Write markdown file** to `{docs_root}/{module}/index.md`

6. **Report completion:**

```
✅ Documentation generated successfully!

📄 File: {docs_root}/{module}/index.md
📁 Folder: {docs_root}/{module}/
🖼️  Screenshots: {count} images saved
   - {docs_root}/{module}/images/{module}.png
   {if flow documented}
   - {flow_name} flow ({step_count} steps)
   {/if}
📊 Sections: Overview, Features, Key Actions, [How to: ...], [Data Display], [Related Pages]

Review the generated documentation and edit as needed.
```

---

## ERROR HANDLING

| Error | Exit Action |
|-------|-------------|
| Invalid URL | Ask user to provide valid URL |
| Playwright MCP missing | Show installation instructions and stop |
| Navigation failed | Report error with suggestions |
| Auth failed | Report "Authentication failed - check credentials" |
| Screenshot failed | Continue with codebase-only analysis if possible |

---

## TIPS FOR USERS

After running `/docs:generate`, you can:
- Edit the generated markdown to add context
- Run on multiple pages to build a documentation set
- Use `--codebase` to point to your project for richer docs
