// Chatbot Toggle Function
const SESSION_ID = (() => {
    let id = localStorage.getItem('chat_session_id');
    if (!id) {
        id = crypto.randomUUID();
        localStorage.setItem('chat_session_id', id);
    }
    return id;
})();

function toggleChat() {
    const chatBox = document.getElementById('chat-window');
    chatBox.style.display = chatBox.style.display === 'none' || chatBox.style.display === '' ? 'flex' : 'none';
}

// Send Message Function
async function sendMessage() {
    const inputField = document.getElementById('chat-input');
    const message = inputField.value.trim();
    if(!message) return;

    const chatMessages = document.getElementById('chat-messages');

    // Add user message to UI
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'message user-message';
    userMsgDiv.innerText = message;
    chatMessages.appendChild(userMsgDiv);

    // Clear input
    inputField.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Show typing status (optional, but good UX)
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.innerText = 'Thinking...';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Call FastAPI Backend
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: message })
        });
        
        const data = await response.json();
        
        // Remove typing status and add bot response
        chatMessages.removeChild(typingDiv);
        
        const botMsgDiv = document.createElement('div');
        botMsgDiv.className = 'message bot-message';
        botMsgDiv.innerText = data.reply;
        chatMessages.appendChild(botMsgDiv);
    } catch (error) {
        chatMessages.removeChild(typingDiv);
        console.error('Error connecting to backend:', error);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message bot-message error-message';
        errorDiv.innerText = "Sorry, I couldn't connect to the server right now.";
        chatMessages.appendChild(errorDiv);
    }
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Assign 'Enter' key to send message
document.addEventListener('DOMContentLoaded', () => {
    const inputField = document.getElementById('chat-input');
    if(inputField) {
        inputField.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

