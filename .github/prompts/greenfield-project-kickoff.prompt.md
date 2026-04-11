---
agent: "agent"
description: "Kick off a new greenfield project in this template: define scope, choose stack, scaffold initial app structure, and prepare first implementation plan"
---

Kick off a new greenfield project using this repository template.

Goals:

1. Confirm product goal, target users, and first milestone.
2. Confirm preferred tech stack (frontend, backend, database, deployment target).
3. Scaffold a minimal but production-minded project structure for the selected stack.
4. Keep repository automation Python-first and unchanged (`validate.py`, hooks, setup scripts).
5. Prepare next coding steps so work can continue immediately.

Workflow:

1. Ask for missing project constraints (stack, runtime, hosting, auth needs, and timeline).
2. Propose a minimal scaffold plan with 2-3 viable options when stack is undecided.
3. Implement the chosen scaffold in clearly separated app directories (for example `app/`, `services/`, or stack-appropriate equivalents).
4. Add/update project docs so the developer can run and iterate locally.
5. Run relevant validation for changed files.
6. Suggest the first three implementation tasks in priority order.

Rules:

- Do not replace or remove repository automation assets.
- Keep scaffold stack-agnostic until developer confirms a stack.
- Prefer minimal foundation over over-engineering.
- If prerequisites are missing, report exact install actions before scaffolding.
