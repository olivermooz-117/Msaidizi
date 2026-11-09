(function () {
  const script = document.currentScript;
  const widgetKey = script.getAttribute("data-key");
  const apiBase = script.getAttribute("data-api") || "http://localhost:5000";

  if (!widgetKey) {
    console.error("Msaidizi: data-key is required");
    return;
  }

  let sessionId = localStorage.getItem("msaidizi_session") || null;
  let open = false;

  // Create UI
  const btn = document.createElement("button");
  btn.innerHTML = "💬";
  btn.style.cssText = "position:fixed;bottom:20px;right:20px;width:56px;height:56px;border-radius:50%;background:#0f766e;color:white;border:none;font-size:24px;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.2);z-index:9999;";
  document.body.appendChild(btn);

  const panel = document.createElement("div");
  panel.style.cssText = "display:none;position:fixed;bottom:90px;right:20px;width:340px;max-height:480px;background:white;border-radius:16px;box-shadow:0 8px 30px rgba(0,0,0,0.15);flex-direction:column;overflow:hidden;z-index:9999;font-family:system-ui,sans-serif;";
  panel.innerHTML = `
    <div style="background:#0f766e;color:white;padding:14px 16px;font-weight:600;">Msaidizi</div>
    <div id="ms-messages" style="flex:1;overflow-y:auto;padding:12px;min-height:280px;max-height:340px;"></div>
    <div style="display:flex;border-top:1px solid #e5e7eb;">
      <input id="ms-input" placeholder="Andika hapa..." style="flex:1;border:none;padding:12px;outline:none;font-size:14px;">
      <button id="ms-send" style="background:#0f766e;color:white;border:none;padding:0 16px;cursor:pointer;">Send</button>
    </div>
  `;
  document.body.appendChild(panel);

  const messagesEl = panel.querySelector("#ms-messages");
  const inputEl = panel.querySelector("#ms-input");
  const sendBtn = panel.querySelector("#ms-send");

  function addMessage(text, role) {
    const div = document.createElement("div");
    div.style.cssText = `margin:8px 0;padding:8px 12px;border-radius:12px;max-width:85%;font-size:14px;line-height:1.4;${
      role === "user" ? "background:#ccfbf1;margin-left:auto;" : "background:#f3f4f6;"
    }`;
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function send() {
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = "";
    addMessage(text, "user");

    try {
      const res = await fetch(`${apiBase}/api/chat/widget`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          widget_key: widgetKey,
          session_id: sessionId,
          message: text,
        }),
      });
      const data = await res.json();
      if (data.session_id) {
        sessionId = data.session_id;
        localStorage.setItem("msaidizi_session", sessionId);
      }
      addMessage(data.reply || data.error || "Error", "agent");
    } catch (e) {
      addMessage("Network error. Try again.", "agent");
    }
  }

  btn.onclick = () => {
    open = !open;
    panel.style.display = open ? "flex" : "none";
  };
  sendBtn.onclick = send;
  inputEl.onkeydown = (e) => { if (e.key === "Enter") send(); };

  addMessage("Habari! Ninaweza kukusaidiaje? / Hi! How can I help?", "agent");
})();
