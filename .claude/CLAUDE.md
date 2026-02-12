# Claude Code Instructions for AutoCircuit

## Verification Workflow

This workflow is **not fixed** - adapt it as needed for each situation.

### Core Principles

- **Simplicity first** - Make every change as simple as possible. Impact minimal code.
- **No laziness** - Find root causes. No temporary fixes. Senior developer standards.
- **Minimal impact** - Changes should only touch what's necessary. Avoid introducing bugs.
- **Verify programmatically** - Verify information programmatically before writing it in SKILL.md, reference files, or code. This applies to:
  - Data structures (JSON schemas, field types, possible values)
  - API contracts (request/response formats)
  - Code behavior (what functions return, side effects)

### Approach

1. **Incremental exploration** - Write small code, run it, observe output, adapt
   ```bash
   # Start simple
   python3 -c "import json; d=json.load(open('file.json')); print(list(d.keys()))"

   # Then go deeper based on what you see
   python3 -c "import json; d=json.load(open('file.json')); print(type(d['nodes'][0]['layer']))"
   ```

2. **Document after verification** - Only write documentation after confirming each fact through code execution

3. **Ask when limited** - If you hit a limitation or need information that isn't available, stop and ask the user rather than guessing

4. **Plan Mode Default**
   - Enter plan mode for any non-trivial task (3+ steps or architectural decisions)
   - If something goes sideways, stop and re-plan immediately, don't keep pushing
   - Use plan mode for verification steps, not just building
   - Write detailed specs upfront to reduce ambiguity

5. **Subagent Strategy**
   - Use subagents liberally to keep main context window clean
   - Offload research, exploration, and parallel analysis to subagents
   - For complex problems, throw more compute at it via subagents
   - One task per subagent for focused execution

6. **Self-Improvement Loop**
   - After any correction from the user: update `tasks/lessons.md` with the pattern
   - Write rules for yourself that prevent the same mistake
   - Ruthlessly iterate on these lessons until mistake rate drops
   - Review lessons at session start for relevant project

7. **Verification Before Done**
   - Never mark a task complete without proving it works
   - Diff behavior between main and your changes when relevant
   - Ask yourself: "Would a staff engineer approve this?"
   - Run tests, check logs, demonstrate correctness

### When Writing Code

Separate code into logical modules instead of one big script:
- Put auxiliary functions in `utils/` or `api/` folders
- Main file imports from these modules
- This makes the main file easy to read and understand
- SKILL.md can then document the main file's purpose clearly

Example structure:
```
graph_analysis/
├── circuit_analysis.py      # Main entry - imports from utils/
├── utils/
│   ├── load_graph_data.py   # One function per file when simple
│   └── analyze_supernodes.py
└── api/
    └── subgraph_save_post.py
```

### Task Management

1. **Plan first** - Write plan to `tasks/todo.md` with checkable items
2. **Verify plan** - Review the plan before executing
3. **Track progress** - Check off items in `tasks/todo.md` as work completes
4. **Explain changes** - Document what was changed and why
5. **Document results** - Add a review section to `tasks/todo.md` summarizing outcomes
6. **Capture lessons** - Update `tasks/lessons.md` after corrections

### When You Hit a Limitation

Stop and ask the user when:
- A skill is insufficient for the task
- You need information that isn't available
- The current approach won't work
- You're unsure about a design decision

The user can help modify the approach or provide missing information. This prevents wasted effort from mistakes that compound in later steps.
