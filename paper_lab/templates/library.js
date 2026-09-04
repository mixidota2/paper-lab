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
  form.addEventListener("input", update);
  form.addEventListener("change", update);
  clear.addEventListener("click", () => { form.reset(); update(); search.focus(); });
  update();
})();
