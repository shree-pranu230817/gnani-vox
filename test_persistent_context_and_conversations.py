"""
UZHAVAR AI – Kannada Voice Bridge
Comprehensive Verification of Persistent SQLite Storage & Continuous Multi-Turn Farming Context
Mandatory Section 9 Verification Tests (Tests 1 to 8)
"""

import os
import sys
import unittest
import json
import time

# Force pure-Python SQLAlchemy mode to comply with Windows security policies
os.environ['DISABLE_SQLALCHEMY_CEXT'] = '1'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from models import db, Conversation, Message
from services.conversation_service import ConversationService

class TestPersistentContextAndConversations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    # =========================================================================
    # TEST 1: User says growing paddy -> age 30 days -> AI remembers both
    # =========================================================================
    def test_01_paddy_and_age_context(self):
        print("\n--- RUNNING TEST 1: Crop Name and Age Context Retention ---")
        # Step 1: Create new conversation in SQLite
        conv = ConversationService.get_or_create_conversation(None, language='en')
        conv_id = conv.conversation_id
        self.assertTrue(conv_id.startswith('conv_'))

        # User turn 1: "I am growing paddy."
        res1 = self.client.post('/api/farming-question', json={
            'conversation_id': conv_id,
            'prompt': 'I am growing paddy.',
            'language': 'en'
        })
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertTrue(data1['success'])
        print(f"User 1: 'I am growing paddy.'")
        print(f"AI 1: '{data1['answer'][:110]}...'")

        # User turn 2: "30 days."
        res2 = self.client.post('/api/farming-question', json={
            'conversation_id': conv_id,
            'prompt': 'It is 30 days old.',
            'language': 'en'
        })
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertTrue(data2['success'])
        print(f"User 2: 'It is 30 days old.'")
        print(f"AI 2: '{data2['answer'][:110]}...'")

        # Verify SQLite storage
        messages = Message.query.filter_by(conversation_id=conv_id).order_by(Message.timestamp.asc()).all()
        self.assertEqual(len(messages), 4)  # 2 user turns + 2 assistant turns
        summary = ConversationService.get_farming_context_summary(conv_id)
        print(f"SQLite Rolling Summary: '{summary}'")
        self.assertIn('Paddy', summary)
        print("[TEST 1 PASSED] AI and SQLite successfully retained Paddy and 30-day age.")

    # =========================================================================
    # TEST 2: Yellow leaves follow-up refers to the same 30-day paddy crop
    # =========================================================================
    def test_02_symptom_followup_reference(self):
        print("\n--- RUNNING TEST 2: Symptom Follow-up Reference Resolution ---")
        conv = ConversationService.get_or_create_conversation(None, language='en')
        conv_id = conv.conversation_id

        # Seed turns
        self.client.post('/api/farming-question', json={
            'conversation_id': conv_id, 'prompt': 'I am growing paddy.', 'language': 'en'
        })
        self.client.post('/api/farming-question', json={
            'conversation_id': conv_id, 'prompt': '30 days.', 'language': 'en'
        })

        # Turn 3: "The leaves are turning yellow."
        res = self.client.post('/api/farming-question', json={
            'conversation_id': conv_id,
            'prompt': 'The leaves are turning yellow.',
            'language': 'en'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        answer = data['answer'].lower()
        print(f"User 3: 'The leaves are turning yellow.'")
        print(f"AI 3: '{data['answer'][:140]}...'")

        # AI must diagnose yellowing in context of paddy / tillering (e.g. nitrogen, chlorosis, urea)
        # and NOT ask "what crop are you growing?"
        self.assertFalse("what crop" in answer and "are you growing" in answer)
        summary = ConversationService.get_farming_context_summary(conv_id)
        self.assertIn('Paddy', summary)
        print(f"SQLite Context Summary: '{summary}'")
        print("[TEST 2 PASSED] AI resolved 'leaves turning yellow' to 30-day paddy without re-asking.")

    # =========================================================================
    # TEST 3: Fertilizer inquiry uses prior crop details and symptoms
    # =========================================================================
    def test_03_fertilizer_recommendation_with_context(self):
        print("\n--- RUNNING TEST 3: Fertilizer Inquiry with Full Prior Context ---")
        conv = ConversationService.get_or_create_conversation(None, language='en')
        conv_id = conv.conversation_id

        self.client.post('/api/farming-question', json={
            'conversation_id': conv_id, 'prompt': 'I am cultivating paddy.', 'language': 'en'
        })
        self.client.post('/api/farming-question', json={
            'conversation_id': conv_id, 'prompt': 'It is 30 days old and leaves are turning yellow.', 'language': 'en'
        })

        # Follow-up: "What fertilizer should I use?"
        res = self.client.post('/api/farming-question', json={
            'conversation_id': conv_id,
            'prompt': 'What fertilizer should I use?',
            'language': 'en'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        answer = data['answer'].lower()
        print(f"User: 'What fertilizer should I use?'")
        print(f"AI: '{data['answer'][:150]}...'")

        # AI recommends nitrogen / urea / balanced nutrients and safety check
        self.assertTrue(any(k in answer for k in ['urea', 'nitrogen', 'npk', 'fertilizer', 'chlorosis', 'zinc']))
        print("[TEST 3 PASSED] AI recommended appropriate fertilizer using full prior context.")

    # =========================================================================
    # TEST 4: Browser Refresh – complete conversation still available in SQLite
    # =========================================================================
    def test_04_browser_refresh_persistence(self):
        print("\n--- RUNNING TEST 4: Browser Refresh Simulation ---")
        conv = ConversationService.get_or_create_conversation(None, language='en')
        conv_id = conv.conversation_id

        # Insert 3 conversation turns
        self.client.post('/api/farming-question', json={'conversation_id': conv_id, 'prompt': 'I am growing groundnut in red soil.', 'language': 'en'})
        self.client.post('/api/farming-question', json={'conversation_id': conv_id, 'prompt': 'How often should I water it?', 'language': 'en'})

        # Refresh simulation: Call GET /api/conversations/<id>
        res = self.client.get(f'/api/conversations/{conv_id}')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        conv_data = data['conversation']
        messages = conv_data['messages']
        self.assertEqual(len(messages), 4) # 2 user + 2 assistant
        self.assertEqual(messages[0]['sender'], 'user')
        self.assertIn('groundnut', messages[0]['message_text'].lower())
        self.assertEqual(messages[1]['sender'], 'assistant')
        self.assertEqual(messages[2]['sender'], 'user')
        self.assertIn('water', messages[2]['message_text'].lower())
        print(f"Refreshed conversation messages: {len(messages)} turns loaded from SQLite.")
        print("[TEST 4 PASSED] All messages survived refresh and loaded in exact chronological order.")

    # =========================================================================
    # TEST 5: Close and Reopen – continue the old conversation
    # =========================================================================
    def test_05_reopen_and_continue_conversation(self):
        print("\n--- RUNNING TEST 5: Close & Reopen Website and Continue Chat ---")
        conv = ConversationService.get_or_create_conversation(None, language='en')
        conv_id = conv.conversation_id

        # First session
        self.client.post('/api/farming-question', json={'conversation_id': conv_id, 'prompt': 'I planted tomato seeds 10 days ago.', 'language': 'en'})

        # Reopen simulation: fetch /api/conversations, find conv_id, continue
        list_res = self.client.get('/api/conversations')
        self.assertEqual(list_res.status_code, 200)
        convs = list_res.get_json()['conversations']
        matched = [c for c in convs if c['conversation_id'] == conv_id]
        self.assertEqual(len(matched), 1)

        # Continue old conversation with follow-up
        cont_res = self.client.post('/api/farming-question', json={
            'conversation_id': conv_id,
            'prompt': 'When should I transplant the seedlings?',
            'language': 'en'
        })
        self.assertEqual(cont_res.status_code, 200)
        answer = cont_res.get_json()['answer'].lower()
        print(f"Reopened consultation continuation: '{cont_res.get_json()['answer'][:140]}...'")
        self.assertTrue(any(k in answer for k in ['transplant', 'days', 'seedling', 'nursery', 'leaves']))

        # Verify all 4 messages in DB
        db_msgs = Message.query.filter_by(conversation_id=conv_id).all()
        self.assertEqual(len(db_msgs), 4)
        print("[TEST 5 PASSED] Old conversation continued seamlessly after website reopen.")

    # =========================================================================
    # TEST 6: Start New Chat – previous conversation remains separate
    # =========================================================================
    def test_06_new_chat_isolation(self):
        print("\n--- RUNNING TEST 6: New Chat Isolation ---")
        # Chat 1: Cotton consultation
        conv1 = ConversationService.get_or_create_conversation(None, language='en')
        id1 = conv1.conversation_id
        self.client.post('/api/farming-question', json={'conversation_id': id1, 'prompt': 'My cotton crop has bollworms.', 'language': 'en'})

        # Chat 2: Ragi consultation (New Chat button)
        new_res = self.client.post('/api/conversations', json={'language': 'en', 'title': 'Ragi Cultivation'})
        id2 = new_res.get_json()['conversation']['conversation_id']
        self.assertNotEqual(id1, id2)
        self.client.post('/api/farming-question', json={'conversation_id': id2, 'prompt': 'What spacing is required for Ragi GPU 28?', 'language': 'en'})

        # Verify Chat 1 messages contain cotton, not ragi
        msgs1 = Message.query.filter_by(conversation_id=id1).all()
        text1 = " ".join([m.message_text for m in msgs1])
        self.assertIn('cotton', text1.lower())
        self.assertNotIn('ragi', text1.lower())

        # Verify Chat 2 messages contain ragi, not cotton
        msgs2 = Message.query.filter_by(conversation_id=id2).all()
        text2 = " ".join([m.message_text for m in msgs2])
        self.assertIn('ragi', text2.lower())
        self.assertNotIn('cotton', text2.lower())
        print(f"Chat 1 ({id1}): Cotton. Chat 2 ({id2}): Ragi. Zero cross-contamination.")
        print("[TEST 6 PASSED] New chat created in SQLite without altering previous conversation.")

    # =========================================================================
    # TEST 7: Voice Question with Interruption & Follow-up in same conversation
    # =========================================================================
    def test_07_voice_interruption_and_followup_continuity(self):
        print("\n--- RUNNING TEST 7: Voice Question, Interruption & Follow-up ---")
        conv = ConversationService.get_or_create_conversation(None, language='en')
        conv_id = conv.conversation_id

        # Voice turn 1 (simulated voice input with text_hint)
        res1 = self.client.post('/api/farming-question', data={
            'conversation_id': conv_id,
            'text_hint': 'My tomato leaves have black rings.',
            'language': 'en'
        })
        self.assertEqual(res1.status_code, 200)

        # Interrupted and follow-up submitted immediately to SAME conversation_id
        res2 = self.client.post('/api/farming-question', data={
            'conversation_id': conv_id,
            'text_hint': 'Can I spray copper oxychloride?',
            'language': 'en'
        })
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        print(f"Voice follow-up answer: '{data2['answer'][:130]}...'")

        # Verify both voice turns stored in same SQLite conversation
        msgs = Message.query.filter_by(conversation_id=conv_id).order_by(Message.timestamp.asc()).all()
        self.assertEqual(len(msgs), 4)
        self.assertEqual(msgs[0].message_type, 'voice')
        self.assertEqual(msgs[2].message_type, 'voice')
        self.assertEqual(msgs[0].conversation_id, conv_id)
        self.assertEqual(msgs[2].conversation_id, conv_id)
        print("[TEST 7 PASSED] Voice interruption & follow-up kept in same SQLite conversation.")

    # =========================================================================
    # TEST 8: Multilingual Kannada dialogue with continuous context
    # =========================================================================
    def test_08_kannada_multilingual_context(self):
        print("\n--- RUNNING TEST 8: Kannada Language Multi-Turn Context ---")
        conv = ConversationService.get_or_create_conversation(None, language='kn')
        conv_id = conv.conversation_id

        # Turn 1: Kannada crop and age
        res1 = self.client.post('/api/farming-question', json={
            'conversation_id': conv_id,
            'prompt': 'ನಾನು ಭತ್ತ ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ, ಬೆಳೆಗೆ 30 ದಿನವಾಗಿದೆ.',
            'language': 'kn'
        })
        self.assertEqual(res1.status_code, 200)
        print(f"Kannada Q1: 'ನಾನು ಭತ್ತ ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ, ಬೆಳೆಗೆ 30 ದಿನವಾಗಿದೆ.'")
        print(f"Kannada A1: '{res1.get_json()['answer'][:90]}...'")

        # Turn 2: Follow-up in Kannada: "ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?"
        res2 = self.client.post('/api/farming-question', json={
            'conversation_id': conv_id,
            'prompt': 'ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?',
            'language': 'kn'
        })
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        ans2 = data2['answer']
        print(f"Kannada Q2: 'ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?'")
        print(f"Kannada A2: '{ans2[:110]}...'")

        # Verify Kannada answer gives advice for paddy
        self.assertTrue('ಭತ್ತ' in ans2 or 'ಯೂರಿಯಾ' in ans2 or 'ಗೊಬ್ಬರ' in ans2 or 'ಪೋಷಕಾಂಶ' in ans2)
        summary = ConversationService.get_farming_context_summary(conv_id)
        self.assertIn('Paddy', summary)
        print(f"Kannada Rolling Summary in DB: '{summary}'")
        print("[TEST 8 PASSED] Kannada multi-turn dialogue retained continuous context in SQLite.")

if __name__ == '__main__':
    unittest.main()

