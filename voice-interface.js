// Voice Interface Manager for Voice Messaging System
// Full implementation with Web Speech API and MediaRecorder

class VoiceInterface {
    constructor() {
        this.recognition = null;
        this.synthesis = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isListening = false;
        this.isRecording = false;
        this.currentStream = null;

        this.init();
    }

    init() {
        // Initialize Web Speech API
        this.initSpeechRecognition();
        this.initSpeechSynthesis();

        // Add global voice commands
        this.setupGlobalCommands();
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                this.isListening = true;
                console.log('Voice recognition started');
            };

            this.recognition.onend = () => {
                this.isListening = false;
                console.log('Voice recognition ended');
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isListening = false;
            };

            console.log('Speech recognition initialized');
        } else {
            console.warn('Speech recognition not supported in this browser');
        }
    }

    initSpeechSynthesis() {
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
            console.log('Speech synthesis initialized');
        } else {
            console.warn('Speech synthesis not supported in this browser');
        }
    }

    setupGlobalCommands() {
        // Add keyboard shortcuts for accessibility
        document.addEventListener('keydown', (e) => {
            // Ctrl + Shift + V for voice commands
            if (e.ctrlKey && e.shiftKey && e.key === 'V') {
                e.preventDefault();
                this.startVoiceCommand();
            }

            // Ctrl + Shift + R for recording
            if (e.ctrlKey && e.shiftKey && e.key === 'R') {
                e.preventDefault();
                if (this.isRecording) {
                    this.stopRecording();
                } else {
                    this.startRecording();
                }
            }
        });
    }

    speakText(text, options = {}) {
        if (!this.synthesis) {
            console.warn('Speech synthesis not available');
            return Promise.reject('Speech synthesis not available');
        }

        return new Promise((resolve, reject) => {
            // Cancel any ongoing speech
            this.synthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);

            // Set voice properties
            utterance.rate = options.rate || 1;
            utterance.pitch = options.pitch || 1;
            utterance.volume = options.volume || 1;

            // Try to use a female voice for better accessibility
            const voices = this.synthesis.getVoices();
            const femaleVoice = voices.find(voice =>
                voice.name.toLowerCase().includes('female') ||
                voice.name.toLowerCase().includes('woman') ||
                voice.name.toLowerCase().includes('zira') ||
                voice.name.toLowerCase().includes('hazel')
            );

            if (femaleVoice) {
                utterance.voice = femaleVoice;
            }

            utterance.onend = () => resolve();
            utterance.onerror = (event) => reject(event.error);

            this.synthesis.speak(utterance);
        });
    }

    startVoiceCommand() {
        if (!this.recognition || this.isListening) {
            return;
        }

        this.speakText('Listening for voice command. Say login, register, compose, inbox, or help.');

        this.recognition.onresult = (event) => {
            const command = event.results[0][0].transcript.toLowerCase().trim();
            console.log('Voice command received:', command);

            this.processVoiceCommand(command);
        };

        setTimeout(() => {
            this.recognition.start();
        }, 2000); // Wait for speech to finish
    }

    processVoiceCommand(command) {
        if (command.includes('login') || command.includes('sign in')) {
            this.speakText('Navigating to login page');
            setTimeout(() => window.location.href = '/login', 1000);
        } else if (command.includes('register') || command.includes('sign up')) {
            this.speakText('Navigating to registration page');
            setTimeout(() => window.location.href = '/register', 1000);
        } else if (command.includes('compose') || command.includes('new message')) {
            this.speakText('Navigating to compose message');
            setTimeout(() => window.location.href = '/compose', 1000);
        } else if (command.includes('inbox') || command.includes('messages')) {
            this.speakText('Navigating to inbox');
            setTimeout(() => window.location.href = '/inbox', 1000);
        } else if (command.includes('dashboard') || command.includes('home')) {
            this.speakText('Navigating to dashboard');
            setTimeout(() => window.location.href = '/dashboard', 1000);
        } else if (command.includes('help')) {
            this.speakText('Available commands: login, register, compose, inbox, dashboard. Press Control Shift V for voice commands, or Control Shift R to start recording.');
        } else {
            this.speakText('Command not recognized. Say help for available commands.');
        }
    }

    async startRecording() {
        if (this.isRecording) {
            console.log('Already recording');
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });

            this.currentStream = stream;
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.handleRecordingComplete(audioBlob);
            };

            this.mediaRecorder.start();
            this.isRecording = true;

            console.log('Recording started');
            this.speakText('Recording started. Speak your message now.');

            return true;
        } catch (error) {
            console.error('Error starting recording:', error);
            this.speakText('Error accessing microphone. Please check your microphone permissions.');
            return false;
        }
    }

    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) {
            console.log('Not currently recording');
            return;
        }

        this.mediaRecorder.stop();
        this.isRecording = false;

        // Stop all tracks
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
            this.currentStream = null;
        }

        console.log('Recording stopped');
        this.speakText('Recording stopped. Converting speech to text.');
    }

    async handleRecordingComplete(audioBlob) {
        // Trigger custom event for other components to handle
        const event = new CustomEvent('voiceRecordingComplete', {
            detail: { audioBlob }
        });
        document.dispatchEvent(event);

        // If we're on the compose page, automatically convert to text
        if (window.location.pathname === '/compose') {
            await this.convertAudioToText(audioBlob);
        }
    }

    async convertAudioToText(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            const sessionToken = localStorage.getItem('session_token');
            if (!sessionToken) {
                this.speakText('Please log in to use speech recognition.');
                return;
            }

            this.speakText('Converting speech to text. Please wait.');

            const response = await fetch('/api/speech/recognize', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${sessionToken}`
                },
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // Fill in the message content if we're on compose page
                const messageContent = document.getElementById('messageContent');
                if (messageContent) {
                    messageContent.value = result.text;
                    messageContent.focus();
                }

                this.speakText(`Speech converted successfully. The text is: ${result.text}`);

                // Trigger custom event
                const event = new CustomEvent('speechToTextComplete', {
                    detail: { text: result.text, confidence: result.confidence }
                });
                document.dispatchEvent(event);

            } else {
                console.error('Speech recognition failed:', result.error);
                this.speakText(`Speech recognition failed: ${result.error.message}`);
            }
        } catch (error) {
            console.error('Error converting speech to text:', error);
            this.speakText('Error converting speech to text. Please try again.');
        }
    }

    // Voice-enabled form filling
    async fillFormWithVoice(fieldName, prompt) {
        if (!this.recognition) {
            this.speakText('Voice input not available');
            return null;
        }

        return new Promise((resolve) => {
            this.speakText(prompt);

            this.recognition.onresult = (event) => {
                const text = event.results[0][0].transcript.trim();
                resolve(text);
            };

            setTimeout(() => {
                this.recognition.start();
            }, 2000);
        });
    }

    // Check if voice features are available
    isVoiceAvailable() {
        return {
            speechRecognition: !!this.recognition,
            speechSynthesis: !!this.synthesis,
            mediaRecorder: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
        };
    }
}

// Initialize voice interface when page loads
document.addEventListener('DOMContentLoaded', function () {
    window.voiceInterface = new VoiceInterface();

    // Announce page load and available shortcuts
    setTimeout(() => {
        if (window.voiceInterface) {
            const pageName = document.title.split(' - ')[0] || 'Voice Messaging System';
            window.voiceInterface.speakText(
                `${pageName} loaded. Press Control Shift V for voice commands, or Control Shift R to start recording. All buttons and links are accessible via keyboard navigation.`
            );
        }
    }, 1000);
});