---
name: markdown-checklist
description: Verify Markdown structure and quality. Use when /markdown-checklist is invoked or when creating or modifying significant Markdown documentation.
---

# markdown-checklist

## Precondition

- `knowledge-vault/Intent/project_intent.md` exists.

If precondition is not met:

- **FAIL CLOSED**
- Ask the operator: "What are you trying to produce in this repo (software, book, research notes, something else), and what does 'done' look like for the first milestone?"
- Initiate the `establish-intent` skill.
- Do **not** continue with any other skill until intent is established.

## Steps

1. **Format**

   - Run `python3 tools/cvr/format_md.py`
   - If it fails, check `tools/check_tools.sh` and resolve dependencies.

2. **Verify Structure**

   - [ ] Fenced code blocks have language identifiers?
   - [ ] Blank lines surround code blocks?
   - [ ] Lists use consistent indentation (2 spaces)?
   - [ ] No mixed bullets (`-` vs `*`)?
   - [ ] No hard-coded file links (`file://`)? (Run `linters/lint_common.py` checks)

3. **Verify Links**

   - [ ] All internal links are repo-relative?
   - [ ] External links are valid (`https://`)?

4. **Commit**

   - Only commit after formatting passes cleanly.
