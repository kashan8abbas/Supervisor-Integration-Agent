"""
HTML/React frontend served by FastAPI. Uses CDN React + Babel to keep the demo
self-contained while providing a richer UI than plain HTML.
"""
from __future__ import annotations

from typing import List
from fastapi.responses import HTMLResponse

from .models import AgentMetadata


def render_home() -> HTMLResponse:
    """Return an HTML page with a small React app mounted at #root."""
    html = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Supervisor Agent Demo</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />
        <style>
          :root {
            --bg: #0f172a;
            --panel: #0b1220;
            --card: #111827;
            --accent: #22d3ee;
            --muted: #94a3b8;
            --text: #e2e8f0;
            --border: #1f2937;
            --success: #22c55e;
            --error: #ef4444;
          }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            background: radial-gradient(circle at 20% 20%, #1e293b, #0f172a 45%),
                        radial-gradient(circle at 80% 0%, #0ea5e9, #0f172a 35%),
                        var(--bg);
            color: var(--text);
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
          }
          .shell {
            max-width: 1100px;
            margin: 0 auto;
            padding: 48px 24px 80px;
          }
          .hero {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 28px;
          }
          .badge { display: inline-flex; gap: 8px; align-items: center; padding: 6px 10px; border-radius: 999px; background: rgba(34,211,238,0.1); color: var(--accent); font-weight: 600; font-size: 13px; border: 1px solid rgba(34,211,238,0.2); }
          .panel {
            background: rgba(11,18,32,0.9);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
          }
          textarea {
            width: 100%;
            min-height: 140px;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text);
            padding: 14px;
            resize: vertical;
            font-size: 15px;
          }
          .controls { display: flex; align-items: center; gap: 14px; margin-top: 12px; flex-wrap: wrap; }
          .checkbox { display: inline-flex; gap: 8px; align-items: center; color: var(--muted); font-size: 14px; }
          button.primary {
            background: linear-gradient(120deg, #22d3ee, #22c55e);
            color: #0b1220;
            border: none;
            padding: 12px 18px;
            font-weight: 700;
            border-radius: 12px;
            cursor: pointer;
            transition: transform 120ms ease, box-shadow 120ms ease;
          }
          button.primary:hover { transform: translateY(-1px); box-shadow: 0 10px 30px rgba(34,211,238,0.25); }
          button.primary:active { transform: translateY(0px); }
          .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-top: 12px; }
          .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            min-height: 150px;
          }
          .card h4 { margin: 0; font-size: 16px; color: #fff; }
          .card p { margin: 0; color: var(--muted); font-size: 14px; }
          .pill { display: inline-flex; padding: 4px 10px; border-radius: 999px; background: rgba(34,211,238,0.12); color: var(--text); font-size: 12px; border: 1px solid rgba(34,211,238,0.2); margin-right: 6px; margin-top: 4px; }
          .section-title { display: flex; align-items: center; gap: 8px; margin: 18px 0 8px; font-weight: 700; color: #fff; }
          .small { color: var(--muted); font-size: 14px; }
          .result-box {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px;
            white-space: pre-wrap;
            min-height: 60px;
          }
          .status { font-size: 14px; color: var(--muted); }
          .used { display: flex; flex-direction: column; gap: 8px; }
          .used-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; border-radius: 10px; background: var(--card); border: 1px solid var(--border); }
          .dot { width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
          .dot.success { background: var(--success); }
          .dot.error { background: var(--error); }
          .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; }
          footer { margin-top: 22px; color: var(--muted); font-size: 13px; text-align: center; }
        </style>
      </head>
      <body>
        <div class="shell">
          <div id="root"></div>
        </div>
        <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script type="text/babel">
          const { useState, useEffect } = React;

          const Pill = ({ text }) => <span className="pill">{text}</span>;

          const AgentCard = ({ agent }) => (
            <div className="card">
              <h4>{agent.name}</h4>
              <p>{agent.description}</p>
              <div>
                {agent.intents.map((intent) => <Pill key={intent} text={intent} />)}
              </div>
            </div>
          );

          const UsedAgent = ({ item }) => (
            <div className="used-item">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span className={`dot ${item.status === 'success' ? 'success' : 'error'}`}></span>
                <span>{item.name}</span>
              </div>
              <span className="mono">{item.intent}</span>
            </div>
          );

          const App = () => {
            const [query, setQuery] = useState('Summarize our project status and flag any deadline risks.');
            const [debug, setDebug] = useState(false);
            const [agents, setAgents] = useState([]);
            const [answer, setAnswer] = useState('');
            const [usedAgents, setUsedAgents] = useState([]);
            const [intermediate, setIntermediate] = useState({});
            const [status, setStatus] = useState('');
            const [error, setError] = useState(null);

            useEffect(() => {
              fetch('/agents').then((r) => r.json()).then(setAgents).catch(() => setAgents([]));
            }, []);

            const handleSubmit = async () => {
              if (!query.trim()) return;
              setStatus('Working...');
              setAnswer('');
              setUsedAgents([]);
              setIntermediate({});
              setError(null);
              try {
                const resp = await fetch('/query', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ query, user_id: null, options: { debug } })
                });
                const data = await resp.json();
                setStatus('');
                setAnswer(data.answer || '');
                setUsedAgents(data.used_agents || []);
                setIntermediate(data.intermediate_results || {});
                setError(data.error);
              } catch (err) {
                setStatus('');
                setError({ message: 'Network error', type: 'network_error' });
              }
            };

            return (
              <div className="panel">
                <div className="hero">
                  <div className="badge">Supervisor · Multi-Agent Orchestrator</div>
                  <div>
                    <h1 style={{ margin: '4px 0 6px' }}>Ask once. Let the supervisor plan the rest.</h1>
                    <p className="small">The LLM planner reads your request, selects the right worker agents, and merges their answers.</p>
                  </div>
                </div>

                <div>
                  <label className="section-title">Your request</label>
                  <textarea value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Type your question here..." />
                  <div className="controls">
                    <label className="checkbox">
                      <input type="checkbox" checked={debug} onChange={(e) => setDebug(e.target.checked)} /> Show debug
                    </label>
                    <button className="primary" onClick={handleSubmit}>Submit</button>
                    {status && <span className="status">{status}</span>}
                  </div>
                </div>

                <div style={{ marginTop: 18 }}>
                  <label className="section-title">Answer</label>
                  <div className="result-box">{answer || 'No answer yet.'}</div>
                  {error && <div className="small" style={{ color: '#f87171', marginTop: 8 }}>Error: {error.message}</div>}
                </div>

                <div style={{ marginTop: 18 }}>
                  <label className="section-title">Worker agents</label>
                  <p className="small">These are the available tools the planner can choose from.</p>
                  <div className="grid">
                    {agents.map((agent) => <AgentCard key={agent.name} agent={agent} />)}
                  </div>
                </div>

                {debug && (
                  <div style={{ marginTop: 18 }}>
                    <label className="section-title">Debug</label>
                    <div className="used">
                      {usedAgents.map((ua) => <UsedAgent key={`${ua.name}-${ua.intent}`} item={ua} />)}
                      {usedAgents.length === 0 && <span className="small">No agents called yet.</span>}
                    </div>
                    <div style={{ marginTop: 12 }}>
                      <div className="small">Intermediate results</div>
                      <pre className="mono" style={{ background: '#0d1524', padding: '10px', borderRadius: '10px', border: '1px solid var(--border)', overflowX: 'auto' }}>{JSON.stringify(intermediate, null, 2)}</pre>
                    </div>
                  </div>
                )}
                <footer>Powered by FastAPI · React · LLM planner · Worker registry</footer>
              </div>
            );
          };

          ReactDOM.createRoot(document.getElementById('root')).render(<App />);
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
