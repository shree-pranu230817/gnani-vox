/**
 * UZHAVAR AI VOICE ASSISTANT CLIENT ENGINE
 * Integrates:
 * 1. Prisma (Speech-to-Text / ASR)
 * 2. Reasoning Model (uzhavar-agri-reasoner-v1.0 / configured Evon)
 * 3. Timbre (Text-to-Speech / TTS)
 */

class GnaniAssistant {
    constructor() {
        this.isOpen = false;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.speechRecognition = null;
        this.audioPlayer = new Audio();
        this.demoIndex = 0;
        this.sessionId = localStorage.getItem('uzhavar_session_id') || ('sess_' + Math.random().toString(36).substring(2, 12));
        localStorage.setItem('uzhavar_session_id', this.sessionId);
        
        this.initElements();
        this.initEvents();
        this.initSpeechEngine();
    }

    initElements() {
        this.launcherBtn = document.getElementById('gnaniLauncherBtn');
        this.modalOverlay = document.getElementById('gnaniModalOverlay');
        this.closeBtn = document.getElementById('gnaniCloseBtn');
        this.chatBody = document.getElementById('gnaniChatBody');
        this.micBtn = document.getElementById('gnaniMicBtn');
        this.statusText = document.getElementById('gnaniStatusText');
        this.textInput = document.getElementById('gnaniTextInput');
        this.sendBtn = document.getElementById('gnaniSendBtn');
        this.demoBtn = document.getElementById('gnaniRunDemoBtn');
        this.stepPrisma = document.getElementById('stepPrisma');
        this.stepEvon = document.getElementById('stepEvon');
        this.stepTimbre = document.getElementById('stepTimbre');
        this.langSelect = document.getElementById('gnaniLangSelect');
        this.resetBtn = document.getElementById('gnaniResetBtn');
    }

    initEvents() {
        if (this.launcherBtn) {
            this.launcherBtn.addEventListener('click', () => this.open());
        }
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.close());
        }
        if (this.resetBtn) {
            this.resetBtn.addEventListener('click', () => this.resetConversationMemory());
        }
        if (this.modalOverlay) {
            this.modalOverlay.addEventListener('click', (e) => {
                if (e.target === this.modalOverlay) this.close();
            });
        }
        if (this.micBtn) {
            this.micBtn.addEventListener('click', () => this.toggleVoiceRecording());
        }
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendTextMessage());
        }
        if (this.textInput) {
            this.textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendTextMessage();
            });
        }
        if (this.demoBtn) {
            this.demoBtn.addEventListener('click', () => this.runCompetitionDemoLoop());
        }
        if (this.langSelect) {
            this.langSelect.addEventListener('change', () => {
                const currentLang = this.getCurrentLang();
                const bcp47 = this.getBcp47(currentLang);
                console.log(`[STAGE: LANG_SELECT] UI Language switched to: ${currentLang} (${bcp47})`);
                if (this.statusText) {
                    const selText = this.langSelect.options[this.langSelect.selectedIndex].text.trim();
                    this.statusText.textContent = `Language switched to ${selText}. Tap mic to speak or type below.`;
                }
            });
        }
    }

    getBcp47(lang = null) {
        const l = (lang || this.getCurrentLang()).toLowerCase().trim();
        const map = {
            'en': 'en-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'hi': 'hi-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',
            'bn': 'bn-IN',
            'mr': 'mr-IN',
            'gu': 'gu-IN',
            'pa': 'pa-IN'
        };
        return map[l] || (l.includes('-') ? l : 'en-IN');
    }

    initSpeechEngine() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.speechRecognition = new SpeechRecognition();
            this.speechRecognition.continuous = false;
            this.speechRecognition.interimResults = false;

            this.speechRecognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript.trim();
                console.log(`[STAGE: PRISMA_STT] Web Speech API recognized transcript: '${transcript}'`);
                this.stopVoiceRecording();
                if (transcript) {
                    this.addMessage(transcript, 'user');
                    this.processEvonAndTimbre(transcript);
                } else {
                    this.addErrorMessage("Could not transcribe speech. Please speak clearly into your microphone.");
                }
            };

            this.speechRecognition.onerror = (event) => {
                console.warn('[STAGE: PRISMA_STT] Speech recognition event error:', event.error);
                this.stopVoiceRecording();
                if (event.error !== 'no-speech') {
                    this.addErrorMessage(`Speech Recognition Notice (${event.error}). You can also type your question below.`);
                }
                this.statusText.textContent = "Voice input ready. Tap mic to speak or type below.";
            };

            this.speechRecognition.onend = () => {
                if (this.isRecording) {
                    this.stopVoiceRecording();
                }
            };
        }
    }

    resetConversationMemory() {
        console.log("[GnaniAssistant] Resetting conversation memory...");
        fetch('/api/gnani/reset-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: this.sessionId })
        })
        .then(() => {
            this.sessionId = 'sess_' + Math.random().toString(36).substring(2, 12);
            localStorage.setItem('uzhavar_session_id', this.sessionId);
            this.chatBody.innerHTML = '';
            this.addMessage("🌾 Conversation memory has been cleared. How can I assist with your farming today?", 'bot');
            this.statusText.textContent = "New consultation started. Tap mic to speak or type below.";
        })
        .catch(err => {
            console.warn("Failed to reset session on server:", err);
            this.sessionId = 'sess_' + Math.random().toString(36).substring(2, 12);
            localStorage.setItem('uzhavar_session_id', this.sessionId);
            this.chatBody.innerHTML = '';
            this.addMessage("🌾 New consultation session started.", 'bot');
        });
    }

    open() {
        if (this.modalOverlay) {
            this.modalOverlay.classList.add('open');
            this.isOpen = true;
            if (this.textInput) this.textInput.focus();
        }
    }

    close() {
        if (this.modalOverlay) {
            this.modalOverlay.classList.remove('open');
            this.isOpen = false;
            this.stopVoiceRecording();
            this.stopAudio();
        }
    }

    getCurrentLang() {
        if (this.langSelect) {
            return this.langSelect.value;
        }
        return document.documentElement.lang || 'en';
    }

    toggleVoiceRecording() {
        if (this.isRecording) {
            this.stopVoiceRecording();
        } else {
            this.startVoiceRecording();
        }
    }

    startVoiceRecording() {
        this.isRecording = true;
        this.micBtn.classList.add('recording');
        this.highlightStep('prisma');

        const lang = this.getCurrentLang();
        const bcp47 = this.getBcp47(lang);
        this.statusText.textContent = `🎙️ Prisma Listening (${bcp47})... Speak your agricultural query now`;

        console.log(`[STAGE: PRISMA_STT] Starting voice recording with language: ${bcp47}`);

        if (this.speechRecognition) {
            try {
                this.speechRecognition.lang = bcp47;
                this.speechRecognition.start();
                return;
            } catch (e) {
                console.warn("[STAGE: PRISMA_STT] SpeechRecognition start fallback to MediaRecorder:", e);
            }
        }

        // MediaStream recording fallback
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    this.mediaRecorder = new MediaRecorder(stream);
                    this.audioChunks = [];
                    this.mediaRecorder.ondataavailable = e => this.audioChunks.push(e.data);
                    this.mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                        this.sendAudioToPrisma(audioBlob);
                    };
                    this.mediaRecorder.start();
                })
                .catch(err => {
                    console.error("[STAGE: PRISMA_STT] Microphone access error:", err);
                    this.addErrorMessage("Microphone access was denied or is unavailable on this device. Please type your question.");
                    this.statusText.textContent = "Microphone access blocked.";
                    this.stopVoiceRecording();
                });
        }
    }

    stopVoiceRecording() {
        this.isRecording = false;
        if (this.micBtn) this.micBtn.classList.remove('recording');
        if (this.statusText) this.statusText.textContent = "Voice input ready. Tap mic to speak.";
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        if (this.speechRecognition) {
            try { this.speechRecognition.stop(); } catch (e) {}
        }
    }

    sendAudioToPrisma(audioBlob) {
        const lang = this.getCurrentLang();
        const bcp47 = this.getBcp47(lang);
        this.highlightStep('prisma');
        this.statusText.textContent = `⚙️ Prisma STT processing audio (${bcp47})...`;

        console.log(`[STAGE: PRISMA_STT] Submitting ${audioBlob.size} bytes audio for language ${bcp47}`);

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('language', lang);

        fetch('/api/gnani/stt', {
            method: 'POST',
            body: formData
        })
        .then(async res => {
            const data = await res.json().catch(() => ({}));
            if (!res.ok || !data.success) {
                throw new Error(data.error || data.message || `Prisma STT request failed (${res.status})`);
            }
            return data;
        })
        .then(data => {
            const transcript = data.text ? data.text.trim() : "";
            if (!transcript) {
                throw new Error("Prisma STT did not detect any speech in the audio. Please try speaking again.");
            }
            console.log(`[STAGE: PRISMA_STT] Transcript received: '${transcript}'`);
            this.addMessage(transcript, 'user');
            this.processEvonAndTimbre(transcript);
        })
        .catch(err => {
            console.error("[STAGE: PRISMA_STT] Error:", err);
            this.addErrorMessage(`Prisma STT Error: ${err.message}`);
            this.statusText.textContent = "Speech recognition error. Tap mic or type below.";
            this.resetStepHighlights();
        });
    }

    sendTextMessage() {
        const text = this.textInput.value.trim();
        if (!text) return;
        this.textInput.value = '';
        this.addMessage(text, 'user');
        this.processEvonAndTimbre(text);
    }

    processEvonAndTimbre(prompt) {
        const lang = this.getCurrentLang();
        const bcp47 = this.getBcp47(lang);
        this.highlightStep('evon');
        this.statusText.textContent = `🧠 Reasoning Model analyzing question in ${bcp47}...`;

        console.log(`[STAGE: REASONING_MODEL] Request status: initiating | Prompt: '${prompt}' | Lang: ${lang} (${bcp47})`);

        fetch('/api/gnani/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt, language: lang, session_id: this.sessionId })
        })
        .then(async res => {
            const data = await res.json().catch(() => ({}));
            if (!res.ok || !data.success) {
                throw new Error(data.error || data.message || `Model reasoning request failed with HTTP ${res.status}`);
            }
            return data;
        })
        .then(data => {
            const answer = data.answer;
            if (!answer) {
                throw new Error("Reasoning model returned an empty answer.");
            }
            console.log(`[STAGE: MODEL_RESPONSE] Answer received from ${data.engine} | Category: ${data.category_name}`);
            this.addMessage(answer, 'bot', data.engine, data.category_name);
            
            // Step 3: Timbre TTS
            this.highlightStep('timbre');
            this.statusText.textContent = `🔊 Timbre synthesizing regional voice (${bcp47})...`;
            this.speakWithTimbre(answer, lang);
        })
        .catch(err => {
            console.error("[STAGE: REASONING_MODEL] Error:", err);
            this.addErrorMessage(`AI Model Error: ${err.message}`);
            this.statusText.textContent = "Assistant ready. Type your agricultural question.";
            this.resetStepHighlights();
        });
    }

    speakWithTimbre(text, lang) {
        const bcp47 = this.getBcp47(lang);
        console.log(`[STAGE: TIMBRE_TTS] Request status: initiating | Target dialect: ${bcp47} | Text length: ${text.length}`);

        fetch('/api/gnani/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, language: lang })
        })
        .then(res => res.json())
        .then(data => {
            if (data && data.audio_base64) {
                console.log("[STAGE: TIMBRE_TTS] Received audio stream from Gnani Timbre.");
                this.audioPlayer.src = `data:audio/wav;base64,${data.audio_base64}`;
                this.audioPlayer.play().catch(e => {
                    console.warn("[STAGE: TIMBRE_TTS] Audio auto-play restricted by browser, handoff to Web Speech:", e);
                    this.speakBrowserSpeech(text, lang);
                });
                this.statusText.textContent = `🔊 Timbre playing audio (${bcp47})...`;
                this.audioPlayer.onended = () => {
                    this.statusText.textContent = "Voice Assistant ready.";
                    this.resetStepHighlights();
                };
            } else {
                console.log(`[STAGE: TIMBRE_TTS] Remote Timbre unavailable. Handoff to browser speech synthesis for: ${bcp47}`);
                this.speakBrowserSpeech(text, lang);
            }
        })
        .catch(err => {
            console.warn("[STAGE: TIMBRE_TTS] Timbre TTS API call failed, handoff to browser speech:", err);
            this.speakBrowserSpeech(text, lang);
        });
    }

    speakBrowserSpeech(text, lang) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            
            // Strip markdown asterisks and hash tags for clean speech
            const cleanText = text.replace(/[*#_`]/g, '').trim();
            const utterance = new SpeechSynthesisUtterance(cleanText);
            const bcp47 = this.getBcp47(lang);
            
            utterance.lang = bcp47;
            utterance.rate = 0.95;
            this.statusText.textContent = `🔊 Voice synthesis speaking (${bcp47})...`;
            
            utterance.onend = () => {
                this.statusText.textContent = "Voice Assistant ready.";
                this.resetStepHighlights();
            };
            utterance.onerror = (e) => {
                console.warn("[STAGE: TIMBRE_TTS] SpeechSynthesis error:", e);
                this.statusText.textContent = "Voice Assistant ready.";
                this.resetStepHighlights();
            };
            window.speechSynthesis.speak(utterance);
        } else {
            this.statusText.textContent = "Voice Assistant ready.";
            this.resetStepHighlights();
        }
    }

    stopAudio() {
        if (this.audioPlayer) {
            this.audioPlayer.pause();
        }
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    }

    addMessage(text, sender, engineInfo = null, categoryName = null) {
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'bot' ? '🌾' : '👤';

        const content = document.createElement('div');
        content.className = 'message-text';

        // Render basic markdown formatting (KaTeX / KaTeX math blocks, bold, lists, newlines)
        const formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        content.innerHTML = formattedText;

        if (sender === 'bot') {
            const actionRow = document.createElement('div');
            actionRow.className = 'message-audio-action';
            
            const speakBtn = document.createElement('button');
            speakBtn.className = 'btn-speak-text';
            speakBtn.innerHTML = '🔊 Speak';
            speakBtn.onclick = () => this.speakWithTimbre(text, this.getCurrentLang());
            actionRow.appendChild(speakBtn);

            if (categoryName) {
                const catTag = document.createElement('span');
                catTag.style.fontSize = '0.72rem';
                catTag.style.color = '#0284c7';
                catTag.style.background = '#e0f2fe';
                catTag.style.padding = '2px 8px';
                catTag.style.borderRadius = '12px';
                catTag.style.fontWeight = '600';
                catTag.style.marginLeft = '8px';
                catTag.textContent = `📂 ${categoryName}`;
                actionRow.appendChild(catTag);
            }

            if (engineInfo) {
                const tag = document.createElement('span');
                tag.style.fontSize = '0.7rem';
                tag.style.color = '#15803d';
                tag.style.fontWeight = '600';
                tag.style.marginLeft = '8px';
                tag.textContent = `⚡ ${engineInfo}`;
                actionRow.appendChild(tag);
            }

            content.appendChild(actionRow);
        }

        bubble.appendChild(avatar);
        bubble.appendChild(content);
        this.chatBody.appendChild(bubble);
        this.chatBody.scrollTop = this.chatBody.scrollHeight;
    }

    addErrorMessage(errorText) {
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble error';
        bubble.style.maxWidth = '90%';
        bubble.style.margin = '10px 0';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '⚠️';

        const content = document.createElement('div');
        content.className = 'message-text';
        content.style.backgroundColor = '#fef2f2';
        content.style.color = '#991b1b';
        content.style.border = '1px solid #fecaca';
        content.style.borderRadius = '12px';
        content.style.padding = '10px 14px';
        content.style.fontSize = '0.88rem';
        content.textContent = errorText;

        bubble.appendChild(avatar);
        bubble.appendChild(content);
        this.chatBody.appendChild(bubble);
        this.chatBody.scrollTop = this.chatBody.scrollHeight;
    }

    highlightStep(step) {
        this.resetStepHighlights();
        if (step === 'prisma' && this.stepPrisma) this.stepPrisma.classList.add('active');
        if (step === 'evon' && this.stepEvon) this.stepEvon.classList.add('active');
        if (step === 'timbre' && this.stepTimbre) this.stepTimbre.classList.add('active');
    }

    resetStepHighlights() {
        if (this.stepPrisma) this.stepPrisma.classList.remove('active');
        if (this.stepEvon) this.stepEvon.classList.remove('active');
        if (this.stepTimbre) this.stepTimbre.classList.remove('active');
    }

    /**
     * DEMONSTRATION LOOP:
     * Rotates through varied agricultural queries in the farmer's selected language.
     */
    runCompetitionDemoLoop() {
        this.open();
        const lang = this.getCurrentLang();
        const bcp47 = this.getBcp47(lang);

        const demoQuestions = {
            'kn': [
                'ಭತ್ತದ ಬೆಳೆಗಳಲ್ಲಿ ಬೆಂಕಿ ರೋಗಕ್ಕೆ ಯಾವ ಔಷಧಿ ಸಿಂಪಡಿಸಬೇಕು?',
                'ರಾಗಿ ಬೆಳೆಗೆ ಶಿಫಾರಸು ಮಾಡಲಾದ ರಸಗೊಬ್ಬರಗಳ ಪ್ರಮಾಣ ಎಷ್ಟು?',
                'ಹನಿ ನೀರಾವರಿ ಪದ್ಧತಿಯಿಂದ ನೀರು ಎಷ್ಟು ಉಳಿತಾಯವಾಗುತ್ತದೆ?',
                'ಬೆಳೆಗಳಿಗೆ ಉತ್ತಮ ಮಂಡಿ ಬೆಲೆ ಪಡೆಯುವುದು ಹೇಗೆ?',
                'ಜೀವಾಮೃತವನ್ನು ಹೇಗೆ ತಯಾರಿಸಬೇಕು ಮತ್ತು ಬಳಸಬೇಕು?'
            ],
            'ta': [
                'நெல் பயிரில் குலை நோயை கட்டுப்படுத்த என்ன செய்ய வேண்டும்?',
                'கேழ்வரகு பயிருக்கு பரிந்துரைக்கப்படும் உர அளவு என்ன?',
                'சொட்டு நீர் பாசனம் மூலம் எவ்வளவு தண்ணீர் சேமிக்க முடியும்?',
                'விளைபொருட்களுக்கு சிறந்த மண்டி விலை பெறுவது எப்படி?',
                'ஜீவாமிர்தம் எவ்வாறு தயாரித்து பயன்படுத்த வேண்டும்?'
            ],
            'en': [
                'How to treat paddy blast disease effectively?',
                'What is the recommended fertilizer schedule for ragi (finger millet)?',
                'How much water is saved using drip irrigation systems?',
                'How can farmers get the best mandi market prices for crops?',
                'How to prepare and apply organic Jeevamrutha on crops?'
            ]
        };

        const questionsList = demoQuestions[lang] || demoQuestions['en'];
        const sampleText = questionsList[this.demoIndex % questionsList.length];
        this.demoIndex++;

        // Step 1: Prisma STT demonstration
        this.highlightStep('prisma');
        this.statusText.textContent = `🎙️ STEP 1 [Prisma ASR]: Farmer speaking audio input in ${bcp47}...`;
        
        setTimeout(() => {
            this.addMessage(sampleText, 'user');
            this.statusText.textContent = `🧠 STEP 2 [AI Reasoner]: Analyzing agronomic question in ${bcp47}...`;
            this.highlightStep('evon');

            setTimeout(() => {
                this.processEvonAndTimbre(sampleText);
            }, 700);
        }, 1000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.gnaniAssistant = new GnaniAssistant();
});
