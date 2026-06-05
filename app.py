from flask import Flask, jsonify, send_from_directory, render_template_string
import csv, os, json

app = Flask(__name__)

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
URLSCAN_CSV     = os.path.join(BASE_DIR, "output_urlscan.csv")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")

def parse_urlscan():
    rows = []
    if not os.path.exists(URLSCAN_CSV):
        return rows
    with open(URLSCAN_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            r = dict(row)
            domain = r.get("DNSTwist Domain", "")
            shot   = os.path.join(SCREENSHOTS_DIR, f"{domain}.png")
            r["has_screenshot"] = os.path.exists(shot)
            r["screenshot_url"] = f"/screenshots/{domain}.png" if r["has_screenshot"] else None
            try:
                raw    = r.get("Links", "[]")
                r["Links"] = json.loads(raw.replace("'", '"')) if raw.startswith("[") else []
            except Exception:
                r["Links"] = []
            rows.append(r)
    return rows

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/results")
def results():
    return jsonify(parse_urlscan())

@app.route("/screenshots/<path:filename>")
def screenshots(filename):
    return send_from_directory(SCREENSHOTS_DIR, filename)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TwistScan</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0c0f;--bg2:#111418;--bg3:#181c22;
  --border:#1e2530;--border2:#2a3340;
  --text:#c8d4e0;--text2:#6b7f92;--text3:#3d4f60;
  --accent:#00d4aa;--blue:#0099ff;
  --red:#ff4757;--amber:#ffa502;--green:#2ed573;--purple:#a55eea;
  --mono:'IBM Plex Mono',monospace;--sans:'IBM Plex Sans',sans-serif;
}
body{background:var(--bg);color:var(--text);font-family:var(--sans);font-size:14px}

header{display:flex;align-items:center;gap:12px;padding:14px 24px;background:var(--bg2);border-bottom:1px solid var(--border)}
.logo{font-family:var(--mono);font-size:18px;font-weight:500;color:var(--accent)}
.logo span{color:var(--text2)}
.updated{font-family:var(--mono);font-size:11px;color:var(--text3);margin-left:auto}
.btn{font-family:var(--mono);font-size:11px;background:none;border:1px solid var(--border2);color:var(--text2);padding:5px 14px;border-radius:4px;cursor:pointer;transition:.15s}
.btn:hover{border-color:var(--accent);color:var(--accent)}

.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1px;background:var(--border);border-bottom:1px solid var(--border)}
.stat{background:var(--bg2);padding:14px 20px}
.stat-label{font-family:var(--mono);font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--text3);margin-bottom:5px}
.stat-num{font-family:var(--mono);font-size:22px;font-weight:500;color:var(--text)}
.stat-num.r{color:var(--red)}.stat-num.a{color:var(--amber)}.stat-num.g{color:var(--accent)}

.tabs{display:flex;background:var(--bg2);border-bottom:1px solid var(--border);padding:0 24px}
.tab{font-family:var(--mono);font-size:12px;padding:11px 16px;cursor:pointer;color:var(--text2);border-bottom:2px solid transparent;transition:.15s}
.tab.active{color:var(--accent);border-bottom-color:var(--accent)}
.tab:hover{color:var(--text)}

.toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:12px 24px;background:var(--bg2);border-bottom:1px solid var(--border)}
.toolbar input,.toolbar select{background:var(--bg3);border:1px solid var(--border2);color:var(--text);font-family:var(--mono);font-size:12px;padding:6px 12px;border-radius:4px;outline:none}
.toolbar input{width:260px}
.toolbar input:focus,.toolbar select:focus{border-color:var(--accent)}
.toolbar input::placeholder{color:var(--text3)}

.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse}
thead th{background:var(--bg2);font-family:var(--mono);font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--text3);padding:10px 16px;text-align:left;border-bottom:1px solid var(--border);cursor:pointer;white-space:nowrap;position:sticky;top:0;z-index:1}
thead th:hover{color:var(--text2)}
tbody tr{border-bottom:1px solid var(--border);cursor:pointer;transition:background .1s}
tbody tr:hover{background:var(--bg3)}
td{padding:10px 16px;font-family:var(--mono);font-size:12px;white-space:nowrap;max-width:200px;overflow:hidden;text-overflow:ellipsis}
.td-d{color:var(--blue);font-weight:500}.td-m{color:var(--text2)}

.sim{display:inline-block;font-family:var(--mono);font-size:11px;font-weight:500;padding:2px 8px;border-radius:3px}
.sh{background:rgba(255,71,87,.15);color:var(--red);border:1px solid rgba(255,71,87,.3)}
.sm{background:rgba(255,165,2,.12);color:var(--amber);border:1px solid rgba(255,165,2,.3)}
.sl{background:rgba(46,213,115,.1);color:var(--green);border:1px solid rgba(46,213,115,.25)}
.sn{background:var(--bg3);color:var(--text3);border:1px solid var(--border2)}
.st{display:inline-block;font-family:var(--mono);font-size:10px;padding:2px 7px;border-radius:3px;text-transform:uppercase;letter-spacing:.5px}
.st-live{background:rgba(0,212,170,.1);color:var(--accent);border:1px solid rgba(0,212,170,.25)}
.st-off{background:rgba(107,127,146,.1);color:var(--text2);border:1px solid var(--border2)}
.st-sub{background:rgba(0,153,255,.1);color:var(--blue);border:1px solid rgba(0,153,255,.25)}
.st-same{background:rgba(255,165,2,.1);color:var(--amber);border:1px solid rgba(255,165,2,.25)}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1px;background:var(--border)}
.card{background:var(--bg2);cursor:pointer;overflow:hidden;transition:background .15s}
.card:hover{background:var(--bg3)}
.card-img{width:100%;height:150px;object-fit:cover;object-position:top;display:block;border-bottom:1px solid var(--border);background:var(--bg3)}
.card-noimg{width:100%;height:150px;display:flex;align-items:center;justify-content:center;color:var(--text3);font-family:var(--mono);font-size:11px;border-bottom:1px solid var(--border)}
.card-body{padding:12px 14px}
.card-domain{font-family:var(--mono);font-size:13px;color:var(--blue);font-weight:500;margin-bottom:6px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.card-meta{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px}
.card-title{font-size:11px;color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* ── Viz ── */
.viz-wrap{padding:24px;display:grid;grid-template-columns:1fr 1fr;gap:20px}
.viz-card{background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:20px}
.viz-card.full{grid-column:1/-1}
.viz-title{font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--text3);margin-bottom:4px}
.viz-subtitle{font-size:12px;color:var(--text2);margin-bottom:16px}
.chart-wrap{position:relative;height:220px}
.chart-wrap.tall{height:280px}

/* risk table inside viz */
.risk-table{width:100%;border-collapse:collapse;margin-top:4px}
.risk-table th{font-family:var(--mono);font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--text3);padding:6px 10px;text-align:left;border-bottom:1px solid var(--border)}
.risk-table td{font-family:var(--mono);font-size:12px;padding:7px 10px;border-bottom:1px solid var(--border);color:var(--text)}
.risk-table tr:last-child td{border:none}
.risk-table tr:hover td{background:var(--bg3)}
.risk-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}

/* modal */
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:100;display:flex;align-items:center;justify-content:center;padding:24px}
.modal{background:var(--bg2);border:1px solid var(--border2);border-radius:6px;width:100%;max-width:760px;max-height:90vh;overflow-y:auto}
.modal-hdr{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px;position:sticky;top:0;background:var(--bg2);z-index:1}
.modal-title{font-family:var(--mono);font-size:15px;color:var(--blue);flex:1}
.modal-x{background:none;border:none;color:var(--text2);font-size:22px;cursor:pointer;line-height:1;padding:0 4px}
.modal-x:hover{color:var(--text)}
.modal-shot{width:100%;max-height:280px;object-fit:cover;object-position:top;display:block;border-bottom:1px solid var(--border)}
.modal-body{padding:20px}
.dgrid{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);margin-bottom:16px;border-radius:4px;overflow:hidden}
.dcell{background:var(--bg3);padding:10px 14px}
.dlabel{font-family:var(--mono);font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--text3);margin-bottom:4px}
.dval{font-family:var(--mono);font-size:12px;color:var(--text);word-break:break-all}
.dval a{color:var(--blue);text-decoration:none}
.dval a:hover{text-decoration:underline}
.links-hdr{font-family:var(--mono);font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--text3);margin-bottom:8px}
.link-row{font-family:var(--mono);font-size:11px;color:var(--text2);padding:5px 0;border-bottom:1px solid var(--border);word-break:break-all}
.link-row:last-child{border:none}

.empty{text-align:center;padding:60px 24px;color:var(--text3);font-family:var(--mono);font-size:13px}
.hidden{display:none!important}
</style>
</head>
<body>

<header>
  <div class="logo">Twist<span>Scan</span></div>
  <div class="updated" id="ts">—</div>
  <button class="btn" onclick="loadData()">↺ refresh</button>
</header>

<div class="stats" id="stats"></div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('table')">Table</div>
  <div class="tab" onclick="switchTab('grid')">Screenshots</div>
  <div class="tab" onclick="switchTab('viz')">Intelligence</div>
</div>

<div class="toolbar" id="toolbar">
  <input id="q" type="text" placeholder="Search domain, IP, title, ASN..." oninput="render()">
  <select id="sf" onchange="render()">
    <option value="">All similarity</option>
    <option value="high">High ≥ 70%</option>
    <option value="mid">Mid 40–69%</option>
    <option value="low">Low &lt; 40%</option>
  </select>
  <select id="stf" onchange="render()">
    <option value="">All status</option>
    <option value="https-only">Live</option>
    <option value="off-domain">Off-domain</option>
    <option value="sub-domain">Subdomain</option>
    <option value="same-domain">Same-domain</option>
  </select>
  <select id="cf" onchange="render()">
    <option value="">All countries</option>
  </select>
</div>

<div id="tableView" class="table-wrap"></div>
<div id="gridView"  class="hidden"></div>
<div id="vizView"   class="hidden viz-wrap"></div>

<div id="overlay" class="overlay hidden" onclick="closeModal(event)">
  <div class="modal" id="modal"></div>
</div>

<script>
let DATA = [], sortCol = 'Similarity', sortDir = -1, activeTab = 'table';
let charts = {};

/* ── Chart.js global defaults ── */
Chart.defaults.color = '#6b7f92';
Chart.defaults.borderColor = '#1e2530';
Chart.defaults.font.family = "'IBM Plex Mono', monospace";
Chart.defaults.font.size = 11;

/* ── fetch ── */
async function loadData() {
  document.getElementById('ts').textContent = 'loading...';
  try {
    const res = await fetch('/api/results');
    DATA = await res.json();
    document.getElementById('ts').textContent = 'updated ' + new Date().toLocaleTimeString();
    buildCountryFilter();
    render();
  } catch(e) {
    document.getElementById('tableView').innerHTML = '<div class="empty">error loading data</div>';
  }
}

function buildCountryFilter() {
  const countries = [...new Set(DATA.map(r => r.Country).filter(Boolean))].sort();
  const sel = document.getElementById('cf');
  sel.innerHTML = '<option value="">All countries</option>' +
    countries.map(c => `<option value="${c}">${c}</option>`).join('');
}

/* ── filter + sort ── */
function getRows() {
  const q   = document.getElementById('q').value.toLowerCase();
  const sf  = document.getElementById('sf').value;
  const stf = document.getElementById('stf').value;
  const cf  = document.getElementById('cf').value;
  return DATA.filter(r => {
    const hay = [r['DNSTwist Domain'],r['URLScan Domain'],r.IP,r.Title,r['ASN Name'],r.ASN].join(' ').toLowerCase();
    if (q && !hay.includes(q)) return false;
    const sim = parseFloat(r.Similarity)||0;
    if (sf==='high' && sim<70) return false;
    if (sf==='mid'  && (sim<40||sim>=70)) return false;
    if (sf==='low'  && sim>=40) return false;
    if (stf && (r.Redirected||'').toLowerCase()!==stf) return false;
    if (cf  && r.Country!==cf) return false;
    return true;
  }).sort((a,b)=>{
    let av=a[sortCol]||'', bv=b[sortCol]||'';
    if(['Similarity','TLS Age Days'].includes(sortCol)){av=parseFloat(av)||0;bv=parseFloat(bv)||0;}
    return av<bv?-sortDir:av>bv?sortDir:0;
  });
}

/* ── badges ── */
function simBadge(v){
  const s=parseFloat(v)||0;
  const c=s>=70?'sh':s>=40?'sm':s>0?'sl':'sn';
  return `<span class="sim ${c}">${s>0?s.toFixed(1)+'%':'N/A'}</span>`;
}
function stBadge(r){
  const v=(r.Redirected||'').toLowerCase();
  if(v==='https-only') return `<span class="st st-live">live</span>`;
  if(v==='off-domain') return `<span class="st st-off">off-domain</span>`;
  if(v==='sub-domain') return `<span class="st st-sub">subdomain</span>`;
  if(v==='same-domain')return `<span class="st st-same">same-domain</span>`;
  return `<span class="st st-off">${v||'—'}</span>`;
}

/* ── stats bar ── */
function renderStats(rows){
  const total  = DATA.length;
  const high   = DATA.filter(r=>(parseFloat(r.Similarity)||0)>=70 && r['DNSTwist Domain']!==r['URLScan Domain']).length;
  const live   = DATA.filter(r=>(r.Redirected||'').toLowerCase()==='https-only').length;
  const fresh  = DATA.filter(r=>{const d=parseInt(r['TLS Age Days']);return !isNaN(d)&&d<=30;}).length;
  const offdom = DATA.filter(r=>(r.Redirected||'').toLowerCase()==='off-domain').length;
  document.getElementById('stats').innerHTML=`
    <div class="stat"><div class="stat-label">Total</div><div class="stat-num">${total}</div></div>
    <div class="stat"><div class="stat-label">High similarity</div><div class="stat-num r">${high}</div></div>
    <div class="stat"><div class="stat-label">Live</div><div class="stat-num g">${live}</div></div>
    <div class="stat"><div class="stat-label">Off-domain</div><div class="stat-num">${offdom}</div></div>
    <div class="stat"><div class="stat-label">Fresh TLS ≤30d</div><div class="stat-num a">${fresh}</div></div>
    <div class="stat"><div class="stat-label">Showing</div><div class="stat-num">${rows.length}</div></div>`;
}

/* ── table ── */
function renderTable(rows){
  const el=document.getElementById('tableView');
  if(!rows.length){el.innerHTML='<div class="empty">no results</div>';return;}
  const cols=[
    {k:'DNSTwist Domain',l:'Domain'},{k:'Similarity',l:'Similarity'},
    {k:'Redirected',l:'Status'},{k:'IP',l:'IP'},{k:'Country',l:'Country'},
    {k:'ASN Name',l:'ASN'},{k:'TLS Age Days',l:'TLS age'},
    {k:'TLS Issuer',l:'Issuer'},{k:'Title',l:'Title'},
  ];
  const thead='<thead><tr>'+cols.map(c=>{
    const arr=sortCol===c.k?(sortDir===-1?' ↓':' ↑'):'';
    return `<th onclick="doSort('${c.k}')">${c.l}${arr}</th>`;
  }).join('')+'</tr></thead>';
  const tbody=rows.map((r,i)=>{
    const age=parseInt(r['TLS Age Days']);
    const ageStr=isNaN(age)?'—':age+'d';
    const ageSt=!isNaN(age)&&age<=30?';color:var(--amber)':'';
    return `<tr onclick="openModal(${i},filteredCache)">
      <td class="td-d">${r['DNSTwist Domain']||'—'}</td>
      <td>${simBadge(r.Similarity)}</td>
      <td>${stBadge(r)}</td>
      <td class="td-m">${r.IP||'—'}</td>
      <td class="td-m">${r.Country||'—'}</td>
      <td class="td-m" title="${r['ASN Name']}">${(r['ASN Name']||'').split(',')[0].substring(0,22)}</td>
      <td style="font-family:var(--mono);font-size:12px${ageSt}">${ageStr}</td>
      <td class="td-m" title="${r['TLS Issuer']}">${(r['TLS Issuer']||'—').substring(0,22)}</td>
      <td class="td-m" title="${r.Title}">${(r.Title||'—').substring(0,38)}</td>
    </tr>`;
  }).join('');
  el.innerHTML=`<table>${thead}<tbody>${tbody}</tbody></table>`;
}

/* ── grid ── */
function renderGrid(rows){
  const el=document.getElementById('gridView');
  if(!rows.length){el.innerHTML='<div class="empty">no results</div>';return;}
  el.innerHTML='<div class="grid">'+rows.map((r,i)=>{
    const img=r.has_screenshot?`<img class="card-img" src="${r.screenshot_url}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">`:'' ;
    const noimg=`<div class="card-noimg"${r.has_screenshot?' style="display:none"':''}>no screenshot</div>`;
    return `<div class="card" onclick="openModal(${i},filteredCache)">
      ${img}${noimg}
      <div class="card-body">
        <div class="card-domain">${r['DNSTwist Domain']}</div>
        <div class="card-meta">${simBadge(r.Similarity)} ${stBadge(r)}</div>
        <div class="card-title">${(r.Title||'No title').substring(0,50)}</div>
      </div>
    </div>`;
  }).join('')+'</div>';
}

/* ── destroy old charts ── */
function destroyCharts(){
  Object.values(charts).forEach(c=>c.destroy());
  charts={};
}

/* ── Intelligence tab ── */
function renderViz(){
  destroyCharts();
  const rows = DATA; // always use full dataset for intel

  /* 1. Risk Priority List — live domains sorted by sim + fresh TLS */
  const risky = rows
    .filter(r => (r.Redirected||'').toLowerCase()==='https-only' && r['DNSTwist Domain']!==r['URLScan Domain'])
    .map(r=>({
      domain: r['DNSTwist Domain'],
      sim: parseFloat(r.Similarity)||0,
      tls: parseInt(r['TLS Age Days'])||999,
      country: r.Country||'—',
      title: (r.Title||'').substring(0,30),
    }))
    .sort((a,b)=> (b.sim - a.sim) || (a.tls - b.tls))
    .slice(0,8);

  /* 2. Similarity distribution buckets */
  const buckets = {'90-100':0,'70-89':0,'50-69':0,'40-49':0,'<40':0};
  rows.forEach(r=>{
    const s=parseFloat(r.Similarity)||0;
    if(s>=90) buckets['90-100']++;
    else if(s>=70) buckets['70-89']++;
    else if(s>=50) buckets['50-69']++;
    else if(s>=40) buckets['40-49']++;
    else buckets['<40']++;
  });

  /* 3. Status breakdown */
  const statusMap={};
  rows.forEach(r=>{
    const v=(r.Redirected||'N/A').toLowerCase();
    statusMap[v]=(statusMap[v]||0)+1;
  });

  /* 4. Top hosting ASNs (suspicious = not your own) */
  const asnMap={};
  rows.filter(r=>r['DNSTwist Domain']!==r['URLScan Domain']).forEach(r=>{
    const a=(r['ASN Name']||'Unknown').split(',')[0].split(' - ')[0].trim().substring(0,20);
    asnMap[a]=(asnMap[a]||0)+1;
  });
  const topASN=Object.entries(asnMap).sort((a,b)=>b[1]-a[1]).slice(0,7);

  /* 5. TLS age buckets — freshness = risk */
  const tlsBuckets={'0-7d':0,'8-30d':0,'31-90d':0,'91-365d':0,'>365d':0,'N/A':0};
  rows.forEach(r=>{
    const d=parseInt(r['TLS Age Days']);
    if(isNaN(d)) tlsBuckets['N/A']++;
    else if(d<=7)   tlsBuckets['0-7d']++;
    else if(d<=30)  tlsBuckets['8-30d']++;
    else if(d<=90)  tlsBuckets['31-90d']++;
    else if(d<=365) tlsBuckets['91-365d']++;
    else            tlsBuckets['>365d']++;
  });

  /* 6. Country distribution */
  const countryMap={};
  rows.forEach(r=>{
    const c=r.Country||'Unknown';
    countryMap[c]=(countryMap[c]||0)+1;
  });
  const topCountry=Object.entries(countryMap).sort((a,b)=>b[1]-a[1]).slice(0,8);

  /* ── build HTML ── */
  const riskRows = risky.map(r=>{
    const dotColor = r.sim>=70?'var(--red)':r.sim>=50?'var(--amber)':'var(--green)';
    const tlsFlag  = r.tls<=30?`<span style="color:var(--amber);margin-left:6px">⚠ ${r.tls}d</span>`:'';
    return `<tr>
      <td><span class="risk-dot" style="background:${dotColor}"></span>${r.domain}</td>
      <td>${r.sim.toFixed(1)}%</td>
      <td>${r.country}</td>
      <td>${r.title}${tlsFlag}</td>
    </tr>`;
  }).join('');

  document.getElementById('vizView').innerHTML = `

    <!-- Risk Priority List -->
    <div class="viz-card full">
      <div class="viz-title">🎯 Priority Investigation List</div>
      <div class="viz-subtitle">Live domains ranked by similarity + fresh TLS — investigate these first</div>
      <table class="risk-table">
        <thead><tr><th>Domain</th><th>Similarity</th><th>Country</th><th>Page Title / TLS Flag</th></tr></thead>
        <tbody>${riskRows||'<tr><td colspan="4" style="color:var(--text3);padding:12px 10px">No live lookalike domains found</td></tr>'}</tbody>
      </table>
    </div>

    <!-- Similarity Distribution -->
    <div class="viz-card">
      <div class="viz-title">📊 Similarity Distribution</div>
      <div class="viz-subtitle">Visual similarity scores vs original domain</div>
      <div class="chart-wrap"><canvas id="cSim"></canvas></div>
    </div>

    <!-- Status Breakdown -->
    <div class="viz-card">
      <div class="viz-title">🌐 Domain Status Breakdown</div>
      <div class="viz-subtitle">Where do lookalike domains resolve?</div>
      <div class="chart-wrap"><canvas id="cStatus"></canvas></div>
    </div>

    <!-- TLS Age -->
    <div class="viz-card">
      <div class="viz-title">🔐 TLS Certificate Age</div>
      <div class="viz-subtitle">Fresh certs (≤30d) indicate newly spun-up infrastructure</div>
      <div class="chart-wrap"><canvas id="cTLS"></canvas></div>
    </div>

    <!-- Top ASNs -->
    <div class="viz-card">
      <div class="viz-title">🏢 Top Hosting Providers</div>
      <div class="viz-subtitle">ASNs hosting lookalike domains — spot shared infrastructure</div>
      <div class="chart-wrap tall"><canvas id="cASN"></canvas></div>
    </div>

    <!-- Country Distribution -->
    <div class="viz-card full">
      <div class="viz-title">🗺 Country Distribution</div>
      <div class="viz-subtitle">Hosting locations of lookalike domains</div>
      <div class="chart-wrap"><canvas id="cCountry"></canvas></div>
    </div>
  `;

  const gridCfg = { responsive:true, maintainAspectRatio:false,
    plugins:{ legend:{ display:false }, tooltip:{ callbacks:{} } } };

  /* Similarity bar chart */
  charts.sim = new Chart(document.getElementById('cSim'), {
    type:'bar',
    data:{
      labels: Object.keys(buckets),
      datasets:[{
        data: Object.values(buckets),
        backgroundColor:['#ff475780','#ff475760','#ffa50260','#2ed57340','#3d4f6060'],
        borderColor:    ['#ff4757',  '#ff4757',  '#ffa502',  '#2ed573',  '#3d4f60'],
        borderWidth:1, borderRadius:3,
      }]
    },
    options:{...gridCfg,
      scales:{
        x:{grid:{color:'#1e2530'},ticks:{color:'#6b7f92'}},
        y:{grid:{color:'#1e2530'},ticks:{color:'#6b7f92',stepSize:1}}
      }
    }
  });

  /* Status doughnut */
  const statusLabels = Object.keys(statusMap);
  const statusColors = statusLabels.map(l=>{
    if(l==='https-only') return '#00d4aa';
    if(l==='off-domain') return '#6b7f92';
    if(l==='sub-domain') return '#0099ff';
    if(l==='same-domain')return '#ffa502';
    return '#3d4f60';
  });
  charts.status = new Chart(document.getElementById('cStatus'), {
    type:'doughnut',
    data:{
      labels: statusLabels,
      datasets:[{ data:Object.values(statusMap), backgroundColor:statusColors, borderColor:'#111418', borderWidth:2 }]
    },
    options:{...gridCfg,
      plugins:{
        legend:{ display:true, position:'right', labels:{ color:'#6b7f92', boxWidth:12, padding:14 } }
      },
      cutout:'60%'
    }
  });

  /* TLS age bar */
  const tlsColors=['#ff4757','#ffa502','#2ed57340','#2ed57320','#3d4f6040','#3d4f60'];
  charts.tls = new Chart(document.getElementById('cTLS'), {
    type:'bar',
    data:{
      labels: Object.keys(tlsBuckets),
      datasets:[{
        data: Object.values(tlsBuckets),
        backgroundColor: tlsColors,
        borderColor: tlsColors.map(c=>c.replace(/[0-9a-f]{2}$/i,'')),
        borderWidth:1, borderRadius:3,
      }]
    },
    options:{...gridCfg,
      scales:{
        x:{grid:{color:'#1e2530'},ticks:{color:'#6b7f92'}},
        y:{grid:{color:'#1e2530'},ticks:{color:'#6b7f92',stepSize:1}}
      }
    }
  });

  /* ASN horizontal bar */
  charts.asn = new Chart(document.getElementById('cASN'), {
    type:'bar',
    data:{
      labels: topASN.map(a=>a[0]),
      datasets:[{
        data: topASN.map(a=>a[1]),
        backgroundColor:'#0099ff30',
        borderColor:'#0099ff',
        borderWidth:1, borderRadius:3,
      }]
    },
    options:{...gridCfg,
      indexAxis:'y',
      scales:{
        x:{grid:{color:'#1e2530'},ticks:{color:'#6b7f92',stepSize:1}},
        y:{grid:{color:'#1e2530'},ticks:{color:'#c8d4e0'}}
      }
    }
  });

  /* Country bar */
  charts.country = new Chart(document.getElementById('cCountry'), {
    type:'bar',
    data:{
      labels: topCountry.map(c=>c[0]||'Unknown'),
      datasets:[{
        data: topCountry.map(c=>c[1]),
        backgroundColor:'#a55eea30',
        borderColor:'#a55eea',
        borderWidth:1, borderRadius:3,
      }]
    },
    options:{...gridCfg,
      scales:{
        x:{grid:{color:'#1e2530'},ticks:{color:'#c8d4e0'}},
        y:{grid:{color:'#1e2530'},ticks:{color:'#6b7f92',stepSize:1}}
      }
    }
  });
}

/* ── main render ── */
let filteredCache = [];
function render(){
  filteredCache = getRows();
  renderStats(filteredCache);
  if(activeTab==='table') renderTable(filteredCache);
  else if(activeTab==='grid') renderGrid(filteredCache);
  else renderViz();
}

function doSort(col){
  sortDir = sortCol===col ? sortDir*-1 : -1;
  sortCol = col;
  render();
}

function switchTab(tab){
  activeTab = tab;
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',['table','grid','viz'][i]===tab));
  document.getElementById('tableView').classList.toggle('hidden', tab!=='table');
  document.getElementById('gridView').classList.toggle('hidden',  tab!=='grid');
  document.getElementById('vizView').classList.toggle('hidden',   tab!=='viz');
  // hide toolbar on viz tab (charts use full dataset)
  document.getElementById('toolbar').classList.toggle('hidden', tab==='viz');
  render();
}

/* ── modal ── */
function openModal(idx, rows){
  const r=rows[idx]; if(!r) return;
  const links=Array.isArray(r.Links)?r.Links:[];
  const linksHtml=links.length
    ?links.map(l=>`<div class="link-row">${l.text?`<span style="color:var(--blue)">${l.text}</span> — `:''}${l.href}</div>`).join('')
    :'<div class="link-row" style="color:var(--text3)">none captured</div>';
  document.getElementById('modal').innerHTML=`
    <div class="modal-hdr">
      <div class="modal-title">${r['DNSTwist Domain']}</div>
      ${simBadge(r.Similarity)} ${stBadge(r)}
      <button class="modal-x" onclick="closeModal()">×</button>
    </div>
    ${r.has_screenshot?`<img class="modal-shot" src="${r.screenshot_url}" alt="screenshot">`:''}
    <div class="modal-body">
      <div class="dgrid">
        <div class="dcell"><div class="dlabel">DNSTwist domain</div><div class="dval">${r['DNSTwist Domain']||'—'}</div></div>
        <div class="dcell"><div class="dlabel">Resolved domain</div><div class="dval">${r['URLScan Domain']||'—'}</div></div>
        <div class="dcell"><div class="dlabel">IP</div><div class="dval">${r.IP||'—'}</div></div>
        <div class="dcell"><div class="dlabel">Country</div><div class="dval">${r.Country||'—'}</div></div>
        <div class="dcell"><div class="dlabel">ASN</div><div class="dval">${r.ASN||'—'}</div></div>
        <div class="dcell"><div class="dlabel">ASN name</div><div class="dval">${r['ASN Name']||'—'}</div></div>
        <div class="dcell"><div class="dlabel">Server</div><div class="dval">${r.Server||'—'}</div></div>
        <div class="dcell"><div class="dlabel">HTTP status</div><div class="dval">${r.Status||'—'}</div></div>
        <div class="dcell"><div class="dlabel">TLS issuer</div><div class="dval">${r['TLS Issuer']||'—'}</div></div>
        <div class="dcell"><div class="dlabel">TLS age (days)</div><div class="dval" style="${(parseInt(r['TLS Age Days'])||999)<=30?'color:var(--amber)':''}">${r['TLS Age Days']||'—'}</div></div>
        <div class="dcell"><div class="dlabel">TLS valid days</div><div class="dval">${r['TLS Valid Days']||'—'}</div></div>
        <div class="dcell"><div class="dlabel">TLS valid from</div><div class="dval">${r['TLS Valid From']||'—'}</div></div>
        <div class="dcell"><div class="dlabel">pHash</div><div class="dval">${r.Phash||'—'}</div></div>
        <div class="dcell"><div class="dlabel">Similarity</div><div class="dval">${r.Similarity||'—'}%</div></div>
        <div class="dcell" style="grid-column:1/-1"><div class="dlabel">Page title</div><div class="dval">${r.Title||'—'}</div></div>
        <div class="dcell" style="grid-column:1/-1"><div class="dlabel">Final URL</div><div class="dval"><a href="${r.URL}" target="_blank">${r.URL||'—'}</a></div></div>
        <div class="dcell" style="grid-column:1/-1"><div class="dlabel">URLScan report</div><div class="dval"><a href="${r['Report URL']}" target="_blank">${r['Report URL']||'—'}</a></div></div>
      </div>
      <div class="links-hdr">Outbound links (${links.length})</div>
      ${linksHtml}
    </div>`;
  document.getElementById('overlay').classList.remove('hidden');
}

function closeModal(e){
  if(!e||e.target===document.getElementById('overlay'))
    document.getElementById('overlay').classList.add('hidden');
}
document.addEventListener('keydown', e=>{ if(e.key==='Escape') closeModal(); });

/* ── init ── */
document.addEventListener('DOMContentLoaded', ()=>{
  loadData();
  setInterval(loadData, 60000);
});
</script>
</body>
</html>"""

if __name__ == "__main__":
    print("TwistScan Dashboard → http://YOUR-VM-IP:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
