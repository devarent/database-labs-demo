const state = {
  engines: [],
  q: "",
  category: "",
  runtime: "",
};

const els = {
  grid: document.querySelector("#grid"),
  empty: document.querySelector("#empty"),
  search: document.querySelector("#search"),
  category: document.querySelector("#category"),
  categoryOptions: document.querySelector("#category-options"),
  resultCount: document.querySelector("#result-count"),
  stats: document.querySelector("#stats"),
  dialog: document.querySelector("#engine-dialog"),
  form: document.querySelector("#engine-form"),
  formError: document.querySelector("#form-error"),
  openForm: document.querySelector("#open-form"),
  cancel: document.querySelector("#cancel"),
  toast: document.querySelector("#toast"),
};

const runtimeButtons = [...document.querySelectorAll("[data-runtime]")];

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`);
  }
  return data;
}

function filteredEngines() {
  const needle = state.q.trim().toLowerCase();
  return state.engines.filter((engine) => {
    if (state.category && engine.category !== state.category) return false;
    if (state.runtime && engine.runtime !== state.runtime) return false;
    if (!needle) return true;
    return `${engine.name} ${engine.category}`.toLowerCase().includes(needle);
  });
}

function engineCard(engine) {
  const card = el("article", "card");

  const top = el("div", "card-top");
  top.append(el("span", "badge", engine.category));
  top.append(el("span", `badge ${engine.runtime}`, engine.runtime === "docker" ? "Docker" : "Cloud"));

  const title = el("h2", "", engine.name);
  const notes = el("p", "", engine.notes || "No notes yet.");

  const actions = el("div", "card-actions");
  const link = el("a", "", "Open lab ↗");
  if (/^https?:\/\//i.test(engine.repo_url)) {
    link.href = engine.repo_url;
  } else {
    link.href = "#";
  }
  link.target = "_blank";
  link.rel = "noopener noreferrer";

  const remove = el("button", "", "Delete");
  remove.type = "button";
  remove.setAttribute("aria-label", `Delete ${engine.name}`);
  remove.addEventListener("click", async () => {
    if (!window.confirm(`Delete ${engine.name} from the live index?`)) return;
    remove.disabled = true;
    try {
      await api(`/api/engines/${engine.id}`, { method: "DELETE" });
      state.engines = state.engines.filter((item) => item.id !== engine.id);
      render();
      await refreshStats();
      toast(`${engine.name} deleted`);
    } catch (error) {
      remove.disabled = false;
      toast(error.message);
    }
  });

  actions.append(link, remove);
  card.append(top, title, notes, actions);
  return card;
}

function render() {
  const rows = filteredEngines();
  els.grid.replaceChildren(...rows.map(engineCard));
  els.grid.setAttribute("aria-busy", "false");
  els.empty.hidden = rows.length !== 0;
  els.resultCount.textContent = `${rows.length} of ${state.engines.length} labs`;
}

function updateStats(stats) {
  for (const [key, value] of Object.entries(stats)) {
    const node = els.stats.querySelector(`[data-stat="${key}"]`);
    if (node) node.textContent = value;
  }
}

async function refreshStats() {
  try {
    updateStats(await api("/api/stats"));
  } catch {
    /* the list still works if the stats endpoint hiccups */
  }
}

function populateCategories(categories) {
  const current = els.category.value;
  els.category.replaceChildren(el("option", "", "All categories"));
  els.category.firstElementChild.value = "";
  for (const category of categories) {
    const option = el("option", "", category);
    option.value = category;
    els.category.append(option);
  }
  els.category.value = categories.includes(current) ? current : "";

  els.categoryOptions.replaceChildren(
    ...categories.map((category) => {
      const option = document.createElement("option");
      option.value = category;
      return option;
    }),
  );
}

let toastTimer;
function toast(message) {
  els.toast.textContent = message;
  els.toast.hidden = false;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    els.toast.hidden = true;
  }, 3200);
}

async function load() {
  try {
    const [engines, stats, categories] = await Promise.all([
      api("/api/engines"),
      api("/api/stats"),
      api("/api/categories"),
    ]);
    state.engines = engines;
    populateCategories(categories);
    updateStats(stats);
    render();
  } catch (error) {
    els.grid.setAttribute("aria-busy", "false");
    els.empty.hidden = false;
    els.empty.textContent = `Cannot reach the API: ${error.message}`;
  }
}

els.search.addEventListener("input", () => {
  state.q = els.search.value;
  render();
});

els.category.addEventListener("change", () => {
  state.category = els.category.value;
  render();
});

for (const button of runtimeButtons) {
  button.addEventListener("click", () => {
    state.runtime = button.dataset.runtime || "";
    for (const other of runtimeButtons) other.classList.toggle("active", other === button);
    render();
  });
}

els.openForm.addEventListener("click", () => {
  els.formError.hidden = true;
  els.dialog.showModal();
  els.form.elements.name.focus();
});

els.cancel.addEventListener("click", () => els.dialog.close());

els.dialog.addEventListener("click", (event) => {
  if (event.target === els.dialog) els.dialog.close();
});

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(els.form).entries());
  payload.notes = payload.notes || "";
  const submit = els.form.querySelector('button[type="submit"]');
  submit.disabled = true;
  els.formError.hidden = true;

  try {
    const created = await api("/api/engines", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.engines.push(created);
    state.engines.sort(
      (a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name),
    );
    els.dialog.close();
    els.form.reset();
    render();
    await refreshStats();
    toast(`${created.name} added`);
  } catch (error) {
    els.formError.textContent = error.message;
    els.formError.hidden = false;
  } finally {
    submit.disabled = false;
  }
});

load();
