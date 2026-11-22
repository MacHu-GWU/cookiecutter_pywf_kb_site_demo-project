// Type-as-you-search for the sidebar search box, backed by Pagefind
// (https://pagefind.app). Pagefind's static index is built after
// sphinx-build into pagefind/ (see build-doc.sh). Needs http(s): on file://
// the import fails and the box falls back to Sphinx's own search page.
(function () {
  "use strict";

  const MAX_RESULTS = 8;
  // Pagefind ranks full text (H1 weight 7, H2 6, H3 5, body 1). Its top
  // CANDIDATES are reranked here so that a title containing the query wins.
  const CANDIDATES = 30;
  // The one piece of UI text, picked by <html lang> (Sphinx's `language`).
  const NO_RESULTS = { zh: "没有结果" };
  const noResults = NO_RESULTS[document.documentElement.lang.slice(0, 2)] || "No results";
  let pagefind = null;
  let panel = null;
  let items = [];
  let active = -1;

  function escapeHtml(s) {
    return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  }

  function escapeRegExp(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  // Query terms, longest first: the whole query, then its space separated words.
  function queryTerms(query) {
    const words = query.split(/\s+/).filter(Boolean);
    return [...new Set([query, ...words])].sort((a, b) => b.length - a.length);
  }

  // How well the title matches, a plain substring test (case-insensitive) that
  // does not depend on how Chinese text was segmented:
  // 2 = contains the whole query, 1 = contains every word, 0 = otherwise.
  function titleRank(title, query) {
    const t = title.toLowerCase();
    const q = query.toLowerCase();
    if (t.includes(q)) return 2;
    const words = q.split(/\s+/).filter(Boolean);
    return words.length > 1 && words.every((w) => t.includes(w)) ? 1 : 0;
  }

  function highlightTitle(title, query) {
    const pattern = queryTerms(query).map(escapeRegExp).join("|");
    const re = new RegExp(`(${pattern})`, "gi");
    return title
      .split(re)
      .map((part, i) => (i % 2 === 1 ? `<mark>${escapeHtml(part)}</mark>` : escapeHtml(part)))
      .join("");
  }

  async function loadPagefind(form) {
    if (pagefind) return pagefind;
    const url = new URL(form.dataset.pagefind, window.location.href).href;
    pagefind = await import(url);
    await pagefind.options({ excerptLength: 24 });
    pagefind.init();
    return pagefind;
  }

  function placePanel(input) {
    const r = input.getBoundingClientRect();
    panel.style.top = `${r.bottom + 4}px`;
    panel.style.left = `${r.left}px`;
  }

  function hidePanel() {
    if (panel) panel.hidden = true;
    items = [];
    active = -1;
  }

  function setActive(i) {
    items.forEach((el, j) => el.classList.toggle("kb-search-active", j === i));
    active = i;
    if (items[i]) items[i].scrollIntoView({ block: "nearest" });
  }

  function render(input, results, query) {
    if (!results.length) {
      panel.innerHTML = `<div class="kb-search-empty">${noResults}: ${escapeHtml(query)}</div>`;
    } else {
      panel.innerHTML = results
        .map((r) => {
          // Prefer the best matching section, so the link lands on the heading.
          const sub = (r.sub_results || []).find((s) => s.url !== r.url);
          const url = sub ? sub.url : r.url;
          const section = sub && sub.title !== r.meta.title ? ` <span class="kb-search-section">› ${escapeHtml(sub.title)}</span>` : "";
          return `<a class="kb-search-item" href="${url}">
              <div class="kb-search-title">${highlightTitle(r.meta.title || r.url, query)}${section}</div>
              <div class="kb-search-excerpt">${(sub || r).excerpt}</div>
            </a>`;
        })
        .join("");
    }
    items = Array.from(panel.querySelectorAll(".kb-search-item"));
    active = -1;
    placePanel(input);
    panel.hidden = false;
  }

  async function onInput(form, input) {
    const query = input.value.trim();
    if (!query) return hidePanel();
    let pf;
    try {
      pf = await loadPagefind(form);
    } catch (e) {
      return; // no Pagefind index (file:// or not built): keep the plain search box
    }
    const search = await pf.debouncedSearch(query, {}, 150);
    if (search === null) return; // superseded by a newer keystroke
    const titles = await loadTitles(form);
    const fullText = await Promise.all(search.results.slice(0, CANDIDATES).map((r) => r.data()));
    if (input.value.trim() === query) render(input, merge(titles, fullText, query), query);
  }

  // kb-titles.json (written by the Sphinx extension): [{title, url, description}].
  let titlesPromise = null;
  function loadTitles(form) {
    if (!titlesPromise) {
      const url = new URL(form.dataset.titles, window.location.href).href;
      titlesPromise = fetch(url)
        .then((r) => (r.ok ? r.json() : []))
        .catch(() => []);
    }
    return titlesPromise;
  }

  // Title substring hits first (whole query, then all words; shorter title =
  // closer match), then Pagefind's full text ranking for the rest.
  function merge(titles, fullText, query) {
    const byUrl = new Map(fullText.map((r) => [r.url, r]));
    const titleHits = titles
      .map((t) => ({ t, rank: titleRank(t.title, query) }))
      .filter((x) => x.rank > 0)
      .sort((a, b) => b.rank - a.rank || a.t.title.length - b.t.title.length)
      .map(({ t }) => byUrl.get(t.url) || { url: t.url, meta: { title: t.title }, excerpt: escapeHtml(t.description || "") });
    const seen = new Set(titleHits.map((r) => r.url));
    const rest = fullText.filter((r) => !seen.has(r.url));
    return [...titleHits, ...rest].slice(0, MAX_RESULTS);
  }

  function setup() {
    const form = document.querySelector("form.sidebar-search-container[data-pagefind]");
    if (!form) return;
    const input = form.querySelector("input.sidebar-search");
    panel = document.createElement("div");
    panel.className = "kb-search-panel";
    panel.hidden = true;
    document.body.appendChild(panel);

    input.addEventListener("input", () => onInput(form, input));
    input.addEventListener("focus", () => input.value.trim() && onInput(form, input));
    input.addEventListener("keydown", (e) => {
      if (panel.hidden) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActive(Math.min(active + 1, items.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setActive(Math.max(active - 1, 0));
      } else if (e.key === "Enter" && items[active]) {
        e.preventDefault();
        window.location.href = items[active].href;
      } else if (e.key === "Escape") {
        hidePanel();
      }
    });
    document.addEventListener("click", (e) => {
      if (!panel.contains(e.target) && e.target !== input) hidePanel();
    });
    window.addEventListener("resize", () => panel.hidden || placePanel(input));
  }

  document.addEventListener("DOMContentLoaded", setup);
})();
