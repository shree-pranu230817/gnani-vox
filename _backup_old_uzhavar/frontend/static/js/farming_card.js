/**
 * UZHAVAR AI - AI FARMING ASSISTANT (THIRD MAIN SERVICE) CONTROLLER
 * Ask Anything About Agriculture - Real-time AI, Gnani Prisma STT & Gnani Timbre TTS
 */

class FarmingAssistantCard {
    constructor() {
        this.sessionId = localStorage.getItem('uzhavar_farming_session_id') || ('farm_sess_' + Math.random().toString(36).substring(2, 12));
        localStorage.setItem('uzhavar_farming_session_id', this.sessionId);

        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.speechRecognition = null;
        this.audioPlayer = new Audio();
        this.isPlayingAudio = false;
        this.currentAnswerText = "";
        this.currentAudioBase64 = null;
        this.history = [];

        this.initElements();
        this.initEvents();
        this.initSpeechEngine();
    }

    initElements() {
        this.container = document.getElementById('farmingCardContainer');
        this.langSelect = document.getElementById('farmingCardLang');
        this.clearBtn = document.getElementById('farmingCardClearBtn');
        this.topicPills = document.querySelectorAll('.topic-pill');

        this.micBtn = document.getElementById('farmingCardMicBtn');
        this.textInput = document.getElementById('farmingCardInput');
        this.submitBtn = document.getElementById('farmingCardSubmitBtn');
        this.micStatusBar = document.getElementById('farmingCardMicStatus');
        this.micStatusText = document.getElementById('farmingCardMicStatusText');

        this.initialState = document.getElementById('farmingCardInitialState');
        this.loadingState = document.getElementById('farmingCardLoadingState');
        this.answerState = document.getElementById('farmingCardAnswerState');

        this.loadingStepText = document.getElementById('farmingLoadingStepText');
        this.stepPrismaBadge = document.getElementById('farmingStepPrisma');
        this.stepGeminiBadge = document.getElementById('farmingStepGemini');
        this.stepTimbreBadge = document.getElementById('farmingStepTimbre');

        this.badgeCategory = document.getElementById('farmingBadgeCategory');
        this.badgeEngine = document.getElementById('farmingBadgeEngine');
        this.badgeContext = document.getElementById('farmingBadgeContext');
        this.answerContent = document.getElementById('farmingAnswerContent');

        this.playAudioBtn = document.getElementById('farmingPlayAudioBtn');
        this.audioVisualizer = document.getElementById('farmingAudioVisualizer');

        this.followupInput = document.getElementById('farmingFollowupInput');
        this.followupSubmitBtn = document.getElementById('farmingFollowupSubmitBtn');
        this.followupMicBtn = document.getElementById('farmingFollowupMicBtn');

        this.historyDrawer = document.getElementById('farmingHistoryDrawer');
        this.historyToggleBtn = document.getElementById('farmingHistoryToggleBtn');
        this.historyList = document.getElementById('farmingHistoryList');

        this.suggestedChips = document.querySelectorAll('.suggested-prompt-chip');
    }

    initEvents() {
        // Clear conversation
        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => this.clearConversation());
        }

        // Submit main question
        if (this.submitBtn) {
            this.submitBtn.addEventListener('click', () => this.handleMainSubmit());
        }
        if (this.textInput) {
            this.textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleMainSubmit();
            });
        }

        // Main mic
        if (this.micBtn) {
            this.micBtn.addEventListener('click', () => this.toggleVoiceRecording('main'));
        }

        // Topic pills
        if (this.topicPills) {
            this.topicPills.forEach(pill => {
                pill.addEventListener('click', () => {
                    const sampleQ = pill.getAttribute('data-sample') || pill.textContent.trim();
                    if (this.textInput) {
                        this.textInput.value = sampleQ;
                        this.textInput.focus();
                    }
                });
            });
        }

        // Suggested chips
        if (this.suggestedChips) {
            this.suggestedChips.forEach(chip => {
                chip.addEventListener('click', () => {
                    const prompt = chip.getAttribute('data-prompt') || chip.textContent.trim();
                    if (this.textInput) {
                        this.textInput.value = prompt;
                        this.handleMainSubmit();
                    }
                });
            });
        }

        // Audio playback button
        if (this.playAudioBtn) {
            this.playAudioBtn.addEventListener('click', () => this.toggleAudioPlayback());
        }

        // Audio player ended event
        this.audioPlayer.onended = () => {
            this.onAudioEnded();
        };

        // Follow-up submit
        if (this.followupSubmitBtn) {
            this.followupSubmitBtn.addEventListener('click', () => this.handleFollowupSubmit());
        }
        if (this.followupInput) {
            this.followupInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleFollowupSubmit();
            });
        }

        // Follow-up mic
        if (this.followupMicBtn) {
            this.followupMicBtn.addEventListener('click', () => this.toggleVoiceRecording('followup'));
        }

        // History toggle
        if (this.historyToggleBtn) {
            this.historyToggleBtn.addEventListener('click', () => {
                if (this.historyList) {
                    const isHidden = this.historyList.style.display === 'none';
                    this.historyList.style.display = isHidden ? 'flex' : 'none';
                    this.historyToggleBtn.innerHTML = isHidden 
                        ? '▲ Hide Previous Turns' 
                        : '▼ View Consultation History (' + this.history.length + ' turns)';
                }
            });
        }
    }

    getCurrentLang() {
        if (this.langSelect) {
            return this.langSelect.value;
        }
        return document.documentElement.lang || 'en';
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

    /* -------------------------------------------------------------------------
       VOICE RECOGNITION (PRISMA STT + BROWSER FALLBACK)
       ------------------------------------------------------------------------- */
    initSpeechEngine() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.speechRecognition = new SpeechRecognition();
            this.speechRecognition.continuous = false;
            this.speechRecognition.interimResults = false;

            this.speechRecognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript.trim();
                console.log(`[FARMING_CARD] Web Speech recognized: "${transcript}"`);
                this.stopVoiceRecording();
                if (transcript) {
                    if (this.activeMicTarget === 'followup' && this.followupInput) {
                        this.followupInput.value = transcript;
                        this.handleFollowupSubmit();
                    } else if (this.textInput) {
                        this.textInput.value = transcript;
                        this.handleMainSubmit();
                    }
                }
            };

            this.speechRecognition.onerror = (event) => {
                console.warn('[FARMING_CARD] Speech recognition error:', event.error);
                this.stopVoiceRecording();
                if (event.error !== 'no-speech') {
                    alert(`Speech recognition notice: ${event.error}. You can also type your question.`);
                }
            };

            this.speechRecognition.onend = () => {
                if (this.isRecording) {
                    this.stopVoiceRecording();
                }
            };
        }
    }

    toggleVoiceRecording(target = 'main') {
        if (this.isRecording) {
            this.stopVoiceRecording();
        } else {
            this.startVoiceRecording(target);
        }
    }

    startVoiceRecording(target = 'main') {
        this.activeMicTarget = target;
        this.isRecording = true;

        const lang = this.getCurrentLang();
        const bcp47 = this.getBcp47(lang);

        if (target === 'followup' && this.followupMicBtn) {
            this.followupMicBtn.classList.add('recording');
        } else if (this.micBtn) {
            this.micBtn.classList.add('recording');
        }

        if (this.micStatusBar) {
            this.micStatusBar.style.display = 'flex';
            if (this.micStatusText) {
                this.micStatusText.textContent = `🎙️ Listening in ${bcp47} via Gnani Prisma... Speak your farming question clearly.`;
            }
        }

        if (this.speechRecognition) {
            try {
                this.speechRecognition.lang = bcp47;
                this.speechRecognition.start();
            } catch (e) {
                console.warn("SpeechRecognition start error:", e);
            }
        } else {
            // MediaRecorder fallback to backend STT
            this.startMediaRecorder(lang);
        }
    }

    startMediaRecorder(lang) {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Microphone not supported on this browser. Please type your agricultural question.");
            this.stopVoiceRecording();
            return;
        }

        this.audioChunks = [];
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                this.mediaRecorder = new MediaRecorder(stream);
                this.mediaRecorder.ondataavailable = e => {
                    if (e.data.size > 0) this.audioChunks.push(e.data);
                };
                this.mediaRecorder.onstop = () => {
                    stream.getTracks().forEach(t => t.stop());
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                    this.sendAudioForSTT(audioBlob, lang);
                };
                this.mediaRecorder.start();
            })
            .catch(err => {
                console.warn("Microphone access denied:", err);
                alert("Microphone permission denied. Please allow microphone access or type your question.");
                this.stopVoiceRecording();
            });
    }

    sendAudioForSTT(audioBlob, lang) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('language', lang);

        if (this.micStatusText) {
            this.micStatusText.textContent = "🎙️ Transcribing speech with Gnani Prisma STT...";
        }

        fetch('/api/gnani/stt', {
            method: 'POST',
            body: formData
        })
        .then(r => r.json())
        .then(data => {
            if (data.success && data.text) {
                if (this.activeMicTarget === 'followup' && this.followupInput) {
                    this.followupInput.value = data.text;
                    this.handleFollowupSubmit();
                } else if (this.textInput) {
                    this.textInput.value = data.text;
                    this.handleMainSubmit();
                }
            } else {
                alert("Could not transcribe speech. Please type your question.");
            }
        })
        .catch(err => {
            console.error("STT error:", err);
        })
        .finally(() => {
            this.stopVoiceRecording();
        });
    }

    stopVoiceRecording() {
        this.isRecording = false;
        if (this.micBtn) this.micBtn.classList.remove('recording');
        if (this.followupMicBtn) this.followupMicBtn.classList.remove('recording');
        if (this.micStatusBar) this.micStatusBar.style.display = 'none';

        if (this.speechRecognition) {
            try { this.speechRecognition.stop(); } catch (e) {}
        }
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            try { this.mediaRecorder.stop(); } catch (e) {}
        }
    }

    /* -------------------------------------------------------------------------
       QUESTION SUBMISSION & MULTI-TURN REASONING
       ------------------------------------------------------------------------- */
    handleMainSubmit() {
        if (!this.textInput) return;
        const prompt = this.textInput.value.trim();
        if (!prompt) {
            this.textInput.focus();
            return;
        }
        this.submitQuestion(prompt, false);
    }

    handleFollowupSubmit() {
        if (!this.followupInput) return;
        const prompt = this.followupInput.value.trim();
        if (!prompt) {
            this.followupInput.focus();
            return;
        }
        this.followupInput.value = "";
        this.submitQuestion(prompt, true);
    }

    submitQuestion(prompt, isFollowup = false) {
        this.stopAudio();
        const lang = this.getCurrentLang();
        const bcp47 = this.getBcp47(lang);

        // Show loading state
        this.showLoadingState(prompt);

        console.log(`[FARMING_CARD] Submitting question: "${prompt}" | Lang: ${lang} | Session: ${this.sessionId}`);

        fetch('/api/gnani/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                language: lang,
                session_id: this.sessionId
            })
        })
        .then(async res => {
            const data = await res.json().catch(() => ({}));
            if (!res.ok || !data.success) {
                throw new Error(data.error || data.message || `Server returned HTTP ${res.status}`);
            }
            return data;
        })
        .then(data => {
            this.handleAnswerSuccess(prompt, data, lang);
        })
        .catch(err => {
            console.error("[FARMING_CARD] Reasoning failed:", err);
            this.handleAnswerError(err.message);
        });
    }

    showLoadingState(prompt) {
        if (this.initialState) this.initialState.style.display = 'none';
        if (this.answerState) this.answerState.style.display = 'none';
        if (this.loadingState) this.loadingState.style.display = 'block';

        if (this.stepPrismaBadge) this.stepPrismaBadge.classList.add('active');
        if (this.stepGeminiBadge) this.stepGeminiBadge.classList.add('active');
        if (this.stepTimbreBadge) this.stepTimbreBadge.classList.remove('active');

        if (this.loadingStepText) {
            this.loadingStepText.textContent = `Analyzing "${prompt.substring(0, 45)}..." with agricultural reasoning models...`;
        }
    }

    handleAnswerSuccess(prompt, data, lang) {
        if (this.loadingState) this.loadingState.style.display = 'none';
        if (this.answerState) this.answerState.style.display = 'block';

        const answer = data.answer || "No response generated.";
        this.currentAnswerText = answer;
        this.currentAudioBase64 = null;

        // Render meta badges
        if (this.badgeCategory) {
            this.badgeCategory.textContent = `📂 ${data.category_name || data.category || 'Agricultural Guidance'}`;
        }
        if (this.badgeEngine) {
            this.badgeEngine.textContent = `⚡ ${data.engine || 'Google Gemini AI'}`;
        }
        if (this.badgeContext) {
            const ctxSummary = data.memory_context;
            if (ctxSummary && ctxSummary !== "No prior context") {
                this.badgeContext.style.display = 'inline-block';
                this.badgeContext.textContent = `🌾 ${ctxSummary}`;
            } else {
                this.badgeContext.style.display = 'none';
            }
        }

        // Render formatted answer HTML
        if (this.answerContent) {
            this.answerContent.innerHTML = this.renderMarkdown(answer);
        }

        // Add to multi-turn history
        this.history.push({
            user: prompt,
            bot: answer,
            category: data.category_name,
            timestamp: new Date().toLocaleTimeString()
        });
        this.updateHistoryDrawer();

        // Prepare audio synthesis via Gnani Timbre
        this.prepareTimbreAudio(answer, lang);

        // Scroll answer into view smoothly
        this.answerState.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    handleAnswerError(errorMsg) {
        if (this.loadingState) this.loadingState.style.display = 'none';
        if (this.answerState) this.answerState.style.display = 'block';

        if (this.answerContent) {
            this.answerContent.innerHTML = `
                <div style="background: #fee2e2; border: 1.5px solid #fca5a5; color: #991b1b; padding: 18px 20px; border-radius: 10px;">
                    <strong>⚠️ Agricultural Assistant Notice:</strong><br>
                    ${errorMsg}<br><br>
                    <small>Please check your question and try again, or rephrase with specific details like crop name, symptoms, and state.</small>
                </div>
            `;
        }
    }

    /* -------------------------------------------------------------------------
       AUDIO PLAYBACK (GNANI TIMBRE + BROWSER FALLBACK)
       ------------------------------------------------------------------------- */
    prepareTimbreAudio(text, lang) {
        if (this.playAudioBtn) {
            this.playAudioBtn.innerHTML = '🔊 Listen to Answer (Gnani Timbre)';
            this.playAudioBtn.disabled = false;
        }

        // Pre-fetch audio from Timbre endpoint
        fetch('/api/gnani/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text.substring(0, 500),
                language: lang
            })
        })
        .then(r => r.json())
        .then(data => {
            if (data && data.audio_base64) {
                this.currentAudioBase64 = data.audio_base64;
                console.log("[FARMING_CARD] Gnani Timbre audio stream ready.");
            }
        })
        .catch(err => {
            console.warn("[FARMING_CARD] Timbre pre-fetch failed:", err);
        });
    }

    toggleAudioPlayback() {
        if (this.isPlayingAudio) {
            this.stopAudio();
        } else {
            this.startAudioPlayback();
        }
    }

    startAudioPlayback() {
        const lang = this.getCurrentLang();
        const bcp47 = this.getBcp47(lang);

        this.isPlayingAudio = true;
        if (this.playAudioBtn) {
            this.playAudioBtn.innerHTML = '⏸️ Pause Audio';
            this.playAudioBtn.classList.add('playing');
        }
        if (this.audioVisualizer) {
            this.audioVisualizer.style.display = 'inline-flex';
        }

        if (this.currentAudioBase64) {
            this.audioPlayer.src = `data:audio/wav;base64,${this.currentAudioBase64}`;
            this.audioPlayer.play().catch(e => {
                console.warn("[FARMING_CARD] Playback restricted, falling back to Web Speech:", e);
                this.speakBrowserSpeech(this.currentAnswerText, lang);
            });
        } else {
            this.speakBrowserSpeech(this.currentAnswerText, lang);
        }
    }

    speakBrowserSpeech(text, lang) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const cleanText = text.replace(/[*#_`]/g, '').trim();
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.lang = this.getBcp47(lang);
            utterance.rate = 0.95;

            utterance.onend = () => this.onAudioEnded();
            utterance.onerror = () => this.onAudioEnded();

            window.speechSynthesis.speak(utterance);
        } else {
            this.onAudioEnded();
        }
    }

    stopAudio() {
        this.isPlayingAudio = false;
        if (this.audioPlayer) this.audioPlayer.pause();
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        this.onAudioEnded();
    }

    onAudioEnded() {
        this.isPlayingAudio = false;
        if (this.playAudioBtn) {
            this.playAudioBtn.innerHTML = '🔊 Listen to Answer (Gnani Timbre)';
            this.playAudioBtn.classList.remove('playing');
        }
        if (this.audioVisualizer) {
            this.audioVisualizer.style.display = 'none';
        }
    }

    /* -------------------------------------------------------------------------
       MULTI-TURN CONVERSATION MEMORY RESET & HISTORY
       ------------------------------------------------------------------------- */
    clearConversation() {
        if (!confirm("Are you sure you want to clear conversation history and start a fresh agricultural consultation?")) {
            return;
        }

        this.stopAudio();
        fetch('/api/gnani/reset-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: this.sessionId })
        })
        .finally(() => {
            this.sessionId = 'farm_sess_' + Math.random().toString(36).substring(2, 12);
            localStorage.setItem('uzhavar_farming_session_id', this.sessionId);
            this.history = [];
            this.currentAnswerText = "";
            this.currentAudioBase64 = null;

            if (this.textInput) this.textInput.value = "";
            if (this.followupInput) this.followupInput.value = "";
            if (this.answerState) this.answerState.style.display = 'none';
            if (this.loadingState) this.loadingState.style.display = 'none';
            if (this.initialState) this.initialState.style.display = 'block';

            if (this.historyDrawer) this.historyDrawer.style.display = 'none';
            if (this.historyList) this.historyList.innerHTML = '';
        });
    }

    updateHistoryDrawer() {
        if (!this.historyDrawer || this.history.length <= 1) {
            if (this.historyDrawer) this.historyDrawer.style.display = 'none';
            return;
        }

        this.historyDrawer.style.display = 'block';
        if (this.historyToggleBtn) {
            this.historyToggleBtn.innerHTML = `▼ View Consultation History (${this.history.length} turns)`;
        }

        if (this.historyList) {
            this.historyList.innerHTML = this.history.map((turn, i) => `
                <div class="history-turn-item">
                    <div class="history-turn-user">🌾 Question ${i + 1}: ${this.escapeHtml(turn.user)}</div>
                    <div class="history-turn-bot">${this.escapeHtml(turn.bot.substring(0, 180))}...</div>
                </div>
            `).join('');
        }
    }

    /* -------------------------------------------------------------------------
       MARKDOWN & FORMATTING UTILITY
       ------------------------------------------------------------------------- */
    renderMarkdown(text) {
        if (!text) return "";
        let html = text
            // Headings
            .replace(/^### (.*$)/gim, '<h4>$1</h4>')
            .replace(/^## (.*$)/gim, '<h3>$1</h3>')
            .replace(/^# (.*$)/gim, '<h2>$1</h2>')
            // Bold & Italics
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            // Numbered lists: 1. Step -> <div class="step-line"><strong>1.</strong> ...</div>
            .replace(/^([0-9]+\.)\s+(.*$)/gim, '<div style="margin-bottom: 6px;"><strong>$1</strong> $2</div>')
            // Bullet points: • or - -> <li>
            .replace(/^[\*•\-]\s+(.*$)/gim, '<li>$1</li>')
            // Line breaks
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');

        return html;
    }

    escapeHtml(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('farmingCardContainer')) {
        window.farmingAssistantCard = new FarmingAssistantCard();
    }
});

