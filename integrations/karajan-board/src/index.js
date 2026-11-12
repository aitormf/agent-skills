// kj-board-changes: the tasks of docs/changes/ as Karajan HUs (D-0048, D-0049).
// A thin adapter: the states come from board.py --json, nothing is stored or written here.
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { BoardRejectedError } from "@karajan-family/story-contract";

export const credentials = [];

const STATUS = { ready: "pending", blocked: "pending", doing: "running", done: "done" };
const DEFAULT_SCRIPT = "skills/task-done/scripts/board.py";

// Names of the changes whose README has `status: open`.
function openChanges(root) {
  let names;
  try {
    names = readdirSync(join(root, "docs/changes"), { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name);
  } catch {
    return [];
  }
  return names.sort().filter((name) => {
    try {
      return /^status:\s*open\s*$/m.test(readFileSync(join(root, "docs/changes", name, "README.md"), "utf8").split(/\r?\n---/)[0]);
    } catch {
      return false;
    }
  });
}

export function createManager({ config = {}, run, projectDir = process.cwd() } = {}) {
  const script = config.script ?? DEFAULT_SCRIPT;
  const notYet = (op) => async () => {
    throw new BoardRejectedError(`${op}: not yet`);
  };

  async function listChange(name) {
    // Arguments as an array, never a shell string: titles and names are data.
    const res = await run("python3", [script, "--json", `docs/changes/${name}`], { cwd: projectDir });
    if (res.exitCode !== 0) throw new BoardRejectedError((res.stderr || res.stdout || `board.py exited ${res.exitCode}`).trim());
    return JSON.parse(res.stdout).tasks.map((t) => ({
      short_id: `${name}/${t.id}`,
      title: t.title,
      status: STATUS[t.kind],
      claimed_by: null,
      ref: t.path,
      blocked_by: t.depends_on.map((d) => `${name}/${d}`),
    }));
  }

  return {
    capabilities: { acceptanceCriteria: "body", dependencies: "graph", assignee: false, verdicts: "pr", offline: true, tier: true },
    credentials,
    async list() {
      const hus = [];
      for (const name of openChanges(projectDir)) hus.push(...(await listChange(name)));
      return hus;
    },
    create: notYet("create"),
    move: notYet("move"),
    claim: notYet("claim"),
  };
}
