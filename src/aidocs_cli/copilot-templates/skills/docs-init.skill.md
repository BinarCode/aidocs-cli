# Documentation Initialization Skill

Initialize documentation settings for the JobMatix-API project.

## What this skill does:

1. Analyzes the codebase structure
2. Asks for documentation preferences
3. Creates `docs/aidocs-config.yml` configuration
4. Sets up documentation templates

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/init/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

If the workflow file doesn't exist, perform these steps:

1. Analyze the project structure and tech stack
2. Ask the user for documentation preferences:
   - Documentation style (API, Architecture, User Guide, etc.)
   - Target audience (developers, users, etc.)
   - Output format preferences
3. Create `docs/aidocs-config.yml` with the configuration
4. Create necessary documentation templates
5. Provide next steps for using the documentation system

## Usage:

In Copilot CLI, simply mention "initialize documentation" or "setup docs" in your prompt.
