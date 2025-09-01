"""
WebSocket Chat Exercise for Web Development Learning.

Build a real-time chat application using WebSockets with rooms, message history,
and user presence management.
"""

from typing import Dict, Any


def get_exercise() -> Dict[str, Any]:
    """Get the complete WebSocket chat exercise."""
    return {
        "title": "Real-time Chat Application",
        "description": "Build a WebSocket-based chat system with multiple rooms and advanced features",
        "difficulty": "hard",
        "estimated_time": "4-6 hours",
        "learning_objectives": [
            "Implement WebSocket connections with FastAPI",
            "Design and manage multiple chat rooms",
            "Handle connection lifecycle and cleanup",
            "Store and retrieve message history",
            "Implement user presence and typing indicators",
            "Handle reconnection and error scenarios",
            "Add real-time notifications and events"
        ],
        "requirements": [
            "FastAPI with WebSocket support",
            "HTML/JavaScript for client interface",
            "In-memory or database storage for messages",
            "JSON for message serialization",
            "Asyncio for concurrent handling"
        ],
        "starter_code": '''
"""
Real-time Chat Application - Starter Code

Complete the TODO sections to build a full-featured WebSocket chat system.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List, Set, Optional
import json
import asyncio
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import uuid

app = FastAPI(title="WebSocket Chat Application")

# Message types
class MessageType(str, Enum):
    CHAT = "chat"
    JOIN = "join"
    LEAVE = "leave"
    TYPING = "typing"
    STOP_TYPING = "stop_typing"
    USER_LIST = "user_list"
    ROOM_LIST = "room_list"
    ERROR = "error"
    SYSTEM = "system"

# Data models
class ChatMessage(BaseModel):
    id: str
    type: MessageType
    room_id: str
    user_id: str
    username: str
    content: str
    timestamp: datetime

class User(BaseModel):
    id: str
    username: str
    current_room: str
    connected_at: datetime
    is_typing: bool = False

class Room(BaseModel):
    id: str
    name: str
    users: Set[str]
    created_at: datetime
    message_count: int = 0

# TODO: Implement ConnectionManager class
class ConnectionManager:
    """Manages WebSocket connections, rooms, and message routing."""
    
    def __init__(self):
        # TODO: Initialize data structures
        # self.active_connections: Dict[str, WebSocket] = {}
        # self.users: Dict[str, User] = {}
        # self.rooms: Dict[str, Room] = {}
        # self.user_rooms: Dict[str, str] = {}  # user_id -> room_id
        pass
    
    async def connect(self, websocket: WebSocket, user_id: str, username: str, room_id: str = "general"):
        """Accept WebSocket connection and add user to room."""
        # TODO: Implement connection logic
        # 1. Accept the WebSocket connection
        # 2. Create or update user object
        # 3. Add user to specified room
        # 4. Store connection mapping
        # 5. Notify room about new user
        # 6. Send welcome message and room info to user
        pass
    
    def disconnect(self, user_id: str):
        """Handle user disconnection and cleanup."""
        # TODO: Implement disconnection logic
        # 1. Remove user from active connections
        # 2. Remove user from their current room
        # 3. Notify room about user leaving
        # 4. Clean up empty rooms if needed
        # 5. Update user presence
        pass
    
    async def send_personal_message(self, message: Dict, user_id: str):
        """Send message to specific user."""
        # TODO: Implement personal message sending
        # 1. Check if user is connected
        # 2. Get user's WebSocket connection
        # 3. Send JSON message
        # 4. Handle connection errors
        pass
    
    async def broadcast_to_room(self, room_id: str, message: Dict, exclude_user: Optional[str] = None):
        """Broadcast message to all users in a room."""
        # TODO: Implement room broadcasting
        # 1. Get all users in the room
        # 2. Iterate through users
        # 3. Send message to each user (except excluded)
        # 4. Handle disconnected users
        pass
    
    async def handle_typing(self, user_id: str, is_typing: bool):
        """Handle typing indicators."""
        # TODO: Implement typing indicators
        # 1. Update user typing status
        # 2. Broadcast typing status to room
        # 3. Set timeout for automatic stop typing
        pass
    
    def create_room(self, room_name: str) -> str:
        """Create a new chat room."""
        # TODO: Implement room creation
        # 1. Generate unique room ID
        # 2. Create Room object
        # 3. Add to rooms storage
        # 4. Return room ID
        pass
    
    def join_room(self, user_id: str, room_id: str):
        """Move user to a different room."""
        # TODO: Implement room switching
        # 1. Remove user from current room
        # 2. Add user to new room
        # 3. Update user's current room
        # 4. Notify both rooms about the change
        pass
    
    def get_room_info(self, room_id: str) -> Dict:
        """Get information about a room."""
        # TODO: Implement room info retrieval
        # 1. Check if room exists
        # 2. Get room details
        # 3. Get list of users in room
        # 4. Return formatted room info
        pass

# TODO: Implement message storage
class MessageStore:
    """Stores and retrieves chat messages."""
    
    def __init__(self):
        # TODO: Initialize message storage
        # self.messages: Dict[str, List[ChatMessage]] = {}  # room_id -> messages
        pass
    
    def add_message(self, message: ChatMessage):
        """Add a message to storage."""
        # TODO: Implement message storage
        # 1. Add message to room's message list
        # 2. Limit message history (e.g., last 100 messages)
        # 3. Update room message count
        pass
    
    def get_room_history(self, room_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get recent messages from a room."""
        # TODO: Implement message retrieval
        # 1. Get messages for room
        # 2. Return last N messages
        # 3. Handle empty room case
        pass
    
    def search_messages(self, room_id: str, query: str) -> List[ChatMessage]:
        """Search messages in a room."""
        # TODO: Implement message search
        # 1. Get room messages
        # 2. Filter by search query
        # 3. Return matching messages
        pass

# Global instances
manager = ConnectionManager()
message_store = MessageStore()

# TODO: Implement WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, username: str = "Anonymous", room: str = "general"):
    """WebSocket endpoint for chat functionality."""
    # TODO: Implement WebSocket handling
    # 1. Connect user to chat
    # 2. Send recent message history
    # 3. Handle incoming messages in loop
    # 4. Process different message types
    # 5. Handle disconnection
    pass

# TODO: Implement REST API endpoints
@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the chat interface."""
    # TODO: Return comprehensive HTML chat interface
    # Include:
    # 1. Connection controls
    # 2. Room selection
    # 3. Message display area
    # 4. Message input
    # 5. User list
    # 6. Typing indicators
    # 7. JavaScript WebSocket handling
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Chat</title>
        <style>
            /* TODO: Add comprehensive CSS styling */
        </style>
    </head>
    <body>
        <div id="app">
            <!-- TODO: Add complete chat interface HTML -->
        </div>
        
        <script>
            // TODO: Implement JavaScript WebSocket client
        </script>
    </body>
    </html>
    """

@app.get("/api/rooms")
async def get_rooms():
    """Get list of available rooms."""
    # TODO: Implement room listing
    pass

@app.post("/api/rooms")
async def create_room(room_name: str):
    """Create a new chat room."""
    # TODO: Implement room creation endpoint
    pass

@app.get("/api/rooms/{room_id}/messages")
async def get_room_messages(room_id: str, limit: int = 50):
    """Get message history for a room."""
    # TODO: Implement message history endpoint
    pass

@app.get("/api/rooms/{room_id}/users")
async def get_room_users(room_id: str):
    """Get users currently in a room."""
    # TODO: Implement room users endpoint
    pass

@app.get("/api/stats")
async def get_chat_stats():
    """Get chat application statistics."""
    # TODO: Implement statistics endpoint
    # Include:
    # 1. Total active users
    # 2. Total rooms
    # 3. Total messages sent
    # 4. Most active rooms
    pass

# TODO: Add error handling and validation
@app.exception_handler(WebSocketDisconnect)
async def websocket_disconnect_handler(websocket: WebSocket, exc: WebSocketDisconnect):
    """Handle WebSocket disconnections."""
    # TODO: Implement proper disconnect handling
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
        "implementation_guide": [
            "Start with the ConnectionManager class - this is the core component",
            "Implement basic connect/disconnect functionality first",
            "Add message broadcasting to rooms",
            "Create the WebSocket endpoint to handle incoming messages",
            "Build a simple HTML interface for testing",
            "Add message persistence with MessageStore",
            "Implement typing indicators and user presence",
            "Add room management features",
            "Create REST API endpoints for room/message management",
            "Add error handling and edge cases"
        ],
        "testing_guide": '''
# Testing Your WebSocket Chat Application

## 1. Basic Connection Testing
```bash
# Start the server
uvicorn main:app --reload

# Test with multiple browser tabs
# Open http://localhost:8000 in multiple tabs
# Use different usernames to simulate multiple users
```

## 2. Manual Testing Checklist
- [ ] Users can connect with different usernames
- [ ] Messages are broadcast to all users in the same room
- [ ] Users can switch between rooms
- [ ] Message history is preserved
- [ ] Typing indicators work
- [ ] Users see when others join/leave
- [ ] Disconnections are handled gracefully

## 3. WebSocket Testing with JavaScript
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user123?username=TestUser&room=general');

ws.onopen = function(event) {
    console.log('Connected to chat');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Send test message
ws.send(JSON.stringify({
    type: 'chat',
    content: 'Hello, World!'
}));
```

## 4. Load Testing
```python
import asyncio
import websockets
import json

async def simulate_user(user_id):
    uri = f"ws://localhost:8000/ws/{user_id}?username=User{user_id}&room=general"
    async with websockets.connect(uri) as websocket:
        # Send messages
        for i in range(10):
            message = {
                "type": "chat",
                "content": f"Message {i} from User {user_id}"
            }
            await websocket.send(json.dumps(message))
            await asyncio.sleep(1)

# Run multiple users concurrently
async def load_test():
    tasks = [simulate_user(i) for i in range(10)]
    await asyncio.gather(*tasks)

asyncio.run(load_test())
```
''',
        "solution_hints": [
            "Use dictionaries to track connections: {user_id: websocket}",
            "Store room membership: {room_id: set_of_user_ids}",
            "Handle WebSocketDisconnect exceptions in the main loop",
            "Use asyncio.create_task() for background operations like typing timeouts",
            "Validate message types and content before processing",
            "Keep message history limited to prevent memory issues",
            "Use UUIDs for unique message and room IDs",
            "Implement heartbeat/ping to detect dead connections"
        ],
        "bonus_challenges": [
            "Add private messaging between users",
            "Implement message reactions and emojis",
            "Add file/image sharing capabilities",
            "Create message threading/replies",
            "Add user roles and permissions (admin, moderator)",
            "Implement message encryption for privacy",
            "Add user authentication and persistent sessions",
            "Create message search across all rooms",
            "Add voice/video call integration",
            "Implement message notifications when user is away",
            "Add chat bots with commands",
            "Create room passwords and private rooms"
        ],
        "common_pitfalls": [
            "Not handling WebSocket disconnections properly",
            "Memory leaks from not cleaning up disconnected users",
            "Race conditions in concurrent message handling",
            "Not validating incoming message format",
            "Blocking operations in WebSocket handlers",
            "Not limiting message history storage",
            "Missing error handling for malformed JSON",
            "Not handling duplicate user connections"
        ]
    }