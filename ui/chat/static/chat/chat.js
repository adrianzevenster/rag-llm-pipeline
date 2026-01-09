function el(id) { return document.getElementById(id); }

function appendBubble(role, meta, text) {
    const log = el("chat-log");

    const wrap = document.createElement("div");
    wrap.className = "bubble " + role;

    const metaDiv = document.createElement("div");
    metaDiv.className = "meta";
    metaDiv.textContent = meta;

    const pre = document.createElement("pre");
    pre.className = "pre text";
    pre.textContent = text;

    wrap.appendChild(metaDiv);
    wrap.appendChild(pre);
    log.appendChild(wrap);
    log.scrollTop = log.scrollHeight;
}

async function send() {
    const agent = el("agent").value.trim() || "FastFinance";
    const message = el("message").value.trim();
    const status = el("status");
    const btn = el("send");

    if (!message) return;

    appendBubble("user", "You · now", message);

    btn.disabled = true;
    status.textContent = "Sending...";

    try {
        const res = await fetch(window.RAG_UI.chatApiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.RAG_UI.csrfToken,
            },
            body: JSON.stringify({ agent_name: agent, message }),
        });

        const data = await res.json();
        if (!data.ok) {
            appendBubble("bot", `${agent} · error`, data.error || "Request failed");
            status.textContent = "Error.";
            return;
        }

        const runId = data.run_id ? ` · run_id: ${data.run_id}` : "";
        appendBubble("bot", `${data.agent_name || agent} · now${runId}`, data.output || "");

        status.textContent = "Done.";
        el("message").value = "";
    } catch (e) {
        appendBubble("bot", `${agent} · error`, String(e));
        status.textContent = "Error.";
    } finally {
        btn.disabled = false;
        setTimeout(() => (status.textContent = ""), 1500);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    el("send").addEventListener("click", send);
    el("message").addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") send();
    });
});
