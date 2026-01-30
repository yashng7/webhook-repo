const POLL_INTERVAL = 15;
const API_URL = "/api/events";

let countdown = POLL_INTERVAL;
let countdownInterval = null;
let currentFilter = "";

function init() {
    setupFilterListener();
    fetchEvents();
    startCountdown();
}

function setupFilterListener() {
    const filterSelect = document.getElementById("action-filter");
    filterSelect.addEventListener("change", function() {
        currentFilter = this.value;
        resetCountdown();
        fetchEvents();
    });
}

function startCountdown() {
    updateCountdownDisplay();
    countdownInterval = setInterval(function() {
        countdown--;
        updateCountdownDisplay();
        if (countdown <= 0) {
            fetchEvents();
            resetCountdown();
        }
    }, 1000);
}

function resetCountdown() {
    countdown = POLL_INTERVAL;
    updateCountdownDisplay();
}

function updateCountdownDisplay() {
    document.getElementById("countdown").textContent = countdown < 10 ? `0${countdown}s` : `${countdown}s`;
}

function fetchEvents() {
    const url = API_URL + "?limit=50" + (currentFilter ? `&action=${encodeURIComponent(currentFilter)}` : "");
    
    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error("API Error");
            return res.json();
        })
        .then(data => {
            renderEvents(data.events);
            updateStatus(true, data.pagination.total);
        })
        .catch(err => {
            console.error(err);
            updateStatus(false, 0);
        });
}

function updateStatus(connected, total) {
    const indicator = document.getElementById("connection-status");
    const lastUpdated = document.getElementById("last-updated");
    const totalEl = document.getElementById("total-count");
    
    if (connected) {
        indicator.classList.add("active");
        indicator.classList.remove("error");
        // Using "HH:MM:SS" format for technical feel
        const now = new Date();
        lastUpdated.textContent = now.toTimeString().split(' ')[0];
    } else {
        indicator.classList.remove("active");
        indicator.classList.add("error");
        lastUpdated.textContent = "ERR_CONN";
    }
    totalEl.textContent = total;
}

function renderEvents(events) {
    const container = document.getElementById("events-container");
    
    if (events.length === 0) {
        container.innerHTML = '<div class="empty-state">No events found in current stream.</div>';
        return;
    }
    
    let html = "";
    events.forEach((event, index) => {
        html += renderEventRow(event, index);
    });
    
    container.innerHTML = html;
}

function renderEventRow(event, index) {
    const action = event.action.toUpperCase();
    const timestamp = formatTimeAgo(event.timestamp);
    
    // Minimalist color coding (CSS vars mapped to specific accents)
    let dotColor = "background-color: var(--text-tertiary)";
    let actionColor = "color: var(--text-primary)";
    
    if (action === "PUSH") {
        dotColor = "background-color: var(--accent-green)";
        actionColor = "color: var(--accent-green)";
    } else if (action === "PULL_REQUEST") {
        dotColor = "background-color: var(--accent-blue)";
        actionColor = "color: var(--accent-blue)";
    } else if (action === "MERGE") {
        dotColor = "background-color: var(--accent-purple)";
        actionColor = "color: var(--accent-purple)";
    }

    // Branch logic
    let flowHtml = '';
    if (event.from_branch && event.to_branch) {
        flowHtml = `${escapeHtml(event.from_branch)} <span style="color:var(--text-tertiary)">→</span> <span class="highlight">${escapeHtml(event.to_branch)}</span>`;
    } else if (event.to_branch) {
        flowHtml = `to <span class="highlight">${escapeHtml(event.to_branch)}</span>`;
    }

    return `
        <article class="event-row" style="--delay: ${index}">
            <div class="event-indicator">
                <span class="type-dot" style="${dotColor}"></span>
            </div>
            <div class="event-main">
                <div class="event-header">
                    <span class="event-action" style="${actionColor}">${action}</span>
                    <span class="event-author">by ${escapeHtml(event.author)}</span>
                </div>
                <div class="branch-flow">
                    ${flowHtml}
                </div>
            </div>
            <div class="event-meta">
                <span class="time-ago">${timestamp}</span>
                <span class="req-id">ID: ${escapeHtml(event.request_id).substring(0, 8)}</span>
            </div>
        </article>
    `;
}

function formatTimeAgo(isoString) {
    if (!isoString) return "--";
    const diff = new Date() - new Date(isoString);
    const mins = Math.floor(diff / 60000);
    
    if (mins < 1) return "< 1m ago";
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return new Date(isoString).toLocaleDateString();
}

function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

document.addEventListener("DOMContentLoaded", init);