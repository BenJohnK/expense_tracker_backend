# Expense Tracker Backend (Django + DRF)

## 🚀 Live Demo

Frontend: https://expense-frontend-blond.vercel.app/
Backend: https://expense-tracker-backend-2x1m.onrender.com/api/expenses/

## Overview

This is a simple expense tracking backend built using Django and Django REST Framework.
It provides APIs to create, list, filter, and summarize expenses.

The system is designed with a focus on:

* Data correctness (especially for monetary values)
* Idempotent request handling
* Clean and maintainable code

---

## Features

* Create expense entries
* List expenses with:

  * Category filtering
  * Date-based sorting
* Total expense calculation
* Idempotent POST requests (prevents duplicate entries)
* Summary aggregation support (handled on frontend)

---

## API Endpoints

### Create Expense

POST `/api/expenses/`

### List Expenses

GET `/api/expenses/`

Query params:

* `category=FOOD`
* `sort=date_desc`

---

## Key Design Decisions

### 1. Decimal for Money Handling

* Used `DecimalField` instead of float
* Avoids floating-point precision issues in financial data

### 2. Idempotency Key

* Each request includes an `Idempotency-Key`
* Stored in DB with unique constraint
* Prevents duplicate expense creation in retry scenarios

### 3. Simple Query-based Filtering

* Filtering and sorting handled via query params
* Keeps API simple and extensible

### 4. Thin Backend, Smart Frontend

* Aggregation (like category summary) is done on frontend
* Reduces backend complexity for this time-boxed task

---

## Trade-offs (Time Constraints)

* No authentication/authorization added
* SQLite used instead of PostgreSQL (simpler setup)
* No pagination implemented
* Minimal validation (basic required fields only)
* No async/background processing

---

## What Was Intentionally Not Done

* No user accounts or multi-user support
* No advanced reporting or analytics APIs
* No caching layer (e.g., Redis)
* No test suite (due to time constraints)
* No production-grade logging/monitoring

---

## Data Integrity Considerations

* Monetary values stored using `Decimal`
* Required fields enforced at API level
* Idempotency ensures safe retries
* Input validation prevents invalid entries (e.g., negative amounts)

---

## Running Locally

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Deployment (Render)

### Steps

1. Push code to GitHub
2. Go to https://render.com
3. Create a new **Web Service**
4. Connect your repository

### Configuration

* **Build Command**

```
pip install -r requirements.txt
```

* **Start Command**

```
gunicorn expense_tracker.wsgi:application
```

* **Environment Variables**

```
DEBUG=False
ALLOWED_HOSTS=*
```

5. Add a **Post-deploy command**

```
python manage.py migrate
```

---

## ⚠️ Cold Start Issue (Render Free Tier)

Render free services go to sleep after inactivity (~15 minutes).
This can cause:

* First request delay (10–30 seconds)
* API appearing "slow" initially

### Mitigation

* This is expected behavior on free tier
* Subsequent requests will be fast
* For production use, a paid plan or uptime pings are recommended

---

## Evaluation Notes

This implementation focuses on:

* Correct handling of financial data
* Preventing duplicate transactions
* Clean and readable code structure
* Delivering core functionality reliably within time constraints

---

