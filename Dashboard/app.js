const API_BASE = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws/live";

let dashboardMode = "auto"; // auto | manual
let streamPaused = false;
let ws = null;

const MAX_ECG_POINTS = 500;
const MAX_VITAL_POINTS = 50;
const MAX_TABLE_ROWS = 20;
const MAX_LOG_ROWS = 30;

const telemetryHistory = [];
const ecgSeries = [];
const alertsState = [];
const logsState = [];

const thresholds = {
  hrLow: 55,
  hrHigh: 120,
  spo2Low: 95,
  tempHigh: 37.8,
  sbpHigh: 140,
  dbpHigh: 90,
};

const el = {
  wsStatus: document.getElementById("wsStatus"),
  modeBtn: document.getElementById("modeBtn"),
  streamBtn: document.getElementById("streamBtn"),

  hrValue: document.getElementById("hrValue"),
  spo2Value: document.getElementById("spo2Value"),
  tempValue: document.getElementById("tempValue"),
  bpValue: document.getElementById("bpValue"),
  ecgValue: document.getElementById("ecgValue"),
  batteryValue: document.getElementById("batteryValue"),

  cardHr: document.getElementById("card-hr"),
  cardSpo2: document.getElementById("card-spo2"),
  cardTemp: document.getElementById("card-temp"),
  cardBp: document.getElementById("card-bp"),
  cardEcg: document.getElementById("card-ecg"),
  cardBattery: document.getElementById("card-battery"),

  alertList: document.getElementById("alertList"),
  logList: document.getElementById("logList"),
  telemetryTableBody: document.getElementById("telemetryTableBody"),

  btnFakeNormal: document.getElementById("btnFakeNormal"),
  btnFakeAbnormal: document.getElementById("btnFakeAbnormal"),
  btnFakeECG: document.getElementById("btnFakeECG"),
  btnClearCharts: document.getElementById("btnClearCharts"),
  btnReloadAlerts: document.getElementById("btnReloadAlerts"),
};

function addLog(message) {
  logsState.unshift({
    ts: new Date().toLocaleTimeString(),
    message,
  });
  if (logsState.length > MAX_LOG_ROWS) logsState.pop();
  renderLogs();
}

function renderLogs() {
  el.logList.innerHTML = "";
  logsState.forEach((item) => {
    const div = document.createElement("div");
    div.className = "log-item";
    div.textContent = `[${item.ts}] ${item.message}`;
    el.logList.appendChild(div);
  });
}

function setWsStatus(connected) {
  el.wsStatus.textContent = connected ? "CONNECTED" : "DISCONNECTED";
  el.wsStatus.className = connected ? "badge badge-green" : "badge badge-red";
}

function setMode(mode) {
  dashboardMode = mode;
  el.modeBtn.textContent = mode.toUpperCase();
  el.modeBtn.className = `mode-btn ${mode}`;
  addLog(`Dashboard mode switched to ${mode.toUpperCase()}`);
}

function toggleMode() {
  setMode(dashboardMode === "auto" ? "manual" : "auto");
}

function toggleStream() {
  streamPaused = !streamPaused;
  el.streamBtn.textContent = streamPaused ? "RESUME" : "PAUSE";
  el.streamBtn.className = streamPaused ? "stream-btn paused" : "stream-btn";
  addLog(streamPaused ? "Realtime stream paused" : "Realtime stream resumed");
}

function formatNumber(v, digits = 1) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return "--";
  return Number(v).toFixed(digits);
}

function resetCardClasses(card) {
  card.classList.remove("status-normal", "status-warning", "status-danger");
}

function setCardStatus(card, status) {
  resetCardClasses(card);
  if (status) card.classList.add(status);
}

function updateMetricCards(t) {
  el.hrValue.textContent =
    t.heart_rate != null ? Math.round(t.heart_rate) : "--";
  el.spo2Value.textContent = t.spo2 != null ? Math.round(t.spo2) : "--";
  el.tempValue.textContent = formatNumber(t.body_temp, 1);
  el.bpValue.textContent = `${t.systolic_bp ?? "--"} / ${t.diastolic_bp ?? "--"}`;
  el.ecgValue.textContent = t.ecg_value ?? "--";
  el.batteryValue.textContent = t.battery_level ?? "--";

  // HR
  if (t.heart_rate > thresholds.hrHigh || t.heart_rate < thresholds.hrLow) {
    setCardStatus(el.cardHr, "status-danger");
  } else {
    setCardStatus(el.cardHr, "status-normal");
  }

  // SpO2
  if (t.spo2 < thresholds.spo2Low) {
    setCardStatus(el.cardSpo2, "status-danger");
  } else {
    setCardStatus(el.cardSpo2, "status-normal");
  }

  // Temp
  if (t.body_temp > thresholds.tempHigh) {
    setCardStatus(el.cardTemp, "status-danger");
  } else {
    setCardStatus(el.cardTemp, "status-normal");
  }

  // BP
  if (
    t.systolic_bp > thresholds.sbpHigh ||
    t.diastolic_bp > thresholds.dbpHigh
  ) {
    setCardStatus(el.cardBp, "status-warning");
  } else {
    setCardStatus(el.cardBp, "status-normal");
  }

  setCardStatus(el.cardEcg, "status-normal");
  setCardStatus(el.cardBattery, "status-normal");
}

function buildLocalAlerts(t) {
  const arr = [];

  if (t.heart_rate != null && t.heart_rate > thresholds.hrHigh) {
    arr.push({
      level: "danger",
      title: "High Heart Rate",
      message: `${t.heart_rate} bpm`,
    });
  }

  if (t.heart_rate != null && t.heart_rate < thresholds.hrLow) {
    arr.push({
      level: "warning",
      title: "Low Heart Rate",
      message: `${t.heart_rate} bpm`,
    });
  }

  if (t.spo2 != null && t.spo2 < thresholds.spo2Low) {
    arr.push({
      level: "danger",
      title: "Low SpO2",
      message: `${t.spo2}%`,
    });
  }

  if (t.body_temp != null && t.body_temp > thresholds.tempHigh) {
    arr.push({
      level: "danger",
      title: "High Temperature",
      message: `${t.body_temp} °C`,
    });
  }

  if (t.systolic_bp != null && t.systolic_bp > thresholds.sbpHigh) {
    arr.push({
      level: "warning",
      title: "High Systolic BP",
      message: `${t.systolic_bp} mmHg`,
    });
  }

  if (t.diastolic_bp != null && t.diastolic_bp > thresholds.dbpHigh) {
    arr.push({
      level: "warning",
      title: "High Diastolic BP",
      message: `${t.diastolic_bp} mmHg`,
    });
  }

  return arr;
}

function renderAlerts() {
  el.alertList.innerHTML = "";

  if (alertsState.length === 0) {
    const div = document.createElement("div");
    div.className = "log-item";
    div.textContent = "No active alerts";
    el.alertList.appendChild(div);
    return;
  }

  alertsState.forEach((a) => {
    const div = document.createElement("div");
    div.className = `alert-item ${a.level === "danger" ? "" : a.level}`;
    div.innerHTML = `
      <div class="alert-title">${a.title}</div>
      <div>${a.message}</div>
      <div class="alert-time">${a.ts}</div>
    `;
    el.alertList.appendChild(div);
  });
}

function pushAlerts(newAlerts) {
  alertsState.length = 0;
  newAlerts.forEach((a) => {
    alertsState.push({
      ...a,
      ts: new Date().toLocaleTimeString(),
    });
  });
  renderAlerts();
}

function pushTelemetryTable(t) {
  telemetryHistory.unshift(t);
  if (telemetryHistory.length > MAX_TABLE_ROWS) telemetryHistory.pop();
  renderTelemetryTable();
}

function renderTelemetryTable() {
  el.telemetryTableBody.innerHTML = "";
  telemetryHistory.forEach((t) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${t.timestamp || "-"}</td>
      <td>${t.heart_rate ?? "-"}</td>
      <td>${t.spo2 ?? "-"}</td>
      <td>${t.body_temp ?? "-"}</td>
      <td>${t.systolic_bp ?? "-"}/${t.diastolic_bp ?? "-"}</td>
      <td>${t.ecg_value ?? "-"}</td>
      <td>${t.signal_quality ?? "-"}</td>
      <td>${t.battery_level ?? "-"}</td>
    `;
    el.telemetryTableBody.appendChild(tr);
  });
}

function handleTelemetry(data) {
  if (streamPaused) return;

  const row = {
    timestamp: data.timestamp || new Date().toLocaleTimeString(),
    heart_rate: data.heart_rate,
    spo2: data.spo2,
    body_temp: data.body_temp,
    systolic_bp: data.systolic_bp,
    diastolic_bp: data.diastolic_bp,
    ecg_value: data.ecg_value,
    signal_quality: data.signal_quality,
    battery_level: data.battery_level,
  };

  updateMetricCards(row);
  pushTelemetryTable(row);
  appendVitalsPoint(row);

  const localAlerts = buildLocalAlerts(row);
  pushAlerts(localAlerts);

  addLog(
    `Telemetry received: HR=${row.heart_rate}, SpO2=${row.spo2}, Temp=${row.body_temp}`,
  );
}

function handleECG(data) {
  if (streamPaused) return;
  if (!data.samples || !Array.isArray(data.samples)) return;

  data.samples.forEach((v) => ecgSeries.push(v));
  while (ecgSeries.length > MAX_ECG_POINTS) ecgSeries.shift();

  ecgChart.data.labels = ecgSeries.map((_, i) => i + 1);
  ecgChart.data.datasets[0].data = ecgSeries;
  ecgChart.update("none");

  addLog(`ECG packet received (${data.samples.length} samples)`);
}

function connectWebSocket() {
  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    setWsStatus(true);
    addLog("WebSocket connected");
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);

      if (msg.type === "telemetry") {
        handleTelemetry(msg.data);
      } else if (msg.type === "ecg") {
        handleECG(msg.data);
      } else if (msg.type === "alert") {
        addLog("Alert event received from backend");
      }
    } catch (err) {
      console.error(err);
      addLog("WS message parse error");
    }
  };

  ws.onclose = () => {
    setWsStatus(false);
    addLog("WebSocket disconnected. Reconnecting in 2s...");
    setTimeout(connectWebSocket, 2000);
  };

  ws.onerror = () => {
    addLog("WebSocket error");
  };
}

// =========================
// Chart: ECG
// =========================
const ecgCtx = document.getElementById("ecgChart").getContext("2d");
const ecgChart = new Chart(ecgCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "ECG",
        data: [],
        borderColor: "#22c55e",
        backgroundColor: "rgba(34,197,94,0.15)",
        borderWidth: 1.5,
        pointRadius: 0,
        tension: 0,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    scales: {
      x: {
        ticks: { color: "#94a3b8" },
        grid: { color: "#1f2937" },
      },
      y: {
        ticks: { color: "#94a3b8" },
        grid: { color: "#1f2937" },
      },
    },
    plugins: {
      legend: {
        labels: { color: "#e5e7eb" },
      },
    },
  },
});

// =========================
// Chart: Vitals
// =========================
const vitalsCtx = document.getElementById("vitalsChart").getContext("2d");
const vitalsChart = new Chart(vitalsCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Heart Rate",
        data: [],
        borderColor: "#ef4444",
        borderWidth: 2,
        pointRadius: 2,
        tension: 0.3,
      },
      {
        label: "SpO2",
        data: [],
        borderColor: "#3b82f6",
        borderWidth: 2,
        pointRadius: 2,
        tension: 0.3,
      },
      {
        label: "Temperature",
        data: [],
        borderColor: "#f59e0b",
        borderWidth: 2,
        pointRadius: 2,
        tension: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    scales: {
      x: {
        ticks: { color: "#94a3b8" },
        grid: { color: "#1f2937" },
      },
      y: {
        ticks: { color: "#94a3b8" },
        grid: { color: "#1f2937" },
      },
    },
    plugins: {
      legend: {
        labels: { color: "#e5e7eb" },
      },
    },
  },
});

function appendVitalsPoint(t) {
  const label = t.timestamp
    ? new Date(t.timestamp).toLocaleTimeString([], { hour12: false })
    : new Date().toLocaleTimeString();

  vitalsChart.data.labels.push(label);
  vitalsChart.data.datasets[0].data.push(t.heart_rate ?? null);
  vitalsChart.data.datasets[1].data.push(t.spo2 ?? null);
  vitalsChart.data.datasets[2].data.push(t.body_temp ?? null);

  if (vitalsChart.data.labels.length > MAX_VITAL_POINTS) {
    vitalsChart.data.labels.shift();
    vitalsChart.data.datasets.forEach((ds) => ds.data.shift());
  }

  vitalsChart.update("none");
}

function clearCharts() {
  ecgSeries.length = 0;
  ecgChart.data.labels = [];
  ecgChart.data.datasets[0].data = [];
  ecgChart.update();

  vitalsChart.data.labels = [];
  vitalsChart.data.datasets.forEach((ds) => (ds.data = []));
  vitalsChart.update();

  telemetryHistory.length = 0;
  renderTelemetryTable();

  alertsState.length = 0;
  renderAlerts();

  addLog("Charts and local states cleared");
}

// =========================
// Manual mode APIs
// =========================
async function postJSON(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || `HTTP ${res.status}`);
  }

  return res.json();
}

function buildFakeNormalTelemetry() {
  return {
    device_code: "esp32_01",
    heart_rate: 78,
    spo2: 98,
    systolic_bp: 118,
    diastolic_bp: 76,
    body_temp: 36.8,
    ecg_value: 2048,
    signal_quality: 0.95,
    battery_level: 87,
  };
}

function buildFakeAbnormalTelemetry() {
  return {
    device_code: "esp32_01",
    heart_rate: 142,
    spo2: 88,
    systolic_bp: 155,
    diastolic_bp: 98,
    body_temp: 38.9,
    ecg_value: 2250,
    signal_quality: 0.6,
    battery_level: 42,
  };
}

function buildFakeECG() {
  const samples = [];
  for (let i = 0; i < 120; i++) {
    const v =
      2048 + Math.round(200 * Math.sin(i * 0.25) + 80 * Math.sin(i * 0.05));
    samples.push(v);
  }
  return {
    device_code: "esp32_01",
    sampling_rate: 250,
    samples,
  };
}

async function sendFakeNormal() {
  if (dashboardMode !== "manual") {
    alert("Switch to MANUAL mode first.");
    return;
  }
  try {
    await postJSON("/control/test/telemetry", buildFakeNormalTelemetry());
    addLog("Fake normal telemetry sent");
  } catch (err) {
    console.error(err);
    alert("Failed to send fake normal telemetry");
  }
}

async function sendFakeAbnormal() {
  if (dashboardMode !== "manual") {
    alert("Switch to MANUAL mode first.");
    return;
  }
  try {
    await postJSON("/control/test/telemetry", buildFakeAbnormalTelemetry());
    addLog("Fake abnormal telemetry sent");
  } catch (err) {
    console.error(err);
    alert("Failed to send fake abnormal telemetry");
  }
}

async function sendFakeECG() {
  if (dashboardMode !== "manual") {
    alert("Switch to MANUAL mode first.");
    return;
  }
  try {
    await postJSON("/control/test/ecg", buildFakeECG());
    addLog("Fake ECG packet sent");
  } catch (err) {
    console.error(err);
    alert("Failed to send fake ECG");
  }
}

async function loadAlerts() {
  // Nếu backend mày chưa có API alerts list thì tạm bỏ qua phần này
  // hoặc sau này tao chỉnh lại theo route thật của mày
  addLog("Reload alerts requested");
}

// bind events
el.modeBtn.addEventListener("click", toggleMode);
el.streamBtn.addEventListener("click", toggleStream);
el.btnFakeNormal.addEventListener("click", sendFakeNormal);
el.btnFakeAbnormal.addEventListener("click", sendFakeAbnormal);
el.btnFakeECG.addEventListener("click", sendFakeECG);
el.btnClearCharts.addEventListener("click", clearCharts);
el.btnReloadAlerts.addEventListener("click", loadAlerts);

// init
renderAlerts();
renderLogs();
setMode("auto");
setWsStatus(false);
connectWebSocket();
