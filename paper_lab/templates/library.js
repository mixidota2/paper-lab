(() => {
  const form = document.querySelector("[data-library-controls]");
  if (!form) return;
  const cards = [...document.querySelectorAll("[data-paper]")];
  const count = document.querySelector("[data-result-count]");
  const empty = document.querySelector("[data-empty]");
  const search = form.elements.search;
  const topic = form.elements.topic;
  const verdict = form.elements.verdict;
  const sort = form.elements.sort;
  const clear = form.querySelector("[data-clear]");

  const controls = { search, topic, verdict, sort };
  const defaults = { search: "", topic: "", verdict: "", sort: "date" };
  const urlStatus = document.querySelector("[data-filter-url-status]");
  const browser = typeof window === "undefined" ? null : window;
  let urlWritable = true;
  let composing = false;
  const readingPanel = document.querySelector("[data-reading-list]");
  const readingSave = document.querySelector("[data-reading-save]");
  const readingSaveText = document.querySelector("[data-reading-save-text]");
  const readingLabel = document.querySelector("[data-reading-label]");
  const readingPreview = document.querySelector("[data-reading-preview]");
  const readingText = document.querySelector("[data-reading-json]");
  const readingStatus = document.querySelector("[data-reading-status]");
  const readingImport = document.querySelector("[data-reading-import]");
  const readingImportStatus = document.querySelector("[data-reading-import-status]");
  let importRequest = 0;
  let readingCards = [];
  let readingFilters = { ...defaults };

  function cancelReadingImport() {
    // A delayed file read must not overwrite a newer edit, navigation or file.
    importRequest += 1;
    if (readingImport) readingImport.value = "";
    if (readingImportStatus) readingImportStatus.textContent = "";
  }

  async function restoreReadingFilters() {
    const file = readingImport.files && readingImport.files[0];
    cancelReadingImport();
    if (!file) return;
    if (composing) {
      readingImportStatus.textContent = "日本語入力を確定してから、JSONを選び直してください。";
      return;
    }
    const request = importRequest;
    readingImportStatus.textContent = "保存済みの検索条件を読み込んでいます。";
    try {
      // Only the four known filter strings are applied. Imported titles, HTML,
      // URLs and other fields are never rendered, followed or fetched.
      const maxBytes = 2 * 1024 * 1024;
      if (!Number.isFinite(file.size) || file.size < 0 || file.size > maxBytes) throw Error("size");
      const text = await file.text();
      if (typeof text !== "string" || text.length > maxBytes) throw Error("size");
      const saved = JSON.parse(text.replace(/^\uFEFF/, ""));
      const filters = saved && saved.filters;
      if (!saved || saved.kind !== "paper-lab-reading-list" || saved.schema_version !== 1
        || !filters || Array.isArray(filters) || typeof filters !== "object"
        || Object.keys(filters).length !== Object.keys(controls).length) throw Error("format");
      for (const [name, control] of Object.entries(controls)) {
        if (!Object.prototype.hasOwnProperty.call(filters, name) || typeof filters[name] !== "string"
          || (name !== "search" && ![...control.options].some((option) => option.value === filters[name]))) {
          throw Error("filter");
        }
      }
      if (request !== importRequest || composing) return;
      Object.entries(controls).forEach(([name, control]) => { control.value = filters[name]; });
      update();
      writeURL();
      readingImportStatus.textContent = `検索条件を戻しました。現在のLabから選んだ結果は${readingCards.length}件です。`;
    } catch (_) {
      if (request !== importRequest) return;
      readingImportStatus.textContent = "検索条件を読み込めませんでした。このライブラリで保存した2 MiB以下のJSONを選んでください。現在の条件は変更していません。";
    }
  }

  function clearReadingSnapshot() {
    if (!readingPanel) return;
    readingText.value = "";
    readingPreview.open = false;
    readingStatus.textContent = "";
    readingSave.disabled = composing || readingCards.length === 0;
    if (readingSaveText) readingSaveText.disabled = readingSave.disabled;
  }

  function optionLabel(control, value) {
    const option = [...control.options].find((item) => item.value === value);
    return option ? option.textContent || value : value;
  }

  function readingListText(payload) {
    // Keep free-form search on one labelled line, including newlines or quotes.
    // Paper fields use the same whitespace collapsing as the visible HTML.
    const line = (value) => String(value).replace(/\s+/g, " ").trim();
    const lines = [
      "研究ライブラリ 読書リスト",
      `表示件数: ${payload.paper_count}件`,
      `検索語: ${JSON.stringify(payload.filters.search)}`,
      `テーマ: ${optionLabel(topic, payload.filters.topic) || "すべて"}`,
      `読む優先度: ${optionLabel(verdict, payload.filters.verdict) || "すべて"}`,
      `並べ替え: ${optionLabel(sort, payload.filters.sort)}`,
      "",
      payload.note.replace("lab_pathは", "Lab 相対パスは"),
      "",
    ];
    payload.papers.forEach((paper, index) => {
      lines.push(
        `${index + 1}. ${line(paper.title)}`,
        `問い: ${line(paper.question)}`,
        `テーマ: ${paper.topics.map((value) => optionLabel(topic, value)).join("、")}`,
        `読む優先度: ${paper.reading_priority} / 発表・公開時期: ${paper.published_date}`,
        `${paper.lab_url ? "Lab URL" : "Lab 相対パス"}: ${paper.lab_url || paper.lab_path}`,
        "",
      );
    });
    return lines.join("\n");
  }

  function saveReadingList(format = "json") {
    // IME drafts and empty results must never export a different visible list.
    if (composing || readingCards.length === 0) return;
    let base = null;
    try {
      const current = new URL(browser.location.href);
      if (["https:", "http:"].includes(current.protocol)) {
        current.username = ""; current.password = "";
        base = new URL(".", current);
      }
    } catch (_) {} // Local files and restricted URLs retain portable lab paths.
    const papers = readingCards.map((card) => {
      const link = card.querySelector("h3 a");
      const path = link.getAttribute("href");
      return {
        id: path.split("/").pop().replace(/\.html$/, ""),
        title: card.querySelector(".paper-title").textContent.trim(),
        question: link.textContent.trim(),
        topics: card.dataset.topics.split("|"),
        reading_priority: card.dataset.verdict,
        published_date: card.dataset.date,
        lab_path: path,
        lab_url: base ? new URL(path, base).href : null,
      };
    });
    const payload = {
      schema_version: 1,
      kind: "paper-lab-reading-list",
      filters: { ...readingFilters },
      paper_count: papers.length,
      papers,
      note: "表示中のLabを表示順に保存した読書リストです。読む優先度は本サイトの読書判断であり、性能順位ではありません。日付は論文の発表・公開時期です。論文本文や実験データは含みません。lab_pathはライブラリ先頭からの相対パスです。",
    };
    const plain = format === "text";
    const kind = plain ? "テキスト" : "JSON";
    const text = plain ? readingListText(payload) : JSON.stringify(payload, null, 2);
    if (readingLabel) readingLabel.textContent = `表示中の読書リストの保存用${kind}`;
    readingText.value = text;
    readingPreview.open = true;
    let url;
    try {
      url = URL.createObjectURL(new Blob([text], { type: plain ? "text/plain;charset=utf-8" : "application/json" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = plain ? "paper-lab-reading-list.txt" : "paper-lab-reading-list.json";
      link.click();
      readingStatus.textContent = `${papers.length}件の保存用${kind}を用意しました。ファイルがダウンロードされない場合は、下の欄からコピーして保存してください。`;
    } catch (_) {
      readingStatus.textContent = "ファイルのダウンロードを開始できませんでした。下の欄からコピーして保存してください。";
    } finally {
      if (url) setTimeout(() => { try { URL.revokeObjectURL(url); } catch (_) {} }, 1000);
    }
  }

  function searchKey(text) {
    // Match Japanese width variants and composed characters without rewriting
    // the user's input, the saved URL, or the displayed paper text.
    return text.normalize("NFKC").toLocaleLowerCase("ja");
  }
  const searchText = new Map(cards.map((card) => [card, searchKey(card.dataset.search || "")]));

  function showURLStatus(saved) {
    if (!urlStatus) return;
    urlStatus.hidden = false;
    const message = saved
      ? "検索語・絞り込み・並べ替えはURLに残ります。このURLを保存すると、同じ条件で開けます。"
      : "この環境では条件をURLに残せません。画面内の検索・絞り込みは引き続き使えます。";
    if (urlStatus.textContent !== message) urlStatus.textContent = message;
  }

  function readURL() {
    if (!browser) return;
    try {
      const params = new URL(browser.location.href).searchParams;
      Object.entries(controls).forEach(([name, control]) => {
        const value = params.get(name);
        control.value = value !== null && (name === "search"
          || [...control.options].some((option) => option.value === value))
          ? value : defaults[name];
      });
    } catch (_) {
      // A restricted or unavailable URL must not disable in-page filtering.
      urlWritable = false;
    }
  }

  function writeURL() {
    if (!browser || !urlWritable) return;
    try {
      const url = new URL(browser.location.href);
      Object.entries(controls).forEach(([name, control]) => {
        url.searchParams.delete(name);
        if (control.value !== defaults[name]) url.searchParams.set(name, control.value);
      });
      // Replace this entry instead of adding a Back step for every edit.
      if (url.href !== browser.location.href) {
        browser.history.replaceState(browser.history.state, "", url.href);
      }
      showURLStatus(true);
    } catch (_) {
      urlWritable = false;
      showURLStatus(false);
    }
  }

  function update() {
    const query = searchKey(search.value).trim();
    const matching = cards.filter((card) => {
      const text = searchText.get(card);
      return (!query || text.includes(query))
        && (!topic.value || card.dataset.topics.split("|").includes(topic.value))
        && (!verdict.value || card.dataset.verdict === verdict.value);
    });
    cards.forEach((card) => { card.hidden = !matching.includes(card); });
    matching.sort((a, b) => {
      if (sort.value === "title") return a.dataset.title.localeCompare(b.dataset.title);
      if (sort.value === "date") return b.dataset.date.localeCompare(a.dataset.date);
      return Number(b.dataset.priority) - Number(a.dataset.priority);
    }).forEach((card) => card.parentElement.append(card));
    readingCards = matching;
    readingFilters = Object.fromEntries(Object.entries(controls).map(([name, control]) => [name, control.value]));
    clearReadingSnapshot();
    count.textContent = `${matching.length}件`;
    empty.hidden = matching.length !== 0;
  }
  function edit(event) {
    cancelReadingImport();
    // IME conversion text is a draft, including Enter used to confirm it.
    // Keep the saved URL and visible results stable until conversion commits.
    if (event && event.isComposing) { composing = true; clearReadingSnapshot(); }
    if (composing) return;
    update();
    writeURL();
  }
  function restore() { cancelReadingImport(); composing = false; readURL(); update(); }
  form.addEventListener("compositionstart", () => { cancelReadingImport(); composing = true; clearReadingSnapshot(); });
  form.addEventListener("compositionend", () => { composing = false; edit(); });
  form.addEventListener("submit", (event) => { event.preventDefault(); edit(event); });
  form.addEventListener("input", edit);
  form.addEventListener("change", edit);
  clear.addEventListener("click", () => { composing = false; form.reset(); edit(); search.focus(); });
  if (browser) {
    browser.addEventListener("popstate", restore);
    browser.addEventListener("pageshow", (event) => {
      // BFCache can revive form controls after initialization. The saved URL wins,
      // unless this environment could not record the user's more recent edits.
      if (!event.persisted) return;
      if (urlWritable) restore();
      else {
        // A restored page has no active conversion session. Keep its displayed
        // controls, rather than replacing unsaved edits from an older URL.
        cancelReadingImport();
        composing = false;
        update();
      }
    });
  }
  restore();
  if (readingPanel) {
    readingSave.addEventListener("click", () => saveReadingList());
    if (readingSaveText) readingSaveText.addEventListener("click", () => saveReadingList("text"));
    readingPanel.hidden = false;
  }
  if (readingImport && readingImportStatus) {
    readingImport.addEventListener("change", restoreReadingFilters);
    readingImport.addEventListener("cancel", cancelReadingImport);
  }
  if (!urlWritable) showURLStatus(false);
})();
