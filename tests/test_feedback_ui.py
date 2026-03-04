"""
Tests for M3.2 - Message Feedback UI components.

These tests verify that the frontend files contain the necessary
feedback UI elements (buttons, styles, handlers).
"""

import pytest


class TestFeedbackButtonsInJS:
    """Test that app.js contains feedback button functionality."""

    @pytest.fixture
    def app_js_content(self):
        with open("frontend/app.js", "r") as f:
            return f.read()

    def test_has_create_feedback_buttons_html(self, app_js_content):
        """Verify createFeedbackButtonsHtml function exists."""
        assert "function createFeedbackButtonsHtml" in app_js_content

    def test_has_add_feedback_buttons(self, app_js_content):
        """Verify addFeedbackButtons function exists."""
        assert "function addFeedbackButtons" in app_js_content

    def test_has_setup_feedback_handlers(self, app_js_content):
        """Verify setupFeedbackHandlers function exists."""
        assert "function setupFeedbackHandlers" in app_js_content

    def test_feedback_buttons_have_thumbs_up(self, app_js_content):
        """Verify thumbs up button is created."""
        assert "thumbs-up" in app_js_content

    def test_feedback_buttons_have_thumbs_down(self, app_js_content):
        """Verify thumbs down button is created."""
        assert "thumbs-down" in app_js_content

    def test_feedback_tracks_timestamp(self, app_js_content):
        """Verify timestamp is stored as data attribute."""
        assert "data-timestamp" in app_js_content

    def test_feedback_buttons_toggle_active_class(self, app_js_content):
        """Verify buttons toggle active class on click."""
        assert "classList.toggle('active'" in app_js_content
        assert "classList.remove('active')" in app_js_content

    def test_finalize_streaming_adds_feedback(self, app_js_content):
        """Verify finalizeStreamingMessage adds feedback buttons."""
        assert "addFeedbackButtons(state.currentMessageElement" in app_js_content

    def test_append_message_adds_feedback_for_assistant(self, app_js_content):
        """Verify appendMessage adds feedback for assistant messages."""
        # Check that assistant messages get feedback buttons
        assert "if (role === 'assistant')" in app_js_content
        assert "addFeedbackButtons(messageDiv" in app_js_content

    def test_append_history_message_adds_feedback(self, app_js_content):
        """Verify appendHistoryMessage adds feedback for assistant."""
        # The function should handle feedback parameter
        assert (
            "function appendHistoryMessage(role, content, timestamp, feedback"
            in app_js_content
        )


class TestFeedbackStylesInCSS:
    """Test that styles.css contains feedback button styles."""

    @pytest.fixture
    def styles_css_content(self):
        with open("frontend/styles.css", "r") as f:
            return f.read()

    def test_has_message_feedback_class(self, styles_css_content):
        """Verify .message-feedback styles exist."""
        assert ".message-feedback" in styles_css_content

    def test_has_feedback_btn_class(self, styles_css_content):
        """Verify .feedback-btn styles exist."""
        assert ".feedback-btn" in styles_css_content

    def test_has_thumbs_up_styles(self, styles_css_content):
        """Verify thumbs-up button styles exist."""
        assert ".feedback-btn.thumbs-up" in styles_css_content

    def test_has_thumbs_down_styles(self, styles_css_content):
        """Verify thumbs-down button styles exist."""
        assert ".feedback-btn.thumbs-down" in styles_css_content

    def test_has_active_state_styles(self, styles_css_content):
        """Verify active state styles exist."""
        assert ".thumbs-up.active" in styles_css_content
        assert ".thumbs-down.active" in styles_css_content

    def test_thumbs_up_uses_success_color(self, styles_css_content):
        """Verify thumbs up uses success (green) color."""
        assert "accent-success" in styles_css_content

    def test_thumbs_down_uses_error_color(self, styles_css_content):
        """Verify thumbs down uses error (red) color."""
        assert "accent-error" in styles_css_content


class TestFeedbackModalInHTML:
    """Test that index.html contains feedback modal markup."""

    @pytest.fixture
    def index_html_content(self):
        with open("frontend/index.html", "r") as f:
            return f.read()

    def test_has_feedback_modal(self, index_html_content):
        """Verify feedback modal element exists."""
        assert 'id="feedbackModal"' in index_html_content

    def test_has_feedback_comment_textarea(self, index_html_content):
        """Verify comment textarea exists."""
        assert 'id="feedbackComment"' in index_html_content

    def test_has_modal_close_button(self, index_html_content):
        """Verify close button exists."""
        assert 'id="feedbackModalClose"' in index_html_content

    def test_has_modal_cancel_button(self, index_html_content):
        """Verify cancel button exists."""
        assert 'id="feedbackModalCancel"' in index_html_content

    def test_has_modal_submit_button(self, index_html_content):
        """Verify submit button exists."""
        assert 'id="feedbackModalSubmit"' in index_html_content

    def test_modal_hidden_by_default(self, index_html_content):
        """Verify modal is hidden by default."""
        assert 'id="feedbackModal" hidden' in index_html_content


class TestFeedbackModalInJS:
    """Test that app.js contains feedback modal functionality."""

    @pytest.fixture
    def app_js_content(self):
        with open("frontend/app.js", "r") as f:
            return f.read()

    def test_has_open_feedback_modal(self, app_js_content):
        """Verify openFeedbackModal function exists."""
        assert "function openFeedbackModal" in app_js_content

    def test_has_close_feedback_modal(self, app_js_content):
        """Verify closeFeedbackModal function exists."""
        assert "function closeFeedbackModal" in app_js_content

    def test_has_submit_feedback_modal(self, app_js_content):
        """Verify submitFeedbackModal function exists."""
        assert "function submitFeedbackModal" in app_js_content

    def test_has_setup_feedback_modal_listeners(self, app_js_content):
        """Verify setupFeedbackModalListeners function exists."""
        assert "function setupFeedbackModalListeners" in app_js_content

    def test_modal_context_in_state(self, app_js_content):
        """Verify feedbackModalContext is in state."""
        assert "feedbackModalContext" in app_js_content

    def test_escape_key_closes_modal(self, app_js_content):
        """Verify Escape key handler exists."""
        assert "e.key === 'Escape'" in app_js_content

    def test_ctrl_enter_submits(self, app_js_content):
        """Verify Ctrl+Enter submit handler exists."""
        assert "e.ctrlKey || e.metaKey" in app_js_content


class TestFeedbackModalInCSS:
    """Test that styles.css contains feedback modal styles."""

    @pytest.fixture
    def styles_css_content(self):
        with open("frontend/styles.css", "r") as f:
            return f.read()

    def test_has_modal_overlay_class(self, styles_css_content):
        """Verify .modal-overlay styles exist."""
        assert ".modal-overlay" in styles_css_content

    def test_has_modal_class(self, styles_css_content):
        """Verify .modal styles exist."""
        assert ".modal {" in styles_css_content

    def test_has_modal_header_class(self, styles_css_content):
        """Verify .modal-header styles exist."""
        assert ".modal-header" in styles_css_content

    def test_has_modal_body_class(self, styles_css_content):
        """Verify .modal-body styles exist."""
        assert ".modal-body" in styles_css_content

    def test_has_modal_footer_class(self, styles_css_content):
        """Verify .modal-footer styles exist."""
        assert ".modal-footer" in styles_css_content

    def test_has_modal_btn_classes(self, styles_css_content):
        """Verify modal button styles exist."""
        assert ".modal-btn-primary" in styles_css_content
        assert ".modal-btn-secondary" in styles_css_content

    def test_modal_has_animation(self, styles_css_content):
        """Verify modal has entrance animation."""
        assert "@keyframes modalIn" in styles_css_content


class TestFeedbackButtonsServedViaAPI:
    """Test that feedback UI is accessible via the web server."""

    @pytest.fixture
    def client(self):
        from httpx import ASGITransport, AsyncClient
        from backend.main import app

        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    async def test_app_js_contains_feedback_functions(self, client):
        """Verify app.js served via API contains feedback code."""
        response = await client.get("/app.js")
        assert response.status_code == 200
        content = response.text
        assert "createFeedbackButtonsHtml" in content
        assert "addFeedbackButtons" in content

    @pytest.mark.asyncio
    async def test_styles_css_contains_feedback_styles(self, client):
        """Verify styles.css served via API contains feedback styles."""
        response = await client.get("/styles.css")
        assert response.status_code == 200
        content = response.text
        assert ".message-feedback" in content
        assert ".feedback-btn" in content
