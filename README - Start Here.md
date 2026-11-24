# Start here

This is the **work vault** — one place for job objectives, projects, and weekly team notes. Code and large data stay in their own project directories on disk; link to them from here.

1. In Obsidian: **Open folder as vault** → this folder.
2. Enable community plugins: **Tasks**, **Dataview**, **Git**, and **Templater** (already listed in `.obsidian`). Reload plugins if Templater is new.
3. Pin [[Dashboard/Home|Home]] and [[Dashboard/Objectives Dashboard|Objectives Dashboard]].

## Layout

| Folder | Use |
|--------|-----|
| `Dashboard/` | Home + rolling task views |
| `Objectives/FY2026-2027/` | Workday objectives and success criteria |
| `Projects/` | Active project notes (Northwoods) |
| `Areas/` | Ongoing roles that are not a single project |
| `Weekly/` | Tuesday team-achievements notes (paste into email) |
| `Archive/` | Source drafts and retired material |

Keep nesting shallow. Prefer `[[wikilinks]]` over deep folders.

## Tasks and accomplishments

Put tasks where the work lives (objective or project note). Nest **accomplishments** under the task so weekly reporting stays organized:

```markdown
- [x] Make review dashboard and share with Melanie ✅ 2026-11-18
  - Accomplishment: Shared prescribed-fire review dashboard with region science partners
- [ ] complete assessment by self if not by CDL
```

**You write the accomplishment** when you check the task — that is the quality bar for the Tuesday email.

- **Task line** = the work item. Use the Tasks plugin date (`✅ YYYY-MM-DD`) on the task only — that drives the weekly date window.
- **Accomplishment line** = high-level outcome for the team. No dates on this line.
- **Do not invent outcomes.** Asking or emailing is not the same as securing a lead, confirming next steps, or opening a pathway. Only claim what actually happened. If nothing stronger than the task is true yet, omit the accomplishment line.
- Tag when useful: `#Northwoods`, `#FSC`, `#publication`, `#R-package`.

A GitHub Action drafts `Weekly/YYYY-MM-DD.md` each Tuesday morning from completed tasks and nested accomplishments, then emails that note to rswaty@tnc.org. Prefer your accomplishment text when present; otherwise stay faithful to the task — never inflate. Completed work must be **committed and pushed** (Obsidian Git) before that run.

## Code and data

Keep implementation repos and large data on disk or GitHub; link them from project notes. Do not copy large outputs into this vault.
