// Configuration
const CONFIG = {
    RASA_URL: 'http://localhost:5005/webhooks/rest/webhook',
    USER_ID: 'user_' + Math.random().toString(36).substr(2, 9),
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000
};

// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const messagesContainer = document.getElementById('messagesContainer');
const clearChatButton = document.getElementById('clearChat');
const resetAllButton = document.getElementById('resetAll');
const typingIndicator = document.getElementById('typingIndicator');
const loadingOverlay = document.getElementById('loadingOverlay');

// State
let isTyping = false;
let retryCount = 0;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupEventListeners();
    setWelcomeTime();
});

// Initialize chat
function initializeChat() {
    // Set initial focus
    messageInput.focus();
    
    // Load chat history from localStorage if available
    loadChatHistory();
}

// Setup event listeners
function setupEventListeners() {
    // Send button click
    sendButton.addEventListener('click', handleSendMessage);
    
    // Enter key press
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Clear chat button
    clearChatButton.addEventListener('click', clearChat);
    
    // Reset all button
    resetAllButton.addEventListener('click', resetAll);
    
    // Input focus management
    messageInput.addEventListener('focus', function() {
        scrollToBottom();
    });
    
    // Auto-resize input (if needed for mobile)
    messageInput.addEventListener('input', function() {
        // Auto-expand logic can be added here
    });
}

// Handle send message
async function handleSendMessage() {
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Disable input while processing
    setInputState(false);
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send to Rasa
        const response = await sendToRasa(message);
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Handle response
        handleRasaResponse(response);
        
        // Reset retry count on success
        retryCount = 0;
        
    } catch (error) {
        console.error('Error sending message:', error);
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Handle error
        handleError(error, message);
    }
    
    // Re-enable input
    setInputState(true);
    
    // Focus back to input
    messageInput.focus();
}

// Send message to Rasa
async function sendToRasa(message) {
    const payload = {
        sender: CONFIG.USER_ID,
        message: message
    };
    
    try {
        const response = await fetch(CONFIG.RASA_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            mode: 'cors',
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Rasa response:', data);
        return data;
        
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Handle Rasa response
function handleRasaResponse(responses) {
    if (!responses || responses.length === 0) {
        addMessage('عذراً، لم أتمكن من فهم طلبك. يرجى المحاولة مرة أخرى.', 'bot');
        return;
    }
    
    // Process each response
    responses.forEach((response, index) => {
        setTimeout(() => {
            if (response.text) {
                addMessage(response.text, 'bot');
            }
            
            // Handle custom actions or buttons if needed
            if (response.buttons) {
                addButtons(response.buttons);
            }
            
            if (response.attachment) {
                addAttachment(response.attachment);
            }
        }, index * 500); // Stagger responses
    });
}

// Add message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = formatMessage(text);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = getCurrentTime();
    
    contentDiv.appendChild(textDiv);
    contentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
    
    // Save to localStorage
    saveChatHistory();
    
    // Add animation class
    setTimeout(() => {
        messageDiv.classList.add('animate-in');
    }, 100);
}

// Format message text (support for links, emojis, etc.)
function formatMessage(text) {
    // Convert URLs to links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    text = text.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    
    // Convert line breaks to <br>
    text = text.replace(/\n/g, '<br>');
    
    // Add emoji support or other formatting if needed
    
    return text;
}

// Add quick action buttons
function addButtons(buttons) {
    const buttonsDiv = document.createElement('div');
    buttonsDiv.className = 'message-buttons';
    
    buttons.forEach(button => {
        const btn = document.createElement('button');
        btn.className = 'quick-btn';
        btn.textContent = button.title;
        btn.onclick = () => sendQuickMessage(button.payload);
        buttonsDiv.appendChild(btn);
    });
    
    const lastMessage = messagesContainer.lastElementChild;
    lastMessage.querySelector('.message-content').appendChild(buttonsDiv);
}

// Send quick message with validation
function sendQuickMessage(message) {
    messageInput.value = message;
    
    // Validate message type and provide immediate feedback
    if (message.includes('الخيار')) {
        // Add visual feedback for option selection
        const quickBtns = document.querySelectorAll('.quick-btn');
        quickBtns.forEach(btn => {
            if (btn.textContent.includes(message.includes('الأول') ? 'الأول' : 'الثاني')) {
                btn.style.background = 'var(--success-color)';
                btn.style.color = 'white';
                setTimeout(() => {
                    btn.style.background = '';
                    btn.style.color = '';
                }, 1000);
            }
        });
    }
    
    handleSendMessage();
}

// Show/Hide typing indicator
function showTypingIndicator() {
    if (isTyping) return;
    
    isTyping = true;
    typingIndicator.classList.add('show');
    scrollToBottom();
}

function hideTypingIndicator() {
    isTyping = false;
    typingIndicator.classList.remove('show');
}

// Set input state (enabled/disabled)
function setInputState(enabled) {
    messageInput.disabled = !enabled;
    sendButton.disabled = !enabled;
    
    if (enabled) {
        messageInput.focus();
    }
}

// Handle errors
function handleError(error, originalMessage) {
    let errorMessage = 'عذراً، حدث خطأ في الاتصال. ';
    
    if (retryCount < CONFIG.MAX_RETRIES) {
        retryCount++;
        errorMessage += `جاري المحاولة مرة أخرى... (${retryCount}/${CONFIG.MAX_RETRIES})`;
        
        addMessage(errorMessage, 'bot');
        
        // Retry after delay
        setTimeout(() => {
            sendToRasa(originalMessage)
                .then(handleRasaResponse)
                .catch(err => handleError(err, originalMessage));
        }, CONFIG.RETRY_DELAY);
        
    } else {
        errorMessage += 'يرجى التحقق من الاتصال والمحاولة لاحقاً.';
        addMessage(errorMessage, 'bot');
        retryCount = 0;
    }
}

// Clear chat
function clearChat() {
    if (confirm('هل تريد مسح جميع الرسائل؟')) {
        // Keep only the welcome message
        const welcomeMessage = messagesContainer.querySelector('.bot-message');
        messagesContainer.innerHTML = '';
        messagesContainer.appendChild(welcomeMessage);
        
        // Clear localStorage
        localStorage.removeItem('chatHistory');
        
        // Reset state
        retryCount = 0;
        hideTypingIndicator();
        
        // Focus input
        messageInput.focus();
    }
}

// Reset all - Complete restart
function resetAll() {
    if (confirm('هل تريد إعادة تشغيل المحادثة بالكامل؟ سيتم مسح كل شيء وإعادة البدء.')) {
        // Show loading
        showLoading();
        
        // Reset Rasa session
        resetRasaSession()
            .then(() => {
                // Clear everything
                messagesContainer.innerHTML = '';
                
                // Add fresh welcome message
                addWelcomeMessage();
                
                // Clear localStorage
                localStorage.removeItem('chatHistory');
                
                // Reset all state
                retryCount = 0;
                hideTypingIndicator();
                
                // Hide loading
                hideLoading();
                
                // Focus input
                messageInput.focus();
                
                console.log('Complete reset successful');
            })
            .catch(error => {
                console.error('Reset failed:', error);
                hideLoading();
                addMessage('حدث خطأ في إعادة التشغيل. يرجى تحديث الصفحة.', 'bot');
            });
    }
}

// Reset Rasa session
async function resetRasaSession() {
    try {
        const response = await fetch(`${CONFIG.RASA_URL.replace('/webhooks/rest/webhook', '')}/conversations/${CONFIG.USER_ID}/tracker/events`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event: "restart"
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to reset session: ${response.status}`);
        }
        
        console.log('Rasa session reset successful');
        
    } catch (error) {
        console.error('Error resetting Rasa session:', error);
        // Continue anyway - the reset will still work locally
    }
}

// Add welcome message
function addWelcomeMessage() {
    const welcomeText = `مرحباً بك في وكالة السفر الذكية! 🌟<br>
كيف يمكنني مساعدتك اليوم؟<br><br>
يمكنني مساعدتك في:
<ul>
<li>✈️ حجز رحلات طيران</li>
<li>🏨 حجز فنادق</li>
<li>🎯 تخطيط رحلتك</li>
</ul>`;
    
    addMessage(welcomeText, 'bot');
}

// Show/Hide loading overlay
function showLoading() {
    if (loadingOverlay) {
        loadingOverlay.classList.add('show');
    }
}

function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.classList.remove('show');
    }
}

// Scroll to bottom
function scrollToBottom() {
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
}

// Get current time
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('ar-SA', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

// Set welcome message time
function setWelcomeTime() {
    const welcomeTimeElement = document.getElementById('welcomeTime');
    if (welcomeTimeElement) {
        welcomeTimeElement.textContent = getCurrentTime();
    }
}

// Save chat history to localStorage
function saveChatHistory() {
    const messages = Array.from(messagesContainer.children).map(msg => {
        const isUser = msg.classList.contains('user-message');
        const text = msg.querySelector('.message-text').textContent;
        const time = msg.querySelector('.message-time').textContent;
        
        return {
            sender: isUser ? 'user' : 'bot',
            text: text,
            time: time
        };
    });
    
    localStorage.setItem('chatHistory', JSON.stringify(messages));
}

// Load chat history from localStorage
function loadChatHistory() {
    const history = localStorage.getItem('chatHistory');
    if (!history) return;
    
    try {
        const messages = JSON.parse(history);
        
        // Clear current messages except welcome
        const welcomeMsg = messagesContainer.querySelector('.bot-message');
        messagesContainer.innerHTML = '';
        messagesContainer.appendChild(welcomeMsg);
        
        // Add saved messages
        messages.forEach(msg => {
            if (msg.sender && msg.text) {
                addMessage(msg.text, msg.sender);
            }
        });
        
        scrollToBottom();
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

// Connection status check
function checkConnection() {
    fetch(CONFIG.RASA_URL.replace('/webhooks/rest/webhook', '/'))
        .then(response => {
            if (response.ok) {
                document.querySelector('.status').className = 'status online';
                document.querySelector('.status').textContent = 'متصل';
            } else {
                throw new Error('Connection failed');
            }
        })
        .catch(() => {
            document.querySelector('.status').className = 'status offline';
            document.querySelector('.status').textContent = 'غير متصل';
        });
}

// Check connection every 30 seconds
setInterval(checkConnection, 30000);

// Initial connection check
checkConnection();

// Handle page visibility change
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Page became visible, check connection
        checkConnection();
        messageInput.focus();
    }
});

// Error handling for uncaught errors
window.addEventListener('error', function(e) {
    console.error('Uncaught error:', e.error);
});

// Service Worker registration (optional, for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment if you want to add service worker
        // navigator.serviceWorker.register('/sw.js');
    });
}