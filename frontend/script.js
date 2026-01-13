let currentMode = "chat";
const chatBox = document.getElementById("chat-box");
const msgInput = document.getElementById("msg");

// Background Animation Generation
function createBackground() {
    const wrap = document.createElement('div');
    wrap.className = 'wrap';
    document.body.prepend(wrap);

    const total = 200;
    const time = 10; // seconds

    for (let i = 0; i < total; i++) {
        const tri = document.createElement('div');
        tri.className = 'tri';

        // Random Generators matches SCSS logic
        // $size: random(50) * 1px;
        const size = Math.floor(Math.random() * 50) + 'px';

        // $rotate: random(360) * 1deg;
        const rotate = Math.floor(Math.random() * 360) + 'deg';

        // hsla(random(360), 100%, 50%, 1)
        const hue = Math.floor(Math.random() * 360);
        const color = `hsla(${hue}, 100%, 50%, 1)`;

        // translate3d(random(1000)px...) 
        // We centre it using range -1000 to 1000 for better spread
        const tx = (Math.random() * 2000 - 1000) + 'px';
        const ty = (Math.random() * 2000 - 1000) + 'px';

        // animation-delay: $i * -($time/$total)
        const delay = (i * -(time / total)) + 's';

        // Set CSS Variables
        tri.style.setProperty('--size', size);
        tri.style.setProperty('--rotate', rotate);
        tri.style.setProperty('--color', color);
        tri.style.setProperty('--tx', tx);
        tri.style.setProperty('--ty', ty);
        tri.style.setProperty('--delay', delay);

        wrap.appendChild(tri);
    }
}

// Init Animation
document.addEventListener('DOMContentLoaded', createBackground);

// Configure Marked.js
marked.setOptions({
    highlight: function (code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    },
    breaks: true
});

function setMode(mode) {
    currentMode = mode;

    // Update styling
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.mode === mode) btn.classList.add('active');
    });

    // Update placeholder
    const placeholders = {
        "chat": "Ask something...",
        "summarize": "Paste text to summarize...",
        "code_explain": "Paste code to explain..."
    };
    msgInput.setAttribute("placeholder", placeholders[mode]);
}

async function send() {
    let msg = msgInput.value.trim();
    if (!msg) return;

    // Add User Message
    addMessage(msg, "user-msg");
    msgInput.value = "";
    resizeTextarea(); // Reset height

    // Add Loading Indicator
    let loadingId = "loading-" + Date.now();
    let loadingDiv = addMessage('<span class="dot-pulse"></span><span class="dot-pulse delay-1"></span><span class="dot-pulse delay-2"></span>', "ai-msg loading", loadingId);

    try {
        let res = await fetch("/api/message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg, mode: currentMode })
        });

        // Remove loading
        document.getElementById(loadingId).remove();

        if (!res.ok) {
            let errorText = "Error communicating with server.";
            if (res.status === 500) {
                try {
                    let errorData = await res.json();
                    errorText = "Error: " + errorData.detail;
                } catch (e) { }
            }
            addMessage(errorText, "ai-msg error");
            return;
        }

        let data = await res.json();

        // Render Markdown and Stream/Type effect
        typeMessage(data.reply);

    } catch (error) {
        if (document.getElementById(loadingId)) document.getElementById(loadingId).remove();
        console.error("Fetch error:", error);
        addMessage("Error: Failed to fetch. (Is the backend server running?)", "ai-msg error");
    }
}

function addMessage(htmlContent, className, id = null) {
    let div = document.createElement("div");
    div.classList.add("message", ...className.split(" "));
    if (id) div.id = id;

    // For user messages, we just set text. For AI, we might pass HTML (loading dots)
    // but the main AI response comes via typeMessage
    div.innerHTML = htmlContent;

    chatBox.appendChild(div);
    scrollToBottom();
    return div;
}

function typeMessage(text) {
    let div = document.createElement("div");
    div.classList.add("message", "ai-msg");
    chatBox.appendChild(div);

    // Parse Markdown first
    let parsedHTML = marked.parse(text);
    div.innerHTML = parsedHTML;

    // Animate entry (Fade In / Slide Up handled by CSS)
    // Code highlighting happens automatically due to marked options + innerHTML set

    scrollToBottom();
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function handleKeyPress(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        send();
    }
}

function resizeTextarea() {
    msgInput.style.height = 'auto';
    msgInput.style.height = msgInput.scrollHeight + 'px';
}

// Event Listeners
msgInput.addEventListener('input', resizeTextarea);
