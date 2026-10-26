---
name: agent-teams
description: Builds and runs a team of Claude subagents in which the current session (on whatever model is currently selected) is the orchestrator and spawns teammates that each get their own model (haiku, sonnet, opus). Use this skill whenever the user mentions a "team", "agent team", "subagents", "orchestrator", "multi-agent", "work in parallel", "several Claudes", "split the work across agents" or "a different model per agent", even if they don't say "skill" or "team" explicitly but a larger task should be split into parallel roles (research, implementation, review, tests, ...). Also applies to German phrasings such as "Bau mir ein Team", "Agent-Team", "Aufgaben aufteilen" or "mehrere Agents".
---

# Agent Teams

The current session is the **orchestrator**: it plans, delegates, collects and delivers the final result. Teammates are **subagents** that it starts with the `Agent` tool. The orchestrator always runs on the model currently selected in the session (the skill cannot change that). Each teammate, however, can be given its own model.

Invoking this skill counts as explicit permission to spawn subagents. Without that permission the orchestrator should not spawn any, because every subagent starts from zero and costs tokens.

Talk to the user in their language; write briefings to teammates in whatever language fits the task.

## Workflow

### 1. Clarify the goal and the team

Briefly settle what should exist at the end and how you will know it is done. Ask only when a wrong assumption would be expensive; otherwise make a reasonable assumption and state it.

Then design the team. Each member has:

| Field | Meaning |
|---|---|
| `name` | short role name, e.g. `research`, `build`, `review` |
| `model` | `haiku`, `sonnet` or `opus`. Omit it and the member inherits the orchestrator's model |
| `subagent_type` | e.g. `general-purpose` (everything), `Explore` (read/search only), `Plan` (designs, writes nothing) |
| `task` | one clearly bounded sub-goal with a result format |
| `depends_on` | members whose result must be available first |

If the user has already named roles and models ("research with haiku, review with opus"), use them exactly. Otherwise propose a line-up using this rule of thumb:

- **haiku**: fast, simple, well-bounded work (skimming files, collecting data, formatting, bulk tasks)
- **sonnet**: the default for implementation, research with analysis, tests, documentation
- **opus**: hard reasoning, architecture, tricky debugging, critical review

More members are not automatically better. Split only when the parts are truly independent or when a second, unbiased view (review) adds something. Two to five members are enough for almost any task.

Show the user the team plan as a short table (role, model, task) and then start right away, unless they asked to confirm first or the plan is expensive (many opus agents) and not clearly wanted. A reusable template is in `assets/team-template.md`, ready-made line-ups in `references/team-examples.md`.

### 2. Spawn the subagents

Call the `Agent` tool for each member:

- `description`: 3–5 words
- `prompt`: the complete brief (see Briefing below)
- `subagent_type`: as planned
- `model`: `"haiku"`, `"sonnet"` or `"opus"`, set only when the member should have a specific model
- `run_in_background`: background is the default. Set `false` only when the next step strictly depends on exactly this result and nothing else can run in parallel.

**Start all independent members in the same turn** so they run in parallel. Start dependent members only once their predecessors are done, and pass their results along in the prompt.

Parallel writers must not get in each other's way: give each its own files or directories, or use `isolation: "worktree"` in a git repository.

### 3. Write the briefing

A subagent has not seen the conversation. Write the prompt so that a smart stranger can start without asking questions:

- the overall goal in one or two sentences and the member's role in it
- the concrete task, its boundaries (what not to touch) and relevant paths, facts and decisions
- the expected result format and length (e.g. "max. 300 words, sources as links" or "write file X, report the path")
- whether it may change things or should only read
- a success criterion, so it knows when it is done

Two things that proved themselves in test runs:

- **Set the output path yourself.** A planner likes to suggest paths (even into unrelated folders such as the skill's own). Tell implementers the target folder explicitly in the prompt and that they may write only there.
- **Read the plan for contradictions before passing it on.** If a plan contains two rules that clash in edge cases (e.g. "never reuse IDs" and "new ID = max+1"), decide it yourself before implementers and testers build on it, and write the decision into their briefs.

### 4. Collect

Subagents' final reports arrive as notifications. A subagent's report is invisible to the user, so you summarize what matters. Never invent a result that has not arrived yet; if the user asks before then, say the agent is still running.

To have a member rework something, continue it with `SendMessage` (agent ID or name). That keeps its context; a new `Agent` call does not.

### 5. Merge and verify

You are responsible for the overall result, not the subagents:

- name and resolve contradictions between reports (check, don't guess)
- spot-check subagents' claims (open files, run code, recompute numbers), especially haiku work
- don't just pass on a reviewer's findings: fix medium and severe issues (yourself, or for larger changes via `SendMessage` to the implementer) and rerun the tests afterwards. A green test only proves what it checks, so read whether the tests really cover their promises.
- for important results, add a review member (preferably a stronger model) that did not do the work itself

At the end, deliver the result itself plus one or two sentences on who contributed what (role and model). No log of every step.

## Limits and pitfalls

- Before planning the team, check that you have the `Agent` tool. A session that is itself a subagent usually does not. In that case don't fake a team: tell the user plainly that subagents are not possible here, give the planned team (roles, models, order) as a proposal, and do the task yourself if that makes sense. The user should invoke the skill in the main session.
- Give researchers today's date and ask them to flag contradictory sources. The checker then reliably catches errors (e.g. wrong payback periods, unsupported deadlines) that would otherwise end up in the report.
- Only the user can change the orchestrator's model, by switching the session's model. If they want "orchestrator = opus", ask them to switch the session to opus.
- Model names: use only `haiku`, `sonnet`, `opus`. If the user names something else, map it to the closest tier and say so.
- Subagents generally cannot start their own subagents. The orchestrator builds nested teams flat itself.
- Team size and model choice drive the cost. Use `sonnet` as the default, `haiku` for simple bulk work, and expensive models only where they visibly pay off.
- If a subagent fails, read its error, fix the brief and restart or continue it, instead of blindly repeating the same request.
- If the user has their own team definition (file or text) that differs from this skill, theirs wins.
