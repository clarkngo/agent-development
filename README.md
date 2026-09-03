# Agent Engineering

A collection of hands-on examples, experiments, and reference implementations for building LLM-powered agents — Google's Agent Development Kit (ADK), the Agent2Agent (A2A) protocol, the Model Context Protocol (MCP), and AWS Strands, mostly in Python with a couple of fullstack (React + agent backend) demos.

Live index at: https://clarkngo.github.io/agent-development/

## What's in it

- [`hos-google-adk/`](hos-google-adk/) — twelve step-by-step ADK walkthroughs, from a basic greeting agent up through multi-agent, stateful, callback-driven, sequential, parallel, and looping pipelines (`hos01` through `hos12`).
- [`hos-a2a/`](hos-a2a/) — Agent2Agent protocol experiments (`hos01` through `hos01-v3`).
- [`hos-adk-mcp/`](hos-adk-mcp/) — ADK agents wired up to MCP servers.
- [`strands-agent/`](strands-agent/) — AWS Strands Agents SDK hello-world.
- [`movie-app-ai-powered/`](movie-app-ai-powered/) — fullstack React + ADK movie app, with an A2A variant.
- [`references/`](references/) — vendored canonical samples from the ADK, A2A, and MCP ecosystems, used as reading material and copy-paste starting points (see [REFERENCES.md](REFERENCES.md) for the source links).
- [`projects/`](projects/) — coursework write-ups and slide decks.
- [`archive/`](archive/) — earlier/superseded experiments kept for reference.
- `index.html` / `styles.css` — the static site above, a browsable index over everything in this repo. No build step, no dependencies — it's plain HTML/CSS.

## Running the examples

Each `hosNN-*` example under `hos-google-adk/` is self-contained. General pattern:

```bash
# from the repo root — one virtual environment covers the Python examples
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# then, per example you want to run
cd hos-google-adk/hos01-greeting-agent
pip install -r requirements.txt
cp .env.example .env        # add your GOOGLE_API_KEY (https://aistudio.google.com/apikey)
adk web                     # or: adk run <agent_module>
```

The `hos-a2a/`, `hos-adk-mcp/`, and `strands-agent/` folders each have their own `requirements.txt` or `package.json` — check the folder for setup notes. `movie-app-ai-powered/` has its own README with a fullstack quickstart.

### Browsing the index locally

```bash
python3 -m http.server 8123
```

Then open http://localhost:8123.

## License

MIT — see [LICENSE](LICENSE).
