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
    chatStarted: false,
    // Streaming message state
    currentMessageElement: null,
    currentMessageContent: '',
    currentThinkingContent: '',
    // Session state
    sessions: [],
    activeSessionId: null,    // Session Pi is working in (can send messages)
    viewingSessionId: null,   // Session currently displayed (null = welcome)
    sessionRefreshPending: false
};

/**
 * Check if we're viewing a past (read-only) session.
 */
function isViewingPastSession() {
    return state.viewingSessionId !== null && 
           state.viewingSessionId !== state.activeSessionId;
}

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
    newSessionBtn: document.getElementById('newSessionBtn'),
    sessionList: document.getElementById('sessionList')
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
            case 'text_delta':
                handleTextDelta(data);
                break;
            case 'thinking_delta':
                handleThinkingDelta(data);
                break;
            case 'tool_start':
                handleToolStart(data);
                break;
            case 'tool_result':
                handleToolResult(data);
                break;
            case 'message_complete':
                handleMessageComplete(data);
                break;
            case 'message':
                // Legacy message format (non-streaming)
                handleChatMessage(data);
                break;
            case 'error':
                handleErrorMessage(data);
                break;
            case 'pong':
                // Ping response received, connection is alive
                break;
            case 'new_session_created':
                handleNewSessionCreated(data);
                break;
            default:
                console.log('Unhandled message type:', data.type);
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
    finalizeStreamingMessage();
    state.isProcessing = false;
    updateInputState();
    
    // Show error in chat
    appendSystemMessage(`Error: ${data.message}`);
}

/**
 * Handle streaming text delta.
 */
function handleTextDelta(data) {
    hideTypingIndicator();
    
    // Create streaming message element if needed
    if (!state.currentMessageElement) {
        createStreamingMessage();
    }
    
    // Append delta to content
    state.currentMessageContent += data.delta;
    updateStreamingMessageContent();
}

/**
 * Handle streaming thinking delta.
 */
function handleThinkingDelta(data) {
    hideTypingIndicator();
    
    // Create streaming message element if needed
    if (!state.currentMessageElement) {
        createStreamingMessage();
    }
    
    // Update thinking content (shown as collapsed by default)
    state.currentThinkingContent += data.delta;
    updateStreamingThinkingContent();
}

/**
 * Handle tool execution start.
 */
function handleToolStart(data) {
    hideTypingIndicator();
    
    // Create streaming message element if needed
    if (!state.currentMessageElement) {
        createStreamingMessage();
    }
    
    // Add tool indicator
    const toolIndicator = document.createElement('div');
    toolIndicator.className = 'tool-indicator running';
    toolIndicator.dataset.toolUseId = data.tool_use_id || '';
    toolIndicator.innerHTML = `
        <span class="tool-icon">🔧</span>
        <span class="tool-name">Running: ${escapeHtml(data.tool)}</span>
        <span class="tool-spinner"></span>
    `;
    
    const contentEl = state.currentMessageElement.querySelector('.message-content');
    if (contentEl) {
        contentEl.appendChild(toolIndicator);
        scrollToBottom();
    }
}

/**
 * Handle tool execution result.
 */
function handleToolResult(data) {
    // Find and update the tool indicator
    if (state.currentMessageElement) {
        const indicators = state.currentMessageElement.querySelectorAll('.tool-indicator.running');
        indicators.forEach(indicator => {
            if (!data.tool_use_id || indicator.dataset.toolUseId === data.tool_use_id) {
                indicator.classList.remove('running');
                indicator.classList.add(data.success ? 'success' : 'error');
                const spinner = indicator.querySelector('.tool-spinner');
                if (spinner) {
                    spinner.remove();
                }
                const icon = indicator.querySelector('.tool-icon');
                if (icon) {
                    icon.textContent = data.success ? '✓' : '✗';
                }
            }
        });
    }
}

/**
 * Handle message complete event.
 */
function handleMessageComplete(data) {
    hideTypingIndicator();
    
    // If we have a streaming message, finalize it
    if (state.currentMessageElement) {
        finalizeStreamingMessage();
    } else if (data.content) {
        // No streaming happened, just show the complete message
        appendMessage('assistant', data.content);
    }
    
    // Update session ID if provided
    if (data.session_id) {
        state.activeSessionId = data.session_id;
        state.viewingSessionId = data.session_id;
    }
    
    // Refresh session list (new session may have been created)
    scheduleSessionRefresh();
}

/**
 * Create a new streaming message element.
 */
function createStreamingMessage() {
    hideWelcome();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant streaming';
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-role">Pi</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-thinking" style="display: none;">
            <details>
                <summary>Thinking...</summary>
                <div class="thinking-content"></div>
            </details>
        </div>
        <div class="message-content"></div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
    state.currentMessageElement = messageDiv;
    state.currentMessageContent = '';
    state.currentThinkingContent = '';
    scrollToBottom();
}

/**
 * Update the streaming message content.
 */
function updateStreamingMessageContent() {
    if (!state.currentMessageElement) return;
    
    const contentEl = state.currentMessageElement.querySelector('.message-content');
    if (contentEl) {
        // Render markdown-ish content (basic for now)
        contentEl.innerHTML = renderContent(state.currentMessageContent);
        scrollToBottom();
    }
}

/**
 * Update the streaming thinking content.
 */
function updateStreamingThinkingContent() {
    if (!state.currentMessageElement) return;
    
    const thinkingEl = state.currentMessageElement.querySelector('.message-thinking');
    const thinkingContentEl = state.currentMessageElement.querySelector('.thinking-content');
    
    if (thinkingEl && thinkingContentEl && state.currentThinkingContent) {
        thinkingEl.style.display = 'block';
        thinkingContentEl.textContent = state.currentThinkingContent;
    }
}

/**
 * Finalize the streaming message.
 */
function finalizeStreamingMessage() {
    if (state.currentMessageElement) {
        state.currentMessageElement.classList.remove('streaming');
        state.currentMessageElement = null;
    }
    state.currentMessageContent = '';
    state.currentThinkingContent = '';
}

/**
 * Render message content with basic formatting.
 */
function renderContent(content) {
    // Basic markdown-like rendering
    let html = escapeHtml(content);
    
    // Code blocks (```)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>');
    
    // Inline code (`)
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold (**)
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic (*)
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    
    return html;
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
    const readOnly = isViewingPastSession();
    const canSend = state.connected && !state.isProcessing && !readOnly && elements.chatInput.value.trim();
    
    elements.sendBtn.disabled = !canSend;
    elements.chatInput.disabled = !state.connected || state.isProcessing || readOnly;
    
    if (readOnly) {
        elements.chatInput.placeholder = 'Viewing past session (read-only)';
    } else if (state.isProcessing) {
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
// Session List
// ============================================

/**
 * Load sessions from the API.
 */
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        
        if (data.sessions) {
            state.sessions = data.sessions;
            renderSessionList();
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

/**
 * Render the session list in the sidebar.
 */
function renderSessionList() {
    if (!elements.sessionList) return;
    
    if (state.sessions.length === 0) {
        elements.sessionList.innerHTML = `
            <div class="session-list-empty">
                <p>No sessions yet</p>
                <p class="hint">Start a conversation below</p>
            </div>
        `;
        return;
    }
    
    const sessionItems = state.sessions.map(session => {
        const isViewing = session.id === state.viewingSessionId;
        const isLive = session.id === state.activeSessionId;
        const date = formatSessionDate(session.timestamp);
        const messageCount = session.message_count || 0;
        
        const classes = ['session-item'];
        if (isViewing) classes.push('active');
        if (isLive) classes.push('live');
        
        return `
            <div class="${classes.join(' ')}" 
                 data-session-id="${escapeHtml(session.id)}"
                 title="${escapeHtml(session.display_name)}">
                <div class="session-item-title">${escapeHtml(session.display_name)}</div>
                <div class="session-item-meta">
                    <span class="session-item-date">${date}</span>
                    <span class="session-item-count">${messageCount} msgs</span>
                </div>
            </div>
        `;
    }).join('');
    
    elements.sessionList.innerHTML = sessionItems;
    
    // Add click handlers
    elements.sessionList.querySelectorAll('.session-item').forEach(item => {
        item.addEventListener('click', () => {
            const sessionId = item.dataset.sessionId;
            handleSessionClick(sessionId);
        });
    });
}

/**
 * Format session timestamp for display.
 */
function formatSessionDate(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    // Today: show time only
    if (diffDays === 0) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Yesterday
    if (diffDays === 1) {
        return 'Yesterday';
    }
    
    // Within a week: show day name
    if (diffDays < 7) {
        return date.toLocaleDateString([], { weekday: 'short' });
    }
    
    // Older: show date
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

/**
 * Handle click on a session in the sidebar.
 */
async function handleSessionClick(sessionId) {
    // Don't reload if already viewing this session
    if (sessionId === state.viewingSessionId) {
        return;
    }
    
    await loadSession(sessionId);
}

/**
 * Load a session from the API and display it.
 */
async function loadSession(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}`);
        
        if (!response.ok) {
            console.error('Failed to load session:', response.status);
            appendSystemMessage(`Failed to load session: ${response.statusText}`);
            return;
        }
        
        const session = await response.json();
        displaySession(session);
        
    } catch (error) {
        console.error('Error loading session:', error);
        appendSystemMessage(`Error loading session: ${error.message}`);
    }
}

/**
 * Display a loaded session.
 * If it's the active session (Pi is using it), keep it editable.
 * Otherwise, show it as read-only.
 */
function displaySession(session) {
    // Update viewing state
    state.viewingSessionId = session.id;
    state.chatStarted = true;
    
    // Clear chat area
    elements.chatMessages.innerHTML = '';
    
    // Hide welcome
    if (elements.welcomeContainer) {
        elements.welcomeContainer.style.display = 'none';
    }
    
    // Add read-only banner for past sessions
    if (isViewingPastSession()) {
        const banner = document.createElement('div');
        banner.className = 'read-only-banner';
        banner.innerHTML = `
            <span class="read-only-icon">📖</span>
            <span class="read-only-text">Viewing past session: ${escapeHtml(session.display_name)}</span>
        `;
        elements.chatMessages.appendChild(banner);
    }
    
    // Display all messages
    for (const msg of session.messages) {
        appendHistoryMessage(msg.role, msg.content, msg.timestamp);
    }
    
    // Update sidebar highlight and input state
    highlightSession(session.id);
    updateInputState();
    
    scrollToBottom();
}

/**
 * Append a message from history (past session).
 */
function appendHistoryMessage(role, content, timestamp) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // Format timestamp
    let timeStr = '';
    if (timestamp) {
        const date = new Date(timestamp);
        timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Determine display role
    let displayRole = 'System';
    if (role === 'user') {
        displayRole = 'You';
    } else if (role === 'assistant') {
        displayRole = 'Pi';
    } else if (role === 'toolResult') {
        displayRole = 'Tool';
    }
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-role">${displayRole}</span>
            ${timeStr ? `<span class="message-time">${timeStr}</span>` : ''}
        </div>
        <div class="message-content">${renderContent(content || '')}</div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
}

/**
 * Highlight a session in the sidebar.
 */
function highlightSession(sessionId) {
    if (!elements.sessionList) return;
    
    elements.sessionList.querySelectorAll('.session-item').forEach(item => {
        item.classList.toggle('active', item.dataset.sessionId === sessionId);
    });
}

/**
 * Schedule a session list refresh (debounced).
 */
function scheduleSessionRefresh() {
    if (state.sessionRefreshPending) return;
    
    state.sessionRefreshPending = true;
    
    // Delay refresh to allow Pi to finish saving
    setTimeout(async () => {
        state.sessionRefreshPending = false;
        await loadSessions();
    }, 1000);
}

/**
 * Request a new session from the server.
 */
function requestNewSession() {
    if (!state.connected || state.isProcessing) {
        return;
    }
    
    state.ws.send(JSON.stringify({ type: 'new_session' }));
}

/**
 * Handle new session created response.
 */
function handleNewSessionCreated(data) {
    console.log('New session created:', data.session_id);
    
    // Update session state - new session is both active and being viewed
    state.activeSessionId = data.session_id;
    state.viewingSessionId = null;  // Will be set when first message is sent
    
    // Reset UI to initial state
    resetChatUI();
    
    // Refresh session list
    scheduleSessionRefresh();
}

/**
 * Reset the chat UI to initial state.
 */
function resetChatUI() {
    // Reset state
    state.chatStarted = false;
    state.viewingSessionId = null;
    
    // Clear any streaming state
    finalizeStreamingMessage();
    
    // Clear chat messages and show welcome
    elements.chatMessages.innerHTML = `
        <div class="welcome-container" id="welcomeContainer">
            <div class="welcome-header">
                <h1>Welcome to Pi Portal</h1>
                <p>Your interface to the Pi coding agent. Ask questions, get help with code, or explore ideas.</p>
            </div>
            
            <div class="starter-prompts">
                <h2>Try asking...</h2>
                <div class="prompt-grid" id="promptGrid">
                    <!-- Starter prompts loaded dynamically -->
                </div>
            </div>
        </div>
    `;
    
    // Update element references
    elements.welcomeContainer = document.getElementById('welcomeContainer');
    elements.promptGrid = document.getElementById('promptGrid');
    
    // Reload starter prompts and update UI
    loadStarterPrompts();
    highlightSession(null);
    updateInputState();
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
    
    // New session button
    elements.newSessionBtn.addEventListener('click', () => {
        requestNewSession();
    });
}

// ============================================
// Initialization
// ============================================

function init() {
    console.log('Pi Portal initializing...');
    
    setupEventListeners();
    loadStarterPrompts();
    loadSessions();
    connect();
    
    // Initial state
    updateInputState();
}

// Start the application
document.addEventListener('DOMContentLoaded', init);
