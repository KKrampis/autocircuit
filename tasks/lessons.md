# Lessons Learned

<!-- Record patterns and corrections here after each session. -->
<!-- Format: ## Date - Context / What went wrong / Rule to prevent it -->

## 2026-02-12 - CLAUDE.md caused over-exploration and double planning

**What went wrong:**
1. "Plan Mode Default" in CLAUDE.md conflicted with system-level plan mode, causing double planning loops
2. "Use subagents liberally" caused agent to explore `/home/tao/jason/circuit-tracer/` (external dependency) instead of staying in autocircuit/
3. No scope boundary meant agent spent excessive time reading files outside the repo

**Rule:**
- Do not add rules to CLAUDE.md that duplicate system-level capabilities (plan mode, subagent launching)
- Always define a scope boundary in CLAUDE.md so agents stay within the repo
- Subagent instructions should describe the workflow (researcher → creates skill), not just "use liberally"