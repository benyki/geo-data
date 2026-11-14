# Agent instructions: geo-data

Claude Code loads `CLAUDE.md`, which only points here. Edit this file for rule
changes.

## Install the skill first

This repo ships its own agent skill in [`skills/geo-data/`](./skills/geo-data/):
what every file is, the licence of each, the join keys and traps, and where to
get data the repo does not hold. Agents only load skills from their usual skill
folder, so copy it there before working with this data:

```bash
mkdir -p ~/.agents/skills && rsync -a --delete skills/geo-data/ ~/.agents/skills/geo-data/
```

Then link it into each coding agent whose skills folder exists:

```bash
for d in ~/.claude/skills ~/.codex/skills ~/.cursor/skills; do [ -d "$d" ] && ln -sfn ~/.agents/skills/geo-data "$d/geo-data"; done
```

Run both from the repo root. Do it again after every `git pull` that changes
`skills/geo-data/`.

**The copy in `~/.agents/skills/geo-data/` is the one agents read; the copy in
this repo is the one that travels.** When you change the skill, edit it in
`~/.agents/skills/geo-data/`, copy it back, and commit:

```bash
rsync -a --delete ~/.agents/skills/geo-data/ skills/geo-data/
```

Keep the skill in step with the data: a commit that adds, removes or renames a
data file, or changes a licence, updates `skills/geo-data/` (the table in
`SKILL.md`, `references/files.md`) in the same commit.

## Rules for this repo

- **It is public.** Nothing private, no API keys, no data whose terms forbid
  redistribution.
- **Record provenance in the same commit.** Every new data file gets its
  source, retrieval date and licence in `PROVENANCE.md`.
- **Do not hand-edit generated files.** `world/admin1.*`, `world/admin2.*`,
  the enrichment columns of `world/countries.*`, and the French région,
  département and collectivité files come out of
  `uv run scripts/build_geo.py`. Change the script and rebuild.
- **Flags are images.** Use `flags/1x1/<cc>.png` in any UI, never a flag
  emoji. See `flags/README.md`.
- **Sync before and after.** `git pull --rebase origin main` before editing
  and again before `git push origin main`: other machines push here too.
