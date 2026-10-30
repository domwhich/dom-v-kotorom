(function () {
  // --- Синхронизация языка с localStorage ---
  const stored = localStorage.getItem("lang");
  const url = new URL(location.href);
  if (stored && !url.searchParams.get("lang") && !sessionStorage.getItem("lang_synced")) {
    sessionStorage.setItem("lang_synced", "1");
    url.searchParams.set("lang", stored);
    location.replace(url.toString());
    return;
  }
  document.querySelectorAll(".lang-switch").forEach((a) => {
    a.addEventListener("click", () => localStorage.setItem("lang", a.dataset.lang));
  });

  // --- Опрос уведомлений (каждые 30 сек) ---
  const badge = document.getElementById("notif-count");
  const menu = document.getElementById("notif-menu");
  if (!badge || !menu) return;

  const ROLE_NAMES = { admin: "Администратор", editor: "Домовец", user: "Житель" };
  const escapeHtml = (s) =>
    String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function renderNotif(n) {
    if (n.type === "event_created") {
      return `📅 Новое событие: ${escapeHtml(n.payload.title || "")}`;
    }
    if (n.type === "role_assigned") {
      return `🎭 Вам назначена роль: ${ROLE_NAMES[n.payload.role] || n.payload.role}`;
    }
    return escapeHtml(n.type);
  }

  async function poll() {
    try {
      const r = await fetch("/api/notifications/unread-count", { credentials: "same-origin" });
      if (!r.ok) return;
      const data = await r.json();

      if (data.count > 0) {
        badge.textContent = data.count;
        badge.classList.remove("d-none");
      } else {
        badge.classList.add("d-none");
      }

      // Перерисовка дропдауна
      menu.querySelectorAll(".notif-item").forEach((el) => el.remove());
      const empty = document.getElementById("notif-empty");
      empty.style.display = data.latest.length ? "none" : "";

      const divider = menu.querySelector("hr");
      data.latest.forEach((n) => {
        const li = document.createElement("li");
        li.className = "notif-item";
        li.innerHTML = `<a class="dropdown-item small ${n.is_read ? "text-muted" : ""}"
                           href="/notifications">${renderNotif(n)}</a>`;
        divider.after(li);
      });
    } catch (_) { /* тихо */ }
  }

  poll();
  setInterval(poll, 30000);
})();