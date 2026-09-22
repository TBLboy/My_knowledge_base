// Harness-level probe for @prevalentware/opencode-goal-plugin (no model calls).
// Drives the plugin's exported hooks directly to observe goal lifecycle behaviour.
process.env.OPENCODE_GOAL_STATE_PATH = "/tmp/oc-goal-test/goals-drive.json";

import { readFileSync, existsSync } from "node:fs";
import plugin from "/tmp/oc-goal-test/xdg/opencode/node_modules/@prevalentware/opencode-goal-plugin/dist/server.js";

const prompts = [];
const client = {
  app: { log: async () => {} },
  session: {
    promptAsync: async (args) => {
      prompts.push(args);
      return { data: {} };
    },
    messages: async () => ({ data: [] }),
    children: async () => ({ data: [] }),
  },
};

const hooks = await plugin.server({ client, directory: "/tmp/oc-goal-test/sandbox", worktree: "/tmp/oc-goal-test/sandbox" }, {
  auto_continue: true,
  min_continue_interval_seconds: 0,
  max_auto_turns: 5,
});

console.log("HOOK_KEYS", JSON.stringify(Object.keys(hooks)));
console.log("TOOL_NAMES", JSON.stringify(Object.keys(hooks.tool ?? {})));

const sessionID = "ses_probe_1";
const ctx = { sessionID, agent: "build" };

// --- 1. goal creation -------------------------------------------------
const created = await hooks.tool.set_goal.execute(
  { objective: "add a module docstring to app.py and verify it runs" },
  ctx,
);
console.log("CREATE_GOAL_RESULT", JSON.stringify(created).slice(0, 400));
console.log("STATE_FILE_EXISTS", existsSync(process.env.OPENCODE_GOAL_STATE_PATH));
const state = JSON.parse(readFileSync(process.env.OPENCODE_GOAL_STATE_PATH, "utf8"));
const stored = Object.values(state.goals ?? {})[0];
console.log("STORED_GOAL", JSON.stringify({
  status: stored?.status,
  objective: stored?.objective,
  budget: stored?.tokenBudget ?? stored?.token_budget ?? null,
}));

// --- 2. compaction survival -------------------------------------------
const compactionOutput = { context: [] };
await hooks["experimental.session.compacting"]({ sessionID }, compactionOutput);
console.log("COMPACTION_OUTPUT", JSON.stringify(compactionOutput).slice(0, 600));

// --- 3. idle auto-continuation ----------------------------------------
await hooks.event({ event: { type: "session.idle", properties: { sessionID } } });
await new Promise((resolve) => setTimeout(resolve, 1500));
console.log("PROMPTS_AFTER_IDLE", prompts.length);
console.log("PROMPT_TEXT", JSON.stringify(prompts.at(-1)?.body?.parts?.[0]?.text ?? null).slice(0, 300));

// --- 4. pause stops continuation --------------------------------------
await hooks.tool.update_goal_status.execute({ status: "paused" }, ctx);
const beforePause = prompts.length;
await hooks.event({ event: { type: "session.idle", properties: { sessionID } } });
await new Promise((resolve) => setTimeout(resolve, 1500));
console.log("PROMPTS_AFTER_PAUSED_IDLE", prompts.length, "delta", prompts.length - beforePause);

// --- 5. close with evidence, then idle again --------------------------
await hooks.tool.update_goal_status.execute({ status: "active" }, ctx);
try {
  const noEvidence = await hooks.tool.update_goal.execute({ status: "complete" }, ctx);
  console.log("CLOSE_WITHOUT_EVIDENCE_ACCEPTED", JSON.stringify(noEvidence).slice(0, 200));
} catch (error) {
  console.log("CLOSE_WITHOUT_EVIDENCE_REFUSED", String(error?.cause ?? error?.message ?? error).slice(0, 200));
}
const closed = await hooks.tool.update_goal.execute(
  { status: "complete", evidence: "ran python3 app.py; docstring present" },
  ctx,
);
console.log("CLOSE_WITH_EVIDENCE", JSON.stringify(closed).slice(0, 400));
const afterClose = prompts.length;
await hooks.event({ event: { type: "session.idle", properties: { sessionID } } });
await new Promise((resolve) => setTimeout(resolve, 1500));
console.log("PROMPTS_AFTER_CLOSED_IDLE", prompts.length, "delta", prompts.length - afterClose);
