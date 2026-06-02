# 🤖 OttoMaxAI — AI-Powered Social Media Automation Platform

[![Live](https://img.shields.io/badge/Live-ottomaxai.com-brightgreen)](https://ottomaxai.com)
[![API Docs](https://img.shields.io/badge/API-api.ottomaxai.com%2Fdocs-blue)](https://api.ottomaxai.com/docs)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED)](https://docker.com)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF)](https://github.com/features/actions)
[![Stripe](https://img.shields.io/badge/Payments-Stripe-635BFF)](https://stripe.com)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E)](https://supabase.com)
[![n8n](https://img.shields.io/badge/Automation-n8n-EA4B71)](https://n8n.io)

> **OttoMaxAI** is a B2B SaaS platform that automates social media content creation and publishing for businesses. Users connect their Facebook, Instagram, and Google accounts — and AI generates branded posts with captions and hashtags, publishing them automatically on a weekly schedule.

---

## 🌐 Live

🔗 **Website:** [https://ottomaxai.com](https://ottomaxai.com)  
📡 **API Docs:** [https://api.ottomaxai.com/docs](https://api.ottomaxai.com/docs)

---

## ✨ How It Works — User Journey

```
1. Subscribe       → Choose a monthly plan (Starter / Pro / Premium)
        │
        ▼
2. Onboarding      → Enter business info, select brand tone & theme colors
        │
        ▼
3. Connect Socials → Link Facebook, Instagram & Google via OAuth
        │                (managed via uploadpost.com)
        ▼
4. AI Generation   → Posts + captions + hashtags generated from business data
        │                (OpenAI DALL·E 2 for images, GPT for text)
        ▼
5. Auto Publish    → Posts scheduled & published automatically each week
        │                (n8n workflows handle scheduling & delivery)
        ▼
6. Dashboard       → View past posts, connected accounts & upcoming schedule
```

---

## 💳 Subscription Plans

| Plan | Weekly Posts | Price |
|------|-------------|-------|
| **Starter** | 2 posts/week | Monthly |
| **Pro** | 4 posts/week | Monthly |
| **Premium** | 7 posts/week | Monthly |

All plans include:
- AI-generated images (OpenAI DALL·E 2)
- AI-generated captions & hashtags (OpenAI GPT)
- Auto-publishing to Facebook, Instagram & Google
- Dashboard with post history and upcoming schedule

**Stripe Integration includes:**
- Monthly subscription checkout via `stripe.checkout.Session`
- Webhook handling for payment confirmation, renewal & cancellation
- Plan-based access control (post quota enforced per subscription tier)
- Publishable & secret key separation for frontend/backend security

---

## 🏗️ Project Structure

```
ottomaxai/
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD pipeline (GitHub Actions)
│
├── app/
│   ├── authentication/
│   │   ├── users_oauth.py          # OAuth flow (Google, Facebook)
│   │   └── __init__.py
│   │
│   ├── models/                     # SQLAlchemy / Supabase DB models
│   │   ├── users_models.py
│   │   ├── businesses_model.py
│   │   ├── subscription_model.py
│   │   ├── generated_posts_model.py
│   │   ├── scheduled_post_queue_model.py
│   │   └── Social_Connection_Model.py
│   │
│   ├── routers/                    # FastAPI route handlers
│   │   ├── register_user.py
│   │   ├── login_user.py
│   │   ├── forgot_password.py
│   │   ├── business_onboarding_router.py
│   │   ├── social_auth.py          # Social media OAuth connect
│   │   └── subscription.py         # Stripe subscription management
│   │
│   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── users_schemas.py
│   │   ├── businesses_schema.py
│   │   ├── subscription_schema.py
│   │   ├── social_connect_request.py
│   │   └── forgot_password_schema.py
│   │
│   ├── utils/
│   │   └── resend.py               # Transactional email via Resend
│   │
│   ├── config.py                   # App configuration & env vars
│   ├── database.py                 # Database connection setup
│   ├── supabase_client.py          # Supabase client initialization
│   └── main.py                     # FastAPI app entry point
│
├── tester/                         # Internal test & debug scripts
│   ├── debug.py
│   ├── test_admin_direct.py
│   ├── test_db.py
│   ├── test_smtp.py
│   └── test_supabase.py
│
├── .example.env
├── docker-compose.yml
├── dockerfile
├── requirements.txt
└── README.md
```

---

## 🤖 AI & Automation Engine

OttoMaxAI's content generation and publishing is powered by **n8n workflows** orchestrated through the **FastAPI backend**. Every user gets their own controlled automation workflow.

### How AI Content is Generated

```
Business Profile Data (name, industry, tone, colors)
        │
        ▼
  OpenAI GPT          ← Generates caption + hashtags tailored to brand
        │
  OpenAI DALL·E 2     ← Generates branded post image
        │
        ▼
  n8n Workflow        ← Schedules post based on subscription tier
        │
        ▼
  uploadpost.com      ← Publishes to Facebook, Instagram & Google
```

### n8n Workflow Control via FastAPI

The FastAPI backend acts as the **control layer** for all n8n workflows:

| Action | Backend Trigger |
|--------|----------------|
| New user subscribes | Activates personalized n8n workflow |
| User upgrades plan | Updates post frequency in workflow |
| User cancels | Deactivates workflow via API call |
| Post generated | Logs to `generated_posts_model` |
| Post scheduled | Queued in `scheduled_post_queue_model` |

### AI Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Image Generation** | OpenAI DALL·E 2 | Branded post image creation |
| **Text Generation** | OpenAI GPT (LLM) | Captions, hashtags, brand copy |
| **Workflow Engine** | n8n | Scheduling, publishing, automation |
| **Social Publishing** | uploadpost.com | Multi-platform post delivery |

---

## 🔐 Authentication & Security

Authentication is fully managed through **Supabase**, providing enterprise-grade security out of the box:

- **Email/Password** registration with **bcrypt password hashing**
- **Email verification** flow on signup
- **OAuth** (Google, Facebook) for social media account connection
- **JWT tokens** for API session management
- **Forgot password** flow with secure reset email
- All transactional emails (verification, reset, welcome) handled via **Resend**

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI |
| **Database** | Supabase (PostgreSQL) |
| **Authentication** | Supabase Auth + JWT + OAuth |
| **AI — Images** | OpenAI DALL·E 2 |
| **AI — Text** | OpenAI GPT (LLM) |
| **Automation** | n8n (self-hosted workflows) |
| **Social Publishing** | uploadpost.com |
| **Payments** | Stripe (Monthly Subscriptions) |
| **Email** | Resend |
| **Containerization** | Docker |
| **CI/CD** | GitHub Actions |
| **Web Server** | Nginx + Uvicorn |
| **Hosting** | Hostinger VPS (Ubuntu 24.04) |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | User registration |
| POST | `/auth/login` | User login |
| POST | `/auth/forgot-password` | Password reset request |
| GET | `/auth/social` | Social OAuth connect |
| POST | `/onboarding/business` | Submit business profile |
| POST | `/subscription/subscribe` | Create Stripe checkout |
| POST | `/subscription/webhook` | Stripe webhook handler |
| GET | `/subscription/plans` | Get available plans |
| POST | `/social/connect` | Connect Facebook/Instagram/Google |
| GET | `/posts/history` | Get past generated posts |
| GET | `/posts/scheduled` | Get upcoming post queue |

---

## 💳 Stripe Payment Integration

### How it works

1. **Checkout** — User selects a plan → redirected to Stripe hosted checkout
2. **Webhook** — Stripe sends event to `/subscription/webhook` on payment success, renewal, or cancellation
3. **Access Control** — Backend enforces post quota based on active subscription tier
4. **Cancellation** — Webhook triggers n8n workflow deactivation automatically

### Stripe Setup

```bash
pip install stripe

# .env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Local Webhook Testing

```bash
stripe listen --forward-to localhost:8000/subscription/webhook
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Supabase account
- Docker (optional)
- n8n instance (self-hosted or cloud)
- Stripe account
- Resend account

### Local Development

```bash
# Clone the repository
git clone https://github.com/Latif1218/<repo-name>.git
cd <repo-name>

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .example.env .env
# Fill in your credentials

# Run the application
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Docker

```bash
docker-compose up --build
```

---

## ⚙️ Environment Variables

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key

# Database
DATABASE_URL=postgresql://user:password@host/dbname

# JWT
JWT_SECRET_KEY=your_jwt_secret

# OpenAI
OPENAI_API_KEY=your_openai_key

# Stripe
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# Resend (Email)
RESEND_API_KEY=your_resend_key

# n8n
N8N_BASE_URL=https://your-n8n-instance.com
N8N_API_KEY=your_n8n_key

# Social Publishing
UPLOADPOST_API_KEY=your_uploadpost_key

# Domain
DOMAIN=https://ottomaxai.com
```

---

## 🔄 CI/CD Pipeline

Every push to `main` branch automatically:

1. ✅ Builds Docker image
2. ✅ Pushes to Docker Hub
3. ✅ Deploys to Hostinger VPS via SSH

```
git push origin main → GitHub Actions → Docker Hub → Hostinger VPS 🚀
```

---

## 🗂️ Dashboard Features

Users can view the following from their dashboard:

- ✅ **Post History** — All previously published posts with platform & date
- ✅ **Connected Accounts** — Facebook, Instagram, Google connection status
- ✅ **Upcoming Schedule** — Next queued posts with publish time
- ✅ **Subscription Status** — Current plan, renewal date, usage quota

---

## 👨‍💻 Author

**Md. Abdul Latif Sumon**  
AI Engineer  
📧 mdsabdullotif@gmail.com  
🔗 [GitHub](https://github.com/Latif1218)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

> *OttoMaxAI — Let AI run your social media, so you can run your business.*
