# Pi Portal User Guide

A simple guide to using Pi Portal for everyday coding tasks.

---

## What is Pi Portal?

Pi Portal is a web interface that lets you chat with Pi, an AI coding assistant. Think of it like ChatGPT, but specifically designed for coding tasks and running on your own computer.

### What can Pi help with?

- **Debugging code** - Find and fix errors
- **Explaining code** - Understand what code does
- **Writing code** - Generate code snippets
- **Refactoring** - Improve existing code
- **Documentation** - Write comments and docs
- **Testing** - Create test cases
- **Learning** - Learn new programming concepts

---

## Getting Started

### Opening Pi Portal

1. Make sure the server is running (your administrator should have set this up)
2. Open your web browser
3. Go to **http://localhost:8000**
4. You'll see the Pi Portal welcome screen

### Your First Conversation

When you first open Pi Portal, you'll see **starter prompts** - these are example questions you can click to get started quickly.

**Try clicking:**
- "Help me debug this error"
- "Explain this code snippet"
- "Write tests for my code"

Or **type your own question** in the text box at the bottom.

**Example questions:**
```
How do I read a CSV file in Python?
What does this error mean: "TypeError: 'int' object is not iterable"?
Help me write a function to calculate fibonacci numbers
```

---

## Understanding the Interface

### Sidebar (Left Side)

**New Session Button (+)**
- Click to start a fresh conversation
- Useful when you want to ask about something completely different

**Session List**
- Shows all your past conversations
- Click any session to view it
- The active session has a **green dot** 🟢

**Connection Status**
- Green: Connected and ready
- Yellow: Connecting...
- Red: Disconnected

### Main Chat Area

**Welcome Screen**
- Shows when you start a new session
- Displays starter prompts to help you get started
- Disappears once you send your first message

**Messages**
- Your messages appear on the right
- Pi's responses appear on the left
- Messages appear in real-time as Pi types

**Input Box**
- Type your messages here
- Press **Enter** to send
- Press **Shift+Enter** for a new line

---

## Chatting with Pi

### Asking Questions

**Be specific:**
```
❌ Bad:  "Help with code"
✅ Good: "How do I sort a list of dictionaries by a specific key in Python?"
```

**Provide context:**
```
❌ Bad:  "This doesn't work"
✅ Good: "I'm getting a KeyError when running this code: [paste code]"
```

**Show your work:**
```
✅ "I tried using sorted() but I'm getting an error. Here's my code: [paste]"
```

### Understanding Pi's Responses

**Text Response**
- Pi's main answer to your question
- May include code examples, explanations, or suggestions

**Thinking Section** (collapsible)
- Shows Pi's reasoning process
- Click to expand/collapse
- Useful for understanding how Pi approached the problem

**Tool Indicators**
- Shows when Pi uses tools like:
  - 📖 **Read** - Pi read a file
  - ⚡ **Bash** - Pi ran a command
  - ✏️ **Edit** - Pi edited a file
  - 📝 **Write** - Pi created a file
- Click to see details about what the tool did

### Code in Messages

**Inline code** appears `like this` in text.

**Code blocks** appear in a box:
```python
def hello():
    print("Hello, world!")
```

You can copy code blocks by selecting the text.

---

## Managing Sessions

### Creating a New Session

1. Click the **"+ New"** button in the sidebar
2. Your chat area clears
3. The welcome screen appears again
4. You can start a fresh conversation

**When to start a new session:**
- Switching to a completely different topic
- Starting a new project
- When the current conversation gets too long

### Viewing Past Sessions

1. Click any session in the sidebar
2. The chat area shows that conversation
3. A **📖 banner** appears showing it's read-only
4. You can scroll through the messages
5. You cannot send new messages (it's view-only)

### Session Names

Sessions are automatically named based on your first message.

**Example:**
- You ask: "Help me debug this Python error"
- Session name: "Help me debug this Python error"

---

## Providing Feedback

Help improve Pi by rating responses!

### Rating Messages

**Thumbs Up 👍**
- The response was helpful
- Pi did what you asked
- The code works correctly

**Thumbs Down 👎**
- The response wasn't helpful
- Pi misunderstood your question
- The code doesn't work
- The explanation was wrong

### How to Rate

1. **Hover** over any Pi response
2. **Click** the thumbs up or thumbs down icon
3. For thumbs down, you can add a comment explaining what went wrong
4. Your rating is saved automatically

### Changing Your Rating

- Click the other thumb to change from 👍 to 👎 or vice versa
- Click the same thumb again to remove your rating
- You can rate messages in past sessions too

### Why Feedback Matters

Your feedback helps:
- **Improve Pi** - Developers see what works and what doesn't
- **Train better models** - Feedback data helps improve AI
- **Fix bugs** - Negative feedback highlights problems

---

## Tips & Tricks

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Enter** | Send message |
| **Shift+Enter** | New line in message |
| **Esc** | Close feedback modal |
| **Tab** | Navigate interface |

### Getting Better Answers

**1. Paste error messages:**
```
I'm getting this error:
Traceback (most recent call last):
  File "script.py", line 10, in <module>
    result = data[key]
KeyError: 'name'
```

**2. Share code snippets:**
```
Here's my function that's not working:
[paste code here]
```

**3. Explain what you've tried:**
```
I tried using a try/except block but it didn't help.
I also looked at the documentation but I'm still confused.
```

**4. Ask follow-up questions:**
```
Can you explain that in simpler terms?
What if I wanted to do X instead of Y?
Is there a more efficient way to do this?
```

### What Pi Can See

**Pi can see:**
- Your current message
- Previous messages in the conversation
- Files in your project (if you ask Pi to read them)

**Pi cannot see:**
- Other sessions or conversations
- Files unless you explicitly ask Pi to read them
- Your screen or other applications

---

## Common Questions

### How do I copy code from Pi's response?

Simply select the code text and copy (Ctrl+C or Cmd+C). Code blocks are plain text.

### Can I continue a past session?

No, past sessions are read-only. You can view them, but to continue the conversation, start a new session and reference the old one if needed.

### Will my conversations be saved?

Yes! All sessions are automatically saved. You can view them anytime in the sidebar.

### Can I delete a session?

Currently no. Sessions are stored locally on your computer. Your administrator can delete session files if needed.

### What if Pi gives a wrong answer?

- Click **👎 thumbs down** on the response
- Add a comment explaining what's wrong
- Try rephrasing your question
- Provide more context or examples

### Why is Pi taking so long to respond?

Pi might be:
- Reading large files
- Running commands
- Thinking through a complex problem
- Experiencing high load

If it takes more than 30 seconds, there might be an issue. Try refreshing the page.

### What if I get disconnected?

Pi Portal automatically tries to reconnect. The connection status shows:
- **Yellow dot**: Reconnecting...
- **Green dot**: Reconnected successfully

If reconnection fails, try refreshing the page.

---

## Best Practices

### 📝 Be Clear and Specific

```
❌ "Fix my code"
✅ "This function throws a TypeError when I pass a string. How do I fix it?"
```

### 🔍 Provide Context

```
❌ "How do I do authentication?"
✅ "I'm building a REST API with FastAPI. How do I add JWT authentication?"
```

### 🎯 One Question at a Time

```
❌ "How do I connect to a database and read data and write data and handle errors?"
✅ "How do I connect to a PostgreSQL database in Python?"
     (then ask about reading, writing, errors in follow-up messages)
```

### ✅ Test the Solutions

Always test code Pi provides:
1. Copy the code
2. Try it in your project
3. If it works, give 👍
4. If it doesn't, give 👎 and explain what happened

### 💬 Use Feedback Thoughtfully

- Rate responses that were particularly helpful or unhelpful
- Add comments to negative feedback when possible
- Be specific about what was wrong

---

## Troubleshooting

### The send button is disabled

**Possible reasons:**
- You're viewing a past session (read-only mode)
- The text box is empty
- You're not connected to the server
- Pi is currently processing a message

**Try:**
- Check the connection status
- Make sure you're in an active session (green dot in sidebar)
- Wait for Pi to finish responding

### I can't see my past sessions

**Possible reasons:**
- No sessions have been created yet
- Session files were deleted
- Directory permissions issue

**Try:**
- Send a message to create your first session
- Ask your administrator to check the session directory

### Pi's response seems stuck

**Try:**
- Wait a bit longer (some operations take time)
- Refresh the page
- Check the connection status
- Ask your administrator to check server logs

### The page won't load

**Try:**
- Check the server is running
- Try a different browser
- Clear your browser cache
- Check the URL is correct (http://localhost:8000)

---

## Privacy & Data

### What data is collected?

- **Messages**: All your messages and Pi's responses
- **Feedback**: Your ratings and comments
- **Timestamps**: When messages were sent
- **Sessions**: Conversation metadata

### Where is data stored?

All data is stored **locally** on the computer running Pi Portal. Nothing is sent to external servers (except Pi's API calls which Pi makes directly).

### Who can see my data?

Only people with access to the computer where Pi Portal is running. This is typically:
- You
- Your system administrator
- R&D researchers (if they have access to the server)

### Can I delete my data?

Ask your administrator. Session files are stored in `data/pi_sessions/` and can be deleted manually.

---

## Getting Help

### If something doesn't work:

1. **Check the connection status** (bottom of sidebar)
2. **Try refreshing the page** (Ctrl+R or Cmd+R)
3. **Check with your administrator** if the server is running
4. **Report the issue** with details about what happened

### Information to include when reporting issues:

- What you were trying to do
- What happened instead
- Any error messages you saw
- Your browser (Chrome, Firefox, etc.)
- Screenshots if helpful

---

## Appendix: Example Conversations

### Example 1: Debugging

**You:**
```
I'm getting this error in Python:
TypeError: unsupported operand type(s) for +: 'int' and 'str'

Here's my code:
age = 25
message = "You are " + age + " years old"
```

**Pi:**
```
The error occurs because you're trying to concatenate an integer with strings.
In Python, you can't directly add a number to a string.

Here are two ways to fix it:

1. Convert to string:
message = "You are " + str(age) + " years old"

2. Use f-strings (recommended):
message = f"You are {age} years old"
```

### Example 2: Code Explanation

**You:**
```
Can you explain what this code does?

data = [x**2 for x in range(10) if x % 2 == 0]
```

**Pi:**
```
This is a list comprehension that creates a list of squared even numbers.

Breaking it down:
- range(10) generates numbers 0 through 9
- if x % 2 == 0 filters for even numbers (0, 2, 4, 6, 8)
- x**2 squares each even number
- The result: [0, 4, 16, 36, 64]

It's equivalent to:
data = []
for x in range(10):
    if x % 2 == 0:
        data.append(x**2)
```

### Example 3: Code Generation

**You:**
```
Write a Python function that checks if a string is a palindrome
```

**Pi:**
```
Here's a function to check if a string is a palindrome:

def is_palindrome(text):
    """
    Check if a string is a palindrome (reads same forwards and backwards).
    Case-insensitive and ignores spaces.
    """
    # Remove spaces and convert to lowercase
    cleaned = text.replace(" ", "").lower()
    
    # Compare with reversed string
    return cleaned == cleaned[::-1]

# Examples:
print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False
print(is_palindrome("A man a plan a canal Panama"))  # True
```

---

**Happy coding with Pi Portal! 🚀**
