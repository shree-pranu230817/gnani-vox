/**
 * UZHAVAR AI – Kannada Voice Bridge
 * Centralized Audio State & Voice Pipeline Controller
 * Handles: Microphone Priority, 5-Stage Visual Progress, Audio Interruption,
 *          Tap-to-Speak, Hands-Free VAD, Latency Profiling.
 */

const AudioState = {
    IDLE: 'IDLE',
    LISTENING: 'LISTENING',
    RECORDING: 'RECORDING',
    TRANSCRIBING: 'TRANSCRIBING',
    THINKING: 'THINKING',
    GENERATING_AUDIO: 'GENERATING_AUDIO',
    SPEAKING: 'SPEAKING',
    INTERRUPTED: 'INTERRUPTED',
    ERROR: 'ERROR'
};

class CentralAudioController {
    constructor() {
        this.state = AudioState.IDLE;
        this.audioPlayer = new Audio();
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioStream = null;
        this.audioContext = null;
        this.analyser = null;

        this.handsFreeEnabled = false;
        this.isInterrupted = false;

        this.currentRequestId = 0;
        this.currentAbortController = null;

        this.silenceThresholdMs = 1200; // Optimized silence detection
        this.minSpeechDurationMs = 500;  // Filter out accidental clicks
        this.recordingStartTime = 0;

        this.stateListeners = [];
        this.speechRecognition = null;
        this.liveTranscript = "";

        this.initAudioPlayer();
        this.initSpeechRecognition();
    }

    onStateChange(callback) {
        this.stateListeners.push(callback);
    }

    setState(newState, details = {}) {
        this.state = newState;
        console.log(`[AudioController State] -> ${newState}`, details);
        this.stateListeners.forEach(fn => fn(newState, details));
    }

    initAudioPlayer() {
        this.audioPlayer.addEventListener('ended', () => {
            if (this.state === AudioState.SPEAKING) {
                this.setState(AudioState.IDLE, { message: 'Audio playback finished' });
                if (this.handsFreeEnabled) {
                    this.startHandsFreeListening();
                }
            }
        });

        this.audioPlayer.addEventListener('error', (e) => {
            console.warn('[AudioController] Audio element error:', e);
            if (this.state === AudioState.SPEAKING) {
                this.setState(AudioState.IDLE);
            }
        });
    }

    initSpeechRecognition() {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SR) {
            try {
                this.speechRecognition = new SR();
                this.speechRecognition.continuous = true;
                this.speechRecognition.interimResults = true;
            } catch (e) {
                console.warn('[AudioController] SpeechRecognition init warning:', e);
            }
        }
    }

    /* =========================================================================
       CRITICAL: MICROPHONE PRIORITY & IMMEDIATE PLAYBACK INTERRUPTION
       ========================================================================= */
    interruptCurrentPlayback() {
        let interruptedSomething = false;

        // 1. Stop HTML5 audio element immediately
        if (this.audioPlayer && !this.audioPlayer.paused) {
            this.audioPlayer.pause();
            this.audioPlayer.currentTime = 0;
            this.audioPlayer.src = "";
            interruptedSomething = true;
        }

        // 2. Stop browser SpeechSynthesis
        if ('speechSynthesis' in window && window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            interruptedSomething = true;
        }

        // 3. Abort any in-flight fetch requests for audio synthesis/translation
        if (this.currentAbortController) {
            this.currentAbortController.abort();
            this.currentAbortController = null;
            interruptedSomething = true;
        }

        if (interruptedSomething || this.state === AudioState.SPEAKING || this.state === AudioState.GENERATING_AUDIO) {
            this.isInterrupted = true;
            this.setState(AudioState.INTERRUPTED, { message: 'AI speech interrupted by user speech' });
            console.log('[AudioController] ⚡ Interrupted current AI playback/generation!');
        }
    }

    /* =========================================================================
       MODE 1: TAP TO SPEAK
       ========================================================================= */
    async startTapToSpeak(onAudioReady, lang = 'kn-IN') {
        // Microphone priority: immediately halt any AI speech
        this.interruptCurrentPlayback();

        // Increment request ID to invalidate stale responses
        this.currentRequestId++;
        const reqId = this.currentRequestId;
        this.currentAbortController = new AbortController();
        this.liveTranscript = "";

        // Start concurrent client speech recognition if available
        if (this.speechRecognition) {
            try {
                this.speechRecognition.lang = lang;
                this.speechRecognition.onresult = (ev) => {
                    let full = "";
                    for (let i = 0; i < ev.results.length; ++i) {
                        full += ev.results[i][0].transcript + " ";
                    }
                    this.liveTranscript = full.trim();
                };
                this.speechRecognition.start();
            } catch (e) {
                // Ignore if already active
            }
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            this.audioStream = stream;
            this.audioChunks = [];
            this.recordingStartTime = Date.now();

            this.mediaRecorder = new MediaRecorder(stream, { mimeType: this.getSupportedMimeType() });

            this.mediaRecorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) {
                    this.audioChunks.push(e.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                const duration = Date.now() - this.recordingStartTime;
                this.releaseStream();

                if (this.speechRecognition) {
                    try { this.speechRecognition.stop(); } catch (e) {}
                }

                if (duration < this.minSpeechDurationMs) {
                    this.setState(AudioState.IDLE, { message: 'ಧ್ವನಿ ತುಂಬಾ ಚಿಕ್ಕದಾಗಿದೆ (Recording too short)' });
                    return;
                }

                const mimeType = this.mediaRecorder ? this.mediaRecorder.mimeType : 'audio/webm';
                const audioBlob = new Blob(this.audioChunks, { type: mimeType });
                console.log(`[AudioController] Audio captured: ${audioBlob.size} bytes (${duration}ms)`);

                if (reqId === this.currentRequestId && onAudioReady) {
                    onAudioReady(audioBlob, reqId, this.liveTranscript, duration);
                }
            };

            this.mediaRecorder.start(250); // Slice into 250ms chunks
            this.setState(AudioState.RECORDING, { message: 'ನಿಮ್ಮ ಧ್ವನಿಯನ್ನು ಆಲಿಸಲಾಗುತ್ತಿದೆ... (Listening...)' });

        } catch (err) {
            console.warn('[AudioController] getUserMedia error, falling back to Web Speech:', err);
            this.fallbackToWebSpeech(onAudioReady, lang, reqId);
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            try {
                this.mediaRecorder.stop();
            } catch (e) {
                console.warn('[AudioController] Error stopping mediaRecorder:', e);
            }
        }
        if (this.speechRecognition) {
            try { this.speechRecognition.stop(); } catch (e) {}
        }
    }

    fallbackToWebSpeech(onAudioReady, lang, reqId) {
        if (!this.speechRecognition) {
            this.setState(AudioState.ERROR, { message: 'ಮೈಕ್ರೋಫೋನ್ ಅನುಮತಿ ಲಭ್ಯವಿಲ್ಲ (Microphone not accessible).' });
            return;
        }

        try {
            this.speechRecognition.lang = lang;
            this.setState(AudioState.RECORDING, { message: 'ಆಲಿಸಲಾಗುತ್ತಿದೆ (Listening with Web Speech)...' });

            this.speechRecognition.onresult = (event) => {
                const text = event.results[0][0].transcript.trim();
                this.setState(AudioState.IDLE);
                if (reqId === this.currentRequestId && onAudioReady) {
                    onAudioReady(null, reqId, text, 1000);
                }
            };

            this.speechRecognition.onerror = (e) => {
                this.setState(AudioState.ERROR, { message: `Speech recognition error: ${e.error}` });
            };

            this.speechRecognition.start();
        } catch (e) {
            this.setState(AudioState.ERROR, { message: 'Could not start speech recognition' });
        }
    }

    /* =========================================================================
       MODE 2: HANDS-FREE CONVERSATION WITH VAD
       ========================================================================= */
    async enableHandsFree(onSpeechDetectedAndCaptured, lang = 'kn-IN') {
        this.handsFreeEnabled = true;
        this.startHandsFreeListening(onSpeechDetectedAndCaptured, lang);
    }

    disableHandsFree() {
        this.handsFreeEnabled = false;
        this.releaseStream();
        if (this.state === AudioState.LISTENING) {
            this.setState(AudioState.IDLE, { message: 'Hands-free mode disabled' });
        }
    }

    async startHandsFreeListening(onSpeechDetectedAndCaptured, lang = 'kn-IN') {
        if (!this.handsFreeEnabled) return;
        if (this.state === AudioState.RECORDING || this.state === AudioState.TRANSCRIBING) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            this.audioStream = stream;

            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioCtx();
            const source = this.audioContext.createMediaStreamSource(stream);
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 512;
            source.connect(this.analyser);

            this.setState(AudioState.LISTENING, { message: 'ಹ್ಯಾಂಡ್ಸ್-ಫ್ರೀ ಸಕ್ರಿಯವಾಗಿದೆ – ಮಾತನಾಡಿ (Hands-free active)' });

            const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            let speechActive = false;

            const checkAudio = () => {
                if (!this.handsFreeEnabled || this.state === AudioState.RECORDING) return;

                this.analyser.getByteFrequencyData(dataArray);
                let sum = 0;
                for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
                const avgVolume = sum / dataArray.length;

                if (avgVolume > 26) {
                    if (!speechActive) {
                        speechActive = true;
                        console.log('[AudioController VAD] User speech detected!');
                        this.interruptCurrentPlayback();
                        this.startTapToSpeak(onSpeechDetectedAndCaptured, lang);
                    }
                }

                if (this.handsFreeEnabled && this.state === AudioState.LISTENING) {
                    requestAnimationFrame(checkAudio);
                }
            };

            requestAnimationFrame(checkAudio);

        } catch (e) {
            console.warn('[AudioController] Hands-free VAD not supported on this device:', e);
            this.disableHandsFree();
        }
    }

    /* =========================================================================
       AUDIO PLAYBACK (GNANI TIMBRE + BROWSER FALLBACK) WITH STARTUP PROFILING
       ========================================================================= */
    playAudio(audioBase64, fallbackText, lang = 'kn-IN', onFinished = null, onPlaybackStarted = null) {
        const tPlayReq = performance.now();
        this.interruptCurrentPlayback();

        const reqId = ++this.currentRequestId;
        this.setState(AudioState.SPEAKING, { message: 'AI ಮಾತನಾಡುತ್ತಿದೆ (AI is speaking...)' });

        if (audioBase64) {
            const onPlayingHandler = () => {
                const startupMs = Math.round(performance.now() - tPlayReq);
                console.log(`🔊 [AudioController] Timbre audio playback started in ${startupMs}ms`);
                if (onPlaybackStarted) onPlaybackStarted(startupMs);
                this.audioPlayer.removeEventListener('playing', onPlayingHandler);
            };
            this.audioPlayer.addEventListener('playing', onPlayingHandler);
            this.audioPlayer.src = `data:audio/wav;base64,${audioBase64}`;
            this.audioPlayer.play()
                .catch(err => {
                    console.warn('[AudioController] Timbre audio play failed, falling back to Web Speech:', err);
                    this.playBrowserSpeech(fallbackText, lang, reqId, onFinished, onPlaybackStarted, tPlayReq);
                });
        } else {
            this.playBrowserSpeech(fallbackText, lang, reqId, onFinished, onPlaybackStarted, tPlayReq);
        }
    }

    playBrowserSpeech(text, lang, reqId, onFinished, onPlaybackStarted, tPlayReq) {
        if (!('speechSynthesis' in window) || !text) {
            this.setState(AudioState.IDLE);
            if (onFinished) onFinished();
            return;
        }

        window.speechSynthesis.cancel();
        const clean = text.replace(/[*#_`>]/g, ' ').replace(/\s+/g, ' ').trim();
        const utterance = new SpeechSynthesisUtterance(clean);
        utterance.lang = lang;
        utterance.rate = 1.0;

        utterance.onstart = () => {
            const startupMs = Math.round(performance.now() - (tPlayReq || performance.now()));
            console.log(`🔊 [AudioController] Web Speech synthesis started in ${startupMs}ms`);
            if (onPlaybackStarted) onPlaybackStarted(startupMs);
        };

        utterance.onend = () => {
            if (reqId === this.currentRequestId) {
                this.setState(AudioState.IDLE);
                if (onFinished) onFinished();
                if (this.handsFreeEnabled) this.startHandsFreeListening();
            }
        };

        utterance.onerror = () => {
            if (reqId === this.currentRequestId) {
                this.setState(AudioState.IDLE);
                if (onFinished) onFinished();
            }
        };

        window.speechSynthesis.speak(utterance);
    }

    /* =========================================================================
       RESOURCE CLEANUP
       ========================================================================= */
    releaseStream() {
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(t => t.stop());
            this.audioStream = null;
        }
        if (this.audioContext && this.audioContext.state !== 'closed') {
            try { this.audioContext.close(); } catch (e) {}
            this.audioContext = null;
        }
    }

    getSupportedMimeType() {
        const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/wav'];
        for (const t of types) {
            if (MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)) {
                return t;
            }
        }
        return 'audio/webm';
    }
}

// Global Singleton Instance
window.centralAudioController = new CentralAudioController();
