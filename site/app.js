"use strict";

const API_BASE = "https://goldcraft-host.tail26d0f0.ts.net";
const TOKEN_KEY = "goldcraftAdminToken";
const REFRESH_MS = 20000;

let liveData = null;
let adminData = null;
let refreshTimer = null;
let toastTimer = null;

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function formatBytes(bytes) {
  const value = Number(bytes);
  if (!Number.isFinite(value) || value < 0) return "Unknown size";
  const units = ["B", "KB", "MB", "GB"];
  let amount = value;
  let unit = 0;
  while (amount >= 1024 && unit < units.length - 1) {
    amount /= 1024;
    unit += 1;
  }
  return `${amount >= 100 || unit === 0 ? amount.toFixed(0) : amount.toFixed(1)} ${units[unit]}`;
}

function formatUptime(seconds) {
  const value = Number(seconds);
  if (!Number.isFinite(value) || value < 0) return "Not running";
  const days = Math.floor(value / 86400);
  const hours = Math.floor((value % 86400) / 3600);
  const minutes = Math.floor((value % 3600) / 60);
  if (days) return `${days}d ${hours}h ${minutes}m`;
  if (hours) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function formatDate(value) {
  if (!value) return "Unknown";
  const number = Number(value);
  const date = Number.isFinite(number)
    ? new Date(number < 100000000000 ? number * 1000 : number)
    : new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function cleanMinecraftText(value) {
  return String(value || "").replace(/§./g, "").trim();
}

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch(API_BASE + path, {
      cache: "no-store",
      ...options,
      signal: controller.signal,
    });
    let payload = {};
    try {
      payload = await response.json();
    } catch {
      payload = { error: `HTTP ${response.status}` };
    }
    if (!response.ok) {
      const error = new Error(payload.error || payload.message || `HTTP ${response.status}`);
      error.status = response.status;
      error.payload = payload;
      throw error;
    }
    return payload;
  } finally {
    clearTimeout(timeout);
  }
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add("hidden"), 4200);
}

function setText(selector, value) {
  const element = $(selector);
  if (element) element.textContent = value;
}

function setLiveStatus(state, reachable = true) {
  const pill = $("#liveStatusButton");
  pill.classList.remove("status-running", "status-stopped", "status-stopping", "status-checking");
  if (!reachable) {
    pill.classList.add("status-stopped");
    setText("#liveStatusText", "Host unreachable");
    setText("#orbState", "OFFLINE");
    return;
  }
  const normalized = ["running", "stopped", "stopping"].includes(state) ? state : "checking";
  pill.classList.add(`status-${normalized}`);
  setText("#liveStatusText", normalized === "running" ? "Server running" : normalized === "stopping" ? "Server stopping" : normalized === "stopped" ? "Server stopped" : "Checking server");
  setText("#orbState", normalized.toUpperCase());
}

function renderOverview(data) {
  const running = data.state === "running" || data.state === "stopping";
  setLiveStatus(data.state, true);
  setText("#metricState", data.state);
  setText("#metricUptime", running ? `Uptime ${formatUptime(data.uptimeSeconds)}` : "Ready for an owner to start");
  setText("#metricPlayers", String(data.onlinePlayers ?? 0));
  setText("#metricMaxPlayers", String(data.maxPlayers ?? "—"));
  setText("#metricTargetPlayers", String(data.targetPlayers ?? 15));
  setText("#metricMods", String(data.modCount ?? "—"));
  setText("#metricView", String(data.viewDistance ?? "—"));
  setText("#metricSimulation", String(data.simulationDistance ?? "—"));
  setText("#detailMinecraft", data.minecraft || "1.21.1");
  setText("#detailLoader", data.loader || "Fabric");
  setText("#detailPacks", `${data.activeResourcePacks?.length ?? 0} active / ${data.resourcePackCount ?? 0} installed`);
  setText("#detailShader", data.activeShader ? cleanMinecraftText(data.activeShader) : "Disabled");
  setText("#detailInventory", formatDate(data.inventoryUpdatedAt));
  setText("#lastChecked", `Checked ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`);
  $("#connectionNotice").classList.add("hidden");
}

function renderProfiles(profiles) {
  const grid = $("#profileGrid");
  grid.replaceChildren();
  const values = Object.values(profiles || {});
  if (!values.length) {
    grid.append(node("div", "card section-card", "Profiles are unavailable while the host is offline."));
    return;
  }
  values.forEach((profile, index) => {
    const card = node("article", `card profile-card${index === 1 ? " featured" : ""}`);
    card.append(node("span", "profile-tag", index === 1 ? "SAFE DEFAULT" : profile.key === "mobile" ? "ANDROID" : "BALANCED"));
    card.append(node("h2", "", profile.title || "Client profile"));
    card.append(node("p", "", profile.description || profile.target || ""));

    const pills = node("div", "spec-pills");
    [
      `${Math.round((profile.recommendedMemoryMb || 0) / 1024)} GB heap`,
      `${profile.renderDistance ?? "—"}/${profile.simulationDistance ?? "—"} distance`,
      `${profile.modCount ?? "—"} mods`,
      profile.shaderDefault || "Shader optional",
    ].forEach((item) => pills.append(node("span", "spec-pill", item)));
    card.append(pills);

    const notes = node("ul", "profile-notes");
    (profile.notes || []).slice(0, 3).forEach((item) => notes.append(node("li", "", item)));
    card.append(notes);

    const link = node("a", "button primary", `Download · ${formatBytes(profile.bytes)}`);
    link.href = API_BASE + profile.url;
    link.rel = "noreferrer";
    card.append(link);
    grid.append(card);
  });
}

function renderDownloads(downloads) {
  const labels = {
    combined: ["Complete client files", "Mods, active resource packs, and shaders"],
    mods: ["All client mods", "Exact JAR set from the active client"],
    resourcePacks: ["Active resource packs", "Only packs currently enabled"],
    shaders: ["Shader packs", "Current installed shader collection"],
  };
  const grid = $("#downloadGrid");
  grid.replaceChildren();
  Object.entries(downloads || {}).forEach(([key, item]) => {
    const card = node("article", "card download-card");
    const info = node("div");
    info.append(node("h3", "", labels[key]?.[0] || item.file || key));
    info.append(node("div", "download-meta", `${formatBytes(item.bytes)} · Updated ${formatDate(item.updatedAt)}`));
    const hash = node("div", "hash", `SHA-256 ${item.sha256 || "unavailable"}`);
    hash.title = item.sha256 || "";
    info.append(hash);
    card.append(info);

    const link = node("a", "button secondary", "Download");
    link.href = API_BASE + item.url;
    link.rel = "noreferrer";
    card.append(link);
    grid.append(card);
  });
  if (!grid.children.length) grid.append(node("div", "card section-card", "Downloads are unavailable while the host is offline."));
}

function renderMods() {
  const mods = liveData?.mods || [];
  const query = ($("#modSearch").value || "").toLowerCase().trim();
  const filtered = mods.filter((mod) =>
    [mod.name, mod.id, mod.version, mod.file].some((value) => String(value || "").toLowerCase().includes(query))
  );

  setText("#modsTitleCount", String(mods.length || liveData?.modCount || "—"));
  setText("#modResultsInfo", query ? `${filtered.length} of ${mods.length} mods match “${query}”` : `${mods.length} mods in the live client inventory`);

  const list = $("#modList");
  list.replaceChildren();
  filtered.forEach((mod) => {
    const row = node("article", "mod-row");
    row.append(node("div", "mod-name", mod.name || mod.file || "Unknown mod"));
    row.append(node("div", "mod-id", mod.id || mod.file || "No Fabric ID"));
    row.append(node("div", "mod-version", mod.version || "Unknown"));
    list.append(row);
  });
  if (!filtered.length) list.append(node("div", "card section-card", query ? "No mods match this search." : "Mod inventory is unavailable."));
}

function renderAssets(data) {
  setText("#packCountBadge", String(data.resourcePackCount ?? data.resourcePacks?.length ?? "—"));
  setText("#shaderCountBadge", String(data.shaderPackCount ?? data.shaderPacks?.length ?? "—"));

  const packs = $("#resourcePackList");
  packs.replaceChildren();
  (data.resourcePacks || []).forEach((pack) => {
    const item = node("article", "asset-item");
    const title = node("div", "asset-title");
    title.append(node("span", "", cleanMinecraftText(pack.name)));
    title.append(node("span", pack.active ? "active-badge" : "inactive-badge", pack.active ? "ACTIVE" : "INSTALLED"));
    item.append(title);
    item.append(node("small", "", `${formatBytes(pack.bytes)}${pack.description ? ` · ${cleanMinecraftText(pack.description)}` : ""}`));
    packs.append(item);
  });

  const shaders = $("#shaderPackList");
  shaders.replaceChildren();
  (data.shaderPacks || []).forEach((shader) => {
    const item = node("article", "asset-item");
    const title = node("div", "asset-title");
    title.append(node("span", "", cleanMinecraftText(shader.name)));
    title.append(node("span", shader.active ? "active-badge" : "inactive-badge", shader.active ? "ACTIVE" : "INSTALLED"));
    item.append(title);
    item.append(node("small", "", formatBytes(shader.bytes)));
    shaders.append(item);
  });
}

async function refreshPublic(showFailure = true) {
  try {
    const data = await request("/public");
    liveData = data;
    renderOverview(data);
    renderProfiles(data.profiles);
    renderDownloads(data.downloads);
    renderMods();
    renderAssets(data);
    return data;
  } catch (error) {
    setLiveStatus("stopped", false);
    setText("#metricState", "unreachable");
    setText("#metricUptime", "The PC may be offline");
    $("#connectionNotice").classList.remove("hidden");
    if (showFailure) showToast("Live host is unreachable. Static dashboard and repository links still work.");
    throw error;
  }
}

function switchTab(id, updateHash = true) {
  if (!document.getElementById(id)) id = "overview";
  $$(".nav-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === id));
  $$(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === id));
  if (updateHash) history.replaceState(null, "", `#${id}`);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function getToken() {
  try { return localStorage.getItem(TOKEN_KEY) || ""; } catch { return ""; }
}

function saveToken(value) {
  try { localStorage.setItem(TOKEN_KEY, value); } catch {}
}

function removeToken() {
  try { localStorage.removeItem(TOKEN_KEY); } catch {}
}

async function adminRequest(path, options = {}) {
  const token = getToken();
  if (!token) throw new Error("No admin token saved");
  return request(path, {
    ...options,
    headers: { Authorization: `Bearer ${token}`, ...(options.headers || {}) },
  });
}

function renderAdmin(data) {
  adminData = data;
  $("#adminLocked").classList.add("hidden");
  $("#adminUnlocked").classList.remove("hidden");
  setText("#adminState", data.state || "unknown");
  setText("#adminPid", data.pid ? `Java PID ${data.pid}` : "No Fabric JVM detected");
  setText("#adminUptime", formatUptime(data.uptimeSeconds));
  setText("#controlMessage", data.message || `Actual server state: ${data.state || "unknown"}.`);

  const running = data.state === "running" || data.state === "stopping";
  $("#startButton").disabled = running;
  $("#stopButton").disabled = !running || data.state === "stopping";
}

function lockAdmin(message = "") {
  $("#adminLocked").classList.remove("hidden");
  $("#adminUnlocked").classList.add("hidden");
  setText("#adminAuthMessage", message);
}

async function refreshAdmin() {
  try {
    const data = await adminRequest("/status");
    renderAdmin(data);
    return data;
  } catch (error) {
    if (error.status === 401) {
      removeToken();
      lockAdmin("The saved token was rejected. Paste the current token again.");
    } else {
      setText("#controlMessage", `Could not reach the controller: ${error.message}`);
    }
    throw error;
  }
}

async function runControl(action) {
  const buttons = ["#startButton", "#stopButton", "#refreshAdminButton"].map($);
  buttons.forEach((button) => { button.disabled = true; });
  try {
    const data = await adminRequest(`/${action}`, { method: "POST" });
    renderAdmin(data);
    showToast(data.message || `Server ${action} request accepted.`);
    await refreshPublic(false).catch(() => {});
    setTimeout(() => {
      refreshAdmin().catch(() => {});
      refreshPublic(false).catch(() => {});
    }, 3500);
  } catch (error) {
    showToast(`Control request failed: ${error.message}`);
    await refreshAdmin().catch(() => {});
  }
}

function bindEvents() {
  $$(".nav-tab").forEach((button) => button.addEventListener("click", () => switchTab(button.dataset.tab)));
  $$("[data-tab-target]").forEach((button) => button.addEventListener("click", () => switchTab(button.dataset.tabTarget)));
  $("#modSearch").addEventListener("input", renderMods);

  $("#adminForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const value = $("#adminToken").value.trim();
    if (!value) return;
    saveToken(value);
    setText("#adminAuthMessage", "Verifying…");
    try {
      await refreshAdmin();
      $("#adminToken").value = "";
      showToast("Owner controls unlocked on this browser.");
    } catch {
      removeToken();
      lockAdmin("That token was rejected or the controller is offline.");
    }
  });

  $("#startButton").addEventListener("click", () => runControl("start"));
  $("#stopButton").addEventListener("click", () => {
    if (window.confirm("Gracefully stop the Minecraft server? Connected players will be disconnected after the world saves.")) runControl("stop");
  });
  $("#refreshAdminButton").addEventListener("click", () => refreshAdmin().catch(() => showToast("Controller refresh failed.")));
  $("#forgetTokenButton").addEventListener("click", () => {
    removeToken();
    adminData = null;
    lockAdmin("");
    showToast("Admin token removed from this browser.");
  });

  window.addEventListener("hashchange", () => switchTab(location.hash.slice(1) || "overview", false));
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") refreshPublic(false).catch(() => {});
  });
}

async function start() {
  bindEvents();
  switchTab(location.hash.slice(1) || "overview", false);
  await refreshPublic(false).catch(() => {});
  if (getToken()) await refreshAdmin().catch(() => {});
  refreshTimer = setInterval(() => refreshPublic(false).catch(() => {}), REFRESH_MS);
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
}

start();
