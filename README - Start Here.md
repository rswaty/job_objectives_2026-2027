# Start here

This is the **work vault** — one place for job objectives, projects, people, and weekly team notes. Code and large data stay in their own project directories on disk; link to them from here.

1. In Obsidian: **Open folder as vault** → this folder.
2. Enable community plugins: **Tasks**, **Dataview**, and **Git** (already listed in `.obsidian`).
3. Pin [[Dashboard/Home|Home]] and [[Dashboard/Objectives Dashboard|Objectives Dashboard]].

## Layout

| Folder | Use |
|--------|-----|
| `Dashboard/` | Home + rolling task views |
| `Objectives/FY2026-2027/` | Workday objectives and success criteria |
| `Projects/` | Active project notes (Northwoods, LANDFIRE, CDL, …) |
| `People/` | Contacts and relationship context |
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

- **Task line** = what you did / the work item. Use the Tasks plugin date (`✅ YYYY-MM-DD`) on the task only — that drives the weekly date window.
- **Accomplishment line** = high-level outcome for the team (what landed, for whom, why it matters). No dates on this line. Prefer one crisp sentence over process detail (“emailed X about Y”).
- Skip the accomplishment bullet until there is a real outcome to report.
- Tag when useful: `#Northwoods`, `#FSC`, `#publication`, `#R-package`.

A Cursor Automation drafts `Weekly/YYYY-MM-DD.md` each Tuesday at 8:00 from completed tasks and nested accomplishments. It should lift the accomplishment text (not restate the task). Completed work must be **committed and pushed** (Obsidian Git) before that run.

## Outside this vault

Project code stays horizontal on disk, for example:

- `~/Documents/northwoods_fna` — Fire Action Assessment code
- `~/Documents/map_rx_fires` — prescribed-fire footprint mapping
- `~/Documents/ecological_section_dash` — FSC ecological sections dashboard
- `~/Desktop/landfire_dev` — retiring; do not treat as source of truth

Link those paths or GitHub remotes from project notes; do not copy large data into the vault.
