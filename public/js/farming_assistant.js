/**
 * UZHAVAR AI – AI Farming Question & Answer Assistant Controller (Service 3)
 * Features: Permanent SQLite Conversation Storage, Continuous Multi-Turn Context,
 *           Voice Interruption Priority, Gnani Prisma STT, Gnani Timbre TTS,
 *           Clean Multilingual Localization & High-End Minimalist UI.
 */

document.addEventListener('DOMContentLoaded', () => {
    const audioCtrl = window.centralAudioController;
    const t = (k, a) => (window.UzhavarLanguage ? window.UzhavarLanguage.t(k, a) : k);

    // DOM Elements - Navigation & Conversations
    const btnNewChat = document.getElementById('btnNewChat');
    const btnClearConversation = document.getElementById('btnClearConversation');
    const conversationsList = document.getElementById('conversationsList');
    const convCountBadge = document.getElementById('convCountBadge');
    const activeConvBadge = document.getElementById('activeConvBadge');

    // Controls
    const assistantLangSelect = document.getElementById('assistantLangSelect');
    const assistantHandsFreeToggle = document.getElementById('assistantHandsFreeToggle');

    // Mic & Input
    const assistantMicBtn = document.getElementById('assistantMicBtn');
    const assistantVoiceStatus = document.getElementById('assistantVoiceStatus');
    const assistantTextInput = document.getElementById('assistantTextInput');
    const assistantSubmitBtn = document.getElementById('assistantSubmitBtn');

    // Chat Thread Display
    const chatThreadContainer = document.getElementById('chatThreadContainer');
    const assistantInitialState = document.getElementById('assistantInitialState');
    const chatMessagesList = document.getElementById('chatMessagesList');
    const chipBtns = document.querySelectorAll('.chip-btn');

    // State Variables
    let activeConversationId = localStorage.getItem('uzhavar_active_conv_id') || null;
    let isRecording = false;
    let currentlyPlayingAudioId = null;
    let cachedConversations = [];
    let cachedCurrentConv = null;

    // =========================================================================
    // 1. CONVERSATION MANAGEMENT & DATABASE RESTORATION
    // =========================================================================

    // Initialize Active Conversation on Page Load
    async function initConversationStore() {
        try {
            const resp = await fetch('/api/conversations');
            const data = await resp.json();

            if (data.success && data.conversations) {
                cachedConversations = data.conversations;
                renderConversationsList(data.conversations);

                // If active conversation is valid and present in SQLite, restore it
                const exists = data.conversations.some(c => c.conversation_id === activeConversationId);
                if (activeConversationId && exists) {
                    await selectConversation(activeConversationId, false);
                } else if (data.conversations.length > 0) {
                    // Restore most recent conversation
                    await selectConversation(data.conversations[0].conversation_id, false);
                } else {
                    // Create first default conversation in SQLite
                    await createNewConversation(false);
                }
            } else {
                await createNewConversation(false);
            }
        } catch (e) {
            console.error('[FarmingAssistant] Failed to initialize conversations:', e);
            await createNewConversation(false);
        }
    }

    // Render Conversation Sidebar List
    function renderConversationsList(convs) {
        if (!conversationsList) return;
        cachedConversations = convs || [];
        conversationsList.innerHTML = '';
        if (convCountBadge) convCountBadge.textContent = cachedConversations.length;

        if (cachedConversations.length === 0) {
            conversationsList.innerHTML = `
                <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 24px 0;">
                    ${escapeHtml(t('no_past_chats'))}
                </div>`;
            return;
        }

        cachedConversations.forEach(c => {
            const item = document.createElement('div');
            item.className = 'conv-item' + (c.conversation_id === activeConversationId ? ' active' : '');
            item.setAttribute('data-id', c.conversation_id);

            const timeStr = formatTimestamp(c.updated_at || c.created_at);
            const msgCount = c.message_count || 0;
            const msgLabel = (msgCount === 1) ? t('msg_count_single') : t('msg_count_plural', msgCount);

            item.innerHTML = `
                <div class="conv-item-info">
                    <div class="conv-item-title" title="${escapeHtml(c.conversation_title)}">
                        ${escapeHtml(c.conversation_title)}
                    </div>
                    <div class="conv-item-meta">
                        <span>🕒 ${timeStr}</span>
                        <span>•</span>
                        <span>💬 ${msgLabel}</span>
                    </div>
                </div>
                <button class="conv-item-delete" title="${escapeHtml(t('clear_chat_btn'))}" data-delete-id="${c.conversation_id}">
                    🗑️
                </button>
            `;

            // Select on item click
            item.addEventListener('click', (e) => {
                if (e.target.closest('.conv-item-delete')) return;
                selectConversation(c.conversation_id);
            });

            // Delete on trash icon click
            const delBtn = item.querySelector('.conv-item-delete');
            if (delBtn) {
                delBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    confirmAndDeleteConversation(c.conversation_id, c.conversation_title);
                });
            }

            conversationsList.appendChild(item);
        });
    }

    // Create New Conversation in SQLite
    async function createNewConversation(selectAfter = true) {
        audioCtrl.interruptCurrentPlayback();
        const curLang = assistantLangSelect.value;
        const defaultTitle = (curLang === 'kn') ? 'ಹೊಸ ಕೃಷಿ ಸಮಾಲೋಚನೆ' 
                           : (curLang === 'te' ? 'కొత్త వ్యవసాయ సంప్రదింపు' : 'New Farming Consultation');
        try {
            const resp = await fetch('/api/conversations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    language: curLang,
                    title: defaultTitle
                })
            });
            const data = await resp.json();

            if (data.success && data.conversation) {
                activeConversationId = data.conversation.conversation_id;
                localStorage.setItem('uzhavar_active_conv_id', activeConversationId);

                // Reload list
                const listResp = await fetch('/api/conversations');
                const listData = await listResp.json();
                if (listData.success) {
                    renderConversationsList(listData.conversations);
                }

                if (selectAfter) {
                    await selectConversation(activeConversationId, true);
                }
            }
        } catch (e) {
            console.error('[FarmingAssistant] Error creating new conversation:', e);
        }
    }

    // Select and Load an Existing Conversation
    async function selectConversation(convId, autoFocus = true) {
        if (!convId) return;
        audioCtrl.interruptCurrentPlayback();

        activeConversationId = convId;
        localStorage.setItem('uzhavar_active_conv_id', convId);

        // Highlight active item in sidebar
        document.querySelectorAll('.conv-item').forEach(el => {
            el.classList.toggle('active', el.getAttribute('data-id') === convId);
        });

        try {
            const resp = await fetch(`/api/conversations/${convId}`);
            const data = await resp.json();

            if (data.success && data.conversation) {
                const conv = data.conversation;
                cachedCurrentConv = conv;

                // Sync language selector if stored
                if (conv.selected_language && assistantLangSelect.value !== conv.selected_language) {
                    assistantLangSelect.value = conv.selected_language;
                }

                if (activeConvBadge) {
                    activeConvBadge.textContent = `🌾 ${conv.conversation_title || t('active_chat_badge')}`;
                }

                // Render Messages
                renderChatThread(conv.messages || []);
            }
        } catch (e) {
            console.error('[FarmingAssistant] Error loading conversation details:', e);
        }

        if (autoFocus && assistantTextInput) {
            assistantTextInput.focus();
        }
    }

    // Delete Conversation Confirmation
    async function confirmAndDeleteConversation(convId, title) {
        const confirmed = confirm(`${t('delete_confirm')}\n\n"${title}"`);
        if (!confirmed) return;

        audioCtrl.interruptCurrentPlayback();
        try {
            const resp = await fetch(`/api/conversations/${convId}`, { method: 'DELETE' });
            const data = await resp.json();

            if (data.success) {
                if (activeConversationId === convId) {
                    activeConversationId = null;
                    localStorage.removeItem('uzhavar_active_conv_id');
                }
                // Refresh list
                await initConversationStore();
            }
        } catch (e) {
            console.error('[FarmingAssistant] Error deleting conversation:', e);
        }
    }

    // Clear Messages in Current Active Conversation
    if (btnClearConversation) {
        btnClearConversation.addEventListener('click', async () => {
            if (!activeConversationId) return;
            const confirmed = confirm(t('clear_confirm'));
            if (!confirmed) return;

            audioCtrl.interruptCurrentPlayback();
            try {
                const resp = await fetch(`/api/conversations/${activeConversationId}/clear`, { method: 'POST' });
                const data = await resp.json();

                if (data.success) {
                    renderChatThread([]);
                    // Refresh sidebar
                    const listResp = await fetch('/api/conversations');
                    const listData = await listResp.json();
                    if (listData.success) renderConversationsList(listData.conversations);
                }
            } catch (e) {
                console.error('[FarmingAssistant] Error clearing messages:', e);
            }
        });
    }

    // New Chat Button
    if (btnNewChat) {
        btnNewChat.addEventListener('click', () => {
            createNewConversation(true);
        });
    }

    // =========================================================================
    // 2. CHAT THREAD RENDERING (CHRONOLOGICAL USER & ASSISTANT BUBBLES)
    // =========================================================================

    function renderChatThread(messages) {
        if (!chatMessagesList) return;
        chatMessagesList.innerHTML = '';

        if (!messages || messages.length === 0) {
            if (assistantInitialState) assistantInitialState.style.display = 'block';
            return;
        }

        if (assistantInitialState) assistantInitialState.style.display = 'none';

        messages.forEach((msg) => {
            appendMessageBubble(msg, false);
        });

        // Scroll to bottom
        scrollChatToBottom();
    }

    function appendMessageBubble(msg, animateScroll = true) {
        if (assistantInitialState) assistantInitialState.style.display = 'none';

        const isUser = msg.sender === 'user';
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`;
        const timeStr = formatTimestamp(msg.timestamp);

        if (isUser) {
            const typeText = msg.message_type === 'voice' ? `🎙️ ${t('voice_tag')}` : `⌨️ ${t('text_tag')}`;
            bubble.innerHTML = `
                <div class="chat-bubble-header">
                    <span>🧑‍🌾 ${escapeHtml(t('farmer_role'))}</span>
                    <span style="color: #64748b; font-weight: normal; font-size: 0.72rem;">${typeText} • ${timeStr}</span>
                </div>
                <div class="chat-bubble-body">
                    ${escapeHtml(msg.message_text)}
                </div>
            `;
        } else {
            const bubbleId = `reply_${msg.message_id || Math.random().toString(36).substring(2, 9)}`;
            bubble.innerHTML = `
                <div class="chat-bubble-header">
                    <span>🌾 ${escapeHtml(t('expert_role'))}</span>
                    <span style="color: #64748b; font-weight: normal; font-size: 0.72rem;">🕒 ${timeStr}</span>
                </div>
                <div class="chat-bubble-body">
                    ${renderMarkdown(msg.message_text)}
                </div>
                <!-- Safety Notice -->
                <div style="background: #fffbeb; border-left: 3px solid #f59e0b; padding: 8px 12px; border-radius: 0 6px 6px 0; margin-top: 10px; font-size: 0.8rem; color: #92400e;">
                    <strong>⚠️ ${escapeHtml(t('safety_notice'))}</strong>
                </div>
                <!-- Playback & Audio Controls -->
                <div class="chat-bubble-footer">
                    <button class="btn-icon-action btn-audio-play" data-bubble-id="${bubbleId}" style="background: var(--primary-green); color: #fff;">
                        <span>🔊</span>
                        <span class="audio-btn-label">${escapeHtml(t('listen_voice'))}</span>
                    </button>
                    <button class="btn-icon-action btn-audio-stop" style="display: none; background: #fee2e2; color: #b91c1c;">
                        <span>⏹️</span>
                        <span>${escapeHtml(t('stop_voice'))}</span>
                    </button>
                    ${msg.timings_html ? msg.timings_html : ''}
                </div>
            `;

            // Attach play/stop listeners
            const playBtn = bubble.querySelector('.btn-audio-play');
            const stopBtn = bubble.querySelector('.btn-audio-stop');

            if (playBtn) {
                playBtn.addEventListener('click', () => {
                    playAssistantAnswer(msg.message_text, msg.audio_base64, playBtn, stopBtn);
                });
            }
            if (stopBtn) {
                stopBtn.addEventListener('click', () => {
                    audioCtrl.interruptCurrentPlayback();
                    playBtn.style.display = 'inline-flex';
                    stopBtn.style.display = 'none';
                });
            }
        }

        chatMessagesList.appendChild(bubble);

        if (animateScroll) {
            scrollChatToBottom();
        }
    }

    function scrollChatToBottom() {
        if (chatThreadContainer) {
            setTimeout(() => {
                chatThreadContainer.scrollTop = chatThreadContainer.scrollHeight;
            }, 60);
        }
    }

    function playAssistantAnswer(rawText, audioBase64, playBtn, stopBtn) {
        audioCtrl.interruptCurrentPlayback();
        const langCode = assistantLangSelect.value + '-IN';

        if (playBtn) playBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'inline-flex';

        audioCtrl.playAudio(
            audioBase64,
            rawText,
            langCode,
            // onAudioEnded
            () => {
                if (playBtn) playBtn.style.display = 'inline-flex';
                if (stopBtn) stopBtn.style.display = 'none';
            },
            // onPlaybackStarted
            (startupMs) => {
                console.log(`🔊 [Audio Playback Started] in ${startupMs}ms`);
            }
        );
    }

    // =========================================================================
    // 3. 5-STAGE VISUAL PROGRESS & AUDIO CONTROLLER HOOKS
    // =========================================================================

    audioCtrl.onStateChange((state, details) => {
        if (state === AudioState.RECORDING) {
            isRecording = true;
            assistantMicBtn.classList.add('recording');
            assistantVoiceStatus.className = 'voice-status-banner recording';
            assistantVoiceStatus.textContent = '🎤 ' + t('status_listening');
        } else if (state === AudioState.TRANSCRIBING) {
            assistantVoiceStatus.className = 'voice-status-banner';
            assistantVoiceStatus.textContent = '📝 ' + t('status_transcribing');
        } else if (state === AudioState.THINKING) {
            assistantVoiceStatus.className = 'voice-status-banner';
            assistantVoiceStatus.textContent = '🧠 ' + t('status_thinking');
        } else if (state === AudioState.GENERATING_AUDIO) {
            assistantVoiceStatus.className = 'voice-status-banner';
            assistantVoiceStatus.textContent = '🔊 ' + t('status_preparing_voice');
        } else if (state === AudioState.SPEAKING) {
            assistantVoiceStatus.className = 'voice-status-banner speaking';
            assistantVoiceStatus.textContent = '🗣️ ' + t('status_speaking');
        } else if (state === AudioState.LISTENING) {
            assistantMicBtn.classList.remove('recording');
            assistantVoiceStatus.className = 'voice-status-banner';
            assistantVoiceStatus.textContent = t('status_handsfree');
        } else if (state === AudioState.INTERRUPTED) {
            assistantVoiceStatus.className = 'voice-status-banner recording';
            assistantVoiceStatus.textContent = '⚡ ' + t('status_interrupted');
        } else if (state === AudioState.IDLE) {
            isRecording = false;
            assistantMicBtn.classList.remove('recording');
            assistantVoiceStatus.className = 'voice-status-banner';
            assistantVoiceStatus.textContent = t('status_ready');
        } else if (state === AudioState.ERROR) {
            isRecording = false;
            assistantMicBtn.classList.remove('recording');
            assistantVoiceStatus.className = 'voice-status-banner';
            assistantVoiceStatus.textContent = (details && details.message) || t('status_error');
        }
    });

    // Hands-Free Toggle
    if (assistantHandsFreeToggle) {
        assistantHandsFreeToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                audioCtrl.enableHandsFree((blob, reqId, liveTranscript, recDuration) => {
                    handleFarmingQuestion(blob, reqId, liveTranscript, recDuration);
                }, assistantLangSelect.value + '-IN');
            } else {
                audioCtrl.disableHandsFree();
            }
        });
    }

    // Main Mic Button Press (Tap to Speak + Immediate Interruption of ongoing speech)
    if (assistantMicBtn) {
        assistantMicBtn.addEventListener('click', () => {
            if (isRecording) {
                audioCtrl.stopRecording();
            } else {
                audioCtrl.startTapToSpeak((blob, reqId, liveTranscript, recDuration) => {
                    handleFarmingQuestion(blob, reqId, liveTranscript, recDuration);
                }, assistantLangSelect.value + '-IN');
            }
        });
    }

    // Text Submit buttons
    if (assistantSubmitBtn) {
        assistantSubmitBtn.addEventListener('click', () => {
            const text = assistantTextInput.value.trim();
            if (text) {
                audioCtrl.interruptCurrentPlayback();
                const reqId = ++audioCtrl.currentRequestId;
                assistantTextInput.value = "";
                handleFarmingQuestion(null, reqId, text, 0);
            }
        });
    }

    if (assistantTextInput) {
        assistantTextInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                assistantSubmitBtn.click();
            }
        });
    }

    // Quick Question Chips
    chipBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const q = btn.textContent.replace(/^[^\s]+\s*/, '').trim() || btn.getAttribute('data-q');
            if (q) {
                audioCtrl.interruptCurrentPlayback();
                const reqId = ++audioCtrl.currentRequestId;
                handleFarmingQuestion(null, reqId, q, 0);
            }
        });
    });

    // =========================================================================
    // 4. SUBMIT FARMING QUESTION WITH PERSISTENT SQLITE STORAGE
    // =========================================================================

    async function handleFarmingQuestion(audioBlob, reqId, textPrompt = null, recDurationMs = 0) {
        // Guarantee an active conversation exists
        if (!activeConversationId) {
            await createNewConversation(false);
        }

        audioCtrl.setState(AudioState.TRANSCRIBING);
        const tFetchStart = performance.now();

        // Immediately show optimistic user bubble if text is available
        if (textPrompt) {
            appendMessageBubble({
                sender: 'user',
                message_text: textPrompt,
                message_type: audioBlob ? 'voice' : 'text',
                timestamp: new Date().toISOString()
            });
        }

        const formData = new FormData();
        if (audioBlob) {
            formData.append('audio', audioBlob, 'farm_question.wav');
        }
        if (textPrompt) {
            formData.append('prompt', textPrompt);
            formData.append('text_hint', textPrompt);
        }
        formData.append('language', assistantLangSelect.value);
        formData.append('conversation_id', activeConversationId);

        audioCtrl.setState(AudioState.THINKING);

        fetch('/api/farming-question', {
            method: 'POST',
            body: formData,
            signal: audioCtrl.currentAbortController ? audioCtrl.currentAbortController.signal : null
        })
        .then(r => r.json())
        .then(data => {
            if (reqId !== audioCtrl.currentRequestId) return; // Stale response guard

            const tFetchEnd = performance.now();
            const turnaroundMs = Math.round(tFetchEnd - tFetchStart);

            if (data.success) {
                // If audio was transcribed remotely and we did not render optimistic bubble
                if (!textPrompt && data.question) {
                    appendMessageBubble({
                        sender: 'user',
                        message_text: data.question,
                        message_type: 'voice',
                        timestamp: new Date().toISOString()
                    });
                }

                const timings = data.timings || {};
                const timingsHtml = `
                    <div style="font-size: 0.72rem; color: #64748b; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 10px; border-radius: 4px; font-family: monospace;">
                        ⏱️ ${(turnaroundMs/1000).toFixed(2)}s [STT: ${timings.stt_ms || 0}ms | AI: ${timings.ai_ms || 0}ms | TTS: ${timings.tts_ms || 0}ms]
                    </div>
                `;

                // Append assistant bubble
                appendMessageBubble({
                    message_id: 'ans_' + Math.random().toString(36).substring(2, 9),
                    sender: 'assistant',
                    message_text: data.answer,
                    audio_base64: data.audio_base64,
                    timestamp: new Date().toISOString(),
                    timings_html: timingsHtml
                });

                if (activeConvBadge && data.conversation_title) {
                    activeConvBadge.textContent = `🌾 ${data.conversation_title}`;
                }

                // Play synthesized speech automatically
                audioCtrl.setState(AudioState.GENERATING_AUDIO);
                const langCode = assistantLangSelect.value + '-IN';

                audioCtrl.playAudio(
                    data.audio_base64,
                    data.answer,
                    langCode,
                    null,
                    (startupMs) => {
                        console.log(
                            `⏱️ [LATENCY REPORT - FARMING ASSISTANT]\n` +
                            `  • Speech Turnaround: ${turnaroundMs}ms\n` +
                            `  • Playback Startup: ${startupMs}ms\n` +
                            `  • Total Wait: ${turnaroundMs + startupMs}ms`
                        );
                    }
                );

                // Refresh sidebar conversation list
                fetch('/api/conversations')
                    .then(r => r.json())
                    .then(listData => {
                        if (listData.success) renderConversationsList(listData.conversations);
                    });

            } else {
                audioCtrl.setState(AudioState.ERROR, { message: data.error || t('status_error') });
            }
        })
        .catch(err => {
            if (err.name === 'AbortError') {
                console.log('[FarmingAssistant] Request interrupted by user.');
            } else {
                console.error('[FarmingAssistant] Error:', err);
                audioCtrl.setState(AudioState.ERROR, { message: t('status_error') });
            }
        });
    }

    // =========================================================================
    // 5. HELPER UTILITIES & LANGUAGE REACTIVITY
    // =========================================================================

    function formatTimestamp(isoStr) {
        if (!isoStr) return '';
        try {
            const d = new Date(isoStr);
            return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return '';
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function renderMarkdown(text) {
        if (!text) return "";
        return text
            .replace(/^### (.*$)/gim, '<h4 style="color: #14532d; margin-top: 10px;">$1</h4>')
            .replace(/^## (.*$)/gim, '<h3 style="color: #14532d; margin-top: 12px;">$1</h3>')
            .replace(/^# (.*$)/gim, '<h2 style="color: #14532d; margin-top: 14px;">$1</h2>')
            .replace(/\*\*(.*?)\*\*/gim, '<strong style="color: #0f172a;">$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            .replace(/^([0-9]+\.)\s+(.*$)/gim, '<div style="margin-bottom: 6px;"><strong>$1</strong> $2</div>')
            .replace(/^[\*•\-]\s+(.*$)/gim, '<li style="margin-left: 20px;">$1</li>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');
    }

    // React to language switch immediately
    window.addEventListener('uzhavar:languageChanged', () => {
        if (cachedConversations && cachedConversations.length > 0) {
            renderConversationsList(cachedConversations);
        }
        if (!isRecording && assistantVoiceStatus) {
            assistantVoiceStatus.textContent = t('status_ready');
        }
    });

    // Start Everything!
    initConversationStore();
});
