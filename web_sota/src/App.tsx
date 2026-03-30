import { useCallback, useState } from "react";

function HeroStickFigures() {
  return (
    <svg
      className="hero__art"
      viewBox="0 0 220 130"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <title>Decorative stick figures</title>
      {/* Ground */}
      <path
        d="M8 118c40-8 85-6 130 2 28 5 55 12 74 8"
        stroke="rgba(244,239,228,0.35)"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      {/* Left figure — waving at API */}
      <circle cx="42" cy="38" r="11" stroke="#f4efe4" strokeWidth="2.5" />
      <path d="M42 49v32M42 81l-14 22M42 81l16 20" stroke="#f4efe4" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M42 58l-18-10M42 58l20-6" stroke="#f4efe4" strokeWidth="2.5" strokeLinecap="round" />
      {/* Tiny server doodle */}
      <rect x="68" y="72" width="38" height="44" rx="4" stroke="#8ec5ff" strokeWidth="2" fill="rgba(100,160,255,0.08)" />
      <path d="M76 82h24M76 92h24M76 102h18" stroke="#8ec5ff" strokeWidth="1.8" strokeLinecap="round" opacity="0.85" />
      <text x="74" y="68" fill="#f4efe4" fontSize="11" fontFamily="Comic Neue, Segoe UI, sans-serif" fontStyle="italic">
        JSON
      </text>
      {/* Right figure — skeptical */}
      <circle cx="168" cy="44" r="11" stroke="#f4efe4" strokeWidth="2.5" />
      <path d="M168 55v30M168 85l-12 18M168 85l14 18" stroke="#f4efe4" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M168 64l16 4M168 64l-14 8" stroke="#f4efe4" strokeWidth="2.5" strokeLinecap="round" />
      {/* Speech bubble */}
      <path
        d="M118 18h78a6 6 0 016 6v22a6 6 0 01-6 6h-44l-10 12-2-12h-22a6 6 0 01-6-6V24a6 6 0 016-6z"
        fill="var(--hero-paper)"
        stroke="var(--hero-ink)"
        strokeWidth="2"
      />
      <text x="128" y="38" fill="var(--hero-ink)" fontSize="11.5" fontFamily="Comic Neue, Segoe UI, sans-serif">
        MCP, explain this
      </text>
      {/* Stars — whimsy */}
      <path d="M22 12l2 4 4 1-4 2-2 5-2-5-4-2 4-1 2-4z" fill="#ffd278" opacity="0.9" />
      <path d="M198 88l1.5 3 3 .8-3 1.5-1.5 3.5-1.5-3.5-3-1.5 3-.8 1.5-3z" fill="#ffd278" opacity="0.65" />
    </svg>
  );
}

type Comic = {
  num: number;
  title?: string;
  safe_title?: string;
  alt?: string;
  img?: string;
  xkcd_url?: string;
  explainxkcd_url?: string;
};

export default function App() {
  const [busy, setBusy] = useState(false);
  const [comic, setComic] = useState<Comic | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [numInput, setNumInput] = useState("");

  const load = useCallback(async (operation: "current" | "random" | "by_number", n?: number) => {
    setBusy(true);
    setErr(null);
    setComic(null);
    try {
      const r = await fetch("/api/comic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          operation,
          comic_number: n,
        }),
      });
      const j = (await r.json()) as { success?: boolean; comic?: Comic; error?: string };
      if (!j.success || !j.comic) {
        setErr(j.error ?? "Failed");
        return;
      }
      setComic(j.comic);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }, []);

  return (
    <div className="app-container">
      <header className="hero">
        <div className="hero__inner">
          <div className="hero__copy">
            <span className="hero__badge">Model context protocol</span>
            <h1 className="hero__title">xkcd-mcp</h1>
            <p className="hero__tagline">
              Comics for your LLM. Official API, unofficial amount of stick-figure drama.
            </p>
            <p className="hero__footnote">
              Official JSON API only — no scraping.{" "}
              <a href="https://github.com/sandraschi/xkcd-mcp" target="_blank" rel="noopener noreferrer">
                GitHub
              </a>
            </p>
          </div>
          <HeroStickFigures />
        </div>
        <p className="hero__caption">
          Alt text: A tiny server labeled “JSON” receives enthusiastic waves while someone in a speech bubble negotiates
          with the universe. Hover tooltips not included; that’s what the comic alt is for.
        </p>
      </header>

      <div className="control-panel">
        <button
          type="button"
          className="btn-primary"
          disabled={busy}
          onClick={() => void load("current")}
        >
          Current
        </button>
        <button
          type="button"
          className="btn-primary"
          disabled={busy}
          onClick={() => void load("random")}
        >
          Random
        </button>
        <button
          type="button"
          className="btn-primary"
          disabled={busy}
          onClick={() => {
            const n = parseInt(numInput, 10);
            if (!Number.isFinite(n) || n < 1) {
              setErr("Enter a comic number ≥ 1");
              return;
            }
            void load("by_number", n);
          }}
        >
          #
        </button>
        <input
          type="number"
          min={1}
          placeholder="e.g. 2916"
          className="input-num"
          value={numInput}
          onChange={(e) => setNumInput(e.target.value)}
        />
      </div>

      {err && <p className="error-msg">{err}</p>}

      {comic && (
        <article className="comic-card">
          <h2>
            #{comic.num}. {comic.title ?? comic.safe_title}
          </h2>
          {comic.img && (
            <img
              src={comic.img}
              alt={comic.alt ?? ""}
              className="comic-img"
            />
          )}
          {comic.alt && (
            <p className="comic-alt">{comic.alt}</p>
          )}
          <p className="comic-links">
            <a href={comic.xkcd_url} target="_blank" rel="noopener noreferrer">
              xkcd
            </a>
            {" · "}
            <a href={comic.explainxkcd_url} target="_blank" rel="noopener noreferrer">
              explainxkcd
            </a>
          </p>
        </article>
      )}

      <details className="mcp-box">
        <summary>MCP Server Details (v0.2.0)</summary>
        <div className="mcp-details-content">
          <p>
            Endpoint: <code>http://127.0.0.1:10778/mcp</code>
          </p>
          <p style={{ marginTop: 8, fontWeight: "bold" }}>Discrete Tools Table (SOTA v13.1):</p>
          <ul style={{ paddingLeft: 18 }}>
            <li><code>xkcd_latest</code> — Fetch the current comic</li>
            <li><code>xkcd_get</code> — Get specific comic index</li>
            <li><code>xkcd_random</code> — Surprise random comic</li>
            <li><code>xkcd_help</code> — Interactive guide & port info</li>
          </ul>
        </div>
      </details>
    </div>
  );
}
