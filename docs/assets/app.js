/* The Quantum Engineer — zero-dependency reader.
   Loads Markdown content, renders it, provides TOC / search / bilingual EN-FA UI. */
'use strict';

const $ = (s, r) => (r || document).querySelector(s);
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const state = {
  lang: localStorage.getItem('tqe:lang') ||
        ((navigator.language || '').toLowerCase().startsWith('fa') ? 'fa' : 'en'),
  theme: localStorage.getItem('tqe:theme') ||
         (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
  manifest: null,
  parts: { en: {}, fa: {} },   // partId -> parsed part (per language)
  route: null,
};

const UI = {
  en: {
    home: 'Home', contents: 'Contents', search: 'Search…', indexing: 'Indexing…',
    results: 'results', noResults: 'No results.', prev: 'Previous', next: 'Next',
    part: 'Part', chapter: 'Chapter', appendix: 'Appendix', errorTitle: 'Could not load content',
    errorBody: 'This reader fetches its Markdown files with <code>fetch</code>, which needs a web server (opening <code>index.html</code> directly from disk will not work). Serve the folder locally, with no internet required:',
    searchHint: 'Type at least 2 characters. Press / to focus, Esc to clear.',
    secList: 'In this chapter',
  },
  fa: {
    home: 'خانه', contents: 'فهرست', search: 'جست‌وجو…', indexing: 'در حال نمایه‌سازی…',
    results: 'نتیجه', noResults: 'چیزی یافت نشد.', prev: 'قبلی', next: 'بعدی',
    part: 'بخش', chapter: 'فصل', appendix: 'پیوست', errorTitle: 'بارگذاری محتوا ناموفق بود',
    errorBody: 'این کتابخوان فایل‌های مارک‌داون را با <code>fetch</code> می‌خواند و به یک وب‌سرور محلی نیاز دارد (بازکردن مستقیم <code>index.html</code> از دیسک کار نمی‌کند). بدون نیاز به اینترنت، پوشه را محلی سرو کنید:',
    searchHint: 'حداقل ۲ نویسه بنویسید. با / جست‌وجو، با Esc پاک کنید.',
    secList: 'در این فصل',
  },
};

/* ---------------- markdown ---------------- */

function inline(s) {
  return s
    .replace(/`([^`]+)`/g, (_, c) => '<code>' + c + '</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,!?:;]|$)/g, '$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t, u) =>
      '<a href="' + u + '"' + (u.startsWith('#') ? '' : ' target="_blank" rel="noopener"') + '>' + t + '</a>');
}

function renderCallout(lines, alreadyEscaped) {
  const first = lines[0] || '';
  const m = first.match(/^\[!(\w+)\]\s*(.*)$/);
  const type = m ? m[1].toLowerCase() : 'note';
  const title = m ? m[1] && (m[2] || '') : '';
  const body = (m ? lines.slice(1) : lines).map(esc);
  const cls = ['callout', 'callout-' + type, type === 'levels' ? 'levels' : ''].join(' ');
  const defTitle = { note: 'Note', tip: 'Tip', experiment: 'On your laptop', research: 'Research frontier', warning: 'Warning', levels: 'Five levels' }[type] || 'Note';
  return '<aside class="' + cls + '">' +
    '<strong class="co-title">' + esc(title || defTitle) + '</strong>' +
    mdToHtml(body.join('\n'), true) + '</aside>';
}

function mdToHtml(md, alreadyEscaped) {
  let lines = md.split('\n');
  if (!alreadyEscaped) lines = lines.map(esc);
  const out = [];
  let i = 0;
  const isCellRow = l => /^\|.*\|\s*$/.test(l);
  while (i < lines.length) {
    const L = lines[i];
    if (/^\s*```/.test(L)) {
      const lang = L.trim().slice(3);
      const body = [];
      i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) body.push(lines[i++]);
      i++;
      out.push('<pre' + (lang ? ' data-lang="' + lang + '"' : '') + '><code>' + body.join('\n') + '</code></pre>');
      continue;
    }
    if (isCellRow(L) && /^\|[\s:|-]+\|\s*$/.test(lines[i + 1] || '')) {
      const row = l => l.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
      const head = row(L); i += 2;
      const rows = [];
      while (i < lines.length && isCellRow(lines[i])) rows.push(row(lines[i++]));
      out.push('<table><thead><tr>' + head.map(c => '<th>' + inline(c) + '</th>').join('') +
        '</tr></thead><tbody>' + rows.map(r => '<tr>' + r.map(c => '<td>' + inline(c) + '</td>').join('') + '</tr>').join('') +
        '</tbody></table>');
      continue;
    }
    let m;
    if ((m = L.match(/^(#{1,6})\s+(.+)$/))) {
      const lvl = Math.min(m[1].length + 2, 6); // ### -> h4 inside a section
      out.push('<h' + lvl + '>' + inline(m[2]) + '</h' + lvl + '>'); i++; continue;
    }
    if (/^\s*(-{3,}|\*{3,})\s*$/.test(L)) { out.push('<hr>'); i++; continue; }
    if (/^(&gt;|>)\s?/.test(L)) {
      const body = [];
      while (i < lines.length && /^(&gt;|>)\s?/.test(lines[i])) body.push(lines[i++].replace(/^(&gt;|>)\s?/, ''));
      out.push(renderCallout(body, true));
      continue;
    }
    if (/^\s*[-*]\s+/.test(L)) {
      const items = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*[-*]\s+/, ''));
      out.push('<ul>' + items.map(t => '<li>' + inline(t) + '</li>').join('') + '</ul>');
      continue;
    }
    if (/^\s*\d+[.)]\s+/.test(L)) {
      const items = [];
      while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*\d+[.)]\s+/, ''));
      out.push('<ol>' + items.map(t => '<li>' + inline(t) + '</li>').join('') + '</ol>');
      continue;
    }
    if (/^\s*$/.test(L)) { i++; continue; }
    const body = [];
    while (i < lines.length && !/^\s*$/.test(lines[i]) &&
           !/^\s*(```|&gt;|>|#{1,6}\s|[-*]\s|\d+[.)]\s)/.test(lines[i]) &&
           !isCellRow(lines[i])) body.push(lines[i++]);
    if (body.length === 0 && i < lines.length) body.push(lines[i++]); // always make progress
    out.push('<p>' + inline(body.join(' ')) + '</p>');
  }
  return out.join('\n');
}

/* ---------------- part parsing ---------------- */

function plainText(md) {
  return md.replace(/```[\s\S]*?```/g, ' ')
    .replace(/[`*_[\]()>#|-]/g, ' ').replace(/\s+/g, ' ').trim();
}

function parsePart(raw) {
  const lines = raw.replace(/^﻿/, '').split(/\r?\n/);
  const part = { title: '', intro: [], chapters: [] };
  let cur = null, bucket = part.intro, sec = null;
  for (const line of lines) {
    let m;
    if ((m = line.match(/^#\s+(.+)$/))) { part.title = m[1].trim(); bucket = part.intro; continue; }
    if ((m = line.match(/^##\s+(.+)$/))) {
      cur = { title: m[1].trim(), num: null, intro: [], sections: [] };
      let nm = m[1].match(/^(\d+)\.\s*(.+)$/);
      if (nm) { cur.num = nm[1]; cur.title = nm[2].trim(); }
      else if ((nm = m[1].match(/^(?:Appendix|پیوست)\s+([A-Z])\s*[—–-]\s*(.+)$/i))) { cur.num = nm[1]; cur.title = nm[2].trim(); }
      part.chapters.push(cur);
      bucket = cur.intro; sec = null; continue;
    }
    if ((m = line.match(/^###\s+(.+)$/))) {
      if (!cur) continue;
      sec = { label: '', title: m[1].trim(), md: [] };
      const sm = m[1].match(/^(\d+(?:\.\d+)*)\s+(.+)$/);
      if (sm) { sec.label = sm[1]; sec.title = sm[2].trim(); }
      cur.sections.push(sec);
      bucket = sec.md; continue;
    }
    bucket.push(line);
  }
  part.introMd = part.intro.join('\n').trim();
  for (const ch of part.chapters) {
    ch.introMd = ch.intro.join('\n').trim();
    for (const s of ch.sections) {
      s.mdText = s.md.join('\n').trim();
      s.text = plainText(s.label + ' ' + s.title + ' ' + s.mdText);
    }
  }
  return part;
}

async function loadPart(lang, id) {
  if (state.parts[lang][id]) return state.parts[lang][id];
  const meta = state.manifest.parts.find(p => p.id === id);
  const res = await fetch('content/' + lang + '/' + meta.file);
  if (!res.ok) throw new Error('HTTP ' + res.status + ' for ' + meta.file);
  const part = parsePart(await res.text());
  state.parts[lang][id] = part;
  return part;
}

function allChapters(lang) {
  const out = [];
  for (const meta of state.manifest.parts) {
    const part = state.parts[lang][meta.id];
    if (!part) continue;
    part.chapters.forEach((ch, ci) => out.push({ meta, part, ch, ci, ordinal: out.length }));
  }
  return out;
}

/* ---------------- routing ---------------- */

function parseHash() {
  const h = location.hash.replace(/^#\/?/, '');
  const seg = h.split('/').filter(Boolean);
  const lang = (seg[0] === 'fa' || seg[0] === 'en') ? seg[0] : state.lang;
  if (!seg[1] || seg[1] === 'home') return { lang, view: 'home' };
  let m;
  if ((m = seg[1].match(/^p(\w+)$/))) {
    const id = state.manifest.parts.some(p => p.id === seg[1]) ? seg[1] : ('p' + m[1]);
    return { lang, view: 'part', partId: state.manifest.parts.some(p => p.id === id) ? id : null, view0: 'part' };
  }
  if ((m = seg[1].match(/^ch(\d+)(?:\.(\d+))?$/))) {
    return { lang, view: 'chapter', ordinal: parseInt(m[1], 10) - 1, sec: m[2] != null ? parseInt(m[2], 10) : null };
  }
  return { lang, view: 'home' };
}

function nav(hash) { location.hash = hash; }

/* ---------------- rendering ---------------- */

function applyLang() {
  document.documentElement.lang = state.lang;
  document.documentElement.dir = state.lang === 'fa' ? 'rtl' : 'ltr';
  $('#lang-btn').textContent = state.lang === 'en' ? 'فا' : 'EN';
  $('#search').placeholder = UI[state.lang].search;
  $('#topbar-title').textContent = state.manifest.title[state.lang];
}

function renderSidebar() {
  const lang = state.lang;
  const toc = $('#toc');
  const r = state.route || {};
  let html = '';
  for (const meta of state.manifest.parts) {
    const open = r.view === 'chapter' ? (r.chMeta && r.chMeta.meta.id === meta.id)
               : r.view === 'part' ? r.partId === meta.id : false;
    const t = meta.title[lang];
    html += '<div class="toc-part' + (open ? ' open' : '') + '" data-part="' + meta.id + '">' +
      '<button type="button"><span class="pnum">' + (meta.num ? meta.num : '¶') + '</span>' +
      '<span>' + esc(t) + '</span></button><div class="toc-chs">';
    const part = state.parts[lang][meta.id];
    if (part) {
      if (part.introMd) {
        html += '<a href="#/' + lang + '/' + meta.id + '"' + (r.view === 'part' && r.partId === meta.id ? ' class="active"' : '') + '>· ' + UI[lang].contents + '</a>';
      }
      for (const ch of part.chapters) {
        const ord = allChapters(lang).find(x => x.ch === ch);
        html += '<a href="#/' + lang + '/ch' + (ord ? ord.ordinal + 1 : '') + '">' +
          (ch.num ? esc(ch.num) + '. ' : '') + esc(ch.title) + '</a>';
      }
    } else if (open) {
      html += '<div class="toc-loading">…</div>';
    }
    html += '</div></div>';
  }
  if (r.view === 'chapter' && r.chMeta) {
    // mark active chapter link
    const target = r.chMeta.ordinal + 1;
    html = html.replace(new RegExp('(href="#/' + lang + '/ch' + target + '")'), '$1 class="active"');
  }
  toc.innerHTML = html;
  toc.querySelectorAll('.toc-part > button').forEach(btn => {
    btn.addEventListener('click', () => {
      const wrap = btn.parentElement;
      const wasOpen = wrap.classList.contains('open');
      toc.querySelectorAll('.toc-part.open').forEach(x => x.classList.remove('open'));
      if (!wasOpen) {
        wrap.classList.add('open');
        ensurePartInSidebar(wrap.dataset.part);
      }
    });
  });
}

async function ensurePartInSidebar(partId) {
  const lang = state.lang;
  if (state.parts[lang][partId]) { renderSidebar(); return; }
  try { await loadPart(lang, partId); } catch (e) { console.error(e); return; }
  renderSidebar();
  if (state.route && state.route.view === 'chapter') expandActivePart();
}

function expandActivePart() {
  const r = state.route;
  const id = r.view === 'chapter' ? (r.chMeta && r.chMeta.meta.id) : r.view === 'part' ? r.partId : null;
  if (!id) return;
  const wrap = $('#toc .toc-part[data-part="' + id + '"]');
  if (wrap && !wrap.classList.contains('open')) {
    wrap.classList.add('open');
    if (!state.parts[state.lang][id]) ensurePartInSidebar(id);
  }
}

function crumbHtml(parts) {
  return '<div class="crumb">' + parts.map(p =>
    p.href ? '<a href="' + p.href + '">' + esc(p.t) + '</a>' : '<span>' + esc(p.t) + '</span>'
  ).join('<span class="sep">›</span>') + '</div>';
}

function showLoading() {
  $('#content').innerHTML = '<p style="color:var(--muted)">…</p>';
}

function showError(e) {
  const u = UI[state.lang];
  $('#content').innerHTML = '<div class="err-panel"><h2 style="margin-top:0">' + u.errorTitle + '</h2>' +
    '<p>' + u.errorBody + '</p><pre><code>cd ' + (state.lang === 'fa' ? 'پوشهٔ کتاب' : 'docs') + ' &amp;&amp; python3 -m http.server 8080</code></pre>' +
    '<p style="color:var(--muted)">' + esc(String(e && e.message || e)) + '</p></div>';
}

/* ----- views ----- */

async function viewHome() {
  const lang = state.lang;
  showLoading();
  let homeHtml = '';
  try {
    const res = await fetch('content/' + lang + '/home.md');
    if (res.ok) homeHtml = mdToHtml(esc(await res.text()));
  } catch (_) { /* fall through to generated TOC */ }
  const cards = state.manifest.parts.map(p =>
    '<a href="#/' + lang + '/' + p.id + '"><span class="pnum">' + (p.num || '¶') + '</span><span>' +
    esc(p.title[lang]) + '</span></a>').join('');
  $('#content').innerHTML = homeHtml +
    '<h2>' + UI[lang].contents + '</h2><div class="part-cards">' + cards + '</div>';
  document.title = state.manifest.title[lang] + ' — ' + state.manifest.subtitle[lang];
}

async function viewPart(partId) {
  const lang = state.lang;
  showLoading();
  let part;
  try {
    part = await loadPart(lang, partId);
    // load every part so chapter ordinals are global, not part-local
    for (const meta of state.manifest.parts) await loadPart(lang, meta.id);
  }
  catch (e) { showError(e); return; }
  const meta = state.manifest.parts.find(p => p.id === partId);
  const chItems = part.chapters.map(ch => {
    const ord = allChapters(lang).find(x => x.ch === ch);
    return '<li><a href="#/' + lang + '/ch' + (ord ? ord.ordinal + 1 : '') + '"><span class="cnum">' +
      (ch.num ? esc(ch.num) : '¶') + '</span><span>' + esc(ch.title) + '</span></a></li>';
  }).join('');
  $('#content').innerHTML = crumbHtml([{ t: state.manifest.title[lang], href: '#/' + lang + '/home' }, { t: meta.title[lang] }]) +
    '<h1>' + esc(part.title || meta.title[lang]) + '</h1>' +
    (part.introMd ? mdToHtml(part.introMd) : '') +
    (chItems ? '<h2>' + UI[lang].contents + '</h2><ul class="ch-cards">' + chItems + '</ul>' : '');
  document.title = part.title + ' — ' + state.manifest.title[lang];
}

async function viewChapter(ordinal, secIdx) {
  const lang = state.lang;
  showLoading();
  // make sure every part before the target is loaded so ordinals are stable
  const metas = state.manifest.parts;
  try {
    for (const meta of metas) {
      await loadPart(lang, meta.id);
      const flat = allChapters(lang);
      if (flat.length > ordinal) break;
    }
  } catch (e) { showError(e); return; }
  const flat = allChapters(lang);
  const cur = flat[ordinal];
  if (!cur) { nav('#/' + lang + '/home'); return; }
  const { part, ch, meta } = cur;
  const chLabel = (ch.num && /^\d+$/.test(ch.num)) ? UI[lang].chapter + ' ' + ch.num
    : ch.num ? UI[lang].appendix + ' ' + ch.num : '';
  let html = crumbHtml([
    { t: state.manifest.title[lang], href: '#/' + lang + '/home' },
    { t: meta.title[lang], href: '#/' + lang + '/' + meta.id },
  ].concat(chLabel ? [{ t: chLabel }].map(x => ({ ...x, href: '#/' + lang + '/ch' + (ordinal + 1) })) : []));
  html += '<h1>' + (ch.num ? '<span style="color:var(--accent)">' + esc(ch.num) + '.</span> ' : '') + esc(ch.title) + '</h1>';
  if (ch.introMd) html += mdToHtml(ch.introMd);
  if (ch.sections.length > 1) {
    html += '<nav class="sec-nav">' + UI[lang].secList + ': ' + ch.sections.map((s, si) =>
      '<a href="#/' + lang + '/ch' + (ordinal + 1) + '.' + si + '">' + esc(s.label || (si + 1)) + '</a>').join(' ') + '</nav>';
  }
  ch.sections.forEach((s, si) => {
    html += '<section class="sec" id="sec-' + si + '"><h3>' +
      (s.label ? '<span class="secnum">' + esc(s.label) + '</span>' : '') + esc(s.title) + '</h3>' +
      mdToHtml(s.mdText) + '</section>';
  });
  const prev = flat[ordinal - 1], next = flat[ordinal + 1];
  html += '<nav class="pager">';
  html += prev ? '<a class="prev" href="#/' + lang + '/ch' + ordinal + '"><span class="pg-label">' + UI[lang].prev + '</span><span class="pg-title">' +
    (prev.ch.num ? esc(prev.ch.num) + '. ' : '') + esc(prev.ch.title) + '</span></a>' : '<span style="flex:1"></span>';
  html += next ? '<a class="next" href="#/' + lang + '/ch' + (ordinal + 2) + '"><span class="pg-label">' + UI[lang].next + '</span><span class="pg-title">' +
    (next.ch.num ? esc(next.ch.num) + '. ' : '') + esc(next.ch.title) + '</span></a>' : '<span style="flex:1"></span>';
  html += '</nav>';
  $('#content').innerHTML = html;
  document.title = (ch.num ? ch.num + '. ' : '') + ch.title + ' — ' + state.manifest.title[lang];
  state.route.chMeta = cur;
  if (secIdx != null) {
    const el = $('#sec-' + secIdx);
    if (el) requestAnimationFrame(() => {
      el.scrollIntoView();
      history.replaceState(null, '', '#/' + lang + '/ch' + (ordinal + 1) + '.' + secIdx);
    });
  }
}

/* ---------------- search ---------------- */

let searchTimer = null;
async function runSearch(q) {
  const lang = state.lang;
  const toc = $('#toc');
  if (q.trim().length < 2) { renderSidebar(); return; }
  $('#search-status').hidden = false;
  $('#search-status').textContent = UI[lang].indexing;
  try {
    await Promise.all(state.manifest.parts.map(p => loadPart(lang, p.id)));
  } catch (e) { $('#search-status').textContent = String(e.message || e); return; }
  const needle = q.trim().toLowerCase();
  const results = [];
  for (const meta of state.manifest.parts) {
    const part = state.parts[lang][meta.id];
    for (const ch of part.chapters) {
      for (let si = 0; si < ch.sections.length; si++) {
        const s = ch.sections[si];
        const hay = s.text.toLowerCase();
        const at = hay.indexOf(needle);
        if (at === -1) continue;
        const snip = s.text.slice(Math.max(0, at - 40), at + 90).replace(/</g, '&lt;');
        results.push({ meta, ch, si, s, snip, titleAt: (s.title + ' ' + s.label).toLowerCase().indexOf(needle) !== -1 });
      }
    }
  }
  results.sort((a, b) => (b.titleAt - a.titleAt));
  const top = results.slice(0, 40);
  $('#search-status').textContent = results.length + ' ' + UI[lang].results;
  toc.innerHTML = '<div class="search-results">' +
    (top.length ? top.map(r => {
      const ord = allChapters(lang).find(x => x.ch === r.ch);
      const href = '#/' + lang + '/ch' + (ord ? ord.ordinal + 1 : '') + '.' + r.si;
      const marked = esc(r.snip).replace(new RegExp(needle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), m => '<mark>' + m + '</mark>');
      return '<a class="sr" href="' + href + '"><span class="sr-where">' +
        (r.ch.num ? esc(r.ch.num) + '. ' : '') + esc(r.ch.title) + (r.s.label ? ' · ' + esc(r.s.label) : '') + '</span><br>' +
        '<span class="sr-snip">…' + marked + '…</span></a>';
    }).join('') : '<div class="toc-loading">' + UI[lang].noResults + '</div>') +
    '<div class="toc-loading">' + UI[lang].searchHint + '</div></div>';
}

/* ---------------- boot ---------------- */

async function render() {
  const r = parseHash();
  if (r.lang !== state.lang) { state.lang = r.lang; localStorage.setItem('tqe:lang', state.lang); }
  state.route = r;
  applyLang();
  document.body.classList.remove('nav-open');
  $('#search').value = '';
  $('#search-status').hidden = true;
  if (r.view === 'home') { renderSidebar(); await viewHome(); }
  else if (r.view === 'part') { renderSidebar(); await viewPart(r.partId); }
  else if (r.view === 'chapter') { renderSidebar(); await viewChapter(r.ordinal, r.sec); }
  expandActivePart();
  $('#main').scrollTop = 0; window.scrollTo(0, 0);
}

async function boot() {
  document.documentElement.dataset.theme = state.theme;
  try {
    const res = await fetch('content/manifest.json');
    if (!res.ok) throw new Error('manifest: HTTP ' + res.status);
    state.manifest = await res.json();
  } catch (e) { showError(e); return; }
  applyLang();
  window.addEventListener('hashchange', render);
  $('#lang-btn').addEventListener('click', () => {
    state.lang = state.lang === 'en' ? 'fa' : 'en';
    localStorage.setItem('tqe:lang', state.lang);
    const r = parseHash();
    nav('#/' + state.lang + (r.view === 'chapter' ? '/ch' + (r.ordinal + 1) + (r.sec != null ? '.' + r.sec : '')
      : r.view === 'part' && r.partId ? '/' + r.partId : '/home'));
  });
  $('#theme-btn').addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('tqe:theme', state.theme);
    document.documentElement.dataset.theme = state.theme;
  });
  $('#menu-btn').addEventListener('click', () => document.body.classList.toggle('nav-open'));
  $('#scrim').addEventListener('click', () => document.body.classList.remove('nav-open'));
  $('#search').addEventListener('input', e => {
    clearTimeout(searchTimer);
    const q = e.target.value;
    searchTimer = setTimeout(() => runSearch(q), 180);
  });
  $('#search').addEventListener('keydown', e => {
    if (e.key === 'Escape') { e.target.value = ''; renderSidebar(); $('#search-status').hidden = true; }
  });
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement !== $('#search')) { e.preventDefault(); $('#search').focus(); }
  });
  if (!location.hash) nav('#/' + state.lang + '/home');
  await render();
}

boot();
