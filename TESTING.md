# Pi Portal - Testing Checklist

Manual testing checklist for M4.5 - Testing & bug fixes

## Test Environment

- **Date:** 2026-03-10
- **Tester:** Agent
- **Python:** 3.12.13
- **Browser:** To be tested manually by user
- **Platform:** Linux

---

## Automated Tests

### ✅ Unit Tests
- [x] All 132 tests passing
- [x] Coverage: Backend functionality
- [x] Test framework: pytest
- [x] Code quality: ruff (format + lint)

**Results:**
```
====================== 132 passed, 20 deselected in 0.15s ======================
All checks passed!
```

---

## Manual Testing Checklist

### 1. Basic Chat Flow

#### 1.1 Server Startup
- [ ] Server starts without errors
- [ ] Health endpoint responds (GET /health)
- [ ] Static files served correctly
- [ ] No errors in console

#### 1.2 First Connection
- [ ] Browser loads interface
- [ ] Welcome screen displays
- [ ] Starter prompts visible
- [ ] Connection status shows "Connecting..." then "Connected"
- [ ] WebSocket connects successfully

#### 1.3 Send First Message
- [ ] Click a starter prompt
- [ ] Welcome screen disappears
- [ ] User message appears in chat
- [ ] Pi starts responding
- [ ] Typing indicator shows briefly
- [ ] Response streams in real-time
- [ ] Response completes successfully

#### 1.4 Message Display
- [ ] User messages right-aligned/styled correctly
- [ ] Assistant messages left-aligned/styled correctly
- [ ] Timestamps displayed
- [ ] Auto-scroll to bottom works

#### 1.5 Streaming Features
- [ ] Text appears as Pi types
- [ ] Thinking section shows (if Pi uses thinking)
- [ ] Thinking section is collapsible
- [ ] Tool indicators show (if Pi uses tools)
- [ ] Tool status updates (running → success/error)
- [ ] Tool details expandable

#### 1.6 Input Handling
- [ ] Text input works
- [ ] Enter sends message
- [ ] Shift+Enter creates new line
- [ ] Send button enables/disables correctly
- [ ] Input clears after sending
- [ ] Can send multiple messages

---

### 2. Session Management

#### 2.1 Session Creation
- [ ] First message creates session
- [ ] Session appears in sidebar
- [ ] Session has correct title (from first message)
- [ ] Session has green dot (active indicator)
- [ ] Session has timestamp

#### 2.2 New Session Button
- [ ] Click "New Session" button
- [ ] Chat area clears
- [ ] Welcome screen reappears
- [ ] Starter prompts visible again
- [ ] Old session moves to sidebar (no longer active)
- [ ] Send message in new session
- [ ] New session appears in sidebar with green dot

#### 2.3 Session List
- [ ] All sessions visible in sidebar
- [ ] Sessions ordered by most recent
- [ ] Active session highlighted
- [ ] Session titles truncated if long
- [ ] Message count displayed

#### 2.4 View Past Session
- [ ] Click past session in sidebar
- [ ] Chat area loads past messages
- [ ] Read-only banner appears
- [ ] All messages displayed correctly
- [ ] Existing feedback shown
- [ ] Input field disabled
- [ ] Cannot send new messages
- [ ] Can scroll through history

#### 2.5 Session Persistence
- [ ] Refresh browser
- [ ] Sessions still in sidebar
- [ ] Active session restored
- [ ] Messages persisted correctly
- [ ] Feedback persisted correctly

---

### 3. Feedback System

#### 3.1 Thumbs Up
- [ ] Hover over assistant message
- [ ] Thumbs up/down buttons appear
- [ ] Click thumbs up
- [ ] Button highlights green
- [ ] Feedback saved (check confirmation)
- [ ] Refresh: feedback still shows

#### 3.2 Thumbs Down
- [ ] Click thumbs down
- [ ] Modal opens
- [ ] Modal has comment textarea
- [ ] Modal has Cancel button
- [ ] Modal has Submit button
- [ ] Can close modal (X, Cancel, or Esc)

#### 3.3 Thumbs Down with Comment
- [ ] Click thumbs down
- [ ] Enter comment in textarea
- [ ] Click Submit
- [ ] Modal closes
- [ ] Button highlights red
- [ ] Feedback saved
- [ ] Refresh: feedback still shows

#### 3.4 Thumbs Down without Comment
- [ ] Click thumbs down
- [ ] Leave comment empty
- [ ] Click Submit
- [ ] Feedback saved successfully

#### 3.5 Change Feedback
- [ ] Rate message thumbs up
- [ ] Click thumbs down (change rating)
- [ ] Modal opens
- [ ] Submit with/without comment
- [ ] Rating changes to thumbs down
- [ ] Previous comment cleared if changed to up

#### 3.6 Remove Feedback
- [ ] Rate message thumbs up
- [ ] Click thumbs up again
- [ ] Rating removed
- [ ] No highlight on buttons

#### 3.7 Feedback on Past Sessions
- [ ] View past session
- [ ] Hover over message
- [ ] Feedback buttons appear
- [ ] Can rate messages
- [ ] Feedback saved to correct session file
- [ ] Refresh: feedback persists

---

### 4. Error Scenarios

#### 4.1 WebSocket Disconnection
- [ ] Disconnect network/stop server
- [ ] Connection status shows "Disconnected"
- [ ] Red dot in sidebar
- [ ] Error notification appears
- [ ] Reconnect network/restart server
- [ ] Auto-reconnect works
- [ ] Connection status shows "Connected"
- [ ] Success notification appears

#### 4.2 Send Message While Disconnected
- [ ] Disconnect
- [ ] Try to send message
- [ ] Send button disabled
- [ ] Or error message shown

#### 4.3 Pi Subprocess Crash
- [ ] Start chat session
- [ ] Send message to Pi
- [ ] Kill Pi process manually (simulate crash)
- [ ] Backend detects crash
- [ ] Error message shown
- [ ] Backend restarts Pi
- [ ] Send new message
- [ ] Works correctly

#### 4.4 Invalid Session File
- [ ] Create corrupted JSONL file
- [ ] Refresh page
- [ ] Session list loads
- [ ] Corrupted session skipped or error handled
- [ ] Other sessions still work

#### 4.5 Missing Session File
- [ ] Delete a session file
- [ ] Try to view that session
- [ ] 404 error returned
- [ ] Error notification shown
- [ ] Session list updates

#### 4.6 Network Errors
- [ ] Simulate slow network
- [ ] Messages still work (may be slower)
- [ ] Timeout handling works
- [ ] No crashes or hangs

---

### 5. UI/UX Polish

#### 5.1 Responsive Design
- [ ] Desktop view works (1920x1080)
- [ ] Laptop view works (1366x768)
- [ ] Tablet view works (768x1024)
- [ ] Mobile view works (375x667)
- [ ] Sidebar adapts on mobile
- [ ] Messages readable on all sizes

#### 5.2 Animations
- [ ] Button hover effects work
- [ ] Button click animations work
- [ ] Message appears with fade-in
- [ ] Typing indicator animates
- [ ] Modal opens with animation
- [ ] Smooth scrolling works
- [ ] Session hover effects work

#### 5.3 Keyboard Navigation
- [ ] Tab through interface
- [ ] Focus visible on elements
- [ ] Enter sends message
- [ ] Shift+Enter adds line
- [ ] Esc closes modal
- [ ] All interactive elements accessible

#### 5.4 Visual Feedback
- [ ] Send button changes on hover
- [ ] Feedback buttons highlight
- [ ] Active session highlighted
- [ ] Tool status colors correct
- [ ] Connection status colors correct
- [ ] Loading states visible

---

### 6. Edge Cases

#### 6.1 Empty/Whitespace Messages
- [ ] Send empty message
- [ ] Ignored/prevented
- [ ] Send only whitespace
- [ ] Ignored/prevented

#### 6.2 Very Long Messages
- [ ] Send 1000+ character message
- [ ] Displays correctly
- [ ] Input expands appropriately
- [ ] Scrolling works

#### 6.3 Special Characters
- [ ] Send message with <, >, &
- [ ] HTML escaped correctly
- [ ] Send message with quotes
- [ ] Escaped correctly
- [ ] Send code blocks
- [ ] Rendered correctly

#### 6.4 Rapid Messages
- [ ] Send multiple messages quickly
- [ ] All queued and processed
- [ ] No race conditions
- [ ] No lost messages

#### 6.5 Many Sessions
- [ ] Create 20+ sessions
- [ ] All listed in sidebar
- [ ] Scrolling works
- [ ] Performance acceptable

#### 6.6 Large Session History
- [ ] View session with 50+ messages
- [ ] All messages load
- [ ] Scrolling works
- [ ] Performance acceptable

---

### 7. Configuration

#### 7.1 Default Configuration
- [ ] Run without .env file
- [ ] Defaults applied correctly
- [ ] Server starts on port 8000
- [ ] Pi executable found
- [ ] Sessions save to data/pi_sessions/

#### 7.2 Custom Configuration
- [ ] Create .env file
- [ ] Set custom port
- [ ] Set custom session directory
- [ ] Set custom Pi path
- [ ] All settings respected

---

### 8. API Endpoints

#### 8.1 Health Check
- [ ] GET /health returns 200
- [ ] Response: {"status": "ok"}

#### 8.2 List Sessions
- [ ] GET /api/sessions returns sessions
- [ ] Sessions have correct fields
- [ ] Sessions ordered by date
- [ ] Empty directory returns []

#### 8.3 Get Session
- [ ] GET /api/sessions/{id} returns session
- [ ] Messages included
- [ ] Feedback included
- [ ] 404 for missing session

#### 8.4 Starter Prompts
- [ ] GET /api/config/starter-prompts works
- [ ] Returns configured prompts
- [ ] Prompts have icon and text

---

### 9. Browser Compatibility

#### 9.1 Chrome
- [ ] All features work
- [ ] WebSocket connects
- [ ] Animations smooth
- [ ] No console errors

#### 9.2 Firefox
- [ ] All features work
- [ ] WebSocket connects
- [ ] Animations smooth
- [ ] No console errors

#### 9.3 Safari
- [ ] All features work
- [ ] WebSocket connects
- [ ] Animations smooth
- [ ] No console errors

#### 9.4 Edge
- [ ] All features work
- [ ] WebSocket connects
- [ ] Animations smooth
- [ ] No console errors

---

## Performance Tests

### Load Time
- [ ] Page loads in < 2 seconds
- [ ] WebSocket connects in < 1 second
- [ ] First message response in < 5 seconds

### Memory
- [ ] No memory leaks after 10 sessions
- [ ] Browser tab stable over time
- [ ] Backend process stable

### Responsiveness
- [ ] UI remains responsive during Pi processing
- [ ] Scrolling smooth with many messages
- [ ] No lag on input

---

## Security Tests

### Input Validation
- [ ] XSS attempts blocked (escaped)
- [ ] SQL injection N/A (no SQL)
- [ ] Path traversal blocked

### File Access
- [ ] Cannot access files outside session dir
- [ ] Session files readable only by owner
- [ ] No unauthorized file writes

---

## Bugs Found

### Bug #1
**Status:** [ ] Open / [ ] Fixed
**Description:**
**Steps to reproduce:**
**Expected:**
**Actual:**
**Fix:**

### Bug #2
**Status:** [ ] Open / [ ] Fixed
**Description:**
**Steps to reproduce:**
**Expected:**
**Actual:**
**Fix:**

---

## Final Checklist

- [ ] All critical bugs fixed
- [ ] All automated tests passing
- [ ] All manual tests completed
- [ ] Documentation reviewed
- [ ] Code cleaned up
- [ ] Ready for deployment

---

## Test Results Summary

**Date Completed:** ___________
**Total Tests:** ___________
**Passed:** ___________
**Failed:** ___________
**Bugs Found:** ___________
**Bugs Fixed:** ___________

**Overall Status:** [ ] Pass [ ] Fail [ ] Needs Work

**Notes:**
