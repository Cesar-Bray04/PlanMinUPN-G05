(() => {
  "use strict";
  const data = window.G05_DATA;
  if (!data) {
    document.body.textContent = "No se pudo cargar el resumen local del proyecto G05.";
    return;
  }
  const number = new Intl.NumberFormat("es-PE");
  const screens = [...document.querySelectorAll(".screen")];
  const links = [...document.querySelectorAll("#main-nav a")];

  function valueAt(path) {
    return path.split(".").reduce((value, key) => value && value[key], data);
  }
  document.querySelectorAll("[data-value]").forEach((element) => {
    const value = valueAt(element.dataset.value);
    if (value !== undefined && value !== null) element.textContent = typeof value === "number" ? number.format(value) : value;
  });

  function showScreen() {
    const requested = decodeURIComponent(location.hash.slice(1));
    const target = screens.some((screen) => screen.id === requested) ? requested : "proyecto";
    screens.forEach((screen) => { screen.hidden = screen.id !== target; });
    links.forEach((link) => {
      const active = link.dataset.target === target;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    window.scrollTo({ top: 0, behavior: "instant" });
  }
  addEventListener("hashchange", showScreen);
  showScreen();

  const drillFrame = document.getElementById("hero-drill-frame");
  addEventListener("message", (event) => {
    if (drillFrame && event.source === drillFrame.contentWindow && event.data?.kind === "g05-sondajes-3d-ready") {
      document.querySelector(".hero-drill-visual").classList.add("is-ready");
    }
  });
  drillFrame?.addEventListener("load", () => {
    drillFrame.contentWindow?.postMessage({ kind: "g05-sondajes-3d-check" }, "*");
  });

  function makeBar(group, max, count, type) {
    const line = document.createElement("div");
    line.className = "chart-group";
    const label = document.createElement("strong");
    label.textContent = group;
    const track = document.createElement("div");
    track.className = "chart-track";
    const fill = document.createElement("div");
    fill.className = `chart-fill ${type}`;
    fill.style.width = `${(count / max) * 100}%`;
    track.append(fill);
    const output = document.createElement("output");
    output.textContent = number.format(count);
    line.append(label, track, output);
    return line;
  }
  const campaigns = data.exploration.campaigns;
  const campaignChart = document.getElementById("campaign-chart");
  const chartSections = [
    ["SONDAJES", "sondajes", "holes"],
    ["ENSAYES", "ensayes", "assays"]
  ];
  for (const [heading, field, color] of chartSections) {
    const title = document.createElement("div");
    title.className = "chart-subheading";
    title.textContent = heading;
    campaignChart.append(title);
    const max = Math.max(...campaigns.map((campaign) => campaign[field]));
    campaigns.forEach((campaign) => {
      campaignChart.append(makeBar(campaign.id.replace("CAMPAIGN_", "Camp. "), max, campaign[field], color));
    });
  }
  const campaignTable = document.getElementById("campaign-table");
  campaigns.forEach((campaign) => {
    const row = document.createElement("tr");
    for (const field of ["id", "sondajes", "survey", "ensayes", "litologia", "densidad"]) {
      const cell = document.createElement("td");
      cell.textContent = field === "id" ? campaign.id.replace("CAMPAIGN_", "Campaña ") : number.format(campaign[field]);
      row.append(cell);
    }
    campaignTable.append(row);
  });

  const topo = data.model.topography;
  const total = data.model.block_count;
  const pRock = topo.ROCK / total * 100;
  const pAir = (topo.ROCK + topo.AIR) / total * 100;
  const donut = document.getElementById("topo-donut");
  donut.style.background = `conic-gradient(var(--rock) 0 ${pRock}%,var(--air) ${pRock}% ${pAir}%,var(--partial) ${pAir}% 100%)`;
  donut.setAttribute("aria-label", `ROCK ${number.format(topo.ROCK)}, AIR ${number.format(topo.AIR)}, PARTIAL ${number.format(topo.PARTIAL)} de ${number.format(total)} bloques`);
  const topoLegend = document.getElementById("topo-legend");
  for (const [status, css] of [["ROCK", "rock"], ["AIR", "air"], ["PARTIAL", "partial"]]) {
    const row = document.createElement("div");
    row.className = "legend-item";
    const dot = document.createElement("i");
    dot.style.background = `var(--${css})`;
    const label = document.createElement("span");
    label.textContent = status;
    const count = document.createElement("b");
    count.textContent = number.format(topo[status]);
    row.append(dot, label, count);
    topoLegend.append(row);
  }
  const assigned = data.model.lithology.ASSIGNED;
  const unknown = data.model.lithology["UNKNOWN/UNASSIGNED"];
  const assignment = document.getElementById("assignment-chart");
  const assignedPart = document.createElement("div");
  assignedPart.className = "assigned-part";
  assignedPart.style.width = `${assigned / total * 100}%`;
  const unknownPart = document.createElement("div");
  unknownPart.className = "unknown-part";
  unknownPart.style.width = `${unknown / total * 100}%`;
  assignment.append(assignedPart, unknownPart);
  const assignmentLabels = document.createElement("div");
  assignmentLabels.className = "assignment-labels";
  assignmentLabels.innerHTML = `<span><strong>${number.format(assigned)}</strong> asignados</span><span><strong>${number.format(unknown)}</strong> sin asignar</span>`;
  assignment.after(assignmentLabels);
  const codeList = document.getElementById("lith-code-list");
  for (const code of ["BRX", "OVB", "POR", "VOL"]) {
    const card = document.createElement("div");
    const heading = document.createElement("strong");
    heading.textContent = code;
    const count = document.createElement("span");
    count.textContent = `${number.format(data.model.assigned_codes[code])} bloques`;
    card.append(heading, count);
    codeList.append(card);
  }

  const example = data.compositing.example;
  function makeTimeline(id, intervals, kind) {
    const track = document.getElementById(id);
    const [start, end] = example.window_m;
    const span = end - start;
    for (const interval of intervals) {
      const from = Number(interval.from_m);
      const to = Number(interval.to_m);
      const clippedFrom = Math.max(from, start);
      const clippedTo = Math.min(to, end);
      if (clippedTo <= clippedFrom) continue;
      const bar = document.createElement("div");
      bar.className = `segment ${kind === "assay" ? "assay" : interval.lith_code.toLowerCase()} ${interval.residual_flag === "true" ? "residual" : ""}`;
      bar.style.left = `${(clippedFrom - start) / span * 100}%`;
      bar.style.width = `calc(${(clippedTo - clippedFrom) / span * 100}% - 2px)`;
      bar.textContent = `${Number(from).toLocaleString("es-PE")}–${Number(to).toLocaleString("es-PE")} m`;
      bar.title = kind === "assay"
        ? `${interval.sample_id} · Cu ${interval.cu_pct} % · intervalo ${from}–${to} m`
        : `${interval.lith_code} · Cu ${interval.cu_pct} % · ${interval.residual_flag === "true" ? "residual" : "completo"} · fuentes ${interval.source_sample_ids}`;
      track.append(bar);
    }
    const contact = document.createElement("div");
    contact.style.cssText = `position:absolute;left:${(example.contact_m - start) / span * 100}%;top:0;bottom:0;border-left:2px dashed var(--amber);pointer-events:none;opacity:.9`;
    track.append(contact);
  }
  makeTimeline("assay-timeline", example.assays, "assay");
  makeTimeline("composite-timeline", example.composites, "composite");

  const loadButton = document.getElementById("load-3d");
  loadButton.addEventListener("click", () => {
    const wrapper = document.getElementById("model-frame-wrap");
    const frame = document.getElementById("model-frame");
    wrapper.hidden = false;
    if (!frame.src) frame.src = "visor/m01b_block_model_geology_topography.html";
    loadButton.disabled = true;
    loadButton.textContent = "3D cargándose…";
    frame.addEventListener("load", () => { loadButton.textContent = "3D abierto"; }, { once: true });
    wrapper.scrollIntoView({ behavior: "smooth", block: "start" });
  });
})();
