/**
 * Pi Portal - Frontend Application
 * 
 * Handles WebSocket communication, message display, and UI interactions.
 */

// ============================================
// Constants & Configuration
// ============================================

const RECONNECT_DELAY_MS = 2000;
const MAX_RECONNECT_ATTEMPTS = 10;
const PING_INTERVAL_MS = 30000;

// ============================================
// State
// ============================================

const state = {
    ws: null,
    connected: false,
    reconnectAttempts: 0,
    reconnectTimeout: null,
    pingInterval: null,
    isProcessing: false,
    chatStarted: false
};

// ============================================
// DOM Elements
// ============================================

const elements = {
    connectionStatus: document.getElementById('connectionStatus'),
    chatMessages: document.getElementById('chatMessages'),
    chatInput: document.getElementById('chatInput'),
    sendBtn: document.getElementById('sendBtn'),
    welcomeContainer: document.getElementById('welcomeContainer'),
    promptGrid: document.getElementById('promptGrid'),
    newSessionBtn: document.getElementById('newSessionBtn')
};

// ============================================
// WebSocket Connection
// ============================================

/**
 * Get the WebSocket URL based on current location.
 */
function getWebSocketUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/ws`;
}

/**
 * Connect to the WebSocket server.
 */
function connect() {
    if (state.ws && state.ws.readyState === WebSocket.OPEN) {
        return;
    }

    updateConnectionStatus('connecting');
    
    try {
        state.ws = new WebSocket(getWebSocketUrl());
        
        state.ws.onopen = handleOpen;
        state.ws.onclose = handleClose;
        state.ws.onerror = handleError;
        state.ws.onmessage = handleMessage;
    } catch (error) {
        console.error('WebSocket connection error:', error);
        scheduleReconnect();
    }
}

/**
 * Handle WebSocket connection opened.
 */
function handleOpen() {
    console.log('WebSocket connected');
    state.connected = true;
    state.reconnectAttempts = 0;
    updateConnectionStatus('connected');
    updateInputState();
    startPingInterval();
}

/**
 * Handle WebSocket connection closed.
 */
function handleClose(event) {
    console.log('WebSocket closed:', event.code, event.reason);
    state.connected = false;
    state.ws = null;
    updateConnectionStatus('disconnected');
    updateInputState();
    stopPingInterval();
    scheduleReconnect();
}

/**
 * Handle WebSocket error.
 */
function handleError(error) {
    console.error('WebSocket error:', error);
    updateConnectionStatus('disconnected');
}

/**
 * Handle incoming WebSocket message.
 */
function handleMessage(event) {
    try {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
            case 'status':
                handleStatusMessage(data);
                break;
            case 'message':
                handleChatMessage(data);
                break;
            case 'error':
                handleErrorMessage(data);
                break;
            case 'pong':
                // Ping response received, connection is alive
                break;
            default:
                console.warn('Unknown message type:', data.type);
        }
    } catch (error) {
        console.error('Error parsing message:', error);
    }
}

/**
 * Handle status messages from server.
 */
function handleStatusMessage(data) {
    switch (data.status) {
        case 'connected':
            console.log('Server confirmed connection');
            break;
        case 'processing':
            state.isProcessing = true;
            showTypingIndicator();
            updateInputState();
            break;
        case 'ready':
            state.isProcessing = false;
            hideTypingIndicator();
            updateInputState();
            break;
    }
}

/**
 * Handle chat messages from server.
 */
function handleChatMessage(data) {
    hideTypingIndicator();
    appendMessage(data.role, data.content);
}

/**
 * Handle error messages from server.
 */
function handleErrorMessage(data) {
    console.error('Server error:', data.message);
    hideTypingIndicator();
    state.isProcessing = false;
    updateInputState();
    
    // Show error in chat
    appendSystemMessage(`Error: ${data.message}`);
}

/**
 * Schedule a reconnection attempt.
 */
function scheduleReconnect() {
    if (state.reconnectTimeout) {
        return;
    }
    
    if (state.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.log('Max reconnection attempts reached');
        updateConnectionStatus('failed');
        return;
    }
    
    state.reconnectAttempts++;
    const delay = RECONNECT_DELAY_MS * Math.min(state.reconnectAttempts, 5);
    
    console.log(`Reconnecting in ${delay}ms (attempt ${state.reconnectAttempts})`);
    
    state.reconnectTimeout = setTimeout(() => {
        state.reconnectTimeout = null;
        connect();
    }, delay);
}

/**
 * Start ping interval to keep connection alive.
 */
function startPingInterval() {
    stopPingInterval();
    state.pingInterval = setInterval(() => {
        if (state.ws && state.ws.readyState === WebSocket.OPEN) {
            state.ws.send(JSON.stringify({ type: 'ping' }));
        }
    }, PING_INTERVAL_MS);
}

/**
 * Stop ping interval.
 */
function stopPingInterval() {
    if (state.pingInterval) {
        clearInterval(state.pingInterval);
        state.pingInterval = null;
    }
}

// ============================================
// UI Updates
// ============================================

/**
 * Update connection status display.
 */
function updateConnectionStatus(status) {
    const statusDot = elements.connectionStatus.querySelector('.status-dot');
    const statusText = elements.connectionStatus.querySelector('.status-text');
    
    // Remove all status classes
    statusDot.classList.remove('connected', 'connecting', 'disconnected');
    
    switch (status) {
        case 'connected':
            statusDot.classList.add('connected');
            statusText.textContent = 'Connected';
            break;
        case 'connecting':
            statusDot.classList.add('connecting');
            statusText.textContent = 'Connecting...';
            break;
        case 'disconnected':
            statusText.textContent = 'Disconnected';
            break;
        case 'failed':
            statusText.textContent = 'Connection failed';
            break;
    }
}

/**
 * Update input field state based on connection and processing state.
 */
function updateInputState() {
    const canSend = state.connected && !state.isProcessing && elements.chatInput.value.trim();
    elements.sendBtn.disabled = !canSend;
    elements.chatInput.disabled = !state.connected || state.isProcessing;
    
    if (state.isProcessing) {
        elements.chatInput.placeholder = 'Pi is thinking...';
    } else if (!state.connected) {
        elements.chatInput.placeholder = 'Connecting...';
    } else {
        elements.chatInput.placeholder = 'Ask Pi anything...';
    }
}

/**
 * Hide welcome container and show chat.
 */
function hideWelcome() {
    if (elements.welcomeContainer && !state.chatStarted) {
        state.chatStarted = true;
        elements.welcomeContainer.style.display = 'none';
    }
}

/**
 * Append a message to the chat.
 */
function appendMessage(role, content) {
    hideWelcome();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-role">${role === 'user' ? 'You' : 'Pi'}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Append a system message (errors, notifications).
 */
function appendSystemMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.innerHTML = `
        <div class="message-content" style="color: var(--accent-error); border-color: var(--accent-error);">
            ${escapeHtml(content)}
        </div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Show typing indicator.
 */
function showTypingIndicator() {
    hideTypingIndicator(); // Remove any existing indicator
    
    const indicator = document.createElement('div');
    indicator.className = 'message assistant';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = `
        <div class="message-header">
            <span class="message-role">Pi</span>
        </div>
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    elements.chatMessages.appendChild(indicator);
    scrollToBottom();
}

/**
 * Hide typing indicator.
 */
function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Scroll chat to bottom.
 */
function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

/**
 * Escape HTML to prevent XSS.
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Message Sending
// ============================================

/**
 * Send a message to the server.
 */
function sendMessage(content) {
    if (!state.connected || state.isProcessing || !content.trim()) {
        return;
    }
    
    // Display user message
    appendMessage('user', content);
    
    // Send to server
    state.ws.send(JSON.stringify({
        type: 'message',
        content: content.trim()
    }));
    
    // Clear input
    elements.chatInput.value = '';
    autoResizeTextarea();
    updateInputState();
}

// ============================================
// Starter Prompts
// ============================================

/**
 * Load and display starter prompts.
 */
async function loadStarterPrompts() {
    try {
        const response = await fetch('/api/config/starter-prompts');
        const data = await response.json();
        
        if (data.prompts && data.prompts.length > 0) {
            elements.promptGrid.innerHTML = data.prompts.map(prompt => `
                <button class="starter-prompt" data-prompt="${escapeHtml(prompt.text)}">
                    <span class="prompt-icon">${prompt.icon}</span>
                    <span class="prompt-text">${escapeHtml(prompt.text)}</span>
                </button>
            `).join('');
            
            // Add click handlers
            elements.promptGrid.querySelectorAll('.starter-prompt').forEach(btn => {
                btn.addEventListener('click', () => {
                    const promptText = btn.dataset.prompt;
                    if (state.connected) {
                        sendMessage(promptText);
                    }
                });
            });
        }
    } catch (error) {
        console.error('Error loading starter prompts:', error);
    }
}

// ============================================
// Input Handling
// ============================================

/**
 * Auto-resize textarea based on content.
 */
function autoResizeTextarea() {
    const textarea = elements.chatInput;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

/**
 * Handle input changes.
 */
function handleInputChange() {
    autoResizeTextarea();
    updateInputState();
}

/**
 * Handle key press in input.
 */
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        const content = elements.chatInput.value.trim();
        if (content && state.connected && !state.isProcessing) {
            sendMessage(content);
        }
    }
}

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    // Input events
    elements.chatInput.addEventListener('input', handleInputChange);
    elements.chatInput.addEventListener('keypress', handleKeyPress);
    
    // Send button
    elements.sendBtn.addEventListener('click', () => {
        const content = elements.chatInput.value.trim();
        if (content) {
            sendMessage(content);
        }
    });
    
    // New session button (placeholder for M2)
    elements.newSessionBtn.addEventListener('click', () => {
        console.log('New session clicked - will be implemented in M2');
    });
}

// ============================================
// Initialization
// ============================================

function init() {
    console.log('Pi Portal initializing...');
    
    setupEventListeners();
    loadStarterPrompts();
    connect();
    
    // Initial state
    updateInputState();
}

// Start the application
document.addEventListener('DOMContentLoaded', init);
