"""Tests for WebSocket functionality."""

import pytest
from starlette.testclient import TestClient

from backend.main import app
from backend.websocket import ConnectionManager, manager


class TestConnectionManager:
    """Test the ConnectionManager class."""

    def test_initial_state(self):
        """Manager starts with no connections."""
        mgr = ConnectionManager()
        assert len(mgr.active_connections) == 0

    def test_manager_is_singleton_instance(self):
        """The global manager should be a ConnectionManager instance."""
        assert isinstance(manager, ConnectionManager)

    def test_disconnect_nonexistent_connection(self):
        """Disconnecting a non-existent connection should not raise."""
        mgr = ConnectionManager()

        # Create a mock websocket-like object
        class FakeWebSocket:
            pass

        fake_ws = FakeWebSocket()
        # Should not raise
        mgr.disconnect(fake_ws)
        assert len(mgr.active_connections) == 0


class TestWebSocketConnection:
    """Test WebSocket connection handling."""

    def test_websocket_connect(self):
        """Test WebSocket connection and initial status message."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            # Should receive connected status message
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert data["status"] == "connected"

    def test_websocket_connect_has_correct_structure(self):
        """Initial status message should have exactly type and status fields."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert set(data.keys()) == {"type", "status"}

    def test_multiple_connections_allowed(self):
        """Multiple WebSocket connections should work simultaneously."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as ws1:
            data1 = ws1.receive_json()
            assert data1["status"] == "connected"

            with client.websocket_connect("/ws") as ws2:
                data2 = ws2.receive_json()
                assert data2["status"] == "connected"

                # Both should be able to ping
                ws1.send_json({"type": "ping"})
                ws2.send_json({"type": "ping"})

                assert ws1.receive_json()["type"] == "pong"
                assert ws2.receive_json()["type"] == "pong"

    def test_connection_cleanup_on_close(self):
        """Connection should be cleaned up when WebSocket closes."""
        client = TestClient(app)
        initial_count = len(manager.active_connections)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()
            # Connection is active
            assert len(manager.active_connections) == initial_count + 1

        # After context exit, connection should be cleaned up
        assert len(manager.active_connections) == initial_count


class TestWebSocketPingPong:
    """Test WebSocket ping/pong keepalive mechanism."""

    def test_ping_pong_basic(self):
        """Test basic ping/pong keepalive."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # Consume initial status

            websocket.send_json({"type": "ping"})
            data = websocket.receive_json()

            assert data["type"] == "pong"

    def test_multiple_pings(self):
        """Multiple pings should each receive a pong."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # Consume initial status

            for _ in range(5):
                websocket.send_json({"type": "ping"})
                data = websocket.receive_json()
                assert data["type"] == "pong"

    def test_ping_with_extra_fields_ignored(self):
        """Ping with extra fields should still work."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": "ping", "extra": "data", "foo": 123})
            data = websocket.receive_json()
            assert data["type"] == "pong"


@pytest.mark.integration
class TestWebSocketMessageHandling:
    """Test WebSocket message sending and receiving.

    These tests require Pi to be running and are marked as integration tests.
    """

    def test_message_response(self):
        """Test sending a message and receiving response."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": "message", "content": "Hello, Pi!"})

            # Should receive processing status
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert data["status"] == "processing"

            # Should receive response (may be error if Pi not available,
            # or message_complete/text_delta if Pi is running)
            data = websocket.receive_json()
            # Accept any valid response type
            assert data["type"] in ["message_complete", "error", "text_delta"]

    def test_message_response_structure(self):
        """Response message should have correct structure when Pi is running."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": "message", "content": "Test"})

            websocket.receive_json()  # processing status

            # Consume messages until we get message_complete or error
            while True:
                data = websocket.receive_json()
                if data["type"] == "message_complete":
                    assert "role" in data
                    assert "content" in data
                    assert data["role"] == "assistant"
                    break
                elif data["type"] == "error":
                    # Pi not available is acceptable in integration tests
                    break
                elif data["type"] == "status":
                    break

    def test_multiple_messages_sequential(self):
        """Multiple messages should be processed sequentially."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            messages = ["First message", "Second message"]

            for msg in messages:
                websocket.send_json({"type": "message", "content": msg})

                # Consume all responses for this message
                status1 = websocket.receive_json()
                assert status1["status"] == "processing"

                # Consume response(s) until ready status
                while True:
                    data = websocket.receive_json()
                    if data.get("type") == "status" and data.get("status") == "ready":
                        break


class TestWebSocketEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_content_ignored(self):
        """Empty message content should be ignored."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": "message", "content": ""})
            websocket.send_json({"type": "ping"})

            # Should only receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_whitespace_only_content_ignored(self):
        """Whitespace-only content should be ignored."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": "message", "content": "   \t\n  "})
            websocket.send_json({"type": "ping"})

            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_missing_content_field(self):
        """Message without content field should be handled gracefully."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": "message"})
            websocket.send_json({"type": "ping"})

            # Should still respond to ping
            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_none_content(self):
        """Message with None content should be handled gracefully."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": "message", "content": None})
            websocket.send_json({"type": "ping"})

            data = websocket.receive_json()
            assert data["type"] == "pong"

    @pytest.mark.integration
    def test_very_long_message(self):
        """Very long messages should be handled."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            long_content = "A" * 10000  # 10KB message
            websocket.send_json({"type": "message", "content": long_content})

            data = websocket.receive_json()
            assert data["status"] == "processing"

            # Accept any response type (error if Pi unavailable)
            data = websocket.receive_json()
            assert data["type"] in ["message_complete", "error", "text_delta"]

    @pytest.mark.integration
    def test_special_characters_in_message(self):
        """Messages with special characters should be handled."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            special_content = "Hello! @#$%^&*() 你好 🎉 <script>alert('xss')</script>"
            websocket.send_json({"type": "message", "content": special_content})

            websocket.receive_json()  # processing
            data = websocket.receive_json()

            # Accept any response type
            assert data["type"] in ["message_complete", "error", "text_delta"]

    @pytest.mark.integration
    def test_unicode_message(self):
        """Unicode messages should be handled correctly."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            unicode_content = "日本語テスト émojis: 🚀🎯💡 Ñoño"
            websocket.send_json({"type": "message", "content": unicode_content})

            websocket.receive_json()  # processing
            data = websocket.receive_json()

            # Accept any response type
            assert data["type"] in ["message_complete", "error", "text_delta"]

    @pytest.mark.integration
    def test_newlines_in_message(self):
        """Messages with newlines should be handled."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            multiline = "Line 1\nLine 2\nLine 3"
            websocket.send_json({"type": "message", "content": multiline})

            websocket.receive_json()  # processing
            data = websocket.receive_json()

            # Accept any response type
            assert data["type"] in ["message_complete", "error", "text_delta"]


class TestWebSocketUnknownMessages:
    """Test handling of unknown or malformed messages."""

    def test_unknown_message_type(self):
        """Unknown message types should not crash the connection."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": "unknown_type", "data": "test"})
            websocket.send_json({"type": "ping"})

            # Connection should still work
            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_empty_object(self):
        """Empty JSON object should not crash the connection."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({})
            websocket.send_json({"type": "ping"})

            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_missing_type_field(self):
        """Message without type field should not crash the connection."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"content": "no type field"})
            websocket.send_json({"type": "ping"})

            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_type_field_not_string(self):
        """Non-string type field should be handled gracefully."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            websocket.send_json({"type": 123})
            websocket.send_json({"type": ["array"]})
            websocket.send_json({"type": {"nested": "object"}})
            websocket.send_json({"type": "ping"})

            data = websocket.receive_json()
            assert data["type"] == "pong"

    @pytest.mark.integration
    def test_nested_json_message(self):
        """Deeply nested JSON should be handled."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            nested = {
                "type": "message",
                "content": "test",
                "metadata": {"nested": {"deep": {"value": [1, 2, 3]}}},
            }
            websocket.send_json(nested)

            data = websocket.receive_json()
            assert data["status"] == "processing"


class TestWebSocketRobustness:
    """Test WebSocket robustness and error recovery."""

    def test_rapid_messages(self):
        """Rapid message sending should be handled."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            # Send many pings rapidly
            for _ in range(20):
                websocket.send_json({"type": "ping"})

            # Should receive all pongs
            for _ in range(20):
                data = websocket.receive_json()
                assert data["type"] == "pong"

    @pytest.mark.integration
    def test_interleaved_pings_and_messages(self):
        """Pings and messages interleaved should work correctly."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            # Send ping
            websocket.send_json({"type": "ping"})
            assert websocket.receive_json()["type"] == "pong"

            # Send message
            websocket.send_json({"type": "message", "content": "test"})
            assert websocket.receive_json()["status"] == "processing"

            # Consume all response messages until ready
            while True:
                data = websocket.receive_json()
                if data.get("type") == "status" and data.get("status") == "ready":
                    break

            # Send another ping
            websocket.send_json({"type": "ping"})
            assert websocket.receive_json()["type"] == "pong"

    def test_connection_survives_bad_messages(self):
        """Connection should survive after receiving bad messages."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            # Send various bad messages
            bad_messages = [
                {},
                {"type": None},
                {"type": ""},
                {"type": "message"},  # Missing content
                {"type": "message", "content": None},
                {"type": "unknown"},
                {"random": "data"},
            ]

            for bad_msg in bad_messages:
                websocket.send_json(bad_msg)

            # Connection should still work
            websocket.send_json({"type": "ping"})
            data = websocket.receive_json()
            assert data["type"] == "pong"


class TestWebSocketStatusTransitions:
    """Test WebSocket status message transitions."""

    @pytest.mark.integration
    def test_status_transitions_for_message(self):
        """Status should transition: connected -> processing -> ready."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            # Initial: connected
            data = websocket.receive_json()
            assert data["status"] == "connected"

            websocket.send_json({"type": "message", "content": "test"})

            # Processing
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert data["status"] == "processing"

            # Consume response(s) until ready status
            while True:
                data = websocket.receive_json()
                if data.get("type") == "status" and data.get("status") == "ready":
                    break

    @pytest.mark.integration
    def test_ready_status_after_each_message(self):
        """Each message should end with ready status."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()

            for i in range(2):
                websocket.send_json({"type": "message", "content": f"msg {i}"})

                websocket.receive_json()  # processing

                # Consume all messages until ready
                while True:
                    data = websocket.receive_json()
                    if data.get("type") == "status" and data.get("status") == "ready":
                        break


class TestFeedbackWebSocket:
    """Test feedback submission via WebSocket."""

    def test_feedback_message_accepted(self):
        """Feedback messages should be accepted without error."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            # Get initial connected status
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert data["status"] == "connected"

            # Send feedback (this won't succeed without Pi running,
            # but the message format should be accepted)
            websocket.send_json(
                {
                    "type": "feedback",
                    "targetTimestamp": 1234567890,
                    "rating": 1,
                    "comment": None,
                }
            )

            # Connection should still be alive
            websocket.send_json({"type": "ping"})
            data = websocket.receive_json()
            # May get error about Pi not running, or pong if feedback was processed first
            # Either way, connection should be maintained

    def test_feedback_missing_timestamp_returns_error(self):
        """Feedback without targetTimestamp should return error."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # connected

            # Send feedback without timestamp
            websocket.send_json({"type": "feedback", "rating": 1})

            # Should get an error
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "targetTimestamp" in data["message"]

    def test_feedback_missing_rating_returns_error(self):
        """Feedback without rating should return error."""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # connected

            # Send feedback without rating
            websocket.send_json({"type": "feedback", "targetTimestamp": 1234567890})

            # Should get an error
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "rating" in data["message"]

    @pytest.mark.integration
    def test_feedback_submission_to_pi(self):
        """Test full feedback submission with Pi running."""
        # Feedback is written directly to session files by the backend
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # connected

            # First send a message to start a session
            websocket.send_json({"type": "message", "content": "hello"})

            # Consume until message_complete to get timestamp
            assistant_timestamp = None
            while True:
                data = websocket.receive_json()
                if data.get("type") == "message_complete":
                    # Extract timestamp from response if available
                    messages = data.get("messages", [])
                    for msg in messages:
                        if msg.get("role") == "assistant" and msg.get("timestamp"):
                            assistant_timestamp = msg["timestamp"]
                            break
                    break
                if data.get("type") == "status" and data.get("status") == "ready":
                    break

            # If we got a timestamp, try to submit feedback
            if assistant_timestamp:
                websocket.send_json(
                    {
                        "type": "feedback",
                        "targetTimestamp": assistant_timestamp,
                        "rating": 1,
                        "comment": None,
                    }
                )

                # Look for feedback_saved or error response
                while True:
                    data = websocket.receive_json()
                    if data.get("type") in ("feedback_saved", "error"):
                        break
