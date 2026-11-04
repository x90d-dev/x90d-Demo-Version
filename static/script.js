const textarea = document.querySelector("#question");
const charCount = document.querySelector("#charCount");
const chatTextarea = document.querySelector("#message");
const chatCharCount = document.querySelector("#chatCharCount");
const attachmentInput = document.querySelector("#attachment");
const attachmentName = document.querySelector("#attachmentName");
const themeToggle = document.querySelector("#themeToggle");
const chatStream = document.querySelector("#chatStream");
const sidebarClose = document.querySelector("#sidebarClose");
const sidebarOpen = document.querySelector("#sidebarOpen");
const composerPlus = document.querySelector("#composerPlus");
const composerMenu = document.querySelector("#composerMenu");

if (textarea && charCount) {
  const updateCount = () => {
    charCount.textContent = `${textarea.value.length} / ${textarea.maxLength}`;
  };
  textarea.addEventListener("input", updateCount);
  updateCount();
}

if (chatTextarea && chatCharCount) {
  const updateChatCount = () => {
    chatCharCount.textContent = `${chatTextarea.value.length} / ${chatTextarea.maxLength}`;
  };
  const resizeChatBox = () => {
    chatTextarea.style.height = "auto";
    chatTextarea.style.height = `${Math.min(chatTextarea.scrollHeight, 96)}px`;
  };
  chatTextarea.addEventListener("input", updateChatCount);
  chatTextarea.addEventListener("input", resizeChatBox);
  chatTextarea.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      chatTextarea.form?.requestSubmit();
    }
  });
  updateChatCount();
  resizeChatBox();
}

document.addEventListener("click", (event) => {
  const button = event.target.closest(".quick-prompt");
  if (!button || button.classList.contains("copy-code-button")) return;
  if (!chatTextarea) return;
  chatTextarea.value = button.dataset.prompt || "";
  chatTextarea.focus();
  chatTextarea.dispatchEvent(new Event("input"));
});

const chatForm = document.querySelector("#chatForm");
if (chatForm) {
  chatForm.addEventListener("submit", async (event) => {
    const asyncUrl = chatForm.dataset.sendUrl;
    if (!asyncUrl) return;
    event.preventDefault();
    if (chatForm.dataset.pending === "true") return;

    const submitButton = chatForm.querySelector("button[type='submit']");
    const formData = new FormData(chatForm);
    const message = String(formData.get("message") || "").trim();
    const file = attachmentInput?.files?.[0];
    if (!message && !file) {
      chatTextarea?.focus();
      return;
    }

    const displayMessage = buildPendingUserMessage(message, file, formData.get("web_search") === "on");
    appendUserMessage(displayMessage, getSelectedModeLabel());
    resetComposer();
    closeComposerMenu();
    setSubmitState(submitButton, true);
    const loading = showThinkingState();

    try {
      const response = await fetch(asyncUrl, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "fetch" },
      });
      const payload = await response.json();
      if (!payload.ok) {
        throw new Error(payload.message || "Terjadi masalah saat memproses jawaban.");
      }
      updateSelectedOptions(payload);
      loading?.remove();
      await appendAiMessageTyping(payload.ai_response || "");
    } catch (error) {
      loading?.remove();
      appendAiMessage(String(error.message || "Terjadi masalah saat memproses jawaban. Coba kirim ulang soal atau jawaban."), true);
    } finally {
      setSubmitState(submitButton, false);
    }
  });
}

if (composerPlus && chatForm) {
  composerPlus.addEventListener("click", (event) => {
    event.stopPropagation();
    const isOpen = chatForm.classList.toggle("composer-menu-open");
    composerPlus.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });
}

document.addEventListener("click", (event) => {
  if (!chatForm?.classList.contains("composer-menu-open")) return;
  if (event.target.closest("#composerMenu") || event.target.closest("#composerPlus")) return;
  closeComposerMenu();
});

function closeComposerMenu() {
  chatForm?.classList.remove("composer-menu-open");
  composerPlus?.setAttribute("aria-expanded", "false");
}

if (sidebarClose) {
  sidebarClose.addEventListener("click", () => {
    document.body.classList.add("sidebar-collapsed");
    localStorage.setItem("corechiper-sidebar", "closed");
  });
}

if (sidebarOpen) {
  sidebarOpen.addEventListener("click", () => {
    document.body.classList.remove("sidebar-collapsed");
    localStorage.setItem("corechiper-sidebar", "open");
  });
}

if (document.body.classList.contains("chat-page") && localStorage.getItem("corechiper-sidebar") === "closed") {
  document.body.classList.add("sidebar-collapsed");
}

if (attachmentInput && attachmentName) {
  attachmentInput.addEventListener("change", () => {
    const file = attachmentInput.files?.[0];
    attachmentName.textContent = file ? file.name : "";
  });
}

renderAiMessages();

if (chatStream) {
  chatStream.scrollTop = chatStream.scrollHeight;
}

if (themeToggle) {
  const isChatPage = document.body.classList.contains("chat-page");
  const savedTheme = localStorage.getItem("corechiper-theme");
  if (isChatPage) {
    if (savedTheme === "light") {
      document.body.classList.add("theme-light");
    }
    themeToggle.textContent = document.body.classList.contains("theme-light") ? "Gelap" : "Terang";
    themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("theme-light");
      const isLight = document.body.classList.contains("theme-light");
      localStorage.setItem("corechiper-theme", isLight ? "light" : "dark");
      themeToggle.textContent = isLight ? "Gelap" : "Terang";
    });
  } else {
    if (savedTheme === "dark") {
      document.body.classList.add("theme-dark");
    }
    themeToggle.textContent = document.body.classList.contains("theme-dark") ? "Terang" : "Gelap";
    themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("theme-dark");
      const isDark = document.body.classList.contains("theme-dark");
      localStorage.setItem("corechiper-theme", isDark ? "dark" : "light");
      themeToggle.textContent = isDark ? "Terang" : "Gelap";
    });
  }
}

function showThinkingState() {
  if (!chatStream) return null;
  const loading = document.createElement("article");
  loading.className = "message-row ai-row loading-bubble";
  loading.innerHTML = `
    <div class="avatar ai-avatar">C</div>
    <div class="message-content">
      <span class="chat-meta">CoreChiperAgent</span>
      <p><span class="typing-dots"><span></span><span></span><span></span></span>Berpikir</p>
    </div>
  `;
  chatStream.appendChild(loading);
  chatStream.scrollTop = chatStream.scrollHeight;
  return loading;
}

function buildPendingUserMessage(message, file, webSearchOn) {
  let display = message || "Tolong analisis file ini.";
  if (file?.name) {
    display += `\n\n[File: ${file.name}]`;
  }
  if (webSearchOn) {
    display += "\n\n[Web search aktif]";
  }
  return display;
}

function appendUserMessage(message, modeLabel) {
  if (!chatStream) return;
  removeWelcomeState();
  const userName = chatForm?.dataset.userName || "Admin";
  const userInitial = chatForm?.dataset.userInitial || "A";
  const row = document.createElement("article");
  row.className = "message-row user-row";
  row.innerHTML = `
    <div class="avatar user-avatar">${escapeHtml(userInitial)}</div>
    <div class="message-content">
      <span class="chat-meta">${escapeHtml(userName)} - ${escapeHtml(modeLabel || "Chat")}</span>
      <p>${escapeHtml(message)}</p>
    </div>
  `;
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
}

function appendAiMessage(message, isError = false) {
  if (!chatStream) return null;
  const row = createAiMessageRow();
  const content = row.querySelector(".ai-message-content");
  const source = content.querySelector(".markdown-source");
  if (isError) {
    content.classList.add("error-ai-message");
  }
  source.textContent = message;
  chatStream.appendChild(row);
  renderAiMessages();
  chatStream.scrollTop = chatStream.scrollHeight;
  return row;
}

async function appendAiMessageTyping(message) {
  if (!chatStream) return;
  const row = createAiMessageRow();
  const content = row.querySelector(".ai-message-content");
  const source = content.querySelector(".markdown-source");
  source.classList.add("typing-response");
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;

  const text = String(message || "");
  let index = 0;
  const chunkSize = Math.max(2, Math.ceil(text.length / 900));
  await new Promise((resolve) => {
    const tick = () => {
      index = Math.min(index + chunkSize, text.length);
      source.textContent = text.slice(0, index);
      chatStream.scrollTop = chatStream.scrollHeight;
      if (index < text.length) {
        setTimeout(tick, 12);
      } else {
        resolve();
      }
    };
    tick();
  });

  source.classList.remove("typing-response");
  const insightCard = buildInsightCard(text);
  if (insightCard) {
    source.insertAdjacentHTML("beforebegin", insightCard);
  }
  source.innerHTML = renderBasicMarkdown(text);
  source.classList.add("rendered");
  source.dataset.rendered = "true";
  addMessageTools(content);
  chatStream.scrollTop = chatStream.scrollHeight;
}

function createAiMessageRow() {
  const logoUrl = chatForm?.dataset.logoUrl || "";
  const row = document.createElement("article");
  row.className = "message-row ai-row";
  row.innerHTML = `
    ${logoUrl ? `<img class="avatar ai-avatar image-avatar" src="${escapeHtml(logoUrl)}" alt="CoreChiperAgent">` : `<div class="avatar ai-avatar">C</div>`}
    <div class="message-content ai-message-content">
      <span class="chat-meta">CoreChiperAgent</span>
      <div class="ai-response markdown-source"></div>
    </div>
  `;
  return row;
}

function addMessageTools(content) {
  if (!content || content.querySelector(".message-tools")) return;
  content.insertAdjacentHTML("beforeend", `
    <div class="message-tools" aria-label="Aksi lanjutan">
      <button class="mini-action quick-prompt" type="button" data-prompt="Uji lagi jawaban terakhir dengan cara berbeda dan cek semua syarat.">Uji Lagi</button>
      <button class="mini-action quick-prompt" type="button" data-prompt="Buat training dari kesalahan jawaban terakhir. Tulis trigger dan koreksi singkatnya.">Buat Training</button>
      <button class="mini-action quick-prompt" type="button" data-prompt="Naikkan level soal terakhir menjadi lebih sulit dan multi-syarat.">Naikkan Level</button>
      <button class="mini-action quick-prompt" type="button" data-prompt="Cek konsistensi soal terakhir. Jika data bertentangan, jelaskan kontradiksinya.">Cek Konsistensi</button>
      <button class="mini-action quick-prompt" type="button" data-prompt="Ringkas koreksi jawaban terakhir dalam poin pendek.">Ringkas Koreksi</button>
    </div>
  `);
}

function removeWelcomeState() {
  chatStream?.querySelector(".welcome-chat")?.remove();
}

function resetComposer() {
  if (chatTextarea) {
    chatTextarea.value = "";
    chatTextarea.dispatchEvent(new Event("input"));
  }
  if (attachmentInput) {
    attachmentInput.value = "";
  }
  if (attachmentName) {
    attachmentName.textContent = "";
  }
}

function setSubmitState(button, pending) {
  if (!button || !chatForm) return;
  chatForm.dataset.pending = pending ? "true" : "false";
  button.disabled = pending;
  button.textContent = pending ? "Berpikir" : "Kirim";
}

function getSelectedModeLabel() {
  const select = document.querySelector("#mode");
  const profile = document.querySelector("#agent_profile");
  const modeLabel = select?.selectedOptions?.[0]?.textContent || "Chat";
  const profileLabel = profile?.selectedOptions?.[0]?.textContent || "Normal";
  return `${modeLabel} / ${profileLabel}`;
}

function updateSelectedOptions(payload) {
  const modeSelect = document.querySelector("#mode");
  const levelSelect = document.querySelector("#reasoning_level");
  const profileSelect = document.querySelector("#agent_profile");
  if (modeSelect && payload.selected_mode) modeSelect.value = payload.selected_mode;
  if (levelSelect && payload.reasoning_level) levelSelect.value = payload.reasoning_level;
  if (profileSelect && payload.selected_agent_profile) profileSelect.value = payload.selected_agent_profile;
}

function renderAiMessages() {
  document.querySelectorAll(".ai-message-content").forEach((content) => {
    const source = content.querySelector(".markdown-source");
    if (!source || source.dataset.rendered === "true") return;
    const text = source.textContent || "";
    const insightCard = buildInsightCard(text);
    if (insightCard) {
      source.insertAdjacentHTML("beforebegin", insightCard);
    }
    source.innerHTML = renderBasicMarkdown(text);
    source.classList.add("rendered");
    source.dataset.rendered = "true";
  });
  document.querySelectorAll(".markdown-source").forEach((source) => {
    if (source.dataset.rendered === "true" || source.closest(".ai-message-content")) return;
    const text = source.textContent || "";
    source.innerHTML = renderBasicMarkdown(text);
    source.classList.add("rendered");
    source.dataset.rendered = "true";
  });
}

function renderBasicMarkdown(text) {
  const codeBlocks = [];
  let working = text.replace(/```([\w-]*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    const index = codeBlocks.length;
    const language = lang ? `<span>${escapeHtml(lang)}</span>` : "<span>Kode</span>";
    codeBlocks.push(`
      <div class="code-block">
        <div class="code-toolbar">
          ${language}
          <button class="copy-code-button" type="button">Copy</button>
        </div>
        <pre><code>${escapeHtml(code.trim())}</code></pre>
      </div>
    `);
    return `@@CODE_BLOCK_${index}@@`;
  });

  const mathBlocks = [];
  working = working.replace(/\$\$([\s\S]*?)\$\$/g, (_, math) => {
    const index = mathBlocks.length;
    mathBlocks.push(renderMathBlock(math.trim()));
    return `@@MATH_BLOCK_${index}@@`;
  });

  working = escapeHtml(working);
  working = working.replace(/`([^`]+)`/g, "<code>$1</code>");

  const blocks = working.split(/\n{2,}/).map((block) => renderBlock(block.trim())).filter(Boolean);
  let html = blocks.join("");
  codeBlocks.forEach((code, index) => {
    html = html.replace(`@@CODE_BLOCK_${index}@@`, code);
  });
  mathBlocks.forEach((math, index) => {
    html = html.replace(`@@MATH_BLOCK_${index}@@`, math);
  });
  return html;
}

function renderBlock(block) {
  if (!block) return "";
  if (/^@@CODE_BLOCK_\d+@@$/.test(block)) {
    return block;
  }
  if (/^@@MATH_BLOCK_\d+@@$/.test(block)) {
    return block;
  }
  const lines = block.split("\n").filter((line) => line.trim());
  if (lines.every((line) => /^\s*[-*]\s+/.test(line))) {
    return `<ul>${lines.map((line) => `<li>${line.replace(/^\s*[-*]\s+/, "")}</li>`).join("")}</ul>`;
  }
  if (lines.every((line) => /^\s*\d+\.\s+/.test(line))) {
    return `<ol>${lines.map((line) => `<li>${line.replace(/^\s*\d+\.\s+/, "")}</li>`).join("")}</ol>`;
  }
  if (/^(jawaban akhir|kesimpulan|tidak ada solusi|status|nilai)\s*:/i.test(lines[0]) || /^tidak ada solusi/i.test(lines[0])) {
    const paragraph = lines.join("<br>");
    return `<p class="final-answer-line">${paragraph}</p>`;
  }
  if (lines.some((line) => isAutoMathLine(line))) {
    return renderMixedMathLines(lines);
  }
  return `<p>${lines.join("<br>")}</p>`;
}

function renderMathBlock(math) {
  const lines = String(math || "")
    .split(/\\\\|\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  if (!lines.length) return "";
  return `<div class="math-block">${lines.map((line) => `<div class="math-line">${renderMathExpression(line)}</div>`).join("")}</div>`;
}

function renderMathExpression(expression) {
  const source = String(expression || "").trim();
  let output = "";
  let index = 0;

  while (index < source.length) {
    if (source.startsWith("\\,", index)) {
      output += " ";
      index += 2;
      continue;
    }

    if (source.startsWith("\\text", index)) {
      const group = readMathGroup(source, index + 5);
      if (group) {
        output += `<span class="math-text">${escapeHtml(group.value)}</span>`;
        index = group.end;
        continue;
      }
    }

    if (source.startsWith("\\frac", index)) {
      const numerator = readMathGroup(source, index + 5);
      const denominator = numerator ? readMathGroup(source, numerator.end) : null;
      if (numerator && denominator) {
        output += `<span class="math-frac"><span class="math-num">${renderMathExpression(numerator.value)}</span><span class="math-den">${renderMathExpression(denominator.value)}</span></span>`;
        index = denominator.end;
        continue;
      }
    }

    if (source.startsWith("\\sqrt", index)) {
      const radicand = readMathGroup(source, index + 5);
      if (radicand) {
        output += `<span class="math-root"><span class="math-root-symbol">&radic;</span><span class="math-radicand">${renderMathExpression(radicand.value)}</span></span>`;
        index = radicand.end;
        continue;
      }
    }

    const char = source[index];
    if (char === "√") {
      const radicand = readRootRadicand(source, index + 1);
      if (radicand) {
        output += `<span class="math-root"><span class="math-root-symbol">&radic;</span><span class="math-radicand">${renderMathExpression(radicand.value)}</span></span>`;
        index = radicand.end;
        continue;
      }
    }

    if (char === "^" || char === "_") {
      const group = readMathGroup(source, index + 1, true);
      if (group) {
        const tag = char === "^" ? "sup" : "sub";
        output += `<${tag}>${renderMathExpression(group.value)}</${tag}>`;
        index = group.end;
        continue;
      }
    }

    if (/[A-Za-z]/.test(char)) {
      let end = index + 1;
      while (end < source.length && /[A-Za-z]/.test(source[end])) end += 1;
      output += `<var>${escapeHtml(source.slice(index, end))}</var>`;
      index = end;
      continue;
    }

    if (char === "\\") {
      const command = source.slice(index).match(/^\\([a-zA-Z]+)/);
      if (command) {
        output += escapeHtml(command[1]);
        index += command[0].length;
        continue;
      }
    }

    output += escapeHtml(char);
    index += 1;
  }

  return output;
}

function renderMixedMathLines(lines) {
  const parts = [];
  let textBuffer = [];

  const flushText = () => {
    if (!textBuffer.length) return;
    parts.push(`<p>${textBuffer.join("<br>")}</p>`);
    textBuffer = [];
  };

  lines.forEach((line) => {
    if (isAutoMathLine(line)) {
      flushText();
      parts.push(renderMathBlock(convertPlainMathToLatex(line)));
    } else {
      textBuffer.push(line);
    }
  });
  flushText();
  return parts.join("");
}

function isAutoMathLine(line) {
  const clean = String(line || "").trim();
  if (!clean || clean.length > 180) return false;
  if (/^https?:\/\//i.test(clean)) return false;
  const hasRelation = /=|≤|≥|&lt;|&gt;/.test(clean);
  const hasMathToken = /\bper\b|\^|√|\\sqrt|\\frac|\([^)]+\)|[A-Za-z]\d|\d\s*[+\-x*]\s*\d/.test(clean);
  const hasVariableOrNumber = /[A-Za-z]|\d/.test(clean);
  return hasRelation && hasMathToken && hasVariableOrNumber;
}

function convertPlainMathToLatex(line) {
  let clean = String(line || "").trim();
  clean = clean.replace(/&lt;/g, "<").replace(/&gt;/g, ">");
  clean = clean.replace(/√\(([^()]+)\)/g, "\\sqrt{$1}");
  clean = clean.replace(/√([A-Za-z0-9]+)/g, "\\sqrt{$1}");
  const relation = clean.match(/(<=|>=|=|<|>)/);
  if (!relation) return convertPerExpression(clean);

  const operator = relation[0];
  const index = clean.indexOf(operator);
  const left = clean.slice(0, index).trim();
  const right = clean.slice(index + operator.length).trim();
  return `${convertPerExpression(left)} ${operator} ${convertPerExpression(right)}`;
}

function convertPerExpression(part) {
  const clean = String(part || "").trim();
  const match = clean.match(/^(.+?)\s+per\s+(.+)$/i);
  if (!match) return clean;
  return `\\frac{${trimOuterParentheses(match[1].trim())}}{${trimOuterParentheses(match[2].trim())}}`;
}

function trimOuterParentheses(value) {
  const clean = String(value || "").trim();
  if (clean.startsWith("(") && clean.endsWith(")") && hasBalancedOuterParentheses(clean)) {
    return clean.slice(1, -1).trim();
  }
  return clean;
}

function hasBalancedOuterParentheses(value) {
  let depth = 0;
  for (let index = 0; index < value.length; index += 1) {
    if (value[index] === "(") depth += 1;
    if (value[index] === ")") depth -= 1;
    if (depth === 0 && index < value.length - 1) return false;
  }
  return depth === 0;
}

function readRootRadicand(source, start) {
  let index = start;
  while (index < source.length && /\s/.test(source[index])) index += 1;
  if (source[index] === "(") {
    let depth = 0;
    let value = "";
    for (let cursor = index; cursor < source.length; cursor += 1) {
      const char = source[cursor];
      if (char === "(") {
        if (depth > 0) value += char;
        depth += 1;
        continue;
      }
      if (char === ")") {
        depth -= 1;
        if (depth === 0) return { value, end: cursor + 1 };
        value += char;
        continue;
      }
      value += char;
    }
    return null;
  }

  const match = source.slice(index).match(/^([A-Za-z0-9]+)/);
  if (!match) return null;
  return { value: match[1], end: index + match[1].length };
}

function readMathGroup(source, start, allowSingle = false) {
  let index = start;
  while (index < source.length && /\s/.test(source[index])) index += 1;
  if (source[index] !== "{") {
    if (!allowSingle || index >= source.length) return null;
    return { value: source[index], end: index + 1 };
  }

  let depth = 0;
  let value = "";
  for (let cursor = index; cursor < source.length; cursor += 1) {
    const char = source[cursor];
    if (char === "{") {
      if (depth > 0) value += char;
      depth += 1;
      continue;
    }
    if (char === "}") {
      depth -= 1;
      if (depth === 0) {
        return { value, end: cursor + 1 };
      }
      value += char;
      continue;
    }
    value += char;
  }
  return null;
}

function buildInsightCard(text) {
  const lower = text.toLowerCase();
  const isReasoning = [
    "analisis kondisi awal",
    "analisis perubahan",
    "bentuk kondisi akhir",
    "persamaan",
    "validasi semua syarat",
    "tidak ada solusi",
  ].some((keyword) => lower.includes(keyword));
  const isEvaluation = ["nilai:", "status:", "kesalahan utama", "koreksi"].some((keyword) => lower.includes(keyword));

  if (!isReasoning && !isEvaluation) return "";

  const title = isEvaluation ? "Evaluation Card" : "Reasoning Summary Card";
  const rows = isEvaluation
    ? [
        ["Nilai", findLine(text, "Nilai") || "Lihat pembahasan"],
        ["Status", findLine(text, "Status") || "Lihat pembahasan"],
        ["Kesalahan utama", findLine(text, "Kesalahan utama") || "Dicek di jawaban"],
        ["Koreksi", findLine(text, "Koreksi") || "Dicek di jawaban"],
      ]
    : [
        ["Variabel", findLine(text, "Variabel") || "Ada di pembahasan"],
        ["Kondisi awal", hasText(lower, "kondisi awal")],
        ["Kondisi akhir", hasText(lower, "kondisi akhir")],
        ["Persamaan", hasText(lower, "persamaan")],
        ["Validasi", hasText(lower, "validasi")],
        ["Kesimpulan", findLine(text, "Kesimpulan") || hasText(lower, "tidak ada solusi")],
      ];

  return `
    <section class="insight-card">
      <h3>${title}</h3>
      <div class="insight-grid">
        ${rows.map(([label, value]) => `<div><strong>${escapeHtml(label)}</strong>${escapeHtml(value)}</div>`).join("")}
      </div>
    </section>
  `;
}

function findLine(text, label) {
  const pattern = new RegExp(`^\\s*${label}\\s*:?\\s*(.+)$`, "im");
  const match = text.match(pattern);
  return match ? match[1].trim().slice(0, 120) : "";
}

function hasText(text, keyword) {
  return text.includes(keyword) ? "Terdeteksi" : "Belum terdeteksi";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest(".copy-code-button");
  if (!button) return;

  const codeBlock = button.closest(".code-block");
  const code = codeBlock?.querySelector("code")?.textContent || "";
  if (!code.trim()) return;

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(code);
    } else {
      fallbackCopy(code);
    }
    const original = button.textContent;
    button.textContent = "Tersalin";
    button.disabled = true;
    setTimeout(() => {
      button.textContent = original || "Copy";
      button.disabled = false;
    }, 1200);
  } catch (_error) {
    fallbackCopy(code);
  }
});

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}
