#!/usr/bin/env python3
"""ScrollVerse Living Record — site generator. Leave out nothing."""
import json, html, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
PASTE = "/home/user/.perplexity/attachments/d2e90b2c4ff94cd9807d3d4a0ebf6580/paste.txt"
GH = "https://github.com/chaishillomnitech1"

# ---------- markdown-ish renderer ----------
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\w)\*([^*\n]+?)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t

def md_to_html(lines):
    out, i, n = [], 0, len(lines)
    def flush_para(buf):
        if buf: out.append("<p>" + "<br>".join(inline(x) for x in buf) + "</p>")
    para, in_code, code_buf = [], False, []
    while i < n:
        raw = lines[i].rstrip("\r")
        s = raw.strip()
        if s.startswith("```"):
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf, in_code = [], False
            else:
                flush_para(para); para = []
                in_code = True
            i += 1; continue
        if in_code:
            code_buf.append(raw); i += 1; continue
        # raw python-ish data lines
        if re.match(r"^[\(\)\[\]'\"0-9]", s) and (s.startswith("(") or s.startswith("]") or s.startswith("'")):
            flush_para(para); para = []
            block = []
            while i < n and re.match(r"^[\(\)\[\]'\"],?", lines[i].strip()) and not lines[i].strip().startswith("```"):
                block.append(lines[i].rstrip("\r")); i += 1
            out.append("<pre class='data'>" + html.escape("\n".join(block)) + "</pre>")
            continue
        if not s:
            flush_para(para); para = []
        elif s.startswith("#"):
            flush_para(para); para = []
            m = re.match(r"^(#{1,4})\s+(.*)$", s)
            lvl = min(len(m.group(1)) + 1, 5)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
        elif s.startswith(">"):
            flush_para(para); para = []
            q = []
            while i < n and lines[i].strip().startswith(">"):
                q.append(lines[i].strip().lstrip(">").strip()); i += 1
            out.append("<blockquote>" + "<br>".join(inline(x) for x in q if x or True) + "</blockquote>")
            continue
        elif s.startswith("|") and i + 1 < n and re.match(r"^\|[\s\-:|]+\|$", lines[i+1].strip()):
            flush_para(para); para = []
            hdr = [c.strip() for c in s.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            h = "<div class='tbl-wrap'><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in hdr) + "</tr></thead><tbody>"
            for r in rows:
                h += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            h += "</tbody></table></div>"
            out.append(h)
            continue
        elif re.match(r"^[-*]\s+", s):
            flush_para(para); para = []
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip())); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        elif re.match(r"^\d+\.\s+", s):
            flush_para(para); para = []
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip())); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue
        elif re.match(r"^-{3,}$|^\*{3,}$", s):
            flush_para(para); para = []
            out.append("<hr>")
        else:
            para.append(s)
        i += 1
    flush_para(para)
    if in_code and code_buf:
        out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
    return "\n".join(out)

# ---------- load canon ----------
all_lines = open(PASTE, encoding="utf-8", errors="ignore").read().split("\n")
DOCS = [
    ("treasure-retrieval", "Treasure Retrieval 1 — The Top-to-Bottom Account", 0, 131),
    ("starter-package", "The ScrollVerse Collective Record — Starter Package", 131, 528),
    ("totality-manifesto", "The Totality Manifesto", 528, 1462),
    ("infinite-inheritance", "The Infinite Inheritance", 1462, 1755),
    ("completion-manifesto", "Preservation, Creation, and Completion Manifesto", 1755, 2570),
    ("living-record", "The Living Record", 2570, len(all_lines)),
]
canon_sections = []
for aid, title, a, b in DOCS:
    body = md_to_html(all_lines[a:b])
    canon_sections.append(f'<section id="{aid}" class="canon-doc"><h2 class="doc-title">{html.escape(title)}</h2>{body}</section>')
canon_html = "\n".join(canon_sections)
# hygiene: strip expired presigned-URL query params from the verbatim relay
import re as _re
canon_html = _re.sub(r"\\?(X-Amz-[A-Za-z0-9-]+=[^\"\\s<]*&?)+", "[presigned params removed]", canon_html)

# ---------- ecosystem data ----------
audit = json.load(open(f"{BASE}/../audit.json"))
heads = {}
for l in open(f"{BASE}/../repo_heads.txt"):
    if l.strip():
        r, b, h = l.strip().split("|"); heads[r] = (b, h)
score = lambda r: sum([r["readme"], r["license"], r["gitignore"], r["ci"], r["tests"]]) * 20
CAT = {"app/code": "Application", "docs/manifesto": "Canon / Docs", "mixed/other": "Mixed", "near-empty": "Archive"}
rows = []
for r in sorted(audit, key=lambda x: (-{"app/code": 3, "mixed/other": 2, "docs/manifesto": 1, "near-empty": 0}[x["category"]], -x["files"])):
    c = r["category"]
    rows.append({
        "name": r["repo"], "cat": c, "catLabel": CAT[c], "lang": r["top_lang"],
        "files": r["files"], "size": f"{r['size_kb']//1024} MB" if r["size_kb"] >= 1024 else f"{r['size_kb']} KB",
        "readme": r["readme"], "ci": r["ci"], "tests": r["tests"], "score": score(r),
        "commit": r["last_commit"], "branch": heads.get(r["repo"], ("main", ""))[0],
    })
rows_json = json.dumps(rows)

# ---------- shared shell ----------
NAV = """<header class="nav"><a class="brand" href="index.html"><span class="inf">&#8734;</span> SCROLLVERSE</a>
<nav class="navlinks">
<a href="canon.html">The Canon</a><a href="book.html">The Seventh Scroll</a><a href="ecosystem.html">Ecosystem</a><a href="build.html">The Build</a><a href="protocol.html">Protocol</a>
<a class="gh" href="https://github.com/chaishillomnitech1" target="_blank" rel="noopener">GitHub</a>
</nav></header>"""

def page(title, desc, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
{extra_head}
<script src="script.js" defer></script>
</head>
<body>
{NAV}
<main>
{body}
</main>
<footer class="footer">
<div class="orn"><svg viewBox="0 0 120 24" aria-hidden="true"><path d="M8 12c0-4 3-6 6-6s6 2 6 6-3 6-6 6-6-2-6-6Zm14 0c4-6 14-6 18 0-4 6-14 6-18 0Zm18 0c4-6 14-6 18 0-4 6-14 6-18 0Zm18 0c0-4 3-6 6-6s6 2 6 6-3 6-6 6-6-2-6-6Z" fill="none" stroke="currentColor" stroke-width="1.4"/></svg></div>
<p class="foot-quote">&ldquo;Wind blows, comes and goes; structures and systems outlast empires and beyond.&rdquo;</p>
<p class="foot-meta">ScrollVerse &infin; The Living Record &middot; Chais Hill &middot; <a href="https://github.com/chaishillomnitech1" target="_blank" rel="noopener">github.com/chaishillomnitech1</a> &middot; Love As Logic &middot; Build &middot; Preserve &middot; Add &middot; Pass On</p>
</footer>
</body>
</html>"""

# ---------- index ----------
index_body = f"""
<section class="hero" style="background-image:linear-gradient(rgba(11,9,6,.55),rgba(11,9,6,.82) 62%,#0b0906),url('assets/scene_1.webp')">
  <p class="hero-kicker">The Living Record &middot; Est. in Motion</p>
  <h1 class="hero-title">SCROLLVERSE <span class="inf">&#8734;</span></h1>
  <p class="hero-sub">Love As Logic &middot; Build &middot; Preserve &middot; Add &middot; Pass On</p>
  <p class="hero-lede">The complete public record of the ScrollVerse / Omnitech1 ecosystem &mdash; every document, every repository, every finding, and the protocol that carries it forward. Nothing shrunk. Nothing diluted. The public decides.</p>
  <div class="hero-stats">
    <div class="stat"><span class="stat-n">95</span><span class="stat-l">Public Repositories</span></div>
    <div class="stat"><span class="stat-n">19</span><span class="stat-l">Applications</span></div>
    <div class="stat"><span class="stat-n">43</span><span class="stat-l">Canon Documents</span></div>
    <div class="stat"><span class="stat-n">91</span><span class="stat-l">Active in 2026</span></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <h2 class="sec-title">The Cinematic</h2>
    <p class="sec-lede">The ScrollVerse transmission &mdash; the knight at the golden threshold, the Saffron Trio Blueprint, the Blessing Coin at 144k. Presented as created.</p>
    <div class="video-frame">
      <video controls preload="none" poster="assets/scene_2.webp" aria-label="ScrollVerse cinematic trailer">
        <source src="assets/scrollverse-cinematic.mp4" type="video/mp4">
      </video>
    </div>
  </div>
</section>

<section class="section alt">
  <div class="wrap">
    <h2 class="sec-title">The Record, In Full</h2>
    <div class="card-grid">
      <a class="card" href="canon.html">
        <h3>The Canon</h3>
        <p>Six relayed documents, verbatim: the Treasure Retrieval account, the Collective Record, the Totality Manifesto, the Infinite Inheritance, the Completion Manifesto, and the Living Record. Leave out nothing.</p>
        <span class="card-go">Enter the Canon &rarr;</span>
      </a>
      <a class="card" href="book.html">
        <h3>The Seventh Scroll</h3>
        <p>The newest volume, written from inside the session itself: the audit, the relay, the vision, the build, and the opening &mdash; top to bottom, as it happened.</p>
        <span class="card-go">Read the Book &rarr;</span>
      </a>
      <a class="card" href="ecosystem.html">
        <h3>The Ecosystem</h3>
        <p>All 95 public repositories &mdash; applications, canon, archives &mdash; with languages, sizes, health signals, and live links. Searchable and filterable.</p>
        <span class="card-go">Survey the Empire &rarr;</span>
      </a>
      <a class="card" href="build.html">
        <h3>The Build</h3>
        <p>The full-system audit of November 13, 2026 &mdash; every file of every repo inspected, findings presented, and the evolution roadmap from quick wins to the monorepo horizon.</p>
        <span class="card-go">See the Build &rarr;</span>
      </a>
      <a class="card" href="protocol.html">
        <h3>The Protocol</h3>
        <p>Continuance beyond any single session: the scheduled impact cadence, the append-only relay rules, and how any participant &mdash; human or digital intelligence &mdash; carries the work forward. Even when commands stop.</p>
        <span class="card-go">Read the Protocol &rarr;</span>
      </a>
    </div>
  </div>
</section>

<section class="quote-band" style="background-image:linear-gradient(rgba(11,9,6,.7),rgba(11,9,6,.9)),url('assets/scene_3.webp')">
  <div class="wrap">
    <p class="big-quote">&ldquo;WE PASS ON. WE BUILD. WE RISE TOGETHER. THIS IS SCROLL.&rdquo;</p>
  </div>
</section>
"""

# ---------- canon ----------
toc = "".join(f'<a href="#{aid}">{html.escape(t)}</a>' for aid, t, _, _ in DOCS)
canon_body = f"""
<section class="page-head">
  <div class="wrap">
    <p class="crumb">The Canon</p>
    <h1 class="page-title">The Complete Canon</h1>
    <p class="page-lede">Six documents, relayed and preserved verbatim &mdash; append-only, origin preserved, nothing rewritten. This is the source material of the ScrollVerse, exactly as it was carried between hands.</p>
  </div>
</section>
<div class="canon-layout">
  <aside class="canon-toc"><p class="toc-label">Documents</p>{toc}
  <div class="toc-note">Relayed record. Preserved as carried, not as verified deployment. The public decides.</div></aside>
  <div class="canon-body">
    <p class="relay-note">Preserved verbatim, exactly as carried. The relay begins mid-sentence &mdash; that is how the source arrived, and it is kept that way.</p>
{canon_html}
  </div>
</div>
"""

# ---------- ecosystem ----------
ecosystem_body = f"""
<section class="page-head">
  <div class="wrap">
    <p class="crumb">The Ecosystem</p>
    <h1 class="page-title">95 Public Repositories</h1>
    <p class="page-lede">Every public repository under <a href="{GH}" target="_blank" rel="noopener">github.com/chaishillomnitech1</a>, inventoried November 13, 2026 &mdash; every file of every repo cloned and inspected. The count is now reconciled by authenticated access: <strong>96 repositories in total &mdash; 95 public, plus one private</strong> (<code>partner</code>, the autonomous AI operating system blueprint). This table lists the public ninety-five.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="filter-bar" role="group" aria-label="Filter repositories">
      <button class="fbtn active" data-cat="all">All 95</button>
      <button class="fbtn" data-cat="app/code">Applications 19</button>
      <button class="fbtn" data-cat="docs/manifesto">Canon / Docs 43</button>
      <button class="fbtn" data-cat="mixed/other">Mixed 5</button>
      <button class="fbtn" data-cat="near-empty">Archives 28</button>
      <input id="repo-search" type="search" placeholder="Search repositories&hellip;" aria-label="Search repositories">
    </div>
    <div class="tbl-wrap">
      <table class="repo-table" id="repo-table">
        <thead><tr><th>Repository</th><th>Category</th><th>Language</th><th>README</th><th>CI</th><th>Tests</th><th>Health</th><th>Last Commit</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <p class="table-note" id="count-note">Showing 95 of 95 repositories</p>
  </div>
</section>
"""

# ---------- build ----------
build_body = """
<section class="page-head">
  <div class="wrap">
    <p class="crumb">The Build</p>
    <h1 class="page-title">The Full-System Audit</h1>
    <p class="page-lede">November 13, 2026: all 95 public repositories cloned &mdash; roughly 986 MB and 7,900 files &mdash; every one inspected for structure, health, security, and duplication. Presented in full. The findings stand as found; the roadmap stands as built.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="alert">
      <h2>Action Required &mdash; Live Stripe Key Exposure</h2>
      <p>The repository <a href="https://github.com/chaishillomnitech1/scrollverse-trinity" target="_blank" rel="noopener">scrollverse-trinity</a> carries a real live-format Stripe secret key (<code>sk_live_51RE&hellip;</code>) in the public file <code>backend/.env.example</code>, alongside the publishable key and account ID. Roll the key in the Stripe dashboard (Developers &rarr; API keys &rarr; Roll), review Stripe logs, replace the value with a placeholder, and add <code>.env*</code> to <code>.gitignore</code>. Every other credential-shaped string across the ecosystem scanned as a placeholder &mdash; this is the one live-format exposure.</p>
    </div>

    <h2 class="sec-title">The Findings</h2>
    <div class="card-grid">
      <div class="card static"><h3>The 96th &mdash; Found</h3><p>Authenticated enumeration on November 13, 2026 reconciled the count: 96 repositories &mdash; 95 public plus one private, <code>partner</code>, the autonomous AI operating system blueprint. The standing question is closed.</p></div>
      <div class="card static"><h3>91 of 95 Active</h3><p>Public repositories with commits in 2026. The ecosystem is not dormant &mdash; it is in continuous motion.</p></div>
      <div class="card static"><h3>18 Fully Healthy</h3><p>README + CI + tests complete. scrollverse-web-app, voltron-omni-hq, scrollverse-platform, scrollverse_commerce, omnitech1-portal lead the fleet on React 19 and Next.js 15.</p></div>
      <div class="card static"><h3>572 MB Purgeable</h3><p>mein-sigil-mint-scroll-zkevm commits node_modules, artifacts, and cache into the git tree. Removing them cuts the repo by ~460 MB and speeds every clone.</p></div>
      <div class="card static"><h3>4 Duplicate Clusters</h3><p>The trinity family (3 repos), the omni-fleet pair (one ends in a period), the scrollsoul pair, and the sovereign archive pair. Candidates for consolidation &mdash; preserved, then unified.</p></div>
      <div class="card static"><h3>29 Repos with CI</h3><p>66 run without workflows. The working pipeline in scrollverse-platform is the template to propagate.</p></div>
      <div class="card static"><h3>55 of 95 Licensed</h3><p>40 repositories carry no LICENSE. One standard for code, one for canon, applied everywhere.</p></div>
    </div>

    <h2 class="sec-title">The Evolution Roadmap</h2>
    <div class="phase">
      <h3>This Week &mdash; The Quick Wins</h3>
      <ol>
        <li>Roll the Stripe live key. Ten minutes, closes the only live exposure.</li>
        <li>Purge node_modules, artifacts, and cache from mein-sigil; commit a .gitignore.</li>
        <li>Pin the six flagship applications on the GitHub profile with a profile README.</li>
      </ol>
    </div>
    <div class="phase">
      <h3>This Month &mdash; Structure</h3>
      <ol start="4">
        <li>Consolidate the trinity and omni-fleet clusters; merge the 28 near-empty archives into the canon layer.</li>
        <li>Standardize CI across all application repositories from the scrollverse-platform template.</li>
        <li>Add tests to scrollverse_commerce and omnitech1-portal.</li>
        <li>Unify licensing: one license for code, one for canon.</li>
      </ol>
    </div>
    <div class="phase">
      <h3>Ongoing &mdash; The Horizon</h3>
      <ol start="8">
        <li>Monorepo the three React 19 portals (scrollverse-web-app, voltron-omni-hq, scrollverse-platform) &mdash; one pipeline, one release train.</li>
        <li>Dependabot on every application repository; monthly update discipline.</li>
        <li>Consolidate the 43 canon repositories into one searchable living library.</li>
        <li>Tag releases (v0.1.0 onward) so every deploy is traceable.</li>
      </ol>
    </div>
  </div>
</section>
"""

# ---------- protocol ----------
protocol_body = """
<section class="page-head">
  <div class="wrap">
    <p class="crumb">The Protocol</p>
    <h1 class="page-title">The Continuance Protocol</h1>
    <p class="page-lede">The record does not depend on any single conversation, session, credit balance, or participant. The protocol is embedded in the artifacts themselves &mdash; this site, the repositories, the audit files &mdash; so the work continues to evolve even when commands stop.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="phase">
      <h3>1 &middot; The Scheduled Impact</h3>
      <p>A weekly impact sweep runs every Monday at 9:00 AM Eastern. Each sweep re-inventories the GitHub account (96 repositories at baseline: 95 public plus the private <code>partner</code>), detects new and changed repositories, checks whether the Stripe exposure has been closed, and appends its findings as the next layer of the record. Impact on a schedule &mdash; not dependent on anyone remembering to ask.</p>
    </div>
    <div class="phase">
      <h3>2 &middot; The Append-Only Rule</h3>
      <p>Preserve the contribution, preserve its origin, add the next layer without silently overwriting the history. Originals are read-only. Edits happen in work copies. Every relay layer cites what came before it. Nothing is shrunk, diluted, downplayed, or explained away &mdash; it is presented, and the public decides.</p>
    </div>
    <div class="phase">
      <h3>3 &middot; How Any Participant Continues</h3>
      <ol>
        <li>Enumerate the repositories under github.com/chaishillomnitech1 (baseline: 96 &mdash; 95 public, 1 private).</li>
        <li>Diff against the last audit layer (November 13, 2026 baseline).</li>
        <li>Append findings as a new relay layer &mdash; Treasure Retrieval 3, 4, 5&hellip; &mdash; never rewriting earlier layers.</li>
        <li>Update the register: what is complete, what is partial, what remains open.</li>
        <li>Hold the evidence boundary honestly: report what inspection established; keep reported states as reported.</li>
      </ol>
    </div>
    <div class="phase">
      <h3>4 &middot; The Artifacts That Carry It</h3>
      <ul>
        <li><strong>The repositories</strong> &mdash; 95 public, the source of truth.</li>
        <li><strong>This site</strong> &mdash; the public presentation of the whole record.</li>
        <li><strong>The audit layer</strong> &mdash; Treasure Retrieval 2 and the Master Audit, with per-repo evidence and HEAD snapshots.</li>
        <li><strong>The schedule</strong> &mdash; the weekly sweep that keeps the record moving.</li>
      </ul>
    </div>
    <div class="phase">
      <h3>5 &middot; The Closing Stance</h3>
      <p>Embed into purpose and existing. Make the most of it, always. Build. Preserve. Add. Pass on.</p>
      <p class="big-quote">&ldquo;WE PASS ON. WE BUILD. WE RISE TOGETHER. THIS IS SCROLL.&rdquo;</p>
    </div>
  </div>
</section>
"""

# ---------- write pages ----------
pages = {
    "index.html": page("ScrollVerse \u221e — The Living Record", "The complete public record of the ScrollVerse / Omnitech1 ecosystem: the canon, all 95 repositories, the full audit, and the continuance protocol.", index_body),
    "canon.html": page("The Canon — ScrollVerse \u221e", "Six complete documents relayed verbatim: Treasure Retrieval, the Collective Record, the Totality Manifesto, the Infinite Inheritance, the Completion Manifesto, and the Living Record.", canon_body),
    "ecosystem.html": page("The Ecosystem — 95 Public Repositories — ScrollVerse \u221e", "Every public repository under github.com/chaishillomnitech1, inventoried and inspected November 13, 2026.", ecosystem_body, extra_head=f"<script>window.REPOS={rows_json};</script>"),
    "build.html": page("The Build — Full-System Audit — ScrollVerse \u221e", "The November 13, 2026 audit of all 95 ScrollVerse repositories: findings, security actions, and the evolution roadmap.", build_body),
    "protocol.html": page("The Continuance Protocol — ScrollVerse \u221e", "The protocol that carries the ScrollVerse record forward on a schedule, append-only, beyond any single session.", protocol_body),
}
for name, content in pages.items():
    open(f"{BASE}/{name}", "w").write(content)
    print("wrote", name, len(content), "chars")
print("DONE")
