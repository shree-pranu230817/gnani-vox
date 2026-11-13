/**
 * UZHAVAR AI – Farmer Voice Translator Controller (Service 1)
 * Driven by CentralAudioController with 5-Stage Visual Progress & Real-Time Latency Metrics
 */

document.addEventListener('DOMContentLoaded', () => {
    const audioCtrl = window.centralAudioController;
    const sessionId = 'farmer_trans_' + Math.random().toString(36).substring(2, 10);

    const sourceLangSelect = document.getElementById('sourceLangSelect');
    const targetLangSelect = document.getElementById('targetLangSelect');
    const btnSwapLanguages = document.getElementById('btnSwapLanguages');
    const handsFreeToggle = document.getElementById('handsFreeToggle');
    const modeLabelText = document.getElementById('modeLabelText');

    const mainMicBtn = document.getElementById('mainMicBtn');
    const voiceStatusBanner = document.getElementById('voiceStatusBanner');

    const sourceTextArea = document.getElementById('sourceTextArea');
    const targetTextArea = document.getElementById('targetTextArea');
    const sourceBoxLabel = document.getElementById('sourceBoxLabel');
    const targetBoxLabel = document.getElementById('targetBoxLabel');
    const transTimingBar = document.getElementById('transTimingBar');

    const btnPlayTarget = document.getElementById('btnPlayTarget');
    const btnStopTarget = document.getElementById('btnStopTarget');
    const playBtnText = document.getElementById('playBtnText');

    const btnCopySource = document.getElementById('btnCopySource');
    const btnCopyTarget = document.getElementById('btnCopyTarget');
    const btnClearScreen = document.getElementById('btnClearScreen');

    const chipBtns = document.querySelectorAll('.chip-btn');

    const t = (k, a) => (window.UzhavarLanguage ? window.UzhavarLanguage.t(k, a) : k);
    let currentAudioBase64 = null;
    let currentTargetText = "";
    let isRecording = false;

    // 5-Stage Visual Progress
    audioCtrl.onStateChange((state, details) => {
        if (state === AudioState.RECORDING) {
            isRecording = true;
            mainMicBtn.classList.add('recording');
            voiceStatusBanner.className = 'voice-status-banner recording';
            voiceStatusBanner.textContent = '🎤 ' + t('status_listening');
        } else if (state === AudioState.TRANSCRIBING) {
            voiceStatusBanner.className = 'voice-status-banner';
            voiceStatusBanner.textContent = '📝 ' + t('status_transcribing');
        } else if (state === AudioState.THINKING) {
            voiceStatusBanner.className = 'voice-status-banner';
            voiceStatusBanner.textContent = '🌐 ' + t('status_thinking');
        } else if (state === AudioState.GENERATING_AUDIO) {
            voiceStatusBanner.className = 'voice-status-banner';
            voiceStatusBanner.textContent = '🔊 ' + t('status_preparing_voice');
        } else if (state === AudioState.SPEAKING) {
            voiceStatusBanner.className = 'voice-status-banner speaking';
            voiceStatusBanner.textContent = '🗣️ ' + t('status_speaking');
            if (playBtnText) playBtnText.textContent = t('stop_btn');
        } else if (state === AudioState.LISTENING) {
            mainMicBtn.classList.remove('recording');
            voiceStatusBanner.className = 'voice-status-banner';
            voiceStatusBanner.textContent = t('status_handsfree');
        } else if (state === AudioState.INTERRUPTED) {
            voiceStatusBanner.className = 'voice-status-banner recording';
            voiceStatusBanner.textContent = '⚡ ' + t('status_interrupted');
        } else if (state === AudioState.IDLE) {
            isRecording = false;
            mainMicBtn.classList.remove('recording');
            voiceStatusBanner.className = 'voice-status-banner';
            voiceStatusBanner.textContent = t('status_ready');
            if (playBtnText) playBtnText.textContent = t('play_btn');
        } else if (state === AudioState.ERROR) {
            isRecording = false;
            mainMicBtn.classList.remove('recording');
            voiceStatusBanner.className = 'voice-status-banner';
            voiceStatusBanner.textContent = (details && details.message) || t('status_error');
        }
    });

    // Update labels on language change
    function updateLabels() {
        const srcText = sourceLangSelect.options[sourceLangSelect.selectedIndex].text;
        const tgtText = targetLangSelect.options[targetLangSelect.selectedIndex].text;
        if (sourceBoxLabel) sourceBoxLabel.textContent = `${t('source_box_title')} (${srcText}):`;
        if (targetBoxLabel) targetBoxLabel.textContent = `${t('target_box_title')} (${tgtText}):`;
    }

    sourceLangSelect.addEventListener('change', updateLabels);
    targetLangSelect.addEventListener('change', updateLabels);

    // Swap Languages
    btnSwapLanguages.addEventListener('click', () => {
        audioCtrl.interruptCurrentPlayback();
        const temp = sourceLangSelect.value;
        sourceLangSelect.value = targetLangSelect.value;
        targetLangSelect.value = temp;
        updateLabels();

        const prevSrc = sourceTextArea.textContent.trim();
        const prevTgt = targetTextArea.textContent.trim();
        if (prevSrc && prevTgt && !prevSrc.startsWith('(')) {
            sourceTextArea.textContent = prevTgt;
            targetTextArea.textContent = prevSrc;
            currentTargetText = prevSrc;
        }
    });

    // Hands-Free Mode Toggle
    handsFreeToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
            modeLabelText.textContent = t('mode_handsfree');
            audioCtrl.enableHandsFree((blob, reqId, liveTranscript, recDuration) => {
                handleAudioSubmission(blob, reqId, liveTranscript, recDuration);
            }, sourceLangSelect.value + '-IN');
        } else {
            modeLabelText.textContent = t('mode_tap');
            audioCtrl.disableHandsFree();
        }
    });

    // Main Mic Button Press: Immediate Interruption Priority
    mainMicBtn.addEventListener('click', () => {
        if (isRecording) {
            audioCtrl.stopRecording();
        } else {
            audioCtrl.startTapToSpeak((blob, reqId, liveTranscript, recDuration) => {
                handleAudioSubmission(blob, reqId, liveTranscript, recDuration);
            }, sourceLangSelect.value + '-IN');
        }
    });

    // Process Recorded Audio / Speech with Latency Profiling
    function handleAudioSubmission(audioBlob, reqId, textPrompt = null, recDurationMs = 0) {
        audioCtrl.setState(AudioState.TRANSCRIBING);
        const tFetchStart = performance.now();

        const formData = new FormData();
        if (audioBlob) {
            formData.append('audio', audioBlob, 'speech.wav');
        }
        if (textPrompt) {
            formData.append('text', textPrompt);
            formData.append('text_hint', textPrompt);
        }
        formData.append('source_lang', sourceLangSelect.value);
        formData.append('target_lang', targetLangSelect.value);
        formData.append('domain', 'farmer');
        formData.append('session_id', sessionId);
        formData.append('speaker', 'farmer');

        fetch('/api/voice-translate', {
            method: 'POST',
            body: formData,
            signal: audioCtrl.currentAbortController ? audioCtrl.currentAbortController.signal : null
        })
        .then(r => r.json())
        .then(data => {
            if (reqId !== audioCtrl.currentRequestId) return; // Stale request guard

            const tFetchEnd = performance.now();
            const networkTurnaroundMs = Math.round(tFetchEnd - tFetchStart);

            if (data.success) {
                sourceTextArea.textContent = data.original_text;
                targetTextArea.textContent = data.translated_text;
                currentTargetText = data.translated_text;
                currentAudioBase64 = data.audio_base64;

                const timings = data.timings || {};
                const sttMs = timings.stt_ms || 0;
                const transMs = timings.translation_ms || 0;
                const ttsMs = timings.tts_ms || 0;

                // Play synthesized speech
                const tgtLangCode = targetLangSelect.value + '-IN';
                audioCtrl.setState(AudioState.GENERATING_AUDIO);

                audioCtrl.playAudio(
                    currentAudioBase64,
                    currentTargetText,
                    tgtLangCode,
                    null,
                    (startupMs) => {
                        const totalWaitMs = networkTurnaroundMs + startupMs;
                        console.log(
                            `⏱️ [LATENCY REPORT - FARMER TRANSLATOR]\n` +
                            `  • Recording Duration: ${recDurationMs}ms\n` +
                            `  • Speech-to-Text: ${sttMs}ms (${data.engines ? data.engines.stt : 'STT'})\n` +
                            `  • Translation: ${transMs}ms (${data.engines ? data.engines.translation : 'Gemini'})\n` +
                            `  • Voice Synthesis: ${ttsMs}ms (${data.engines ? data.engines.tts : 'Timbre'})\n` +
                            `  • Playback Startup: ${startupMs}ms\n` +
                            `  • Total Response Turnaround: ${totalWaitMs}ms (${(totalWaitMs/1000).toFixed(2)}s)`
                        );

                        if (transTimingBar) {
                            transTimingBar.style.display = 'block';
                            transTimingBar.innerHTML =
                                `⏱️ <strong>ಪ್ರತಿಕ್ರಿಯೆ ಸಮಯ: ${(totalWaitMs / 1000).toFixed(2)}s</strong> ` +
                                `[ರೆಕಾರ್ಡಿಂಗ್: ${recDurationMs}ms | STT: ${sttMs}ms | ಅನುವಾದ: ${transMs}ms | TTS: ${ttsMs}ms | ಧ್ವನಿ ಆರಂಭ: ${startupMs}ms]`;
                        }
                    }
                );
            } else {
                audioCtrl.setState(AudioState.ERROR, { message: data.error || 'ಅನುವಾದ ವಿಫಲವಾಗಿದೆ (Translation failed)' });
            }
        })
        .catch(err => {
            if (err.name === 'AbortError') {
                console.log('[FarmerTranslator] Request aborted by user interruption.');
            } else {
                console.error('[FarmerTranslator] Error:', err);
                audioCtrl.setState(AudioState.ERROR, { message: 'ಸಂಪರ್ಕ ದೋಷ (Connection error)' });
            }
        });
    }

    // Playback buttons
    btnPlayTarget.addEventListener('click', () => {
        if (!currentTargetText) return;
        const tgtLangCode = targetLangSelect.value + '-IN';
        if (audioCtrl.state === AudioState.SPEAKING) {
            audioCtrl.interruptCurrentPlayback();
            audioCtrl.setState(AudioState.IDLE);
        } else {
            audioCtrl.playAudio(currentAudioBase64, currentTargetText, tgtLangCode);
        }
    });

    btnStopTarget.addEventListener('click', () => {
        audioCtrl.interruptCurrentPlayback();
        audioCtrl.setState(AudioState.IDLE);
    });

    // Copy to Clipboard
    btnCopySource.addEventListener('click', () => {
        navigator.clipboard.writeText(sourceTextArea.textContent);
        btnCopySource.textContent = '✓ ' + (t('copy_btn') || 'Copied!');
        setTimeout(() => { btnCopySource.textContent = '📋 ' + (t('copy_btn') || 'Copy'); }, 1500);
    });

    btnCopyTarget.addEventListener('click', () => {
        navigator.clipboard.writeText(targetTextArea.textContent);
        btnCopyTarget.textContent = '✓ ' + (t('copy_btn') || 'Copied!');
        setTimeout(() => { btnCopyTarget.textContent = '📋 ' + (t('copy_btn') || 'Copy'); }, 1500);
    });

    // Clear Screen
    btnClearScreen.addEventListener('click', () => {
        audioCtrl.interruptCurrentPlayback();
        sourceTextArea.textContent = '(' + t('source_placeholder') + ')';
        targetTextArea.textContent = '(' + t('target_placeholder') + ')';
        currentTargetText = "";
        currentAudioBase64 = null;
        if (transTimingBar) transTimingBar.style.display = 'none';
        voiceStatusBanner.textContent = t('status_ready');
    });

    // Quick Agricultural Chips
    chipBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const text = btn.textContent.replace(/^[^\s]+\s*/, '').trim() || btn.getAttribute('data-text');
            if (text) {
                audioCtrl.interruptCurrentPlayback();
                const reqId = ++audioCtrl.currentRequestId;
                handleAudioSubmission(null, reqId, text, 0);
            }
        });
    });

    // React to language switch immediately
    window.addEventListener('uzhavar:languageChanged', () => {
        updateLabels();
        if (!isRecording && voiceStatusBanner) {
            voiceStatusBanner.textContent = t('status_ready');
        }
    });
});
