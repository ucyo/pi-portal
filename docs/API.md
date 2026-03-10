# Pi Portal API Documentation

Complete API reference for Pi Portal's REST and WebSocket endpoints.

---

## Table of Contents

- [REST API](#rest-api)
  - [Health Check](#health-check)
  - [Sessions](#sessions)
  - [Configuration](#configuration)
- [WebSocket API](#websocket-api)
  - [Connection](#connection)
  - [Client Messages](#client-messages)
  - [Server Messages](#server-messages)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

---

## REST API

Base URL: `http://localhost:8000`

All REST endpoints return JSON responses.

### Health Check

#### `GET /health`

Check if the server is running.

**Response:** `200 OK`
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### Sessions

#### `GET /api/sessions`

List all available sessions with metadata.

**Response:** `200 OK`
```json
{
  "sessions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "display_name": "Debugging Python error",
      "created_at": "2024-12-03T14:00:00.000Z",
      "updated_at": "2024-12-03T14:30:00.000Z",
      "message_count": 10,
      "is_active": true
    },
    {
      "id": "650e8400-e29b-41d4-a716-446655440001",
      "display_name": "Refactoring code",
      "created_at": "2024-12-02T10:00:00.000Z",
      "updated_at": "2024-12-02T11:00:00.000Z",
      "message_count": 15,
      "is_active": false
    }
  ]
}
```

**Fields:**
- `id` (string): Unique session identifier (UUID)
- `display_name` (string): Session title (first user message or custom name)
- `created_at` (string): ISO 8601 timestamp of session creation
- `updated_at` (string): ISO 8601 timestamp of last message
- `message_count` (integer): Number of messages in session
- `is_active` (boolean): True if this is the current active session

**Example:**
```bash
curl http://localhost:8000/api/sessions
```

---

#### `GET /api/sessions/{id}`

Get full session details including messages and feedback.

**Parameters:**
- `id` (path, required): Session UUID

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "display_name": "Debugging Python error",
  "created_at": "2024-12-03T14:00:00.000Z",
  "updated_at": "2024-12-03T14:30:00.000Z",
  "message_count": 2,
  "messages": [
    {
      "role": "user",
      "content": "Help me debug this Python error",
      "message_timestamp": 1733234567890,
      "content_blocks": null
    },
    {
      "role": "assistant",
      "content": "I'll help you debug that error...",
      "message_timestamp": 1733234568123,
      "content_blocks": [
        {
          "type": "text",
          "text": "I'll help you debug that error..."
        },
        {
          "type": "thinking",
          "thinking": "The user needs help with a Python error..."
        },
        {
          "type": "tool_use",
          "id": "toolu_123",
          "name": "Read",
          "input": {"path": "script.py"}
        }
      ]
    }
  ],
  "feedback": [
    {
      "target_timestamp": 1733234568123,
      "rating": 1,
      "comment": null,
      "timestamp": 1733234600000
    }
  ]
}
```

**Message Fields:**
- `role` (string): Message role - `"user"`, `"assistant"`, or `"toolResult"`
- `content` (string): Plain text content of the message
- `message_timestamp` (integer): Unix timestamp in milliseconds
- `content_blocks` (array|null): Structured content blocks (assistant only)

**Content Block Types:**
- `text`: Plain text response
- `thinking`: Pi's internal reasoning
- `tool_use`: Tool execution request

**Feedback Fields:**
- `target_timestamp` (integer): Timestamp of the message being rated
- `rating` (integer): Rating value (-1 = negative, 0 = neutral, 1 = positive)
- `comment` (string|null): Optional feedback comment (for negative ratings)
- `timestamp` (integer): Unix timestamp when feedback was submitted

**Error Responses:**

`404 Not Found` - Session doesn't exist
```json
{
  "detail": "Session not found: 550e8400-e29b-41d4-a716-446655440000"
}
```

`400 Bad Request` - Invalid session ID format
```json
{
  "detail": "Invalid session ID format"
}
```

`500 Internal Server Error` - Failed to parse session file
```json
{
  "detail": "Failed to parse session file"
}
```

**Example:**
```bash
curl http://localhost:8000/api/sessions/550e8400-e29b-41d4-a716-446655440000
```

---

### Configuration

#### `GET /api/config/starter-prompts`

Get configured starter prompts for the welcome screen.

**Response:** `200 OK`
```json
{
  "prompts": [
    {
      "icon": "🐛",
      "text": "Help me debug this error"
    },
    {
      "icon": "📝",
      "text": "Explain this code snippet"
    },
    {
      "icon": "🚀",
      "text": "Optimize this function"
    },
    {
      "icon": "🧪",
      "text": "Write tests for my code"
    }
  ]
}
```

**Fields:**
- `icon` (string): Emoji or icon to display
- `text` (string): Prompt text

**Configuration:**
Edit `config/starter_prompts.json` to customize.

**Example:**
```bash
curl http://localhost:8000/api/config/starter-prompts
```

---

## WebSocket API

WebSocket URL: `ws://localhost:8000/ws`

All messages are JSON objects with a `type` field.

### Connection

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

**Send Message:**
```javascript
ws.send(JSON.stringify({
  type: 'message',
  content: 'Hello Pi'
}));
```

---

### Client Messages

Messages sent from client (browser) to server.

#### `ping`

Keep-alive ping message.

**Format:**
```json
{
  "type": "ping"
}
```

**Response:** `pong` message

**Example:**
```javascript
ws.send(JSON.stringify({ type: 'ping' }));
```

---

#### `message`

Send a chat message to Pi.

**Format:**
```json
{
  "type": "message",
  "content": "Hello Pi, can you help me?"
}
```

**Fields:**
- `content` (string, required): Message text

**Response:** Series of server messages (`text_delta`, `thinking_delta`, `tool_start`, etc.)

**Example:**
```javascript
ws.send(JSON.stringify({
  type: 'message',
  content: 'Help me debug this error'
}));
```

---

#### `new_session`

Create a new Pi session.

**Format:**
```json
{
  "type": "new_session"
}
```

**Response:** Session resets, new session ID assigned

**Example:**
```javascript
ws.send(JSON.stringify({ type: 'new_session' }));
```

---

#### `feedback`

Submit feedback for a message.

**Format:**
```json
{
  "type": "feedback",
  "timestamp": 1733234568123,
  "rating": 1,
  "comment": null,
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fields:**
- `timestamp` (integer, required): Message timestamp to rate
- `rating` (integer, required): -1 (negative), 0 (neutral), or 1 (positive)
- `comment` (string|null, optional): Feedback comment (for negative ratings)
- `session_id` (string, optional): Session ID (if rating past session)

**Response:** `feedback_saved` message

**Example:**
```javascript
// Positive feedback
ws.send(JSON.stringify({
  type: 'feedback',
  timestamp: 1733234568123,
  rating: 1,
  comment: null
}));

// Negative feedback with comment
ws.send(JSON.stringify({
  type: 'feedback',
  timestamp: 1733234568123,
  rating: -1,
  comment: 'The response was inaccurate'
}));
```

---

### Server Messages

Messages sent from server to client (browser).

#### `status`

Connection status update.

**Format:**
```json
{
  "type": "status",
  "status": "connected"
}
```

**Status Values:**
- `"connected"`: WebSocket connected
- `"processing"`: Pi is processing a message
- `"ready"`: Pi is ready for new messages

---

#### `pong`

Response to ping message.

**Format:**
```json
{
  "type": "pong"
}
```

---

#### `message`

Complete message (used for user messages echoed back).

**Format:**
```json
{
  "type": "message",
  "role": "user",
  "content": "Hello Pi",
  "timestamp": 1733234567890
}
```

---

#### `text_delta`

Streaming text chunk from Pi's response.

**Format:**
```json
{
  "type": "text_delta",
  "delta": "Hello! I can help you with that."
}
```

**Fields:**
- `delta` (string): Text chunk to append to current message

---

#### `thinking_delta`

Streaming thinking content from Pi.

**Format:**
```json
{
  "type": "thinking_delta",
  "delta": "The user is asking about Python debugging..."
}
```

**Fields:**
- `delta` (string): Thinking text chunk

---

#### `tool_start`

Pi started executing a tool.

**Format:**
```json
{
  "type": "tool_start",
  "tool_use_id": "toolu_123abc",
  "name": "Read",
  "input": {
    "path": "script.py"
  }
}
```

**Fields:**
- `tool_use_id` (string): Unique tool execution ID
- `name` (string): Tool name (Read, Bash, Edit, Write)
- `input` (object): Tool input parameters

---

#### `tool_end`

Tool execution completed.

**Format:**
```json
{
  "type": "tool_end",
  "tool_use_id": "toolu_123abc",
  "success": true
}
```

**Fields:**
- `tool_use_id` (string): Tool execution ID (matches `tool_start`)
- `success` (boolean): Whether tool executed successfully

---

#### `session_created`

New session was created.

**Format:**
```json
{
  "type": "session_created",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

#### `feedback_saved`

Feedback was successfully saved.

**Format:**
```json
{
  "type": "feedback_saved",
  "timestamp": 1733234568123,
  "rating": 1
}
```

---

#### `error`

Error occurred.

**Format:**
```json
{
  "type": "error",
  "message": "Failed to process message"
}
```

**Common Errors:**
- "Pi process crashed" - Pi subprocess terminated unexpectedly
- "Failed to parse message" - Invalid JSON or message format
- "Session not found" - Trying to rate message in non-existent session

---

## Data Models

### Session

```typescript
interface Session {
  id: string;                    // UUID
  display_name: string;          // Session title
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
  message_count: number;         // Number of messages
  is_active: boolean;            // Is current session
}
```

### Message

```typescript
interface Message {
  role: "user" | "assistant" | "toolResult";
  content: string;               // Plain text content
  message_timestamp: number;     // Unix ms timestamp
  content_blocks: ContentBlock[] | null;
}
```

### Content Block

```typescript
type ContentBlock = 
  | { type: "text"; text: string }
  | { type: "thinking"; thinking: string }
  | { type: "tool_use"; id: string; name: string; input: object };
```

### Feedback

```typescript
interface Feedback {
  target_timestamp: number;      // Unix ms timestamp of message
  rating: -1 | 0 | 1;           // Negative, neutral, positive
  comment: string | null;        // Optional comment
  timestamp: number;             // Unix ms timestamp of feedback
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (session doesn't exist) |
| 500 | Internal Server Error |

### WebSocket Errors

WebSocket errors are sent as `error` type messages:

```json
{
  "type": "error",
  "message": "Error description"
}
```

**Client should:**
1. Display error to user
2. Log error for debugging
3. Attempt reconnection if connection lost
4. Not retry failed requests automatically

### Error Recovery

**Connection Lost:**
- Client automatically reconnects with exponential backoff
- Max 10 reconnection attempts
- 2-second base delay, up to 10 seconds

**Pi Crash:**
- Backend automatically restarts Pi subprocess
- In-progress message fails with error
- Next message will work normally

**Session Parse Error:**
- Session appears as "Error loading session" in UI
- Check session JSONL file for corruption
- May need to manually fix or delete corrupted file

---

## Rate Limits

Currently no rate limits enforced. For production deployment, consider:

- **Messages per minute**: 60
- **WebSocket connections**: 10 per IP
- **Session creation**: 10 per hour

---

## Versioning

API version is not currently included in endpoints. This is v1 of the API.

Future versions may include:
- `/api/v2/sessions`
- Version header: `X-API-Version: 2`

---

## Examples

### Complete Chat Flow

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected!');
  
  // Send message
  ws.send(JSON.stringify({
    type: 'message',
    content: 'Help me debug this error'
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  switch (msg.type) {
    case 'status':
      console.log('Status:', msg.status);
      break;
      
    case 'text_delta':
      // Append to current message
      appendText(msg.delta);
      break;
      
    case 'thinking_delta':
      // Show thinking
      appendThinking(msg.delta);
      break;
      
    case 'tool_start':
      console.log('Tool:', msg.name);
      break;
      
    case 'tool_end':
      console.log('Tool done:', msg.success);
      break;
      
    case 'error':
      console.error('Error:', msg.message);
      break;
  }
};
```

### Submit Feedback

```javascript
// Thumbs up
ws.send(JSON.stringify({
  type: 'feedback',
  timestamp: messageTimestamp,
  rating: 1,
  comment: null
}));

// Thumbs down with comment
ws.send(JSON.stringify({
  type: 'feedback',
  timestamp: messageTimestamp,
  rating: -1,
  comment: 'The response was inaccurate'
}));
```

### Load Past Session

```javascript
// Fetch session
const response = await fetch(`/api/sessions/${sessionId}`);
const session = await response.json();

// Display messages
session.messages.forEach(msg => {
  displayMessage(msg.role, msg.content);
  
  // Check for feedback
  const feedback = session.feedback.find(
    f => f.target_timestamp === msg.message_timestamp
  );
  
  if (feedback) {
    showFeedback(feedback.rating);
  }
});
```

---

## Security Considerations

**Current deployment:** Local laptop only (localhost)

**For production deployment:**
- Add authentication (session tokens, OAuth)
- Use HTTPS/WSS for encryption
- Implement rate limiting
- Validate all user input
- Sanitize displayed content (XSS prevention)
- Add CORS restrictions
- Implement session timeouts

---

## Support

For API issues or questions:
- Check [README.md](../README.md) for general documentation
- See [SPEC.md](../SPEC.md) for detailed specification
- Report bugs via GitHub Issues
