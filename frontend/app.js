/**
 * Pi Portal - Client-side JavaScript
 * 
 * Handles UI interactions, WebSocket communication, and message rendering.
 */

// ============================================
// DOM Elements
// ============================================
const elements = {
    chatMessages: document.getElementById('chatMessages'),
    chatInput: document.getElementById('chatInput'),
    sendBtn: document.getElementById('sendBtn'),
    newSessionBtn: document.getElementById('newSessionBtn'),
    sessionList: document.getElementById('sessionList'),
    connectionStatus: document.getElementById('connectionStatus'),
    welcomeContainer: document.getElementById('welcomeContainer'),
    promptGrid: document.getElementById('promptGrid'),
};

// ============================================
// State
// ============================================
const state = {
    connected: false,
    chatStarted: false,
    isStreaming: false,
};

// ============================================
// UI Functions
// ============================================

/**
 * Update connection status indicator
 */
function updateConnectionStatus(status) {
    const statusDot = elements.connectionStatus.querySelector('.status-dot');
    const statusText = elements.connectionStatus.querySelector('.status-text');
    
    statusDot.className = 'status-dot';
    
    switch (status) {
        case 'connected':
            statusDot.classList.add('connected');
            statusText.textContent = 'Connected';
            state.connected = true;
            break;
        case 'connecting':
            statusDot.classList.add('connecting');
            statusText.textContent = 'Connecting...';
            state.connected = false;
            break;
        case 'disconnected':
        default:
            statusDot.classList.add('disconnected');
            statusText.textContent = 'Disconnected';
            state.connected = false;
            break;
    }
}

/**
 * Hide welcome screen and show chat
 */
function hideWelcome() {
    if (elements.welcomeContainer) {
        elements.welcomeContainer.style.display = 'none';
        state.chatStarted = true;
    }
}

/**
 * Show welcome screen
 */
function showWelcome() {
    if (elements.welcomeContainer) {
        elements.welcomeContainer.style.display = 'block';
        state.chatStarted = false;
    }
}

/**
 * Create a message element
 */
function createMessageElement(role, content) {
    const message = document.createElement('div');
    message.className = `message ${role}`;
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    message.innerHTML = `
        <div class="message-header">
            <span class="message-role">${role === 'user' ? 'You' : 'Pi'}</span>
            <span class="message-time">${timeStr}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    return message;
}

/**
 * Add a message to the chat
 */
function addMessage(role, content) {
    hideWelcome();
    
    const message = createMessageElement(role, content);
    elements.chatMessages.appendChild(message);
    scrollToBottom();
    
    return message;
}

/**
 * Create typing indicator
 */
function createTypingIndicator() {
    const container = document.createElement('div');
    container.className = 'message assistant';
    container.id = 'typingIndicator';
    
    container.innerHTML = `
        <div class="message-header">
            <span class="message-role">Pi</span>
        </div>
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    return container;
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    removeTypingIndicator();
    const indicator = createTypingIndicator();
    elements.chatMessages.appendChild(indicator);
    scrollToBottom();
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Update send button state
 */
function updateSendButton() {
    const hasText = elements.chatInput.value.trim().length > 0;
    elements.sendBtn.disabled = !hasText || state.isStreaming;
}

/**
 * Auto-resize textarea
 */
function autoResizeTextarea() {
    const textarea = elements.chatInput;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

// ============================================
// Message Handling
// ============================================

/**
 * Send a message
 */
function sendMessage(text) {
    if (!text.trim() || state.isStreaming) return;
    
    // Add user message to chat
    addMessage('user', text);
    
    // Clear input
    elements.chatInput.value = '';
    autoResizeTextarea();
    updateSendButton();
    
    // Show typing indicator
    showTypingIndicator();
    state.isStreaming = true;
    
    // TODO: Send via WebSocket (M1.2)
    // For now, simulate a response after a delay
    setTimeout(() => {
        removeTypingIndicator();
        addMessage('assistant', 'WebSocket connection not yet implemented. This is a placeholder response.');
        state.isStreaming = false;
        updateSendButton();
    }, 1500);
}

// ============================================
// Event Listeners
// ============================================

// Send button click
elements.sendBtn.addEventListener('click', () => {
    sendMessage(elements.chatInput.value);
});

// Input field events
elements.chatInput.addEventListener('input', () => {
    updateSendButton();
    autoResizeTextarea();
});

elements.chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(elements.chatInput.value);
    }
});

/**
 * Load and render starter prompts from config
 */
async function loadStarterPrompts() {
    try {
        const response = await fetch('/api/config/starter-prompts');
        if (!response.ok) throw new Error('Failed to load prompts');
        
        const data = await response.json();
        renderStarterPrompts(data.prompts || []);
    } catch (error) {
        console.error('Error loading starter prompts:', error);
        // Render default prompt on error
        renderStarterPrompts([
            { icon: '💡', text: 'What can you help me with?' }
        ]);
    }
}

/**
 * Render starter prompts to the grid
 */
function renderStarterPrompts(prompts) {
    if (!elements.promptGrid) return;
    
    elements.promptGrid.innerHTML = prompts.map(prompt => `
        <button class="starter-prompt" data-prompt="${escapeHtml(prompt.text)}">
            <span class="prompt-icon">${prompt.icon || '💬'}</span>
            <span class="prompt-text">${escapeHtml(prompt.text)}</span>
        </button>
    `).join('');
    
    // Attach click handlers
    attachStarterPromptHandlers();
}

/**
 * Attach click handlers to starter prompts
 */
function attachStarterPromptHandlers() {
    document.querySelectorAll('.starter-prompt').forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.dataset.prompt;
            if (prompt) {
                elements.chatInput.value = prompt;
                updateSendButton();
                elements.chatInput.focus();
            }
        });
    });
}

// New session button
elements.newSessionBtn.addEventListener('click', () => {
    // Clear chat messages (except welcome)
    const messages = elements.chatMessages.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());
    
    // Show welcome again
    showWelcome();
    
    // Clear input
    elements.chatInput.value = '';
    updateSendButton();
    
    // TODO: Create new session via API (M2.6)
});

// ============================================
// Initialization
// ============================================

async function init() {
    console.log('Pi Portal initialized');
    
    // Set initial states
    updateConnectionStatus('disconnected');
    updateSendButton();
    
    // Load starter prompts from config
    await loadStarterPrompts();
    
    // Focus input
    elements.chatInput.focus();
    
    // TODO: Connect WebSocket (M1.2)
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
