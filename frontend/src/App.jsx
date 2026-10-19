import { useState } from "react";

const money = (n) => "$" + n.toLocaleString(undefined, { maximumFractionDigits: 0 });
const SUGGESTIONS = ["Why did sales drop today?", "Is the payment failure rate higher than yesterday?", "Which metrics should I check first?"];
const delta = (a, b) => (b ? `${a >= b ? "+" : ""}${(((a - b) / b) * 100).toFixed(0)}% vs yesterday` : "");

function Card({ label, value, sub }) {
  return (
    <div className="card">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      <div className="sub">{sub}</div>
    </div>
  );
}

export default function App() {
  const [question, setQuestion] = useState("Why did sales drop today?");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze(q = question) {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);
      const d = await res.json();
      setData(d);
      setError(d.error || "");
    } catch (e) {
      setError(e.message + " — is the backend running on port 8000?");
    } finally {
      setLoading(false);
    }
  }

  const t = data?.metrics.today;
  const y = data?.metrics.yesterday;

  return (
    <main>
      <h1><span className="hl">Sales Drop Assistant</span> 📉</h1>
      <p className="hero">How can I help you today?</p>
      <p className="badge">Demo data · {data ? data.router : "Router: click Analyze to check"}</p>

      {!data && !loading && (
        <div className="suggest">
          {SUGGESTIONS.map((s) => (
            <button key={s} className="tile" onClick={() => { setQuestion(s); analyze(s); }}>
              <span className="label">Suggested question</span>
              {s}
            </button>
          ))}
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {data && (
        <>
          <p className="muted">Window: {data.metrics.window} ({y.date} vs {t.date})</p>
          <div className="cards">
            <Card label="Revenue" value={money(t.revenue)} sub={delta(t.revenue, y.revenue)} />
            <Card label="Successful orders" value={t.successful_orders} sub={delta(t.successful_orders, y.successful_orders)} />
            <Card label="Payment failure rate" value={t.failure_rate_pct + "%"} sub={`yesterday ${y.failure_rate_pct}%`} />
          </div>
        </>
      )}

      {loading && <div className="panel muted">The analyst agent is checking the data…</div>}
      {data?.answer && !loading && (
        <div className="panel">
          <h2>Answer</h2>
          <div className="answer">{data.answer}</div>
        </div>
      )}

      {data && (
        <details className="panel">
          <summary>Selected knowledge files ({Object.keys(data.files).length}) · {data.router}</summary>
          {Object.entries(data.files).map(([name, text]) => (
            <details key={name} className="file">
              <summary>{name}</summary>
              <pre>{text}</pre>
            </details>
          ))}
        </details>
      )}

      <div className="ask">
        <input value={question} placeholder="Ask about a sales drop…" onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && analyze()} />
        <button className="send" aria-label="Analyze" onClick={() => analyze()} disabled={loading || !question.trim()}>
          {loading ? "…" : "➤"}
        </button>
      </div>
    </main>
  );
}
