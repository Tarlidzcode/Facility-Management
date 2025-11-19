// static/js/app.js - small demo data for charts
document.addEventListener("DOMContentLoaded", function () {
  const coffeeCanvas = document.getElementById("coffeeChart");
  const tempCanvas = document.getElementById("tempChart");
  const presencePie = document.getElementById("presencePie");

  // simple view navigation
  document.querySelectorAll(".nav a").forEach((el, idx) => {
    el.addEventListener("click", () => {
      document
        .querySelectorAll(".nav a")
        .forEach((n) => n.classList.remove("active"));
      el.classList.add("active");
      const map = [
        "dashboard",
        "employees",
        "safety",
        "coffee",
        "temperature",
        "stock",
        "presence",
      ];
      const view = map[idx];
      document
        .querySelectorAll(".view")
        .forEach((v) => v.classList.add("hidden"));
      const elView = document.getElementById("view-" + view);
      if (elView) elView.classList.remove("hidden");
    });
  });

  // helper to create charts
  function makeCoffeeChart(ctx, labels, data) {
    const root = getComputedStyle(document.documentElement);
    const blue = root.getPropertyValue("--blue-dark") || "#356b98";
    return new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{ label: "Cups", data: data, backgroundColor: blue.trim() }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  function makeTempChart(ctx, labels, data) {
    return new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Temperature",
            data: data,
            borderColor: "#2c9f6a",
            backgroundColor: "rgba(44,159,106,0.1)",
            tension: 0.3,
            fill: true,
          },
        ],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: false } },
      },
    });
  }

  // employees render helper + search state
  let employeesData = [];
  function initials(name) {
    if (!name) return "";
    const parts = name.split(" ");
    return (parts[0][0] || "") + (parts[1] ? parts[1][0] : "");
  }

  function statusClass(status) {
    const s = (status || "").toLowerCase();
    if (s.includes("in")) return "status-pill in";
    if (s.includes("out")) return "status-pill out";
    return "status-pill away";
  }

  function renderEmployees(list) {
    const tbody = document.getElementById("employeeRows");
    if (!tbody) return;
    tbody.innerHTML = list
      .map((e) => {
        const name = e.name || "";
        const init = initials(name).toUpperCase();
        const contact = `<div><div class="emp-avatar">${init}</div><div style="display:inline-block;vertical-align:middle"><div style="font-weight:600">${name}</div></div>`;
        const contactInfo = `<div class="muted"><i class="fa-regular fa-envelope"></i> ${e.email}<br><i class="fa-solid fa-phone"></i> ${e.phone}</div>`;
        const status = `<div class="${statusClass(e.status)}">${
          e.status
        }</div>`;
        return `<tr>
        <td>${contact}</td>
        <td>${contactInfo}</td>
        <td>${e.dept || ""}</td>
        <td>${status}</td>
        <td>${e.coffee || ""}</td>
        <td>${e.last || ""}</td>
      </tr>`;
      })
      .join("");
  }

  // Fetch data from API and populate UI, fallback to demo data on failure
  fetch("/api/dashboard")
    .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
    .then((json) => {
      const m = json.metrics || {};
      document.getElementById("employees_in").textContent = m.employees_in ?? 0;
      document.getElementById("employees_total").textContent =
        m.employees_total ?? 0;
      document.getElementById("coffee_today").textContent = m.coffee_today ?? 0;
      document.getElementById("temperature").textContent = m.temperature ?? "";
      document.getElementById("low_stock").textContent = m.low_stock ?? 0;

      const c = json.coffee_series || { labels: [], data: [] };
      const t = json.temp_series || { labels: [], data: [] };
      if (coffeeCanvas)
        makeCoffeeChart(coffeeCanvas.getContext("2d"), c.labels, c.data);
      if (tempCanvas)
        makeTempChart(tempCanvas.getContext("2d"), t.labels, t.data);

      // populate recent activity demo list
      const recent = [
        { t: "14:32", text: "Sarah Johnson made a coffee", tag: "coffee" },
        { t: "14:28", text: "Temperature adjusted to 22°C", tag: "temp" },
        { t: "14:15", text: "Mike Peters left the office", tag: "presence" },
        { t: "14:10", text: "Low stock alert: Coffee beans", tag: "alert" },
        { t: "14:05", text: "Emma Wilson returned to office", tag: "presence" },
      ];
      const recentList = document.getElementById("recentList");
      if (recentList) {
        recentList.innerHTML = recent
          .map(
            (r) =>
              `<li><div class="time">${r.t}</div><div class="text">${r.text}</div><div class="tag">${r.tag}</div></li>`
          )
          .join("");
      }

      // populate employee table demo data
      const employees = [
        {
          name: "Sarah Johnson",
          email: "sarah.j@company.com",
          phone: "+1 234 567 8901",
          dept: "Engineering",
          status: "In Office",
          coffee: "3 cups",
          last: "Just now",
        },
        {
          name: "Mike Peters",
          email: "mike.p@company.com",
          phone: "+1 234 567 8902",
          dept: "Design",
          status: "Out",
          coffee: "2 cups",
          last: "5 min ago",
        },
        {
          name: "Emma Wilson",
          email: "emma.w@company.com",
          phone: "+1 234 567 8903",
          dept: "Marketing",
          status: "In Office",
          coffee: "4 cups",
          last: "2 min ago",
        },
        {
          name: "James Brown",
          email: "james.b@company.com",
          phone: "+1 234 567 8904",
          dept: "Sales",
          status: "In Office",
          coffee: "2 cups",
          last: "Just now",
        },
      ];
      employeesData = employees;
      renderEmployees(employeesData);

      // wire simple search (by name or department)
      const searchEl = document.querySelector(".search");
      if (searchEl) {
        searchEl.addEventListener("input", (ev) => {
          const q = (ev.target.value || "").toLowerCase().trim();
          if (!q) return renderEmployees(employeesData);
          const filtered = employeesData.filter(
            (x) =>
              (x.name || "").toLowerCase().includes(q) ||
              (x.dept || "").toLowerCase().includes(q)
          );
          renderEmployees(filtered);
        });
      }

      // presence pie demo
      if (presencePie) {
        new Chart(presencePie.getContext("2d"), {
          type: "pie",
          data: {
            labels: ["In Office", "Toilet/Away", "Out"],
            datasets: [
              {
                data: [24, 5, 3],
                backgroundColor: ["#7fcf9b", "#f7d36b", "#f28b82"],
              },
            ],
          },
          options: { plugins: { legend: { position: "bottom" } } },
        });
      }
      // update bottom machine progress bars and summary
      const pbCoffee = document.getElementById("pb-coffee");
      const pbWater = document.getElementById("pb-water");
      const pbMilk = document.getElementById("pb-milk");
      const lowcount = document.getElementById("lowcount");
      const tempLarge = document.getElementById("temp-large");
      if (pbCoffee) pbCoffee.style.width = (m.coffee_level ?? 12) + "%";
      if (pbWater) pbWater.style.width = (m.water_level ?? 68) + "%";
      if (pbMilk) pbMilk.style.width = (m.milk_level ?? 45) + "%";
      if (lowcount) lowcount.textContent = m.low_stock ?? 0;
      if (tempLarge) tempLarge.textContent = m.temperature ?? "";

      // coffee page extras: cups, cleaning, health
      const pbCups = document.getElementById("pb-cups");
      const pbCleaning = document.getElementById("pb-cleaning");
      const pbHealth = document.getElementById("pb-health");
      const noteCups = document.getElementById("note-cups");
      const noteCleaning = document.getElementById("note-cleaning");
      const noteHealth = document.getElementById("note-health");
      if (pbCups) pbCups.style.width = (m.cups_remaining ?? 82) + "%";
      if (pbCleaning) pbCleaning.style.width = (m.cleaning_status ?? 92) + "%";
      if (pbHealth) pbHealth.style.width = (m.machine_health ?? 95) + "%";
      if (noteCups) noteCups.textContent = m.cups_note ?? "✓ Good";
      if (noteCleaning)
        noteCleaning.textContent =
          m.cleaning_note ?? "✓ Next cleaning in 8 days";
      if (noteHealth) noteHealth.textContent = m.health_note ?? "✓ Excellent";
    })
    .catch((err) => {
      // fallback: use local demo data if API fetch fails (e.g., CORS or server not running)
      console.warn("Dashboard API fetch failed, using demo data", err);
      const demoCoffee = {
        labels: ["8am", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm"],
        data: [3, 12, 9, 6, 5, 4, 10, 8],
      };
      const demoTemp = {
        labels: ["6am", "9am", "12pm", "3pm", "6pm"],
        data: [21.5, 22.0, 22.3, 22.5, 21.9],
      };
      document.getElementById("employees_in").textContent = 24;
      document.getElementById("employees_total").textContent = 32;
      document.getElementById("coffee_today").textContent = 47;
      document.getElementById("temperature").textContent = 22;
      document.getElementById("low_stock").textContent = 3;
      if (coffeeCanvas)
        makeCoffeeChart(
          coffeeCanvas.getContext("2d"),
          demoCoffee.labels,
          demoCoffee.data
        );
      if (tempCanvas)
        makeTempChart(
          tempCanvas.getContext("2d"),
          demoTemp.labels,
          demoTemp.data
        );
      // populate recent and employees fallback
      const recent = [
        { t: "14:32", text: "Sarah Johnson made a coffee", tag: "coffee" },
        { t: "14:28", text: "Temperature adjusted to 22°C", tag: "temp" },
        { t: "14:15", text: "Mike Peters left the office", tag: "presence" },
        { t: "14:10", text: "Low stock alert: Coffee beans", tag: "alert" },
        { t: "14:05", text: "Emma Wilson returned to office", tag: "presence" },
      ];
      const recentList = document.getElementById("recentList");
      if (recentList) {
        recentList.innerHTML = recent
          .map(
            (r) =>
              `<li><div class="time">${r.t}</div><div class="text">${r.text}</div><div class="tag">${r.tag}</div></li>`
          )
          .join("");
      }

      const employees = [
        {
          name: "Sarah Johnson",
          email: "sarah.j@company.com",
          phone: "+1 234 567 8901",
          dept: "Engineering",
          status: "In Office",
          coffee: "3 cups",
          last: "Just now",
        },
        {
          name: "Mike Peters",
          email: "mike.p@company.com",
          phone: "+1 234 567 8902",
          dept: "Design",
          status: "Out",
          coffee: "2 cups",
          last: "5 min ago",
        },
      ];
      employeesData = employees;
      renderEmployees(employeesData);

      if (presencePie) {
        new Chart(presencePie.getContext("2d"), {
          type: "pie",
          data: {
            labels: ["In Office", "Toilet/Away", "Out"],
            datasets: [
              {
                data: [24, 5, 3],
                backgroundColor: ["#7fcf9b", "#f7d36b", "#f28b82"],
              },
            ],
          },
          options: { plugins: { legend: { position: "bottom" } } },
        });
      }
      // fallback: update small bottom elements
      const pbCoffee = document.getElementById("pb-coffee");
      const pbWater = document.getElementById("pb-water");
      const pbMilk = document.getElementById("pb-milk");
      const lowcount = document.getElementById("lowcount");
      const tempLarge = document.getElementById("temp-large");
      if (pbCoffee) pbCoffee.style.width = "12%";
      if (pbWater) pbWater.style.width = "68%";
      if (pbMilk) pbMilk.style.width = "45%";
      if (lowcount) lowcount.textContent = "3";
      if (tempLarge) tempLarge.textContent = "22";
    });

  // Chat UI behaviour with conversation history
  const chatBtn = document.querySelector(".chat-btn");
  const chatPanel = document.getElementById("chatPanel");
  const closeChat = document.getElementById("closeChat");
  const sendChat = document.getElementById("sendChat");
  const chatInput = document.getElementById("chatInput");
  const chatLog = document.getElementById("chatLog");
  let streamingController = null; // AbortController for SSE

  // Conversation history management
  let conversationHistory = JSON.parse(localStorage.getItem('officeChat_history') || '[]');
  let isChatOpen = false;
  let isFirstOpen = true;

  function saveConversationHistory() {
    localStorage.setItem('officeChat_history', JSON.stringify(conversationHistory));
  }

  function loadConversationHistory() {
    if (!chatLog) return;
    
    // Clear current log first
    chatLog.innerHTML = '';

    // Show welcome message only on first open or if no history exists
    if (isFirstOpen || conversationHistory.length === 0) {
      showWelcomeMessage();
      isFirstOpen = false;
    }

    // Load previous conversations
    conversationHistory.forEach(msg => {
      appendMessageToDOM(msg.type, msg.content, msg.timestamp, false);
    });
    
    scrollToBottom();
  }

  function showWelcomeMessage() {
    if (!chatLog) return;
    
    const welcomeMsg = document.createElement('div');
    welcomeMsg.className = 'chat-msg bot welcome-msg';
    welcomeMsg.innerHTML = `
      <div class="welcome-text">
        👋 <strong>Hello! I'm your Office Assistant</strong><br>
        I'm here to help you with everything in the office! I can assist you with:
        <ul>
          <li>☕ Coffee machine status and usage</li>
          <li>🌡️ Temperature monitoring and control</li>
          <li>📊 Dashboard metrics and analytics</li>
          <li>👥 Employee presence tracking</li>
          <li>📦 Stock levels and inventory</li>
          <li>🏢 General office management</li>
        </ul>
        Feel free to ask me anything like "How many people are in the office?" or "What's the coffee level?"
      </div>
    `;
    chatLog.appendChild(welcomeMsg);
  }

  function appendMessage(who, text, saveToHistory = true) {
    const timestamp = new Date().toISOString();
    
    if (saveToHistory) {
      conversationHistory.push({
        type: who,
        content: text,
        timestamp: timestamp
      });
      saveConversationHistory();
    }
    
    appendMessageToDOM(who, text, timestamp, true);
  }

  function appendMessageToDOM(who, text, timestamp, shouldScroll = true) {
    if (!chatLog) return;
    
    const el = document.createElement("div");
    el.className = "chat-msg " + (who === "user" ? "user" : "bot");
    
    const messageContent = document.createElement("div");
    messageContent.className = "message-content";
  messageContent.innerHTML = renderMarkdown(text);
    
    const messageTime = document.createElement("div");
    messageTime.className = "message-time";
    const time = new Date(timestamp);
    messageTime.textContent = time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    el.appendChild(messageContent);
    el.appendChild(messageTime);
    chatLog.appendChild(el);
    
    if (shouldScroll) {
      scrollToBottom();
    }
  }

  function scrollToBottom() {
    if (chatLog) {
      chatLog.scrollTop = chatLog.scrollHeight;
    }
  }

  function showTypingIndicator() {
    if (!chatLog) return;
    const el = document.createElement("div");
    el.className = "chat-msg bot typing-indicator";
    el.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    el.id = "typing-indicator";
    chatLog.appendChild(el);
    scrollToBottom();
  }

  function renderMarkdown(md) {
    if (!md) return '';
    // Basic escaping of HTML first
    const escape = (s) => s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
    md = md.replace(/\r\n/g, '\n');
    // Code blocks ```
    md = md.replace(/```([\s\S]*?)```/g, (m, code) => `<pre class="code-block"><code>${escape(code.trim())}</code></pre>`);
    // Inline code `code`
    md = md.replace(/`([^`]+)`/g, (m, code) => `<code class="inline-code">${escape(code)}</code>`);
    // Bold **text**
    md = md.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Italic *text*
    md = md.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    // Unordered lists - lines starting with - or *
    md = md.replace(/^(?:-|\*) (.+)(?:\n(?:-|\*) .+)*/gm, block => {
      const items = block.split(/\n/).map(line => line.replace(/^(?:-|\*) /,'')).map(li => `<li>${li}</li>`).join('');
      return `<ul>${items}</ul>`;
    });
    // Line breaks - keep double newlines as paragraph separators
    md = md.split(/\n\n+/).map(p => `<p>${p.replace(/\n/g,'<br>')}</p>`).join('');
    return md;
  }

  function hideTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  function openChat() {
    if (chatPanel && !isChatOpen) {
      chatPanel.classList.remove("hidden");
      chatPanel.classList.remove('chat-collapse');
      chatPanel.style.display = "flex";
      requestAnimationFrame(() => chatPanel.classList.add('chat-expand'));
      isChatOpen = true;
      loadConversationHistory();
      setTimeout(() => chatInput?.focus(), 100);
      
      // Update button appearance when chat is open
      chatBtn?.classList.add("chat-open");
      
      // Update button icon to show close indicator
      const icon = chatBtn?.querySelector('i');
      if (icon) {
        icon.className = 'fa-solid fa-times';
      }
    }
  }

  function closeChatPanel() {
    if (chatPanel && isChatOpen) {
      chatPanel.classList.remove('chat-expand');
      chatPanel.classList.add('chat-collapse');
      setTimeout(() => {
        if (!isChatOpen) return;
      }, 300);
      setTimeout(() => {
        if (!isChatOpen) {
          chatPanel.classList.add("hidden");
          chatPanel.style.display = "none";
        }
      }, 280);
      isChatOpen = false;
      chatBtn?.classList.remove("chat-open");
      
      // Update button icon back to chat
      const icon = chatBtn?.querySelector('i');
      if (icon) {
        icon.className = 'fa-solid fa-comment-dots';
      }
    }
  }

  function toggleChat() {
    if (isChatOpen) {
      closeChatPanel();
    } else {
      openChat();
    }
  }

  // Event listeners
  if (chatBtn && chatPanel) {
    chatBtn.addEventListener("click", toggleChat);
  }
  
  if (document.getElementById("closeChat") && chatPanel) {
    document.getElementById("closeChat").addEventListener("click", closeChatPanel);
  }

  // Clear history functionality
  if (document.getElementById("clearHistory")) {
    document.getElementById("clearHistory").addEventListener("click", () => {
      if (confirm("Are you sure you want to clear all conversation history?")) {
        conversationHistory = [];
        saveConversationHistory();
        
        // Clear the chat log and show welcome message
        chatLog.innerHTML = '';
        showWelcomeMessage();
        
        // Show confirmation
        setTimeout(() => {
          appendMessage("bot", "🗑️ Conversation history has been cleared!", false);
        }, 500);
      }
    });
  }

  // Test AI functionality removed

  if (sendChat && chatInput) {
    sendChat.addEventListener("click", sendMessage);
  }
  
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    appendMessage("user", text);
    chatInput.value = "";
    
    // Disable input while processing
    chatInput.disabled = true;
    sendChat.disabled = true;
    
    // Show typing indicator
    showTypingIndicator();
    
    // Add timeout to prevent long waits
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout
    
    // Prefer streaming endpoint
    startStreamingResponse(text, controller, timeoutId);
  }

  function startStreamingResponse(userText, controller, timeoutId) {
    let botMessageEl = null;
    let aggregated = '';

    function createStreamingMessage() {
      const timestamp = new Date().toISOString();
      const el = document.createElement('div');
      el.className = 'chat-msg bot';
      const content = document.createElement('div');
      content.className = 'message-content';
      content.innerHTML = '<em>Thinking...</em>';
      const timeEl = document.createElement('div');
      timeEl.className = 'message-time';
      const time = new Date(timestamp);
      timeEl.textContent = time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      el.appendChild(content);
      el.appendChild(timeEl);
      chatLog.appendChild(el);
      scrollToBottom();
      return el;
    }

    showTypingIndicator();
    botMessageEl = createStreamingMessage();
    const contentDiv = botMessageEl.querySelector('.message-content');

    // Initiate fetch to SSE endpoint
    fetch('/api/ai_stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userText }),
      signal: controller.signal
    }).then(response => {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      hideTypingIndicator();
      clearTimeout(timeoutId);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      function read() {
        reader.read().then(({done, value}) => {
          if (done) {
            finalize();
            return;
          }
          const chunk = decoder.decode(value, {stream: true});
            chunk.split('\n\n').forEach(line => {
              if (line.startsWith('data: ')) {
                try {
                  const payload = JSON.parse(line.replace('data: ', ''));
                  if (payload.delta) {
                    aggregated += payload.delta;
                    if (contentDiv) contentDiv.innerHTML = renderMarkdown(aggregated);
                    scrollToBottom();
                  }
                  if (payload.done) {
                    finalize();
                  }
                  if (payload.error) {
                    if (contentDiv) contentDiv.innerHTML = renderMarkdown('❌ ' + payload.error);
                  }
                } catch (err) {
                  // ignore parse errors for partial lines
                }
              }
            });
          read();
        }).catch(err => {
          console.error('Stream read error', err);
          finalize();
        });
      }
      read();
    }).catch(e => {
      hideTypingIndicator();
      clearTimeout(timeoutId);
      if (contentDiv) contentDiv.innerHTML = renderMarkdown('❌ Streaming failed; falling back to full reply...');
      // Fallback non-stream request
      fetch('/api/ai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText })
      }).then(r => r.json()).then(j => {
        aggregated = j.reply || 'Assistant unavailable.';
        if (contentDiv) contentDiv.innerHTML = renderMarkdown(aggregated);
      });
    }).finally(() => {
      chatInput.disabled = false;
      sendChat.disabled = false;
      chatInput.focus();
    });

    function finalize() {
      if (!aggregated) aggregated = 'No response.';
      conversationHistory.push({ type: 'bot', content: aggregated, timestamp: new Date().toISOString() });
      saveConversationHistory();
    }
  }

  // Initialize chat state on page load - ensure chat is completely hidden
  if (chatPanel) {
    chatPanel.classList.add("hidden");
    chatPanel.style.display = "none";
    isChatOpen = false;
    
    // Ensure chat log is empty initially - welcome message only shows when opened
    if (chatLog) {
      chatLog.innerHTML = '';
    }
    
    // Ensure button shows correct initial icon
    const icon = chatBtn?.querySelector('i');
    if (icon) {
      icon.className = 'fa-solid fa-comment-dots';
    }
    
    // Remove any existing chat-open class
    if (chatBtn) {
      chatBtn.classList.remove("chat-open");
    }
  }

  // Temperature page behavior: update target display and Apply button
  const targetRange = document.getElementById("targetRange");
  const targetDisplay = document.getElementById("targetDisplay");
  const applyBtn = document.getElementById("applySettings");
  if (targetRange && targetDisplay) {
    targetRange.addEventListener("input", (e) => {
      targetDisplay.textContent = e.target.value + "°C";
    });
  }
  if (applyBtn) {
    applyBtn.addEventListener("click", () => {
      applyBtn.style.transform = "scale(0.98)";
      setTimeout(() => (applyBtn.style.transform = ""), 150);
      // visual confirmation — in a real app we'd POST settings to the API here
    });
  }
});
