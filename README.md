# 🧠 NeuroVaidya

Ayurvedic medicine e-commerce platform built with Django.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd neurovaidya

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your values

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## 📁 Project Structure

```
neurovaidya/
├── config/          # Django settings
├── users/           # User authentication & profiles
├── medicines/       # Product catalog
├── orders/          # Cart & order management
├── payments/        # Razorpay integration
├── search/          # Search functionality
├── templates/       # HTML templates
├── static/          # CSS, JS, images
└── media/           # User uploads
```

---

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Dev key (change in prod!) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `RAZORPAY_KEY_ID` | Razorpay API key | - |
| `RAZORPAY_KEY_SECRET` | Razorpay secret | - |

---

## 🌐 Deployment

### Option 1: Render (Recommended)

1. Push code to GitHub
2. Create new Web Service on [Render](https://render.com)
3. Set environment variables in Render dashboard
4. Set build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
5. Set start command: `gunicorn config.wsgi:application`

### Option 2: Railway

1. Connect GitHub repo to [Railway](https://railway.app)
2. Add environment variables
3. Railway auto-detects Django and deploys

### Option 3: Manual (VPS)

```bash
# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

## 📡 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/medicines/` | Medicine catalog |
| `/api/cart/` | Cart operations |
| `/api/orders/` | Order management |
| `/api/coupons/apply/` | Apply promo code |

---

## 🛠️ Development Commands

```bash
# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

---

## 📄 License

MIT License
