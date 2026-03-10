/**
 * Error Handler Module
 * Centralized error handling and user notifications
 */

class ErrorHandler {
    constructor() {
        this.errorContainer = null;
        this.init();
    }

    init() {
        // Create error notification container
        this.errorContainer = document.createElement('div');
        this.errorContainer.id = 'errorNotifications';
        this.errorContainer.className = 'error-notifications';
        document.body.appendChild(this.errorContainer);
    }

    /**
     * Show an error notification to the user
     * @param {string} message - Error message
     * @param {string} type - Error type: 'error', 'warning', 'info'
     * @param {number} duration - Duration in ms (0 = persistent)
     */
    showNotification(message, type = 'error', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `error-notification ${type}`;
        
        const icon = this.getIcon(type);
        notification.innerHTML = `
            <div class="notification-icon">${icon}</div>
            <div class="notification-content">
                <div class="notification-message">${this.escapeHtml(message)}</div>
            </div>
            <button class="notification-close" aria-label="Close">×</button>
        `;

        // Add to container
        this.errorContainer.appendChild(notification);

        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.hideNotification(notification);
        });

        // Auto-hide
        if (duration > 0) {
            setTimeout(() => {
                this.hideNotification(notification);
            }, duration);
        }

        return notification;
    }

    hideNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    getIcon(type) {
        const icons = {
            error: '⚠️',
            warning: '⚠️',
            info: 'ℹ️',
            success: '✓'
        };
        return icons[type] || icons.info;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Handle WebSocket errors
     */
    handleWebSocketError(error) {
        console.error('WebSocket error:', error);
        this.showNotification(
            'Connection lost. Attempting to reconnect...',
            'warning',
            0
        );
    }

    /**
     * Handle reconnection success
     */
    handleReconnectSuccess() {
        // Clear any connection error notifications
        const notifications = this.errorContainer.querySelectorAll('.error-notification.warning');
        notifications.forEach(n => this.hideNotification(n));
        
        this.showNotification(
            'Reconnected successfully',
            'success',
            3000
        );
    }

    /**
     * Handle Pi process errors
     */
    handlePiError(message) {
        this.showNotification(
            `Pi Error: ${message}`,
            'error',
            8000
        );
    }

    /**
     * Handle session loading errors
     */
    handleSessionError(sessionId) {
        this.showNotification(
            `Failed to load session. The session file may be corrupted.`,
            'error',
            6000
        );
    }

    /**
     * Handle feedback submission errors
     */
    handleFeedbackError() {
        this.showNotification(
            'Failed to submit feedback. Please try again.',
            'error',
            5000
        );
    }

    /**
     * Handle generic API errors
     */
    handleApiError(endpoint, status) {
        this.showNotification(
            `Server error (${status}). Please try again or refresh the page.`,
            'error',
            6000
        );
    }
}

// Export singleton instance
const errorHandler = new ErrorHandler();
