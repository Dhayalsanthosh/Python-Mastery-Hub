"""
WebSocket Examples for Web Development Learning.

Real-time communication with WebSocket implementation.
"""

from typing import Dict, Any


def get_websocket_examples() -> Dict[str, Any]:
    """Get WebSocket examples."""
    return {
        "websocket_chat": {
            "code": '''
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime
import uuid

app = FastAPI(title="WebSocket Chat Demo")

# Connection manager for handling multiple WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_rooms: Dict[str, str] = {}  # user_id -> room_id
        self.room_users: Dict[str, Set[str]] = {}  # room_id -> set of user_ids
    
    async def connect(self, websocket: WebSocket, user_id: str, room_id: str = "general"):
        """Accept WebSocket connection and add user to room."""
        await websocket.accept()
        
        # Store connection
        self.active_connections[user_id] = websocket
        self.user_rooms[user_id] = room_id
        
        # Add user to room
        if room_id not in self.room_users:
            self.room_users[room_id] = set()
        self.room_users[room_id].add(user_id)
        
        # Notify room about new user
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "message": f"{user_id} joined the room",
            "timestamp": datetime.now().isoformat(),
            "room_users": list(self.room_users[room_id])
        }, exclude_user=user_id)
        
        # Send welcome message to new user
        await self.send_personal_message({
            "type": "welcome",
            "message": f"Welcome to room '{room_id}'!",
            "room_id": room_id,
            "room_users": list(self.room_users[room_id])
        }, user_id)
    
    def disconnect(self, user_id: str):
        """Remove user connection and clean up."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.user_rooms:
            room_id = self.user_rooms[user_id]
            del self.user_rooms[user_id]
            
            # Remove user from room
            if room_id in self.room_users:
                self.room_users[room_id].discard(user_id)
                
                # Clean up empty rooms
                if not self.room_users[room_id]:
                    del self.room_users[room_id]
                else:
                    # Notify remaining users
                    asyncio.create_task(self.broadcast_to_room(room_id, {
                        "type": "user_left",
                        "user_id": user_id,
                        "message": f"{user_id} left the room",
                        "timestamp": datetime.now().isoformat(),
                        "room_users": list(self.room_users[room_id])
                    }))
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps(message))
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in a room."""
        if room_id not in self.room_users:
            return
        
        disconnected_users = []
        
        for user_id in self.room_users[room_id]:
            if exclude_user and user_id == exclude_user:
                continue
                
            if user_id in self.active_connections:
                try:
                    websocket = self.active_connections[user_id]
                    await websocket.send_text(json.dumps(message))
                except:
                    # Connection is dead, mark for removal
                    disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)

# Global connection manager
manager = ConnectionManager()

# Store chat history (in production, use a database)
chat_history: Dict[str, List[dict]] = {}

# HTML client for testing
@app.get("/", response_class=HTMLResponse)
async def get_chat_client():
    """Serve a simple HTML chat client."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Chat</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #messages { border: 1px solid #ccc; height: 400px; padding: 10px; overflow-y: scroll; margin-bottom: 10px; }
            #messageInput { width: 70%; padding: 10px; }
            #sendButton { padding: 10px 20px; }
            .message { margin-bottom: 10px; }
            .system { color: #666; font-style: italic; }
            .user { color: #0066cc; }
            .error { color: #cc0000; }
            #userInfo { background: #f0f0f0; padding: 10px; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>WebSocket Chat Demo</h1>
        
        <div id="userInfo">
            <label>User ID: <input type="text" id="userId" value="user123"></label>
            <label>Room: <input type="text" id="roomId" value="general"></label>
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
            <span id="status">Disconnected</span>
        </div>
        
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="Type a message..." disabled>
        <button id="sendButton" onclick="sendMessage()" disabled>Send</button>
        
        <script>
            let ws = null;
            let userId = '';
            let roomId = '';
            
            function connect() {
                userId = document.getElementById('userId').value;
                roomId = document.getElementById('roomId').value;
                
                if (!userId) {
                    alert('Please enter a User ID');
                    return;
                }
                
                ws = new WebSocket(`ws://localhost:8000/ws/${userId}?room=${roomId}`);
                
                ws.onopen = function(event) {
                    document.getElementById('status').textContent = 'Connected';
                    document.getElementById('messageInput').disabled = false;
                    document.getElementById('sendButton').disabled = false;
                    addMessage('system', 'Connected to chat');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                };
                
                ws.onclose = function(event) {
                    document.getElementById('status').textContent = 'Disconnected';
                    document.getElementById('messageInput').disabled = true;
                    document.getElementById('sendButton').disabled = true;
                    addMessage('system', 'Disconnected from chat');
                };
                
                ws.onerror = function(error) {
                    addMessage('error', 'WebSocket error: ' + error);
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                }
            }
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (message && ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'chat',
                        message: message
                    }));
                    input.value = '';
                }
            }
            
            function handleMessage(data) {
                switch(data.type) {
                    case 'chat':
                        addMessage('user', `${data.user_id}: ${data.message}`, data.timestamp);
                        break;
                    case 'welcome':
                        addMessage('system', data.message);
                        break;
                    case 'user_joined':
                    case 'user_left':
                        addMessage('system', data.message);
                        break;
                    case 'error':
                        addMessage('error', data.message);
                        break;
                    default:
                        addMessage('system', JSON.stringify(data));
                }
            }
            
            function addMessage(type, message, timestamp = null) {
                const messages = document.getElementById('messages');
                const messageElement = document.createElement('div');
                messageElement.className = `message ${type}`;
                
                const time = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
                messageElement.innerHTML = `<small>[${time}]</small> ${message}`;
                
                messages.appendChild(messageElement);
                messages.scrollTop = messages.scrollHeight;
            }
            
            // Allow sending message with Enter key
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, room: str = "general"):
    """WebSocket endpoint for chat functionality."""
    await manager.connect(websocket, user_id, room)
    
    # Send recent chat history to new user
    if room in chat_history:
        recent_messages = chat_history[room][-10:]  # Last 10 messages
        for msg in recent_messages:
            await manager.send_personal_message(msg, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "chat":
                # Regular chat message
                chat_message = {
                    "type": "chat",
                    "user_id": user_id,
                    "message": message_data["message"],
                    "timestamp": datetime.now().isoformat(),
                    "room_id": room
                }
                
                # Store in chat history
                if room not in chat_history:
                    chat_history[room] = []
                chat_history[room].append(chat_message)
                
                # Keep only last 100 messages per room
                if len(chat_history[room]) > 100:
                    chat_history[room] = chat_history[room][-100:]
                
                # Broadcast to room
                await manager.broadcast_to_room(room, chat_message, exclude_user=user_id)
            
            elif message_data.get("type") == "ping":
                # Handle ping/keepalive
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, user_id)
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# REST API endpoints for chat management
@app.get("/rooms")
async def get_rooms():
    """Get list of active chat rooms."""
    return {"rooms": [{"room_id": room_id, "users": list(users)} 
                     for room_id, users in manager.room_users.items()]}

@app.get("/rooms/{room_id}/history")
async def get_room_history(room_id: str, limit: int = 50):
    """Get chat history for a specific room."""
    if room_id not in chat_history:
        return {"room_id": room_id, "messages": []}
    
    messages = chat_history[room_id][-limit:]
    return {
        "room_id": room_id,
        "messages": messages,
        "total_messages": len(chat_history[room_id])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
            "explanation": "Real-time WebSocket chat with connection management and room support"
        }
    }