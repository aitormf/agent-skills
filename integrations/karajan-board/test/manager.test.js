import { test } from "node:test";
import assert from "node:assert/strict";
import { execFile, execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import { assertManager, BoardRejectedError } from "@karajan-family/story-contract";
import { createManager, credentials } from "../src/index.js";

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), "../../../skills/task-done/scripts/board.py");
const exec = promisify(execFile);
// Same shape as Karajan's run: (command, args, options) -> { exitCode, stdout, stderr }, no shell.
const run = async (cmd, args, options) => {
  try {
    const { stdout, stderr } = await exec(cmd, args, options);
    return { exitCode: 0, stdout, stderr };
  } catch (e) {
    return { exitCode: e.code, stdout: e.stdout ?? "", stderr: e.stderr ?? "" };
  }
};

const git = (dir, ...args) => execFileSync("git", ["-C", dir, "-c", "user.name=t", "-c", "user.email=t@t", ...args], { stdio: "pipe" });
const task = (n, { status = "todo", deps = "[]", title = `Tarea ${n}` } = {}) =>
  `---\nid: T${n}\ntitle: ${title}\nstatus: ${status}\ndepends_on: ${deps}\nexamples: [E1]\nverification: true\n---\nCuerpo\n`;

// changes: { "42-x": { readme: "open", tasks: { "T1-a": text } } }; committed on main.
function repo(changes = {}) {
  const dir = mkdtempSync(join(tmpdir(), "kjb-"));
  git(dir, "init", "-q", "-b", "main");
  for (const [name, { readme = "open", tasks = {} }] of Object.entries(changes)) {
    const base = join(dir, "docs/changes", name);
    mkdirSync(join(base, "tasks"), { recursive: true });
    writeFileSync(join(base, "README.md"), `---\nstatus: ${readme}\n---\n# ${name}\n`);
    for (const [file, text] of Object.entries(tasks)) writeFileSync(join(base, "tasks", `${file}.md`), text);
  }
  writeFileSync(join(dir, ".keep"), "");
  git(dir, "add", "-A");
  git(dir, "commit", "-q", "-m", "init");
  return dir;
}
const manager = (dir) => createManager({ config: { script: SCRIPT }, env: {}, run, projectDir: dir });
const statusOf = async (dir, id) => (await manager(dir).list()).find((h) => h.short_id === id)?.status;
const one = (t) => repo({ "42-cancelar-viaje": { tasks: { "T3-reembolso": t } } });

test("test_E1_hu_from_task_file", async () => {
  const dir = repo({ "42-cancelar-viaje": { tasks: { "T1-base": task(1), "T3-reembolso": task(3, { deps: "[T1]", title: "Reembolso" }) } } });
  const hu = (await manager(dir).list()).find((h) => h.short_id === "42-cancelar-viaje/T3");
  assert.equal(hu.title, "Reembolso");
  assert.equal(hu.ref, "docs/changes/42-cancelar-viaje/tasks/T3-reembolso.md");
  assert.equal(hu.claimed_by, null);
  assert.deepEqual(hu.blocked_by, ["42-cancelar-viaje/T1"]);
});

test("test_E1_title_with_shell_characters_is_data", async () => {
  const dir = one(task(3, { title: 'a $(touch pwned); `id` | x' }));
  assert.equal((await manager(dir).list())[0].title, 'a $(touch pwned); `id` | x');
});

test("test_E2_done_change_is_not_listed", async () => {
  const dir = repo({ "42-a": { readme: "done", tasks: { "T1-x": task(1) } }, "43-b": { tasks: { "T1-x": task(1) } } });
  assert.deepEqual((await manager(dir).list()).map((h) => h.short_id), ["43-b/T1"]);
});

test("test_E3_no_changes_folder", async () => {
  assert.deepEqual(await manager(repo()).list(), []);
});

test("test_E4_malformed_task_rejects_with_board_message", async () => {
  const dir = repo({ "42-a": { tasks: { "T1-x": task(1), "T2-y": "sin frontmatter\n" } } });
  await assert.rejects(manager(dir).list(), (e) => e instanceof BoardRejectedError && /board:/.test(e.message));
});

test("test_E5_ready_is_pending", async () => {
  assert.equal(await statusOf(one(task(3)), "42-cancelar-viaje/T3"), "pending");
});

test("test_E6_blocked_is_pending", async () => {
  const dir = repo({ "42-a": { tasks: { "T1-x": task(1), "T3-y": task(3, { deps: "[T1]" }) } } });
  assert.equal(await statusOf(dir, "42-a/T3"), "pending");
});

test("test_E7_branch_is_running", async () => {
  const dir = one(task(3));
  git(dir, "branch", "42-cancelar-viaje/T3");
  assert.equal(await statusOf(dir, "42-cancelar-viaje/T3"), "running");
});

test("test_E8_done_in_base_is_done", async () => {
  assert.equal(await statusOf(one(task(3, { status: "done" })), "42-cancelar-viaje/T3"), "done");
});

test("test_E9_done_only_in_task_branch_is_running", async () => {
  const dir = one(task(3));
  git(dir, "switch", "-q", "-c", "42-cancelar-viaje/T3");
  writeFileSync(join(dir, "docs/changes/42-cancelar-viaje/tasks/T3-reembolso.md"), task(3, { status: "done" }));
  git(dir, "commit", "-q", "-am", "done");
  assert.equal(await statusOf(dir, "42-cancelar-viaje/T3"), "running");
});

test("test_E10_never_failed_or_skipped", async () => {
  const dir = repo({ "42-a": { tasks: { "T1-x": task(1, { status: "done" }), "T2-y": task(2), "T3-z": task(3, { deps: "[T2]" }) } } });
  git(dir, "branch", "42-a/T2");
  const seen = (await manager(dir).list()).map((h) => h.status);
  assert.ok(seen.every((s) => ["pending", "running", "done"].includes(s)));
});

test("test_E26_conforms_to_the_contract", () => {
  const m = manager(repo());
  assertManager(m);
  assert.deepEqual(m.capabilities, { acceptanceCriteria: "body", dependencies: "graph", assignee: false, verdicts: "pr", offline: true, tier: true });
  assert.deepEqual(credentials, []);
});

test("test_not_yet_move_claim_create", async () => {
  const m = manager(repo());
  for (const call of [() => m.move("a/T1", "running"), () => m.claim("a/T1", "x"), () => m.create({ title: "t" })]) {
    await assert.rejects(call(), (e) => e instanceof BoardRejectedError && /not yet/.test(e.message));
  }
});
