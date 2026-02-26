# 🚲 UniCycle — University Cycle Booking System

A complete Django web application for booking cycles on university campuses.

## ✨ Features

### User Features
- Register / Login / Logout
- Profile management (name, roll number, department, phone, photo)
- Browse available cycles with images & details
- Book a cycle — enter custom duration, live cost preview
- **QR code payment** generated at checkout (UPI deep-link)
- Get 4-digit PIN to unlock cycle after payment
- **Return cycle early** — get refund for unused time
- My Bookings — view all history, PINs, return status

### Admin Features  
- Add cycles with: name, ID, image, description, color, gear type, condition
- Manage cycle status (Available / Booked / Maintenance)
- View all bookings with PIN, refund info, return time

---

## 🚀 Setup

### 1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Migrate database
```bash
python manage.py migrate
```

### 4. Create admin superuser
```bash
python manage.py createsuperuser
```

### 5. Run server
```bash
python manage.py runserver
```

### 6. Open in browser
- **Main site:** http://127.0.0.1:8000/
- **Admin panel:** http://127.0.0.1:8000/admin/

---

## 💰 Pricing
| Duration | Cost |
|----------|------|
| 10 min   | ₹3   |
| 30 min   | ₹9   |
| 1 hour   | ₹18  |
| 2 hours  | ₹36  |

---

## 🔄 Return Cycle Flow
1. User goes to **My Bookings** → clicks **Return Cycle**
2. App calculates actual usage time (from payment confirmation)
3. Shows estimated refund if returned early
4. User confirms return → cycle status → **Available**
5. Refund amount saved to booking record

---

## 📁 Project Structure
```
cyclebooking/
├── manage.py
├── requirements.txt
├── README.md
├── cyclebooking/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── booking/
│   ├── models.py          # Cycle, Booking, UserProfile
│   ├── views.py           # All views + QR generator
│   ├── urls.py            # URL routes
│   ├── admin.py
│   ├── migrations/
│   │   └── 0001_initial.py
│   └── templates/booking/
│       ├── base.html
│       ├── home.html
│       ├── login.html
│       ├── register.html
│       ├── profile.html
│       ├── my_bookings.html
│       ├── cycle_detail.html
│       ├── payment.html          ← QR code here
│       ├── booking_success.html  ← PIN + Return button
│       ├── return_cycle.html     ← Return confirmation
│       └── return_summary.html   ← After return
└── media/
    ├── cycles/    ← cycle images
    └── avatars/   ← user avatars
```
