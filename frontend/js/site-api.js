(function () {
  var banner =
    '<div id="file-protocol-warn" style="background:#b91c1c;color:#fff;padding:12px 16px;text-align:center;font-size:14px;">' +
    "You opened HTML as a file. API will not work. Start <strong>run.bat</strong>, then open " +
    '<a href="http://127.0.0.1:8000/" style="color:#fff;text-decoration:underline;">http://127.0.0.1:8000/</a></div>';

  if (window.location.protocol === "file:") {
    document.body.insertAdjacentHTML("afterbegin", banner);
    return;
  }

  var statusEl = document.getElementById("api-status");
  if (!statusEl) return;

  statusEl.textContent = "Connecting to API…";

  fetch("/health", { cache: "no-store" })
    .then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    })
    .then(function (data) {
      statusEl.innerHTML =
        'Backend API: <strong style="color:#15803d;">online</strong> (GET /health) · v' +
        (data.version || "?") +
        ' · <a href="/docs">Open API docs</a>';
    })
    .catch(function () {
      statusEl.innerHTML =
        'Backend API: <strong style="color:#b91c1c;">offline</strong> — run <strong>run.bat</strong>, then use ' +
        '<a href="http://127.0.0.1:8000/">http://127.0.0.1:8000/</a>';
    });
})();
