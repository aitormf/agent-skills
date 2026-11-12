# kj-board-changes

Board manager of [Karajan Code](https://github.com/manufosela/karajan-code): the tasks of `docs/changes/*/tasks/` (open changes) as HUs. It calls `skills/task-done/scripts/board.py --json` through the `run` Karajan passes, with an argument array and never a shell string, and writes nothing (D-0048, D-0049). Tests: `npm ci && npm test` (Node >= 22; `scripts/check.sh` runs them).

Today only `list()` works: `short_id` is `<change>/T<n>`, `ref` the task file, `blocked_by` the ids of `depends_on`; `ready | blocked` are `pending`, `doing` is `running`, `done` is `done`. `move`, `claim` and `create` reject with "not yet" (T4). Config key `script` overrides the path of `board.py` (default `skills/task-done/scripts/board.py`, from the project root).

## What Karajan does (read in its code, 2026-11)

- **Loading** (`src/hu/managers/index.js`, `loadCommunity`): the package named in `.karajan/board.yml` `managers.allow` (`{ name, version }`, exact version) is resolved with `createRequire(<projectDir>/package.json).resolve(name)`, so it must be installed in the project's `node_modules`; a path in the repo is not read. The installed `package.json` version must equal the listed one, or kj refuses. kj never installs. Q2 of the change is therefore answered with option a): from the repo, `npm install --no-save ./integrations/karajan-board` (a symlink, so the version is the one in this `package.json`), then `managers.allow: [{ name: kj-board-changes, version: 0.1.0 }]` and `backend: changes`.
- **Dependencies** (`src/hu/graph.js`): the field is `blocked_by`, a list of HU ids. The manager returns it in each HU.

## Not verified

- `@karajan-family/story-contract` is pinned to `1.0.0`, the only release on npm. The repo of Karajan has `1.1.0` with the optional `tier` capability, not published; with `1.0.0`, `runStoryContract` requires exactly the five capabilities, so T5 and T7 need `1.1.0` published.
