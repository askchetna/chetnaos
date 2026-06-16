(() => {
  // Lightweight chat/agent bridge for ChetnaOS runtime frontend ↔ backend.

  const chat = document.getElementById('chat');
  const input = document.getElementById('msg');
  const send = document.getElementById('send');
  const modeSelect = document.getElementById('modeSelect');

  function addBubble(text, who) {
    const line = document.createElement('div');
    line.className = 'chatline';
    const bubble = document.createElement('div');
    bubble.className = `bubble ${who === 'user' ? 'user' : 'assistant'}`;
    // preserve newlines & format
    if (typeof text === 'string' && text.includes('\\n')) {
      bubble.innerHTML = text.split('\\n').map(escapeHtml).join('<br/>');
    } else {
      bubble.textContent = (typeof text === 'string') ? text : String(text);
    }
    line.appendChild(bubble);
    chat.appendChild(line);
    chat.scrollTop = chat.scrollHeight;
  }

  function addErrorBubble(text) {
    const line = document.createElement('div');
    line.className = 'chatline';
    const bubble = document.createElement('div');
    bubble.className = 'bubble error';
    bubble.textContent = text;
    line.appendChild(bubble);
    chat.appendChild(line);
    chat.scrollTop = chat.scrollHeight;
  }

  function addTypingIndicator() {
    // Ensure only one typing indicator
    removeTypingIndicator();
    const line = document.createElement('div');
    line.className = 'chatline';
    const bubble = document.createElement('div');
    bubble.className = 'bubble assistant typing';
    bubble.textContent = 'typing...';
    bubble.id = 'typing-indicator';
    line.appendChild(bubble);
    chat.appendChild(line);
    chat.scrollTop = chat.scrollHeight;
  }

  function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator && indicator.parentElement) {
      indicator.parentElement.remove();
    }
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  async function callChat(payload) {
    // Use same-origin relative paths so this works on Railway and locally.
    return fetchJson('/api/chat', payload);
  }

  async function callAgent(payload) {
    return fetchJson('/api/agent', payload);
  }

  async function callGoal(payload) {
    return fetchJson('/api/goal', payload);
  }

  async function fetchJson(url, payload) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json().catch(() => null);
    if (!res.ok) {
      const serverMsg = data && data.detail ? data.detail : `HTTP ${res.status}`;
      throw new Error(typeof serverMsg === 'string' ? serverMsg : JSON.stringify(serverMsg));
    }
    if (!data) {
      throw new Error('Invalid JSON response from server.');
    }
    return data;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    const mode = (modeSelect?.value || 'chat').toLowerCase();

    // Disable send button and set state
    send.disabled = true;
    const prevLabel = send.textContent;
    send.textContent = 'Sending...';

    addBubble(text, 'user');
    addTypingIndicator();
    input.value = '';
    input.focus();

    const payload = { text, agent: mode };

    try {
      let data;
      if (mode === 'agent') {
        data = await callAgent(payload);
      } else if (mode === 'goal') {
        data = await callGoal({
          goal: text,
          context: { mode, client: 'web' },
          constraints: {}
        });
      } else {
        data = await callChat(payload);
      }

      removeTypingIndicator();

      if (typeof data.reply === 'string') {
        addBubble(data.reply, 'assistant');
      } else {
        addBubble(formatChetnaResponse(data), 'assistant');
      }
    } catch (e) {
      removeTypingIndicator();
      addErrorBubble(`Request error: ${e && e.message ? e.message : e}`);
    } finally {
      // Re-enable send button
      send.disabled = false;
      send.textContent = prevLabel || 'Send';
    }
  }

  function formatChetnaResponse(obj) {
    // If obj contains identity + filtered + world_state etc, format nicely
    try {
      if (obj.identity || obj.filtered || obj.world_state) {
        const lines = [];
        if (obj.identity) lines.push(`Identity: ${obj.identity}`);
        if (obj.filtered) lines.push(`Filtered: ${obj.filtered}`);
        if (obj.input) lines.push(`Input: ${obj.input}`);
        if (obj.evolution) lines.push(`Evolution: ${obj.evolution}`);
        if (obj.world_state) lines.push(`World: ${JSON.stringify(obj.world_state, null, 2)}`);
        if (obj.timestamp) lines.push(`Timestamp: ${obj.timestamp}`);
        return lines.join('\\n\\n');
      }
      // fallback: pretty JSON
      return JSON.stringify(obj, null, 2);
    } catch (e) {
      return JSON.stringify(obj);
    }
  }

  // Event listeners
  send.addEventListener('click', sendMessage);

  input.addEventListener('keydown', (e) => {
    // Ctrl+Enter or Cmd+Enter to send (as earlier)
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Optional: press plain Enter to add newline (no send)
  // If you prefer Enter to send, uncomment below:
  /*
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  */

  // small helper: allow clicking Enter on send button via keyboard
  send.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });

  // Focus input on load
  try { input.focus(); } catch (e) {}
  // Ensure sendMessage is accessible for potential debugging
  window.sendMessage = sendMessage;
})();