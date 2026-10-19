## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.

## Host Architecture & Machine Roles (CRITICAL CONTEXT)

- **24/7 Production Host**: The trading engine runs 24/7 on a dedicated Windows machine (`seesharpwin1`) at Tailscale IP `100.105.70.120`. It runs all 4 desks (Stocks, Crypto, Futures, Forex) and the FastAPI webapp on port 8080.
- **Local Mac (`macbook-pro`)**: This Mac is a development/client machine, NOT the 24/7 server. The user can close the lid, shut down, or let the Mac sleep at any time without stopping the bot.
- **Remote Mobile Access**: The user views the dashboard and HUD widget from their phone over Tailscale at `http://100.105.70.120:8080/widget`.
- **Do NOT Run Duplicate Bot on Mac**: Never launch duplicate background autopilots (`./quant start`) on this Mac unless explicitly debugging, to prevent conflicting orders with the 24/7 Windows host.
