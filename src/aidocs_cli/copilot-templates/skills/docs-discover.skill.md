# Documentation Discovery Skill

Scan and discover all modules and structure in the JobMatix-API codebase.

## What this skill does:

1. Scans backend for models, controllers, routes
2. Scans frontend for pages, components
3. Identifies relationships between modules
4. Saves analysis to `docs/.knowledge/` directory

## Instructions:

Load and execute the workflow from: `.copilot/workflows/docs/discover/workflow.md` in the project repository.

Follow the workflow instructions exactly as specified in that file.

## Usage Patterns:

The user might say:
- "discover all modules"
- "scan the codebase"
- "map out the application structure"
- "analyze the project structure"

## Output Structure:

Creates the following in `docs/.knowledge/`:
```
docs/.knowledge/
├── _meta/
│   ├── project.json
│   └── modules-index.json
└── modules/
    ├── {module-name}/
    │   ├── entity.json
    │   ├── routes.json
    │   ├── components.json
    │   └── flows/
```

## Next Steps:

After discovery, suggest running:
- `/docs:plan` to create documentation plan
- `/docs:generate` to generate docs for specific modules
