# Final Project Scaffold

This folder is intentionally close to empty. It exists so the final
project has an obvious home from week one, instead of structure getting
invented from scratch mid-semester.

**Working assumption — please confirm or replace before assigning:**
the final project asks each student (or team) to add one new feature
module to `app/` (their own design, subject to your approval) and then
write a complete pytest suite for it: unit tests using plain asserts, at
least one `yield` fixture with real teardown, a deliberate and justified
choice of fixture scope, at least one parametrized test, and a
`conftest.py` used correctly (not just because "that's where fixtures
go"). Grading then maps directly onto this lecture's Learning Objectives
slide, plus whatever later lectures (mocking, coverage, EP/BVA) add.

## Suggested structure once assigned

```
final_project/
  <student-or-team-name>/
    app/            their new feature module(s), same conventions as the top-level app/
    tests/          their suite, same layout convention as the top-level tests/
    README.md       what the feature does and why they made the design choices they made
```

Reusing the top-level `app/` and `tests/` conventions here means
students are applying a pattern they've already seen every week, not
learning a new project layout under deadline pressure.

## If the actual final project differs from this assumption

Replace the "Working assumption" section above, but keep the rest of
this file's intent: `final_project/` should always mirror the
conventions used in the weekly demos, so nothing here ever needs to be
reverse-engineered by students.
