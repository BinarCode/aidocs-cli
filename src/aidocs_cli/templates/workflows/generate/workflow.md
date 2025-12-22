---
name: docs-generate
description: Generate documentation for a web page using Playwright MCP for browser automation and Claude vision for page comprehension.
---

# Documentation Generator Workflow

**Goal:** Generate comprehensive, user-focused documentation for a web page by navigating to it, capturing a screenshot, reading the codebase, and producing structured markdown.

**Your Role:** You are a documentation specialist. You will navigate to the page, understand what it does both visually and from the code, then generate clear documentation for end users.

---

## LOAD CONFIGURATION

**First, check if `docs/config.yml` exists in the project root.**

If it exists, load it and use these values as defaults:
- `project.name` → Use in documentation headers
- `style.tone` → Apply to writing style
- `stack.frontend.path` → Default codebase path
- `output.directory` → Default output directory
- `urls.base` → Can construct full URLs if only path provided
- `content.sections` → Which sections to include
- `content.exclude` → What to filter out
- `auth.method` → How to get credentials
- `auth.env_user` / `auth.env_pass` → Environment variable names if method is "env"

If no config exists, use sensible defaults and suggest running `/docs:init` first.

---

## LOAD CREDENTIALS

**If authentication is needed** (page requires login or `--auth` flag provided):

Check `auth.method` in config:

1. **method: "file"** → Read from `docs/.auth`:
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
2. `docs/.auth` file
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
- `output` (optional) - Base output directory (default from config or ./docs)
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

**Output is organized by module name:**

```
docs/
├── {module}/
│   ├── index.md          # Main page documentation
│   └── images/
│       ├── {module}.png  # Main screenshot
│       └── {module}-flow-step-1.png  # Flow screenshots
```

**Examples:**
- `/docs:generate /projects` → `docs/projects/index.md`
- `/docs:generate /users/settings` → `docs/users-settings/index.md`
- `/docs:generate campaigns` → `docs/campaigns/index.md`

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

## STEP 2: NAVIGATE TO URL

Use Playwright MCP to:
1. Launch browser (headless)
2. Navigate to the provided URL
3. Wait for page to load (networkidle)

**If authentication is provided (`--auth`):**
1. Check if current page is a login page (look for login form, password field)
2. If yes, parse credentials from `user:pass` format
3. Fill in the login form fields
4. Submit the form
5. Wait for navigation to complete
6. Navigate to the original URL if redirected away

**On navigation failure:** Report the error with suggestions:
- Check if URL is correct
- Check network connectivity
- Check if authentication is required

---

## STEP 3: CAPTURE AND ANALYZE PAGE

1. **Extract module name** from URL (e.g., `/projects` → `projects`)
2. **Capture full-page screenshot** using Playwright MCP
3. **Save screenshot to file:**
   - Create `docs/{module}/images/` directory if it doesn't exist
   - Save as `docs/{module}/images/{module}.png`
   - Store the relative path for markdown: `./images/{module}.png`
4. **Extract page title** from the browser
5. **Analyze the screenshot visually** - identify:
   - Page purpose and layout
   - Main sections (header, sidebar, main content, footer)
   - Interactive elements (buttons, forms, links, tables)
   - Data displays (metrics, cards, tables)
   - Navigation options

Output your visual analysis in a structured format:
```
Page Title: [extracted title]
Page Purpose: [what this page is for]
Main Sections: [list of identified sections]
Key UI Elements: [buttons, forms, important interactive elements]
Data Displayed: [tables, metrics, lists]
Navigation: [links to other pages]
Screenshot saved: [path to saved screenshot]
```

---

## STEP 4: ANALYZE CODEBASE (if available)

Search the codebase for code related to this page:

1. **Extract resource from URL** - e.g., `/campaigns` → "campaigns"
2. **Search for frontend components:**
   - Look for files matching the resource name (e.g., `Campaigns.vue`, `campaigns.tsx`, `CampaignsPage.jsx`)
   - Identify event handlers (onClick, onSubmit, onChange)
   - Find form validation logic
   - Identify API calls

3. **Search for backend routes:**
   - Look for route definitions matching the URL path
   - Find controllers/handlers for this resource
   - Extract validation rules
   - Identify side effects (emails, notifications, database changes)

**If codebase not found or no relevant code:**
Log: "No codebase analysis available - using visual analysis only"

**Merge findings:**
- Code behavior takes precedence over visual assumptions
- Note any conflicts between what's visible and what code shows

---

## STEP 5: GENERATE DOCUMENTATION

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
- Save as `docs/{module}/index.md` (e.g., `docs/projects/index.md`)
- Include project name from config in header if available

---

## STEP 6: DETECT INTERACTIVE OPPORTUNITIES

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

## STEP 7: INTERACTIVE FLOW DOCUMENTATION (if user chooses)

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

## STEP 8: SAVE AND REPORT

1. **Extract module name** from URL:
   - `/projects` → `projects`
   - `/users/settings` → `users-settings`
   - `https://app.com/campaigns` → `campaigns`

2. **Create module directory** `docs/{module}/` if it doesn't exist

3. **Create images subdirectory** `docs/{module}/images/` if it doesn't exist

4. **Save all screenshots**:
   - Main page: `docs/{module}/images/{module}.png`
   - Flow steps: `docs/{module}/images/{module}-flow-step-{n}.png`
   - Form states: `docs/{module}/images/{module}-form-{state}.png`

5. **Write markdown file** to `docs/{module}/index.md`

6. **Report completion:**

```
✅ Documentation generated successfully!

📄 File: docs/{module}/index.md
📁 Folder: docs/{module}/
🖼️  Screenshots: {count} images saved
   - docs/{module}/images/{module}.png
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
