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
    const query = search.value.trim().toLocaleLowerCase("ja");
    const matching = cards.filter((card) => {
      const text = card.dataset.search || "";
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
    count.textContent = `${matching.length}件`;
    empty.hidden = matching.length !== 0;
  }
  function edit() { update(); writeURL(); }
  function restore() { readURL(); update(); }
  form.addEventListener("submit", (event) => { event.preventDefault(); edit(); });
  form.addEventListener("input", edit);
  form.addEventListener("change", edit);
  clear.addEventListener("click", () => { form.reset(); edit(); search.focus(); });
  if (browser) {
    browser.addEventListener("popstate", restore);
    browser.addEventListener("pageshow", (event) => {
      // BFCache can revive form controls after initialization. The saved URL wins,
      // unless this environment could not record the user's more recent edits.
      if (event.persisted && urlWritable) restore();
    });
  }
  restore();
  if (!urlWritable) showURLStatus(false);
})();
