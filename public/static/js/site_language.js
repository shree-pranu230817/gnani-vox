/**
 * GNANI VOX – Preferred Website Language & Dynamic Font Controller
 * Supports English, Kannada, Telugu, Tamil, Hindi and all regional languages.
 *
 * Powers two flagship services:
 * 1. VoxConnect – Universal Voice Translator
 * 2. KrishiGuide AI – Farmer Guidance Assistant
 */

(function () {
    'use strict';

    const STORAGE_KEY = 'gnanivox_site_lang';
    const DEFAULT_LANG = 'en'; // English is default

    // Clean, natural multilingual dictionary
    const I18N = {
        'en': {
            'font_family': "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",

            // Header & Navigation
            'brand_subtext': 'One Voice. Many Languages. No Barriers.',
            'nav_home': '🏠 Home',
            'nav_voxconnect': '🌐 VoxConnect',
            'nav_krishiguide': '🌿 KrishiGuide AI',
            'nav_about': 'ℹ️ About',
            // Legacy keys (keep for backward compat)
            'nav_farmer': '🌐 VoxConnect',
            'nav_assistant': '🌿 KrishiGuide AI',
            'status_active': '⚡ Powered by Gnani AI',
            'back_to_home': '← Back to Home',
            'pref_lang_title': 'Choose Preferred Website Language:',

            // Homepage Hero & Services (GNANI VOX)
            'hero_badge': '⚡ Powered by Gnani AI Voice Infrastructure',
            'hero_title': 'Break Language Barriers. Empower Every Farmer.',
            'hero_subtitle': 'Experience intelligent voice translation for everyone and practical AI-powered agricultural guidance for farmers, all in one platform.',
            'hero_btn_voxconnect': 'Open VoxConnect',
            'hero_btn_krishi': 'Ask KrishiGuide AI',
            'services_badge': 'CORE PLATFORM SERVICES',
            'services_heading': 'Two Flagship Voice AI Features',
            'services_subtext': 'Universal voice communication for everyday life, paired with dedicated intelligence for agricultural guidance.',

            's1_badge': 'FEATURE 1',
            's1_title': 'VoxConnect',
            's1_sub': 'Universal Voice Translator',
            's1_quote': 'Speak in Your Language. Understand Any Language.',
            's1_desc': 'Designed for everyone — farmers, workers, travellers, students, shopkeepers. Any two people speaking different languages can communicate naturally through real-time voice translation.',
            's1_f1_t': 'Real-time Speech-to-Text', 's1_f1_d': 'Gnani Prisma STT for 10+ Indian languages',
            's1_f2_t': 'AI-Powered Translation', 's1_f2_d': 'Gemini translates meaning, not just words',
            's1_f3_t': 'Natural Voice Output', 's1_f3_d': 'Gnani Timbre TTS in clear natural voice',
            's1_f4_t': 'Conversation Mode', 's1_f4_d': 'Two-person live dialogue with real-time switching',
            's1_btn': 'Open VoxConnect',

            's2_badge': 'FEATURE 2',
            's2_title': 'KrishiGuide AI',
            's2_sub': 'Farmer Guidance Assistant',
            's2_quote': 'Your Intelligent Agricultural Guidance Assistant.',
            's2_desc': 'Ask questions about crop diseases, pests, fertilizers, soil and irrigation by voice or text. KrishiGuide AI remembers your entire conversation and builds on it with follow-up questions.',
            's2_f1_t': 'Voice & Text Questions', 's2_f1_d': 'Ask farming questions in your language',
            's2_f2_t': 'Persistent Memory', 's2_f2_d': 'Remembers crop, age, symptoms across questions',
            's2_f3_t': 'Visual Crop Diagnosis', 's2_f3_d': 'Upload a photo to identify disease or pest',
            's2_f4_t': 'ICAR Grounded Answers', 's2_f4_d': 'Verified agricultural science via Gemini AI',
            's2_btn': 'Open KrishiGuide AI',

            'footer_tagline': 'AI-Powered Voice Communication & Agricultural Guidance',

            // How it Works section
            'how_badge': 'HOW IT WORKS',
            'how_title': 'Four Simple Steps',
            'how_subtext': 'From speaking to receiving a translated voice answer in seconds',
            'step1_title': 'Speak', 'step1_desc': 'Press the mic and speak naturally in your language',
            'step2_title': 'Transcribe', 'step2_desc': 'Gnani Prisma STT converts speech to text instantly',
            'step3_title': 'Translate / Answer', 'step3_desc': 'Gemini AI translates or answers your farming question',
            'step4_title': 'Listen', 'step4_desc': 'Gnani Timbre TTS speaks the result in natural voice',

            // Highlights
            'hi1_title': '10+ Languages', 'hi1_desc': 'All major Indian languages supported',
            'hi2_title': 'Real-time Voice', 'hi2_desc': 'Near-instant speech recognition and synthesis',
            'hi3_title': 'Farming Memory', 'hi3_desc': 'Remembers your complete farming context',
            'hi4_title': 'No Internet Required', 'hi4_desc': 'Core features work on low-bandwidth connections',

            // VoxConnect screen
            'vox_title': '🌐 VoxConnect – Universal Voice Translator',
            'vox_subtitle': 'Speak in Your Language. Understand Any Language. For everyone — travellers, workers, students, shopkeepers and more.',
            'quick_vox_phrases': 'Quick Phrases:',
            'qv_1': '🏥 Where is the nearest hospital?',
            'qv_2': '💰 How much does this cost?',
            'qv_3': '🆘 I need help, please.',
            'qv_4': '🚌 What is the bus fare to the city?',
            'qv_5': '🧾 Can I get a receipt for this?',
            'qv_6': '👷 What is today\'s work schedule?',

            // KrishiGuide AI screen
            'krishi_title': '🌿 KrishiGuide AI – Farmer Guidance Assistant',
            'krishi_subtitle': 'Your Intelligent Agricultural Guidance Assistant. Ask any question about crops, fertilizers, pests, plant diseases and irrigation – with permanent conversation memory.',

            // AI Farming Assistant / KrishiGuide Screen
            'fa_title': 'KrishiGuide AI – Farmer Guidance Assistant',
            'fa_subtitle': 'Ask any question about crops, fertilizers, pest control, plant diseases and irrigation – with permanent conversation memory.',
            'clear_chat_btn': 'Clear Chat',
            'active_chat_badge': 'Active Consultation',
            'new_chat_btn': 'New Consultation',
            'prev_chats_title': 'Previous Consultations',
            'no_past_chats': 'No past consultations yet',
            'response_lang_label': 'Response Language:',
            'handsfree_label': 'Hands-Free Mode',
            'fa_input_placeholder': 'Type your farming question (e.g., I am growing paddy, 30 days old, leaves are yellow)...',
            'ask_ai_btn': 'Ask AI',
            'fa_welcome_title': 'Welcome! Ask Your Farming Questions',
            'fa_welcome_desc': 'Speak or type your agricultural questions. The assistant remembers your crop name, age, soil type, and symptoms across all follow-up questions.',
            'fa_chips_label': 'Frequently Asked Questions:',
            'chip_paddy': 'I am growing paddy',
            'chip_age': 'Crop is 30 days old',
            'chip_yellow': 'Leaves are turning yellow',
            'chip_fert': 'What fertilizer should I use?',
            'chip_pest': 'How to control stem borers?',
            'chip_water': 'Recommended irrigation schedule?',
            'farmer_role': 'Farmer',
            'expert_role': 'KrishiGuide AI Agri-Expert (ICAR Grounded)',
            'voice_tag': 'Voice',
            'text_tag': 'Text',
            'msg_count_single': '1 message',
            'msg_count_plural': '{n} messages',
            'safety_notice': 'Always check chemical product container labels before applying fertilizers or pesticides. For serious field problems, consult your nearest Krishi Vigyan Kendra (KVK).',
            'listen_voice': 'Listen to Answer',
            'stop_voice': 'Stop',
            
            // Audio Status States
            'status_ready': 'Ready to speak',
            'status_listening': 'Listening to your voice...',
            'status_transcribing': 'Transcribing speech to text...',
            'status_thinking': 'Formulating scientific agricultural guidance...',
            'status_preparing_voice': 'Preparing voice response...',
            'status_speaking': 'Speaking answer...',
            'status_interrupted': 'Interrupted – listening to new question...',
            'status_handsfree': 'Hands-free active – speak your question',
            'status_error': 'An error occurred. Please try again.',
            'clear_confirm': 'Are you sure you want to clear all messages in this conversation?',
            'delete_confirm': 'Are you sure you want to delete this consultation?',

            // Farmer Translator Screen
            'farmer_title': 'Farmer Voice Translator',
            'farmer_subtitle': 'Speak about crops, fertilizers, pesticides, market prices and labor – get immediate translated voice.',
            'clear_conv_btn': 'Clear Conversation',
            'my_lang_label': 'My Language:',
            'translate_to_label': 'Translate To:',
            'mode_label': 'Mode:',
            'mode_tap': 'Tap to Speak',
            'mode_handsfree': 'Hands-Free Mode',
            'source_box_title': 'Original Speech:',
            'target_box_title': 'Translated Speech:',
            'source_placeholder': 'Your spoken words will appear here...',
            'target_placeholder': 'Translated text and audio will appear here...',
            'copy_btn': 'Copy',
            'play_btn': 'Play Audio',
            'stop_btn': 'Stop',
            'quick_farmer_phrases': 'Quick Farming Phrases:',
            'qf_1': 'What is the recommended fertilizer for paddy?',
            'qf_2': 'Tomato leaves are turning yellow, what should I do?',
            'qf_3': 'What is the current mandi price for ragi?',
            'qf_4': 'Are drip irrigation pipes available?',
            'qf_5': 'What is the tractor rental rate per day?',
            'qf_6': 'We need four workers for weeding tomorrow.'
        },

        'kn': {
            'font_family': "'Noto Sans Kannada', 'Plus Jakarta Sans', sans-serif",
            
            // Header & Navigation
            'brand_subtext': 'ಕನ್ನಡ ಧ್ವನಿ ಸೇತು • ಕೃಷಿ ಸಂವಹನ ವೇದಿಕೆ',
            'nav_home': '🏠 ಮುಖಪುಟ',
            'nav_farmer': '🌐 VoxConnect',
            'nav_assistant': '🌿 KrishiGuide AI',
            'nav_voxconnect': '🌐 VoxConnect',
            'nav_krishiguide': '🌿 KrishiGuide AI',
            'nav_about': 'ℹ️ ನಮ್ಮ ಬಗ್ಗೆ',
            'status_active': 'Gnani AI ಸಕ್ರಿಯವಾಗಿದೆ',
            'back_to_home': '← ಮುಖಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಿ',
            'pref_lang_title': 'ವೆಬ್‌ಸೈಟ್‌ಗೆ ಆದ್ಯತೆಯ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:',
            
            // Homepage Hero & Services
            'hero_tagline': 'ಕನ್ನಡ ಧ್ವನಿ ಸೇತು • ಬಹುಭಾಷಾ ಸಂವಹನ ವೇದಿಕೆ',
            'hero_title': 'UZHAVAR AI – ಧ್ವನಿ ಸೇತು',
            'hero_subtitle': 'ರೈತರ ನೈಜ ಸಂವಹನ ಮತ್ತು ಬೆಳೆ ನಿರ್ವಹಣೆ ಸಮಸ್ಯೆಗಳನ್ನು ನಿವಾರಿಸುವ ಅತ್ಯಾಧುನಿಕ ಧ್ವನಿ ತಂತ್ರಜ್ಞಾನ.',
            'services_heading': 'ಪ್ರಮುಖ ಸೇವೆಗಳು',
            'services_subtext': 'ನಿಮ್ಮ ಅಗತ್ಯಕ್ಕೆ ತಕ್ಕಂತೆ ಕೆಳಗಿನ ಸೇವೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ ಮತ್ತು ಧ್ವನಿಯ ಮೂಲಕ ಸುಲಭವಾಗಿ ಮಾತನಾಡಿ.',
            
            's1_badge': 'ಸೇವೆ ೧',
            's1_title': 'ರೈತರ ಧ್ವನಿ ಅನುವಾದಕ',
            's1_sub': 'ರೈತರಿಗಾಗಿ ನೈಜ ಸಮಯದ ಧ್ವನಿ ಅನುವಾದ',
            's1_desc': 'ಕೃಷಿ, ಬಿತ್ತನೆ ಬೀಜಗಳು, ರಸಗೊಬ್ಬರ, ಕ್ರಿಮಿನಾಶಕ, ಯಂತ್ರೋಪಕರಣಗಳು, ಬೆಳೆ ಸಾಗಾಣಿಕೆ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಮಾರಾಟದ ಕುರಿತು ಬೇರೆ ಭಾಷೆಯ ಜನರೊಂದಿಗೆ ನಿಮ್ಮದೇ ಭಾಷೆಯಲ್ಲಿ ಮಾತನಾಡಿ.',
            's1_feat1': 'ಬೆಳೆ ಮತ್ತು ಕೃಷಿ ನಿರ್ವಹಣೆ ಸಂಭಾಷಣೆ',
            's1_feat2': 'ಗೊಬ್ಬರ, ಕೀಟನಾಶಕ ಮತ್ತು ಯಂತ್ರೋಪಕರಣ ಖರೀದಿ',
            's1_feat3': 'ಕನ್ನಡ ಮತ್ತು 10 ಪ್ರಾದೇಶಿಕ ಭಾಷೆಗಳಲ್ಲಿ ಧ್ವನಿ ಅನುವಾದ',
            's1_feat4': 'ನೈಜ ಸಮಯದ Gnani Prisma STT + Timbre TTS',
            's1_btn': 'ರೈತ ಅನುವಾದಕ ತೆರೆಯಿರಿ',
            
            's2_badge': 'ಸೇವೆ ೨',
            's2_title': 'AI ಕೃಷಿ ಪ್ರಶ್ನೋತ್ತರ ಸಹಾಯಕ',
            's2_sub': 'ಶಾಶ್ವತ ಸಂಭಾಷಣಾ ಸ್ಮರಣೆಯೊಂದಿಗೆ ಕೃಷಿ ಮಾರ್ಗದರ್ಶಿ',
            's2_desc': 'ಬೆಳೆ ರೋಗಗಳು, ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ, ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ ಮತ್ತು ಜೈವಿಕ ಕೃಷಿ ಕುರಿತು ಪ್ರಶ್ನೆಗಳನ್ನು ಧ್ವನಿ ಮೂಲಕ ಕೇಳಿ. ICAR ಆಧಾರಿತ ವೈಜ್ಞಾನಿಕ ಉತ್ತರ ಪಡೆಯಿರಿ.',
            's2_feat1': 'ಧ್ವನಿ ಅಥವಾ ಪಠ್ಯದಲ್ಲಿ ಕೃಷಿ ಪ್ರಶ್ನೆ ಕೇಳಿ',
            's2_feat2': 'ಮುಂದುವರಿದ ಪ್ರಶ್ನೆಗಳ ಸಂದರ್ಭ ನೆನಪಿಟ್ಟುಕೊಳ್ಳುತ್ತದೆ',
            's2_feat3': 'Gnani Timbre ಧ್ವನಿಯಲ್ಲಿ ಉತ್ತರವನ್ನು ಆಲಿಸಿ',
            's2_feat4': 'ನೈಜ AI (Gemini / ICAR ವೈಜ್ಞಾನಿಕ ಮಾರ್ಗದರ್ಶಿ)',
            's2_btn': 'AI ಕೃಷಿ ಸಹಾಯಕ ತೆರೆಯಿರಿ',
            
            'footer_tagline': 'ರೈತರಿಗಾಗಿ ಧ್ವನಿ ತಂತ್ರಜ್ಞಾನ ಹಾಗೂ AI ಕೃಷಿ ಮಾರ್ಗದರ್ಶನ',

            // AI Farming Assistant Screen
            'fa_title': 'AI ಕೃಷಿ ಪ್ರಶ್ನೋತ್ತರ ಸಹಾಯಕ',
            'fa_subtitle': 'ಬೆಳೆಗಳು, ಬೀಜ, ಗೊಬ್ಬರ, ರೋಗಗಳು, ಕೀಟನಾಶಕ ಮತ್ತು ನೀರಾವರಿ ಬಗ್ಗೆ ಯಾವುದೇ ಪ್ರಶ್ನೆ ಕೇಳಿ – ಶಾಶ್ವತ ಸಂಭಾಷಣಾ ಸ್ಮರಣೆಯೊಂದಿಗೆ ನಿಖರ ಉತ್ತರ ಪಡೆಯಿರಿ.',
            'clear_chat_btn': 'ಸಂಭಾಷಣೆ ಅಳಿಸಿ',
            'active_chat_badge': 'ಸಕ್ರಿಯ ಸಮಾಲೋಚನೆ',
            'new_chat_btn': 'ಹೊಸ ಸಮಾಲೋಚನೆ',
            'prev_chats_title': 'ಹಿಂದಿನ ಸಮಾಲೋಚನೆಗಳು',
            'no_past_chats': 'ಯಾವುದೇ ಹಿಂದಿನ ಸಮಾಲೋಚನೆಗಳಿಲ್ಲ',
            'response_lang_label': 'ಉತ್ತರದ ಭಾಷೆ:',
            'handsfree_label': 'ಹ್ಯಾಂಡ್ಸ್-ಫ್ರೀ ಮೋಡ್',
            'fa_input_placeholder': 'ಪ್ರಶ್ನೆ ಟೈಪ್ ಮಾಡಿ (ಉದಾ: ನಾನು ಭತ್ತ ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ, 30 ದಿನವಾಗಿದೆ, ಎಲೆ ಹಳದಿಯಾಗಿದೆ)...',
            'ask_ai_btn': 'ಕೇಳಿ',
            'fa_welcome_title': 'ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ',
            'fa_welcome_desc': 'ಧ್ವನಿ ಅಥವಾ ಪಠ್ಯದ ಮೂಲಕ ಪ್ರಶ್ನೆ ಕೇಳಿ. ಕೃಷಿ ಸಂದರ್ಭ, ಬೆಳೆ, ಬೆಳವಣಿಗೆಯ ಹಂತ ಮತ್ತು ರೋಗದ ಲಕ್ಷಣಗಳನ್ನು ನೆನಪಿಟ್ಟುಕೊಂಡು AI ಸಹಾಯಕ ನಿರಂತರವಾಗಿ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತದೆ.',
            'fa_chips_label': 'ಸಾಮಾನ್ಯ ಕೃಷಿ ಪ್ರಶ್ನೆಗಳು:',
            'chip_paddy': 'ನಾನು ಭತ್ತ ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ',
            'chip_age': 'ಬೆಳೆಗೆ 30 ದಿನವಾಗಿದೆ',
            'chip_yellow': 'ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ',
            'chip_fert': 'ಯಾವ ರಸಗೊಬ್ಬರ ಬಳಸಬೇಕು?',
            'chip_pest': 'ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು ನಿವಾರಣೆ ಹೇಗೆ?',
            'chip_water': 'ನೀರಾವರಿ ಎಷ್ಟು ದಿನಕ್ಕೊಮ್ಮೆ ನೀಡಬೇಕು?',
            'farmer_role': 'ರೈತರು',
            'expert_role': 'UZHAVAR AI ಕೃಷಿ ತಜ್ಞರು (ICAR ಆಧಾರಿತ)',
            'voice_tag': 'ಧ್ವನಿ',
            'text_tag': 'ಪಠ್ಯ',
            'msg_count_single': '೧ ಸಂದೇಶ',
            'msg_count_plural': '{n} ಸಂದೇಶಗಳು',
            'safety_notice': 'ರಸಗೊಬ್ಬರ ಅಥವಾ ಕೀಟನಾಶಕ ಬಳಸುವ ಮುನ್ನ ಬಾಟಲಿ ಮೇಲಿನ ಲೇಬಲ್ ಪರಿಶೀಲಿಸಿ. ಸಂದೇಹವಿದ್ದರೆ ಸಮೀಪದ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು (KVK) ಸಂಪರ್ಕಿಸಿ.',
            'listen_voice': 'ಉತ್ತರವನ್ನು ಆಲಿಸಿ',
            'stop_voice': 'ನಿಲ್ಲಿಸಿ',
            
            // Audio Status States
            'status_ready': 'ಮಾತನಾಡಲು ಸಿದ್ಧರಾಗಿ',
            'status_listening': 'ಧ್ವನಿ ರೆಕಾರ್ಡ್ ಆಗುತ್ತಿದೆ... (ಮಾತನಾಡಿ)',
            'status_transcribing': 'ಧ್ವನಿ ಪಠ್ಯವಾಗಿ ಪರಿವರ್ತಿಸಲಾಗುತ್ತಿದೆ...',
            'status_thinking': 'ಕೃಷಿ ವಿಜ್ಞಾನ ಆಧಾರದಲ್ಲಿ ಯೋಚಿಸಲಾಗುತ್ತಿದೆ...',
            'status_preparing_voice': 'ಧ್ವನಿ ಸಿದ್ಧಪಡಿಸಲಾಗುತ್ತಿದೆ...',
            'status_speaking': 'AI ಉತ್ತರಿಸುತ್ತಿದೆ...',
            'status_interrupted': 'ಹಿಂದಿನ ಉತ್ತರ ನಿಲ್ಲಿಸಲಾಗಿದೆ – ಹೊಸ ಪ್ರಶ್ನೆ ಕೇಳಲಾಗುತ್ತಿದೆ...',
            'status_handsfree': 'ಹ್ಯಾಂಡ್ಸ್-ಫ್ರೀ ಸಕ್ರಿಯವಾಗಿದೆ – ಪ್ರಶ್ನೆ ಕೇಳಿ',
            'status_error': 'ದೋಷ ಸಂಭವಿಸಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.',
            'clear_confirm': 'ಪ್ರಸ್ತುತ ಸಮಾಲೋಚನೆಯ ಎಲ್ಲಾ ಸಂದೇಶಗಳನ್ನು ಅಳಿಸಬೇಕೇ?',
            'delete_confirm': 'ಈ ಸಮಾಲೋಚನೆಯನ್ನು ಶಾಶ್ವತವಾಗಿ ಅಳಿಸಬೇಕೇ?',

            // Farmer Translator Screen
            'farmer_title': 'ರೈತರ ಧ್ವನಿ ಅನುವಾದಕ',
            'farmer_subtitle': 'ಬೆಳೆಗಳು, ಗೊಬ್ಬರ, ಕೀಟನಾಶಕ, ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮತ್ತು ಕೂಲಿ ಕಾರ್ಮಿಕರ ಕುರಿತು ಮಾತನಾಡಿ – ತಕ್ಷಣ ಅನುವಾದಿತ ಧ್ವನಿ ಪಡೆಯಿರಿ.',
            'clear_conv_btn': 'ಹೊಸ ಸಂಭಾಷಣೆ',
            'my_lang_label': 'ನನ್ನ ಭಾಷೆ:',
            'translate_to_label': 'ಅನುವಾದಿಸಬೇಕಾದ ಭಾಷೆ:',
            'mode_label': 'ಮೋಡ್:',
            'mode_tap': 'ಟ್ಯಾಪ್ ಮಾಡಿ ಮಾತನಾಡಿ',
            'mode_handsfree': 'ಹ್ಯಾಂಡ್ಸ್-ಫ್ರೀ ಸಂಭಾಷಣೆ',
            'source_box_title': 'ಮೂಲ ಭಾಷಣ:',
            'target_box_title': 'ಅನುವಾದಿತ ಮಾತು:',
            'source_placeholder': 'ನಿಮ್ಮ ಮಾತು ಇಲ್ಲಿ ಪಠ್ಯವಾಗಿ ಕಾಣಿಸುತ್ತದೆ...',
            'target_placeholder': 'ಅನುವಾದಿತ ಪಠ್ಯ ಮತ್ತು ಧ್ವನಿ ಇಲ್ಲಿ ಲಭ್ಯವಾಗುತ್ತದೆ...',
            'copy_btn': 'ನಕಲಿಸಿ',
            'play_btn': 'ಆಲಿಸಿ',
            'stop_btn': 'ನಿಲ್ಲಿಸಿ',
            'quick_farmer_phrases': 'ತ್ವರಿತ ಕೃಷಿ ಸಂಭಾಷಣೆಗಳು:',
            'qf_1': 'ಭತ್ತಕ್ಕೆ ಯಾವ ರಸಗೊಬ್ಬರ ಸೂಕ್ತವಾಗಿದೆ?',
            'qf_2': 'ಟೊಮ್ಯಾಟೊ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ, ಏನು ಮಾಡಬೇಕು?',
            'qf_3': 'ಒಂದು ಕ್ವಿಂಟಾಲ್ ರಾಗಿಗೆ ಬೆಲೆ ಎಷ್ಟು?',
            'qf_4': 'ಹನಿ ನೀರಾವರಿ ಪೈಪ್‌ಗಳು ಲಭ್ಯವಿದೆಯೇ?',
            'qf_5': 'ಟ್ರ್ಯಾಕ್ಟರ್ ಬಾಡಿಗೆಗೆ ದಿನಕ್ಕೆ ಎಷ್ಟು ದರ?',
            'qf_6': 'ಕಳೆ ಕೀಳಲು ನಾಲ್ಕು ಮಂದಿ ಕಾರ್ಮಿಕರು ಬೇಕಾಗಿದ್ದಾರೆ.'
        },

        'te': {
            'font_family': "'Noto Sans Telugu', 'Plus Jakarta Sans', sans-serif",
            
            // Header & Navigation
            'brand_subtext': 'రైతుల బహుభాషా వాయిస్ బ్రిడ్జ్ & AI అసిస్టెంట్',
            'nav_home': '🏠 హోమ్',
            'nav_farmer': '🌐 VoxConnect',
            'nav_assistant': '🌿 KrishiGuide AI',
            'nav_voxconnect': '🌐 VoxConnect',
            'nav_krishiguide': '🌿 KrishiGuide AI',
            'nav_about': 'ℹ️ మా గురించి',
            'status_active': 'Gnani AI చురుకుగా ఉంది',
            'back_to_home': '← హోమ్‌కి తిరిగి వెళ్ళండి',
            'pref_lang_title': 'వెబ్‌సైట్ ప్రాధాన్యత భాషను ఎంచుకోండి:',
            
            // Homepage Hero & Services
            'hero_tagline': 'బహుభాషా వాయిస్ బ్రిడ్జ్ • సంభాషణ వేదిక',
            'hero_title': 'UZHAVAR AI – వాయిస్ బ్రిడ్జ్',
            'hero_subtitle': 'రైతుల భాషా సమస్యలను పరిష్కరించే అధునాతన బహుభాషా వాయిస్ టెక్నాలజీ మరియు వ్యవసాయ సహాయం.',
            'services_heading': 'ముఖ్యమైన సేవలు',
            'services_subtext': 'మీ అవసరానికి సరిపోయే సేవను ఎంచుకోండి మరియు మీ స్వంత భాషలో సులభంగా మాట్లాడండి.',
            
            's1_badge': 'సేవ 1',
            's1_title': 'రైతు వాయిస్ అనువాదకుడు',
            's1_sub': 'రైతుల కోసం రియల్-టైమ్ వాయిస్ అనువాదం',
            's1_desc': 'పంటలు, విత్తనాలు, ఎరువులు, పురుగుమందులు, యంత్రాలు మరియు మార్కెట్ ధరల గురించి ఇతర భాషల వ్యక్తులతో మీ స్వంత భాషలోనే మాట్లాడండి.',
            's1_feat1': 'పంటలు మరియు సాగు సంభాషణలు',
            's1_feat2': 'ఎరువులు, పురుగుమందుల కొనుగోలు',
            's1_feat3': '10 భారతీయ భాషల్లో వాయిస్ అనువాదం',
            's1_feat4': 'రియల్-టైమ్ Gnani Prisma STT + Timbre TTS',
            's1_btn': 'రైతు అనువాదకుడు తెరవండి',
            
            's2_badge': 'సేవ 2',
            's2_title': 'AI వ్యవసాయ సహాయకుడు',
            's2_sub': 'వ్యవసాయ సమస్యల శాశ్వత పరిష్కారాలు',
            's2_desc': 'పంటల తెగుళ్లు, ఎరువులు, నీటి యాజమాన్యం మరియు సేంద్రీయ వ్యవసాయంపై ప్రశ్నలను వాయిస్ ద్వారా అడగండి. ICAR ఆధారిత శాస్త్రీయ సమాధానాలు పొందండి.',
            's2_feat1': 'వాయిస్ లేదా టెక్స్ట్ ద్వారా ప్రశ్నలు అడగండి',
            's2_feat2': 'తదుపరి ప్రశ్నలకు పూర్తి మెమరీ',
            's2_feat3': 'సహజ వాయిస్‌లో సమాధానాలు వినండి',
            's2_feat4': 'ICAR & Gemini ఆధారిత విశ్వసనీయ సమాచారం',
            's2_btn': 'AI వ్యవసాయ సహాయకుడు తెరవండి',
            
            'footer_tagline': 'భారతీయ రైతుల కోసం వాయిస్ AI & వ్యవసాయ సలహాలు',

            // AI Farming Assistant Screen
            'fa_title': 'AI వ్యవసాయ ప్రశ్నల సహాయకుడు',
            'fa_subtitle': 'పంటలు, విత్తనాలు, ఎరువులు, తెగుళ్లు మరియు నీటి యాజమాన్యం గురించి ప్రశ్నలు అడగండి – శాశ్వత మెమరీతో ఖచ్చితమైన సమాధానాలు పొందండి.',
            'clear_chat_btn': 'సంభాషణ క్లియర్ చేయండి',
            'active_chat_badge': 'ప్రస్తుత సంభాషణ',
            'new_chat_btn': 'కొత్త సంభాషణ',
            'prev_chats_title': 'మునుపటి సంభాషణలు',
            'no_past_chats': 'ఇంతవరకు సంభాషణలు లేవు',
            'response_lang_label': 'సమాధాన భాష:',
            'handsfree_label': 'హ్యాండ్స్-ఫ్రీ మోడ్',
            'fa_input_placeholder': 'మీ వ్యవసాయ ప్రశ్నను టైప్ చేయండి (ఉదా: వరి సాగు చేస్తున్నాను, 30 రోజులు అయింది, ఆకులు పసుపు రంగులోకి మారాయి)...',
            'ask_ai_btn': 'అడగండి',
            'fa_welcome_title': 'నమస్కారం! మీ వ్యవసాయ ప్రశ్నలను అడగండి',
            'fa_welcome_desc': 'వాయిస్ లేదా టెక్స్ట్ ద్వారా ప్రశ్నలను అడగండి. AI సహాయకుడు మీ పంట పేరు, వయస్సు, నేల రకం మరియు లక్షణాలను గుర్తుంచుకుని సహాయం చేస్తుంది.',
            'fa_chips_label': 'సాధారణ వ్యవసాయ ప్రశ్నలు:',
            'chip_paddy': 'నేను వరి సాగు చేస్తున్నాను',
            'chip_age': 'పంటకు 30 రోజులు అయింది',
            'chip_yellow': 'ఆకులు పసుపు రంగులోకి మారుతున్నాయి',
            'chip_fert': 'ఏ ఎరువులు వేయాలి?',
            'chip_pest': 'కాండం తొలుచు పురుగు నివారణ ఎలా?',
            'chip_water': 'నీటి తడులు ఎన్ని రోజులకు ఇవ్వాలి?',
            'farmer_role': 'రైతు',
            'expert_role': 'UZHAVAR AI వ్యవసాయ నిపుణులు (ICAR ఆధారిత)',
            'voice_tag': 'వాయిస్',
            'text_tag': 'టెక్స్ట్',
            'msg_count_single': '1 సందేశం',
            'msg_count_plural': '{n} సందేశాలు',
            'safety_notice': 'రసాయన ఎరువులు లేదా పురుగుమందులు వాడే ముందు లేబుల్ పరిశీలించండి. సందేహాలుంటే సమీప కృషి విజ్ఞాన కేంద్రాన్ని (KVK) సంప్రదించండి.',
            'listen_voice': 'సమాధానం వినండి',
            'stop_voice': 'ఆపండి',
            
            // Audio Status States
            'status_ready': 'మాట్లాడటానికి సిద్ధంగా ఉంది',
            'status_listening': 'వాయిస్ రికార్డ్ అవుతోంది... (మాట్లాడండి)',
            'status_transcribing': 'వాయిస్ టెక్స్ట్‌గా మారుతోంది...',
            'status_thinking': 'వ్యవసాయ డేటాను విశ్లేషిస్తోంది...',
            'status_preparing_voice': 'వాయిస్ సిద్ధం చేస్తోంది...',
            'status_speaking': 'సమాధానం చెబుతోంది...',
            'status_interrupted': 'ఆపబడింది – కొత్త ప్రశ్న వింటోంది...',
            'status_handsfree': 'హ్యాండ్స్-ఫ్రీ యాక్టివ్‌గా ఉంది – మాట్లాడండి',
            'status_error': 'లోపం జరిగింది. దయచేసి మళ్లీ ప్రయత్నించండి.',
            'clear_confirm': 'ఈ సంభాషణలోని అన్ని సందేశాలను తొలగించాలా?',
            'delete_confirm': 'ఈ సంభాషణను శాశ్వతంగా తొలగించాలా?',

            // Farmer Translator Screen
            'farmer_title': 'రైతు వాయిస్ అనువాదకుడు',
            'farmer_subtitle': 'పంటలు, ఎరువులు, పురుగుమందులు, మార్కెట్ ధరలు మరియు కూలీల గురించి మాట్లాడండి – తక్షణ వాయిస్ అనువాదం పొందండి.',
            'clear_conv_btn': 'కొత్త సంభాషణ',
            'my_lang_label': 'నా భాష:',
            'translate_to_label': 'అనువదించాల్సిన భాష:',
            'mode_label': 'మోడ్:',
            'mode_tap': 'ట్యాప్ చేసి మాట్లాడండి',
            'mode_handsfree': 'హ్యాండ్స్-ఫ్రీ మోడ్',
            'source_box_title': 'మూల సంభాషణ:',
            'target_box_title': 'అనువాద సంభాషణ:',
            'source_placeholder': 'మీ మాటలు ఇక్కడ టెక్స్ట్‌గా కనిపిస్తాయి...',
            'target_placeholder': 'అనువాద టెక్స్ట్ మరియు వాయిస్ ఇక్కడ లభిస్తాయి...',
            'copy_btn': 'కాపీ',
            'play_btn': 'వినండి',
            'stop_btn': 'ఆపండి',
            'quick_farmer_phrases': 'ముఖ్యమైన వ్యవసాయ సంభాషణలు:',
            'qf_1': 'వరి పంటకు ఏ ఎరువు సరిపోతుంది?',
            'qf_2': 'టమోటా ఆకులు పసుపు రంగులోకి మారుతున్నాయి, ఏం చేయాలి?',
            'qf_3': 'క్వింటాల్ రాగుల ధర ఎంత ఉంది?',
            'qf_4': 'డ్రిప్ ఇరిగేషన్ పైపులు అందుబాటులో ఉన్నాయా?',
            'qf_5': 'ట్రాక్టర్ అద్దె రోజుకు ఎంత?',
            'qf_6': 'కలుపు తీయడానికి రేపు నలుగురు కూలీలు కావాలి.'
        },

        'ta': {
            'font_family': "'Noto Sans Tamil', 'Plus Jakarta Sans', sans-serif",
            'brand_subtext': 'விவசாயிகளுக்கான குரல் பாலம் மற்றும் வேளாண் நுண்ணறிவு',
            'nav_home': '🏠 முகப்பு',
            'nav_farmer': '🌾 உழவர் மொழிபெயர்ப்பாளர்',
            'nav_assistant': '🌿 AI வேளாண் உதவியாளர்',
            'status_active': 'Gnani AI செயலில் உள்ளது',
            'back_to_home': '← முகப்புக்குத் திரும்பு',
            'pref_lang_title': 'இணையதள விருப்ப மொழியைத் தேர்ந்தெடுக்கவும்:',
            'hero_tagline': 'பன்மொழி குரல் பாலம் • தொடர்பு தளம்',
            'hero_title': 'UZHAVAR AI – குரல் பாலம்',
            'hero_subtitle': 'விவசாயிகளின் மொழி தடைகளை அகற்றும் நவீன குரல் தொழில்நுட்பம்.',
            'services_heading': 'முக்கிய சேவைகள்',
            'services_subtext': 'உங்கள் தேவைக்கேற்ப சேவையைத் தேர்ந்தெடுத்து உங்கள் மொழியில் எளிதாகப் பேசுங்கள்.',
            's1_badge': 'சேவை 1',
            's1_title': 'உழவர் குரல் மொழிபெயர்ப்பாளர்',
            's1_sub': 'விவசாயிகளுக்கான நிகழ்நேர குரல் மொழிபெயர்ப்பு',
            's1_desc': 'பயிர்கள், விதைகள், உரங்கள், பூச்சிக்கொல்லிகள், இயந்திரங்கள் மற்றும் சந்தை விற்பனை பற்றி பிற மொழி பேசுபவர்களுடன் உங்கள் சொந்த மொழியிலேயே பேசுங்கள்.',
            's1_btn': 'உழவர் மொழிபெயர்ப்பாளர் திறக்க',
            's2_badge': 'சேவை 2',
            's2_title': 'AI வேளாண் உதவியாளர்',
            's2_sub': 'விவசாய கேள்விகளுக்கு குரல் வழி பதில்கள்',
            's2_desc': 'பயிர் நோய்கள், உரங்கள், நீர்ப்பாசனம் பற்றி குரல் மூலம் கேள்வி கேளுங்கள். விஞ்ஞான அடிப்படையிலான துல்லியமான பதில்களைப் பெறுங்கள்.',
            's2_btn': 'AI வேளாண் உதவியாளர் திறக்க',
            'footer_tagline': 'விவசாயிகளுக்கான குரல் AI',
            'fa_title': 'AI வேளாண் கேள்வி-பதில் உதவியாளர்',
            'fa_subtitle': 'பயிர்கள், உரங்கள், பூச்சிகள் மற்றும் நீர்ப்பாசனம் பற்றி கேளுங்கள் – முழு மெமரியுடன் துல்லியமான வழிகாட்டுதல் பெறுங்கள்.',
            'clear_chat_btn': 'உரையாடலை அழிக்க',
            'active_chat_badge': 'செயலில் உள்ள உரையாடல்',
            'new_chat_btn': 'புதிய உரையாடல்',
            'prev_chats_title': 'முந்தைய உரையாடல்கள்',
            'response_lang_label': 'பதில் மொழி:',
            'handsfree_label': 'ஹேண்ட்ஸ்-ஃப்ரீ பயன்முறை',
            'fa_input_placeholder': 'உங்கள் விவசாய கேள்வியைத் தட்டச்சு செய்க...',
            'ask_ai_btn': 'கேட்கவும்',
            'status_ready': 'பேசத் தயாராக உள்ளது',
            'msg_count_single': '1 செய்தி',
            'msg_count_plural': '{n} செய்திகள்'
        },

        'hi': {
            'font_family': "'Noto Sans Devanagari', 'Plus Jakarta Sans', sans-serif",
            'brand_subtext': 'किसानों के लिए वाणी सेतु एवं कृषि बुद्धिमत्ता',
            'nav_home': '🏠 मुख्य पृष्ठ',
            'nav_farmer': '🌾 किसान अनुवादक',
            'nav_assistant': '🌿 AI कृषि सहायक',
            'status_active': 'Gnani AI सक्रिय है',
            'back_to_home': '← मुख्य पृष्ठ पर वापस जाएं',
            'pref_lang_title': 'वेबसाइट के लिए अपनी पसंदीदा भाषा चुनें:',
            'hero_tagline': 'बहुभाषी वाणी सेतु • संचार मंच',
            'hero_title': 'UZHAVAR AI – वाणी सेतु',
            'hero_subtitle': 'किसानों की भाषा संबंधी समस्याओं को दूर करने वाली आधुनिक बहुभाषी वॉइस तकनीक।',
            'services_heading': 'मुख्य सेवाएं',
            'services_subtext': 'अपनी आवश्यकतानुसार सेवा चुनें और अपनी भाषा में सहजता से बोलें।',
            's1_badge': 'सेवा 1',
            's1_title': 'किसान वॉइस अनुवादक',
            's1_sub': 'किसानों के लिए रियल-टाइम वॉइस अनुवाद',
            's1_desc': 'फसलों, बीजों, खादों, कीटनाशकों, कृषि उपकरणों और मंडी बिक्री के बारे में अपनी भाषा में सहज बातचीत करें।',
            's1_btn': 'किसान अनुवादक खोलें',
            's2_badge': 'सेवा 2',
            's2_title': 'AI कृषि सहायक',
            's2_sub': 'फसलों और खेती के लिए AI प्रश्नोत्तर सहायक',
            's2_desc': 'फसल रोग, खाद, सिंचाई और जैविक खेती से संबंधित कोई भी प्रश्न बोलकर पूछें और प्रमाणिक वैज्ञानिक उत्तर प्राप्त करें।',
            's2_btn': 'AI कृषि सहायक खोलें',
            'footer_tagline': 'भारतीय किसानों के लिए सशक्त वॉइस AI',
            'fa_title': 'AI कृषि प्रश्नोत्तर सहायक',
            'fa_subtitle': 'फसलों, खादों, कीटनाशकों और सिंचाई के बारे में कोई भी प्रश्न पूछें – स्थायी मेमोरी के साथ सटीक उत्तर प्राप्त करें।',
            'clear_chat_btn': 'चैट साफ करें',
            'active_chat_badge': 'सक्रिय परामर्श',
            'new_chat_btn': 'नया परामर्श',
            'prev_chats_title': 'पिछले परामर्श',
            'response_lang_label': 'उत्तर की भाषा:',
            'handsfree_label': 'हैंड्स-फ्री मोड',
            'fa_input_placeholder': 'अपना कृषि प्रश्न यहाँ लिखें (उदा: मैं धान उगा रहा हूँ, 30 दिन हो गए, पत्तियां पीली पड़ रही हैं)...',
            'ask_ai_btn': 'पूछें',
            'status_ready': 'बोलने के लिए तैयार',
            'msg_count_single': '1 संदेश',
            'msg_count_plural': '{n} संदेश'
        }
    };

    /**
     * Get preferred site language from localStorage or default
     */
    function getPreferredLanguage() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved && (saved in I18N || ['ml', 'bn', 'mr', 'gu', 'pa'].includes(saved))) {
                return saved;
            }
        } catch (e) {
            console.warn('[SiteLanguage] localStorage read failed:', e);
        }
        return DEFAULT_LANG;
    }

    /**
     * Translate a key with optional dynamic args
     */
    function t(key, arg = null) {
        const lang = getPreferredLanguage();
        const dict = I18N[lang] || I18N['en'] || I18N['kn'];
        let val = dict[key];
        if (!val && I18N['en']) val = I18N['en'][key];
        if (!val && I18N['kn']) val = I18N['kn'][key];
        if (!val) return key;

        if (arg !== null && typeof val === 'string') {
            val = val.replace('{n}', arg);
        }
        return val;
    }

    /**
     * Set and apply preferred site language and fonts
     */
    function setPreferredLanguage(langCode, syncInputs = true) {
        if (!langCode) return;
        langCode = langCode.toLowerCase().trim();

        try {
            localStorage.setItem(STORAGE_KEY, langCode);
        } catch (e) {
            console.warn('[SiteLanguage] localStorage write failed:', e);
        }

        // Apply HTML lang attribute and body data attribute
        document.documentElement.lang = langCode;
        document.body.setAttribute('data-site-lang', langCode);

        // Update active class on any language pill buttons
        const pillButtons = document.querySelectorAll('.lang-pill-btn');
        pillButtons.forEach(btn => {
            const btnLang = btn.getAttribute('data-lang');
            if (btnLang === langCode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Update header site language selector dropdown if present
        const siteSelector = document.getElementById('siteLanguageSelector');
        if (siteSelector && siteSelector.value !== langCode) {
            siteSelector.value = langCode;
        }

        // Apply translations to all DOM elements with data-i18n
        const dict = I18N[langCode] || I18N['en'] || I18N['kn'];
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                el.textContent = dict[key];
            }
        });

        // Apply translations to placeholders
        const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
        placeholderElements.forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (dict[key]) {
                el.placeholder = dict[key];
            }
        });

        // Apply translations to titles
        const titleElements = document.querySelectorAll('[data-i18n-title]');
        titleElements.forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            if (dict[key]) {
                el.title = dict[key];
            }
        });

        // If requested and on tool pages, synchronize default input or assistant language
        if (syncInputs) {
            const assistantLangSelect = document.getElementById('assistantLangSelect');
            if (assistantLangSelect && !assistantLangSelect.dataset.userExplicitlyChanged) {
                assistantLangSelect.value = langCode;
            }
            const sourceLangSelect = document.getElementById('sourceLangSelect');
            if (sourceLangSelect && !sourceLangSelect.dataset.userExplicitlyChanged) {
                sourceLangSelect.value = langCode;
            }
        }

        // Dispatch a custom event so other components can react
        window.dispatchEvent(new CustomEvent('uzhavar:languageChanged', {
            detail: { language: langCode, font: dict.font_family, t: t }
        }));
    }

    // Initialize on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', () => {
        const initialLang = getPreferredLanguage();

        // Bind header selector
        const siteSelector = document.getElementById('siteLanguageSelector');
        if (siteSelector) {
            siteSelector.value = initialLang;
            siteSelector.addEventListener('change', (e) => {
                setPreferredLanguage(e.target.value, true);
            });
        }

        // Bind homepage quick language pills
        const pillButtons = document.querySelectorAll('.lang-pill-btn');
        pillButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const lang = btn.getAttribute('data-lang');
                if (lang) {
                    setPreferredLanguage(lang, true);
                }
            });
        });

        // Track user explicit choices on tool pages
        ['assistantLangSelect', 'sourceLangSelect', 'targetLangSelect'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', () => {
                    el.dataset.userExplicitlyChanged = 'true';
                });
            }
        });

        // Apply initially saved preference
        setPreferredLanguage(initialLang, false);
    });

    // Expose API globally (backward compat: UzhavarLanguage alias preserved)
    window.GnaniVox = {
        getPreferredLanguage,
        setPreferredLanguage,
        t,
        dictionary: I18N
    };
    // Legacy alias so older JS files using window.UzhavarLanguage still work
    window.UzhavarLanguage = window.GnaniVox;
})();
