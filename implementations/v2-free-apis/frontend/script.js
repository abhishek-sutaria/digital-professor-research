/*
AI AVATAR - FRONTEND JAVASCRIPT

This handles all user interactions and communication with the backend:
1. Captures user input
2. Sends request to Flask backend
3. Displays loading state
4. Shows the avatar video when ready
*/

// Configuration
const API_BASE_URL = 'http://localhost:5001/api';

// Get DOM elements
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const submitBtn = document.getElementById('submitBtn');
const submitText = document.getElementById('submitText');
const micBtn = document.getElementById('micBtn');
const micIcon = document.getElementById('micIcon');
const recordingIndicator = document.getElementById('recordingIndicator');

const videoPlaceholder = document.getElementById('videoPlaceholder');
const loadingState = document.getElementById('loadingState');
const avatarVideo = document.getElementById('avatarVideo');
const responseText = document.getElementById('responseText');
const responseContent = document.getElementById('responseContent');

const exampleBtns = document.querySelectorAll('.example-btn');

// Voice recognition variables
let recognition = null;
let isRecording = false;
let recognitionTimeout = null;

/**
 * MAIN FUNCTION: Handle form submission
 * 
 * This is called when the user clicks "Ask" or presses Enter
 */
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent page reload
    
    const message = userInput.value.trim();
    
    if (!message) {
        alert('Please enter a question!');
        return;
    }
    
    // Send the message to get avatar response
    await getAvatarResponse(message);
});

/**
 * Get avatar response from backend
 * 
 * Flow:
 * 1. Show loading state
 * 2. Call backend API
 * 3. Wait for video to be generated
 * 4. Display the video
 */
async function getAvatarResponse(message) {
    try {
        // Step 1: Show loading state
        showLoadingState();
        disableInput();
        
        console.log('📤 Sending message to backend:', message);
        
        // Step 2: Call the backend API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('📥 Received response:', data);
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to generate response');
        }
        
        // Step 3: Display the response (with or without video)
        if (data.status === 'text_only') {
            displayTextOnlyResponse(data.ai_response, data.message);
        } else if (data.video_url) {
            displayAvatarVideo(data.video_url, data.ai_response);
        } else {
            // Fallback to text if no video URL
            displayTextOnlyResponse(data.ai_response, 'Video generation in progress...');
        }
        
        // Clear the input
        userInput.value = '';
        
    } catch (error) {
        console.error('❌ Error:', error);
        showError(error.message);
    } finally {
        // Re-enable input
        enableInput();
    }
}

/**
 * Display the avatar video
 */
function displayAvatarVideo(videoUrl, responseTextContent) {
    // Hide loading and placeholder
    loadingState.classList.add('hidden');
    videoPlaceholder.classList.add('hidden');
    
    // Show video
    avatarVideo.src = videoUrl;
    avatarVideo.classList.remove('hidden');
    
    // Show response text
    responseContent.textContent = responseTextContent;
    responseText.classList.remove('hidden');
    
    console.log('✅ Video ready to play!');
}

/**
 * Display text-only response (test mode)
 */
function displayTextOnlyResponse(responseTextContent, note) {
    // Hide loading and placeholder
    loadingState.classList.add('hidden');
    videoPlaceholder.classList.add('hidden');
    
    // Hide video player
    avatarVideo.classList.add('hidden');
    
    // Show response text with note
    responseContent.innerHTML = `
        <strong>🎭 Professor Jenniel's Response:</strong><br><br>
        ${responseTextContent}<br><br>
        <em style="color: #667eea;">${note || ''}</em>
    `;
    responseText.classList.remove('hidden');
    
    console.log('✅ Text response ready!');
}

/**
 * Show loading state
 */
function showLoadingState() {
    videoPlaceholder.classList.add('hidden');
    avatarVideo.classList.add('hidden');
    responseText.classList.add('hidden');
    loadingState.classList.remove('hidden');
}

/**
 * Show error message
 */
function showError(message) {
    loadingState.classList.add('hidden');
    videoPlaceholder.classList.remove('hidden');
    
    // Show error in an alert (you could make this prettier)
    alert(`Error: ${message}\n\nPlease try again or check the console for details.`);
}

/**
 * Disable input while processing
 */
function disableInput() {
    userInput.disabled = true;
    submitBtn.disabled = true;
    submitText.textContent = 'Processing...';
}

/**
 * Enable input after processing
 */
function enableInput() {
    userInput.disabled = false;
    submitBtn.disabled = false;
    submitText.textContent = 'Ask';
}

/**
 * Handle example question buttons
 */
exampleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.getAttribute('data-question');
        userInput.value = question;
        userInput.focus();
    });
});

/* ========================================
   VOICE INPUT FUNCTIONALITY
   ======================================== */

/**
 * Initialize Web Speech API
 */
function initializeSpeechRecognition() {
    // Check if browser supports Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.warn('⚠️ Web Speech API not supported in this browser');
        micBtn.disabled = true;
        micBtn.title = 'Voice input not supported in this browser. Please use Chrome or Edge.';
        micIcon.textContent = '🎤❌';
        return false;
    }
    
    // Create recognition instance
    recognition = new SpeechRecognition();
    recognition.continuous = false; // Stop after one result
    recognition.interimResults = true; // Show interim results while speaking
    recognition.lang = 'en-US'; // Set language
    
    // Handle recognition results
    recognition.onresult = (event) => {
        let transcript = '';
        
        // Get the latest transcript
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        
        // Update input field with recognized text
        userInput.value = transcript;
        console.log('🎤 Recognized:', transcript);
    };
    
    // Handle recognition end
    recognition.onend = () => {
        console.log('🎤 Recognition ended');
        
        // If we released the button (not recording anymore), send the message
        if (!isRecording) {
            const message = userInput.value.trim();
            if (message) {
                console.log('📤 Auto-sending voice message:', message);
                getAvatarResponse(message);
            }
        }
    };
    
    // Handle errors
    recognition.onerror = (event) => {
        console.error('🎤 Recognition error:', event.error);
        stopRecording();
        
        if (event.error === 'not-allowed' || event.error === 'permission-denied') {
            alert('Microphone access denied. Please allow microphone access in your browser settings.');
        } else if (event.error === 'no-speech') {
            console.log('No speech detected. Please try again.');
        } else if (event.error !== 'aborted') {
            alert(`Speech recognition error: ${event.error}`);
        }
    };
    
    console.log('✅ Speech recognition initialized');
    return true;
}

/**
 * Start voice recording (called when button is pressed)
 */
function startRecording() {
    if (!recognition) {
        alert('Voice input not available. Please use Chrome or Edge browser.');
        return;
    }
    
    if (isRecording) return; // Already recording
    
    try {
        isRecording = true;
        
        // Visual feedback
        micBtn.classList.add('recording');
        recordingIndicator.classList.remove('hidden');
        
        // Clear previous input
        userInput.value = '';
        
        // Start recognition
        recognition.start();
        console.log('🎤 Recording started...');
        
    } catch (error) {
        console.error('Error starting recording:', error);
        stopRecording();
    }
}

/**
 * Stop voice recording (called when button is released)
 */
function stopRecording() {
    if (!isRecording) return;
    
    isRecording = false;
    
    // Visual feedback
    micBtn.classList.remove('recording');
    recordingIndicator.classList.add('hidden');
    
    // Stop recognition
    try {
        recognition.stop();
        console.log('🎤 Recording stopped');
    } catch (error) {
        console.error('Error stopping recording:', error);
    }
}

/**
 * Set up microphone button event listeners
 * Supports both mouse and touch events for mobile
 */
function setupMicrophoneButton() {
    // Mouse events (desktop)
    micBtn.addEventListener('mousedown', (e) => {
        e.preventDefault();
        startRecording();
    });
    
    micBtn.addEventListener('mouseup', () => {
        stopRecording();
    });
    
    micBtn.addEventListener('mouseleave', () => {
        // Stop if user drags mouse away from button
        if (isRecording) {
            stopRecording();
        }
    });
    
    // Touch events (mobile)
    micBtn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startRecording();
    });
    
    micBtn.addEventListener('touchend', (e) => {
        e.preventDefault();
        stopRecording();
    });
    
    micBtn.addEventListener('touchcancel', () => {
        stopRecording();
    });
    
    console.log('✅ Microphone button events set up');
}

/**
 * Health check on page load
 * 
 * This verifies the backend is running when the page loads
 */
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('✅ Backend health check:', data.message);
    } catch (error) {
        console.warn('⚠️ Backend not responding. Make sure the Flask server is running!');
        console.warn('Run: cd backend && python app.py');
    }
}

// Initialize everything when page loads
window.addEventListener('load', () => {
    checkBackendHealth();
    
    // Initialize voice input
    if (initializeSpeechRecognition()) {
        setupMicrophoneButton();
        console.log('🎤 Voice input ready!');
    } else {
        console.log('⚠️ Voice input not available - text input only');
    }
});

console.log('🎭 AI Avatar Frontend loaded successfully!');

