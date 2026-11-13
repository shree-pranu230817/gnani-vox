# 🌾 UZHAVAR AI – Smart Agriculture Platform
> **Empowering Indian Farmers & Buyers with Artificial Intelligence, Real-Time Mandi Prices, and Multilingual Voice Technology.**  
> Built for the **Gnani.ai Internship Competition 2026**.

---

## 🚀 Overview

**UZHAVAR AI** (உழவர் AI) is a complete, production-grade, responsive agriculture platform designed to bridge the digital and economic divide for smallholder farmers and agricultural buyers across India.

Combining **Python Flask**, **SQLite**, and **modern green-and-white agricultural UI/UX**, Uzhavar AI eliminates middleman exploitation, provides transparent government wholesale APMC rates, offers precision farm budgeting, and introduces a **voice-first AI advisor** in **10 Indian regional languages** powered by **Gnani.ai**.

---

## 🌟 Key Features

### 1. 🌐 Multilingual Support (10 Indian Regional Languages)
- Fully localized interface, prompts, navigation, badges, and AI responses across 10 official languages:
  - **English** (en)
  - **தமிழ்** – Tamil (ta)
  - **తెలుగు** – Telugu (te)
  - **हिंदी** – Hindi (hi)
  - **ಕನ್ನಡ** – Kannada (kn)
  - **മലയാളം** – Malayalam (ml)
  - **বাংলা** – Bengali (bn)
  - **मराठी** – Marathi (mr)
  - **ગુજરાતી** – Gujarati (gu)
  - **ਪੰਜਾਬੀ** – Punjabi (pa)
- Modular dictionary architecture in `backend/utilities/i18n.py` allowing instant addition of new Indian regional languages (e.g., Odia, Assamese).
- Instant language switcher in the navigation bar persisting user preference across sessions.

---

### 2. 🌱 AI Farming Assistant – Ask Anything About Agriculture (Third Main Service)
- **Dedicated Homepage Card & Dedicated View (`/farming-assistant`):**
  - Allows farmers to ask agricultural questions and receive helpful, understandable, accurate answers.
  - Interactive controls directly on the homepage:
    - 🎙️ Microphone button for hands-free voice input via **Gnani Prisma**.
    - 💬 Text question input with instant suggestions.
    - 🚀 Submit question button connected to real AI backend (**Google Gemini 3.5 Flash** & ICAR/SAU package of practices).
    - 📋 Formatted answer display area with step-by-step guidance, explanations, and safety warnings.
    - 🔊 Audio playback button with **Gnani Timbre** spoken answers and audio visualizer.
    - 💬 Follow-up question input preserving conversation context across turns.
    - 🔄 Clear conversation button to reset multi-turn memory.
- **13 Supported Farming Topics:**
  1. Crop cultivation and management
  2. Seed selection
  3. Fertilizers and nutrient deficiencies
  4. Irrigation and water management
  5. Soil health and soil preparation
  6. Crop diseases and diagnosis
  7. Pest identification and integrated pest management (IPM)
  8. Organic farming (Jeevamrutha, Panchagavya, Beejamrutha)
  9. Weed management
  10. Crop harvesting and storage
  11. Weather-related farming precautions
  12. Agricultural equipment and techniques
  13. Sustainable farming practices
- **Answer Quality & Safety Standards:**
  - Contextual understanding of crop, location, soil type, season, and farming conditions.
  - Requests missing important information instead of guessing.
  - Step-by-step numbered recommendations with underlying reasons explained.
  - Strict pesticide and fertilizer safety warnings (never invents dosages; always advises label verification and local KVK / SAU consultation).
  - Flags serious diseases for physical sample verification at local agricultural clinics.
  - Zero fabrication of government schemes, market prices, or scientific claims.

---

### 3. 🎙️ Gnani AI Voice Assistant (Prisma + Evon + Timbre)
- **Prisma (Speech-to-Text / ASR):** Transcribes farmer voice input into high-accuracy text across regional Indian languages.
- **Evon (Conversational AI):** Generates domain-specific agricultural answers (crop diseases, pest control, organic Jeevamrutha recipes, fertilizer dosages, mandi timing, and government schemes).
- **Timbre (Text-to-Speech / TTS):** Synthesizes natural-sounding spoken audio in the farmer's native dialect.
- **⭐ Main Demonstration Loop:**
  $$\text{Farmer Speaks} \xrightarrow{\quad\text{Prisma ASR}\quad} \text{Text Query} \xrightarrow{\quad\text{Evon AI}\quad} \text{Agri Advisory} \xrightarrow{\quad\text{Timbre TTS}\quad} \text{Spoken Audio Answer}$$
- Dual-mode architecture:
  - **Live Mode:** Calls official Gnani.ai endpoints when `GNANI_API_KEY` is present in `.env`.
  - **Zero-Config Intelligent Fallback:** Comprehensive agricultural knowledge engine with browser Web Speech recognition & synthesis so evaluators can test voice loops immediately without API limits or network blocks.

---

### 3. 🚜 Farmer Dashboard
- **Registration & Profile:** Mobile-first authentication with farm acreage, primary crops, UPI ID, and geographic coordinates.
- **Crop Management:** Add, edit, and delete produce with name, category, price per unit, available stock, unit (`kg`, `quintal`, `tonne`, `bag`, `crate`), harvest location, state, district, harvest date, availability date, and photo uploads.
- **Order Management:** View incoming purchase orders from buyers with instant status transition:
  $$\text{Pending} \longrightarrow \text{Confirmed} \longrightarrow \text{Shipped} \longrightarrow \text{Delivered}$$
- **Earnings & Rewards:** Automated reward points (+20 points for listing, +50 points for fulfilled orders).

---

### 4. 🛒 Buyer Marketplace
- **Search & Filters:** Search by crop name, category pills (Grains, Pulses, Vegetables, Fruits, Spices, Oilseeds, Organic), and Indian states.
- **Product Details:** High-resolution crop imagery, stock quantity, verified farmer badge, farm size, direct call button, and interactive **Leaflet.js OpenStreetMap** farm location preview.
- **Seamless Checkout:** Direct purchasing with order quantity validation, delivery address, discount coupon redemption (`FARMER10`, `KISAN10`, `HARVEST50`), and Cash on Delivery / UPI payout options.
- **Order Tracking:** Visual 4-step progress timeline for every shipment.
- **Verified Reviews & Ratings:** 1-to-5 star rating system with buyer feedback (+10 reward points earned per review).

---

### 5. 📊 Live Market Prices (AGMARKNET Government Rates)
- **Official Daily Mandi Bhav:** Direct data integration with **AGMARKNET / Ministry of Agriculture & Farmers Welfare**.
- **Transparency:** Displays Commodity Name, APMC Mandi, District, State, Minimum Price, Maximum Price, Modal/Typical Price, Date, and Official Data Source. **Never invents live prices.**
- **Government API Sync:** One-click live sync button pulling verified records from `data.gov.in` with persistent SQLite caching.

---

### 6. 🧮 Crop Profit & Expense Calculator
- **Farming Expense Breakdown:** Seeds, Fertilizers & Manure, Pesticides & Bio-control, Labour & Machinery, Irrigation & Fuel, Transport, and Miscellaneous costs.
- **Dynamic Yield Revenue:** Expected Yield (Quintals/Tonnes/Bags) $\times$ Expected Market Price.
- **Calculated Metrics:**
  - Total Farm Expenses ($₹$)
  - Gross Revenue ($₹$)
  - Net Profit / Loss ($₹$)
  - **Profit per Acre** ($₹/\text{Acre}$)
  - Return on Investment (ROI %)
  - Break-Even Price per Unit
- **Chart.js Visualizer:** Interactive expense distribution donut chart.
- **Farm History Storage:** Save calculations to SQLite database to track profitability across seasons.

---

### 7. ⚡ Admin Dashboard & Control Center
- **System Overview:** Total farmers, buyers, listed produce, gross revenue, and pending approval queues.
- **Crop Moderation:** 1-click Approve or Reject (with feedback reason) for submitted crops.
- **User Management:** View all accounts, inspect reward points, and toggle Active/Suspended status.
- **Coupon Manager:** Create percentage or fixed-amount promo codes with minimum order thresholds and discount caps.
- **Reports & Analytics:** Top crops by volume, state distribution charts, and monthly revenue audit tables.

---

### 8. 🔒 Security & Backend Architecture
- **Environment Isolation:** Gnani AI and Data.gov.in API keys are stored strictly in backend `.env` and never exposed to client-side JavaScript.
- **Password Security:** Scrypt password hashing via `werkzeug.security`.
- **Role-Based Access Control (RBAC):** Custom decorators (`@login_required`, `@farmer_required`, `@buyer_required`, `@admin_required`).
- **SQL Injection Prevention:** 100% parameterized queries across all database operations.
- **File Upload Protection:** Whitelisted image extensions (`png`, `jpg`, `jpeg`, `webp`), size limits (16 MB), and secure UUID-based filenames.

---

## 📁 Project Directory Structure

```
gnani ai/
│
├── app.py                      # Flask Application entry point & factory
├── config.py                   # Centralized application configurations
├── requirements.txt            # Python dependencies
├── .env                        # Local environment variables
├── .env.example                # Sample environment file template
├── uzhavar.db                  # SQLite database with complete schemas & seed data
├── test_app.py                 # Automated test suite (10 test cases)
├── test_e2e.py                 # End-to-end integration test suite
│
├── database/
│   ├── __init__.py
│   ├── db.py                   # SQLite connection helpers, query_db, execute_db
│   └── seed_data.py            # Password reset and demo data verification script
│
├── backend/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── auth_routes.py      # Login, Register, Profile, Language switcher
│   │   └── security.py         # RBAC decorators (@farmer_required, etc.)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main_routes.py      # Home, Notifications, Gnani AI APIs (/api/gnani/*)
│   │   ├── marketplace_routes.py # Crop listing, search, product detail, reviews
│   │   ├── farmer_routes.py    # Farmer dashboard, crop CRUD, order fulfillment
│   │   ├── buyer_routes.py     # Buyer dashboard, checkout, order tracking
│   │   ├── mandi_routes.py     # Live AGMARKNET market rates & API sync
│   │   ├── calculator_routes.py# Farm profit calculator formulas & history
│   │   └── admin_routes.py     # Admin dashboard, approvals, users, coupons, reports
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gnani_service.py    # Prisma (STT), Evon (AI), Timbre (TTS) service
│   │   ├── agmarknet_service.py# Data.gov.in AGMARKNET sync service
│   │   └── notification_service.py # In-app notification delivery
│   └── utilities/
│       ├── __init__.py
│       ├── i18n.py             # 10 Indian Regional Languages dictionary
│       └── helpers.py          # Currency format, image upload validator, order IDs
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css        # Clean green-and-white responsive theme
│   │   │   ├── assistant.css   # Voice AI widget, mic pulse, chat bubbles
│   │   │   └── dashboard.css   # Stats cards, tables, tracking timeline
│   │   └── js/
│   │       ├── main.js         # Mobile navbar, dropdowns, dismissible alerts
│   │       ├── assistant.js    # Gnani AI client engine (Prisma + Evon + Timbre loop)
│   │       └── calculator.js   # Live profit calculation & Chart.js graph
│   └── templates/
│       ├── base.html           # Master layout with navbar, footer, assistant modal
│       ├── index.html          # Hero homepage with stats, live rates, top crops
│       ├── notifications.html  # User alerts & notifications
│       ├── 404.html & 500.html # Error handling templates
│       ├── auth/               # Login, Register, Profile templates
│       ├── marketplace/        # Browse, Product Detail, Checkout templates
│       ├── farmer/             # Dashboard, Add Crop, Edit Crop, Orders templates
│       ├── buyer/              # Dashboard, Order Tracking templates
│       ├── mandi/              # AGMARKNET Live Prices template
│       ├── calculator/         # Crop Profit Calculator template
│       └── admin/              # Dashboard, Users, Products, Orders, Coupons, Reports
│
└── uploads/                    # Uploaded crop product images
```

---

## 🛠️ Installation & Setup Guide

### 1. Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12+
- `pip` package manager

### 2. Clone / Open the Workspace
```bash
cd "c:\Users\RAM\OneDrive\Documents\gnani ai"
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Inside `.env`, configure:
```ini
SECRET_KEY=uzhavar-secret-session-key-2026
DATABASE_PATH=uzhavar.db

# Gnani AI API Credentials (Optional - works in simulation fallback if empty)
GNANI_API_KEY=your_gnani_api_key_here
GNANI_BASE_URL=https://api.gnani.ai/v1
GNANI_PRISMA_ENDPOINT=https://api.gnani.ai/v1/prisma/asr
GNANI_EVON_ENDPOINT=https://api.gnani.ai/v1/evon/chat
GNANI_TIMBRE_ENDPOINT=https://api.gnani.ai/v1/timbre/tts

# AGMARKNET Govt API Key (Optional from data.gov.in)
DATA_GOV_API_KEY=your_datagov_api_key_here
AGMARKNET_ENDPOINT=https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
```

### 5. Verify & Seed Database
Ensure all initial test accounts and sample agricultural records are seeded:
```bash
python database/seed_data.py
```

### 6. Run the Test Suites
Run the automated test suites to ensure 100% functionality:
```bash
python test_app.py
python test_e2e.py
```

### 7. Start the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 👥 Demo Accounts for Competition Judges

For convenient 1-click evaluation, the login page (`/auth/login`) features **1-Click Demo Login Buttons**:

| Role | Name | Mobile / Email | Password | Pre-seeded Features |
|---|---|---|---|---|
| **Farmer** | Ramesh Kumar | `9876543211` / `ramesh.farmer@uzhavar.ai` | `farmer123` | Listed paddy crops, incoming orders, 170 pts |
| **Buyer** | Anand Subramanian | `9876543220` / `anand.buyer@uzhavar.ai` | `buyer123` | Order history, order tracking, wishlist |
| **Admin** | Administrator | `9876543210` / `admin@uzhavar.ai` | `admin123` | Product approval queue, coupons, analytics |

*Note: New users can also register freely as either a Farmer or a Buyer.*

---

## 🎙️ Demonstrating Gnani AI Assistant

1. Click the floating green **"🎙️ Speak with Gnani AI"** button at the bottom-right of any page.
2. Select your preferred Indian regional language from the dropdown (e.g., Tamil, Telugu, Hindi, English).
3. **Run 3-Step Demo:**
   - Click the gold **"▶ Run Voice Demo"** button on the top bar.
   - **Step 1 (Prisma STT):** Farmer speaks an agricultural question in their regional tongue.
   - **Step 2 (Evon AI):** Generates actionable agronomic advice.
   - **Step 3 (Timbre TTS):** Synthesizes and plays back regional voice audio.
4. **Live Microphone Interaction:**
   - Tap the large pulsating microphone button.
   - Speak your question (e.g., *"How to control pest in cotton crop?"* or *"நெல் பயிர் உரம்"*).
   - Listen to the audio response spoken back to you!

---

## 📊 Summary of Implemented Requirements

| Requirement | Implementation Details | Status |
|---|---|---|
| **Multilingual Support** | 10 Indian Regional Languages (EN, TA, TE, HI, KN, ML, BN, MR, GU, PA) + extensible dictionary | ✅ Complete |
| **Gnani AI Assistant** | Prisma (STT), Evon (Agri Conversational AI), Timbre (TTS) + voice input, text chat, audio synthesis | ✅ Complete |
| **Farmer Dashboard** | Crop CRUD with photos, category, pricing, harvest location, orders fulfillment, and reward points | ✅ Complete |
| **Buyer Marketplace** | Crop browsing, search, category filter, state filter, Leaflet map preview, checkout, tracking & reviews | ✅ Complete |
| **Live Market Prices** | AGMARKNET government daily wholesale rates (Min, Max, Modal prices) with source attribution & live sync | ✅ Complete |
| **Profit Calculator** | Input cost breakdown, expected yield revenue, net profit per acre, ROI %, and saved calculation history | ✅ Complete |
| **Admin Dashboard** | Product moderation queue (Approve/Reject), user management, orders audit, promo coupons & reports | ✅ Complete |
| **Backend & Security** | SQLite parameterized DB, password hashing, RBAC decorators, server-side `.env` protecting Gnani key | ✅ Complete |

---

## 📜 License & Acknowledgments
- Developed for the **Gnani.ai Internship Competition 2026**.
- Open agricultural data provided by **AGMARKNET**, Directorate of Marketing & Inspection (DMI), Ministry of Agriculture & Farmers Welfare, Government of India.
- Conversational voice AI powered by **Gnani.ai Prisma, Evon, and Timbre APIs**.
#   g n a n i - v o x  
 