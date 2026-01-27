# Claude Code Instructions for AutoCircuit

## Verification Workflow

This workflow is **not fixed** - adapt it as needed for each situation.

### Core Principle

Verify information programmatically before writing it in SKILL.md, reference files, or code. This applies to:
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

### When You Hit a Limitation

Stop and ask the user when:
- A skill is insufficient for the task
- You need information that isn't available
- The current approach won't work
- You're unsure about a design decision

The user can help modify the approach or provide missing information. This prevents wasted effort from mistakes that compound in later steps.
