# Quickstart
1) Start the backend API server

Open a new terminal
```bash
cd movie-agent-server

# create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the API server used by the client. This repository uses the ADK dev server command during development:
adk api_server --port 9000 --allow_origins="*"
# (Or run your backend entrypoint / framework runner that binds to port 9000.)
```

2) Start the frontend dev server

Open a new terminal
```bash
cd movie-client
npm install    # first time only
npm run dev
```