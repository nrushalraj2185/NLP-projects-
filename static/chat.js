// Chat Application State
let currentSessionId = null;
let conversationHistory = [];

// DOM Elements
const dashboardContainer = document.getElementById('dashboard-container');
const modeAdvisor = document.getElementById('mode-advisor');
const modeResume = document.getElementById('mode-resume');
const backToDashboard = document.getElementById('back-to-dashboard');
const uploadContainer = document.getElementById('upload-container');
const chatContainer = document.getElementById('chat-container');
const loadingOverlay = document.getElementById('loading-overlay');
const resumeUpload = document.getElementById('resume-upload');
const fileName = document.getElementById('file-name');
const startChatBtn = document.getElementById('start-chat-btn');
const messagesContainer = document.getElementById('messages-container');
const suggestionsContainer = document.getElementById('suggestions-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');

// ===== DASHBOARD HANDLING =====
modeAdvisor.addEventListener('click', async () => {
    // Start General Chat immediately
    showLoading(true, "Launching Career Advisor...");
    try {
        const response = await fetch('/chatbot/session/general', { method: 'POST' });
        if (!response.ok) throw new Error('Failed to start general session');

        const data = await response.json();
        currentSessionId = data.session_id;
        conversationHistory = data.conversation_history;

        // UI Switch
        dashboardContainer.style.display = 'none';
        chatContainer.style.display = 'flex';
        renderMessages();
        if (data.suggestions) renderSuggestions(data.suggestions);

    } catch (error) {
        console.error(error);
        alert('Could not start Career Advisor');
    } finally {
        showLoading(false);
    }
});

modeResume.addEventListener('click', () => {
    dashboardContainer.style.display = 'none';
    uploadContainer.style.display = 'flex';
});

backToDashboard.addEventListener('click', () => {
    uploadContainer.style.display = 'none';
    dashboardContainer.style.display = 'flex';
});

// ===== FILE UPLOAD HANDLING =====
resumeUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = `✓ ${file.name}`;
        startChatBtn.disabled = false;
    } else {
        fileName.textContent = '';
        startChatBtn.disabled = true;
    }
});

// ===== START CHAT SESSION =====
startChatBtn.addEventListener('click', async () => {
    const file = resumeUpload.files[0];
    if (!file) return;

    showLoading(true, "Analyzing Resume & Initializing Toolkit...");

    try {
        const formData = new FormData();
        formData.append('resume_file', file);

        const response = await fetch('/chatbot/session', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to create session');
        }

        const data = await response.json();
        currentSessionId = data.session_id;
        conversationHistory = data.conversation_history;

        // Switch to chat interface
        uploadContainer.style.display = 'none';
        chatContainer.style.display = 'flex';
        showLoading(false);

        // Display conversation history
        renderMessages();

        // Render initial suggestions if available
        if (data.suggestions && data.suggestions.length > 0) {
            renderSuggestions(data.suggestions);
        }

        // Focus input
        messageInput.focus();

    } catch (error) {
        console.error('Error creating session:', error);
        alert('Failed to start chat session. Please try again.');
        showLoading(false);
    }
});

// ===== SEND MESSAGE =====
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !currentSessionId) return;

    // Clear input
    messageInput.value = '';
    sendBtn.disabled = true;

    // Add user message to UI
    addMessage('user', message);

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch('/chatbot/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });

        if (!response.ok) {
            throw new Error('Failed to send message');
        }

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator();

        // Add assistant response
        addMessage('assistant', data.answer, data.confidence);

        // Update suggestions
        if (data.suggestions && data.suggestions.length > 0) {
            renderSuggestions(data.suggestions);
        }

        // Update conversation history
        conversationHistory = data.conversation_history;

    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        addMessage('assistant', 'Sorry, I encountered an error. Please try again.', 0);
    } finally {
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// ===== MESSAGE RENDERING =====
function addMessage(role, content, confidence = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = role === 'assistant'
        ? '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>'
        : '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Format content with line breaks
    contentDiv.innerHTML = content.replace(/\n/g, '<br>');

    // Add confidence indicator for low confidence responses
    if (confidence !== null && confidence < 0.5) {
        const confidenceNote = document.createElement('div');
        confidenceNote.style.fontSize = '0.85rem';
        confidenceNote.style.marginTop = '0.5rem';
        confidenceNote.style.opacity = '0.7';
        confidenceNote.textContent = '(Low confidence - please verify)';
        contentDiv.appendChild(confidenceNote);
    }

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    contentDiv.appendChild(time);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function renderMessages() {
    messagesContainer.innerHTML = '';
    conversationHistory.forEach(msg => {
        addMessage(msg.role, msg.content, msg.confidence);
    });
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant typing-indicator-message';
    typingDiv.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;

    typingDiv.appendChild(avatar);
    typingDiv.appendChild(contentDiv);
    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// ===== SUGGESTIONS =====
function renderSuggestions(suggestions) {
    suggestionsContainer.innerHTML = '';

    suggestions.forEach(suggestion => {
        const chip = document.createElement('button');
        chip.className = 'suggestion-chip';
        chip.textContent = suggestion;
        chip.addEventListener('click', () => {
            messageInput.value = suggestion;
            messageInput.focus();
            sendMessage();
        });
        suggestionsContainer.appendChild(chip);
    });
}

// ===== NEW CHAT =====
newChatBtn.addEventListener('click', () => {
    if (confirm('Start a new conversation? This will clear the current chat.')) {
        currentSessionId = null;
        conversationHistory = [];
        messagesContainer.innerHTML = '';
        suggestionsContainer.innerHTML = '';
        messageInput.value = '';
        resumeUpload.value = '';
        fileName.textContent = '';
        startChatBtn.disabled = true;

        chatContainer.style.display = 'none';

        // Reset to Dashboard
        uploadContainer.style.display = 'none';
        dashboardContainer.style.display = 'flex';
    }
});

// ===== INPUT HANDLING =====
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

messageInput.addEventListener('input', () => {
    sendBtn.disabled = !messageInput.value.trim();
});

// ===== UTILITY FUNCTIONS =====
function showLoading(show, message = "Processing...") {
    loadingOverlay.style.display = show ? 'flex' : 'none';
    if (show) {
        const textElement = loadingOverlay.querySelector('p');
        if (textElement) {
            textElement.textContent = message;
        }
    }
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        messageInput.focus();
    }

    // Escape to blur input
    if (e.key === 'Escape') {
        messageInput.blur();
    }
});

// ===== WELCOME ANIMATION =====
window.addEventListener('load', () => {
    // Add subtle entrance animations
    document.querySelector('.upload-card').style.animation = 'fadeIn 0.8s ease';
});

// ===== AUTO-RESIZE TEXTAREA (if needed in future) =====
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// ===== ERROR HANDLING =====
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    // Optionally show user-friendly error message
});

// ===== SESSION PERSISTENCE (Optional - for future enhancement) =====
// Save session ID to localStorage for recovery
function saveSession() {
    if (currentSessionId) {
        localStorage.setItem('chatSessionId', currentSessionId);
    }
}

function loadSession() {
    const savedSessionId = localStorage.getItem('chatSessionId');
    if (savedSessionId) {
        // Could implement session recovery here
        // For now, we'll start fresh each time
        localStorage.removeItem('chatSessionId');
    }
}

// Initialize
loadSession();

console.log('🤖 Smart Resume AI Chatbot initialized');
console.log('💡 Tip: Press Ctrl+K to focus the message input');
