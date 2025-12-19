---
name: docs:discover
description: Incremental analysis of a specific module/entity to build knowledge graph
---

# Discover Module Structure

Analyze a specific module or entity to understand its routes, components, validation rules, and relationships. Works incrementally - one module at a time for large projects.

**Usage:**
```
/docs:discover <module>            # Required: specify which module
/docs:discover campaigns           # Analyze campaigns module
/docs:discover users --deep        # Deep analysis with relationships
/docs:discover orders --with-flows # Include flow detection
/docs:discover --list              # List detected modules (quick scan)
```

**Arguments:**
- `<module>` - Required module/entity name to analyze
- `--deep` - Include relationship analysis with other modules
- `--with-flows` - Detect and document user flows
- `--list` - Quick scan to list all detectable modules
- `--refresh` - Re-analyze and overwrite existing knowledge

**Knowledge Base Structure:**
```
.docs-knowledge/
├── _meta/
│   ├── project.json              # Project-level info
│   ├── stack.json                # Tech stack details
│   └── modules-index.json        # List of discovered modules
│
├── modules/
│   ├── {module-name}/            # e.g., campaigns/, users/, orders/
│   │   ├── entity.json           # Entity definition, fields, types
│   │   ├── routes.json           # Backend routes for this module
│   │   ├── components.json       # Frontend components
│   │   ├── validation.json       # Validation rules from code
│   │   ├── api-endpoints.json    # API endpoints with request/response
│   │   ├── flows/
│   │   │   ├── create.json       # Create flow steps
│   │   │   ├── edit.json         # Edit flow steps
│   │   │   ├── delete.json       # Delete flow steps
│   │   │   └── custom/           # Custom flows for this module
│   │   └── ui-states/
│   │       ├── list.json         # List page UI states
│   │       ├── form.json         # Form UI states & conditionals
│   │       └── detail.json       # Detail page UI states
│   │
│   └── {another-module}/
│       └── ...
│
├── relationships/
│   ├── {entity}-{entity}.json    # e.g., campaign-user.json
│   └── ...                       # Explicit relationship definitions
│
└── cross-module-flows/
    ├── {flow-name}.json          # e.g., checkout.json, onboarding.json
    └── ...                       # Flows spanning multiple modules
```

**What it analyzes:**

### Backend Analysis
- Models/Entities → fields, types, relationships, fillable/guarded
- Routes → endpoints, methods, middleware, controllers
- Controllers → actions, validation, business logic
- Validation → rules, custom validators, error messages
- Events/Listeners → side effects, notifications
- Policies → authorization rules

### Frontend Analysis
- Pages/Views → route mapping, layout, components used
- Components → props, events, slots, state
- Forms → fields, validation, conditional logic
- State Management → stores, actions, getters
- API Calls → endpoints used, request/response handling

### Relationship Discovery
- Database foreign keys
- Eloquent/ORM relationships
- Frontend data dependencies
- Cross-module navigation

---

**Execute workflow:** `@docs-workflows/discover/workflow.md`
