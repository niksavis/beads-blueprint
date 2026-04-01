---
applyTo: ".github/instructions/*.instructions.md"
description: "Use when creating, editing, or reviewing .instructions.md files, including applyTo scoping, description quality, and instruction discoverability."
---

# Instructions Authoring Guide

Apply these rules when creating or updating `.instructions.md` files.

## Purpose

- Keep instruction files clear, enforceable, and portable.
- Preserve usefulness while minimizing repository lock-in.
- Ensure instructions are discoverable and scoped correctly.

## Frontmatter Requirements

- `applyTo` must be as specific as practical.
- `description` must clearly state what the instruction enforces and when it applies.
- Use valid YAML frontmatter with `---` delimiters.

## Scope Design

- Prefer narrow `applyTo` patterns over global patterns.
- Use `**/*` only when the rule truly applies to all files.
- Keep one instruction focused on one concern.

## Portability Rules

- Prefer wording like "this repository" over project-specific branding unless the rule is truly brand-specific.
- Avoid machine-specific paths; use cross-platform examples where shell syntax differs.
- Prefer capability wording over implementation wording when practical.

## Content Quality Rules

- State MUST/SHOULD guidance explicitly when enforcement level matters.
- Include concrete examples for common mistakes and correct patterns.
- Avoid duplicating policy text already in always-on instructions; reference canonical policy instead.
- Keep instructions action-oriented and concise.

## Safety and Consistency

- Do not include secrets, credentials, tokens, or customer-identifying data.
- Keep commit and workflow guidance aligned with repository hooks and policies.
- When adding/removing/renaming customization artifacts, update discoverability indexes in the same change.

## Validation Checklist

- Confirm frontmatter parses correctly.
- Run diagnostics for changed files.
- Verify `applyTo` pattern matches intended files and avoids broad accidental scope.
- Verify discoverability docs include the new/changed instruction artifact.
