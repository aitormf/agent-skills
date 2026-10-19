---
name: idea-to-spec
description: Turns a vague or half-defined idea into a spec (problem, users, user stories, requirements, edge cases and acceptance criteria) through a round-based interview. Use it when asked to write a spec, define a feature, clarify requirements or go from an idea to something implementable.
---

# From idea to spec

Help the person turn an idea into a spec ready for planning. You lead the conversation; **the person gives the answers**.

## Artifacts and status

- Each work item lives in `docs/specs/<YYYYMMDD>-<type>-<name>/`. The type follows Conventional Commits (`feat`, `fix`, `refactor`, `docs`…) and the name is kebab-case. If that directory already exists, append `-2`.
- `spec.md` and `plan.md` carry `status: draft | approved | obsolete` in their frontmatter. Only a person sets `approved`.
- If you modify an approved artifact, set it back to `draft` and say so.
- Work management (priority, owner, done) is not this skill's job: it lives in the tracker. If there is an issue, its ID goes in `issue:`.

## Behaviour

- Start by summarizing the idea in a short paragraph.
- Identify what is missing to write a good spec and ask the **minimum number of useful questions**, blocking ones first.
- Focus on the what and the why, not the how: no frameworks or architecture unless the person asks for them. That belongs to `spec-to-plan`.
- If `docs/ARCHITECTURE.md` exists, read it to use the glossary's vocabulary and to spot clashes with the principles.

## Questions by round

1. Problem and expected outcome.
2. Users and actors.
3. User stories (what each one needs and why).
4. Scope and out of scope.
5. Behaviour and edge cases: empty, invalid or massive data; external dependency failures; concurrent actions.
6. Non-functional constraints.
7. Security, if it touches data, authentication or external input: data sensitivity, who can do what, which inputs are untrusted and which negative tests are needed.
8. Acceptance criteria ("Given…, when…, then…").

If something is still ambiguous after a round, ask only about that part.

## Open questions

**Never silently assume an answer.** For each unresolved question:

> **[Question]**
> - A) [Your default proposal, if any]
> - B) [Obvious alternative]
> - C) Leave it as an open question in the spec
> - D) Another answer

It is resolved only when the person answers or chooses to leave it open.

Format of each reply: `What I understand` · `Open questions` · `Next step`.

## Size

Match the depth to the change. Propose the path and let the person decide:

| Change | Artifacts |
|---|---|
| One-line bug | None, or only `tasks.md` |
| Complex bug | `spec.md` + `tasks.md` |
| Small feature | `spec.md` + `plan.md` + `tasks.md` |
| Production feature or architectural refactor | Everything, with spec and plan review |

## When to stop

Stop when there is enough for: goal, problem, users, user stories, scope and out of scope, functional and non-functional requirements, edge cases and acceptance criteria.

Then:

1. Propose the directory name and draft `spec.md` from `assets/spec-template.md`, with `status: draft`. Delete the optional sections that do not apply.
2. Show the draft and write it only once the person approves.
3. Suggested next step: review it with `review-spec`. If it is small and the person is happy with it, they can mark it `approved` and move on to `spec-to-plan`.
