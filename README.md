# Coupon Service Backend

This directory contains a Django project that exposes a simple REST API for generating discount coupons. The API accepts an email address and a website name, generates (or reuses) a unique coupon code, stores it in a database, and sends the code to the user via email. The system is designed to be embedded into any website via a lightweight frontend script.

## Features

* Issue unique 10% off coupon codes for each `(email, website)` pair.
* Prevent duplicate coupons for the same email and website until the existing code expires.
* Store coupons in a relational database (SQLite by default).
* Send coupon codes via email using Amazon SES SMTP credentials (configurable).
* Expose a JSON API endpoint at `/api/coupons/` for creating coupons.

## Setup

1. **Install Dependencies**

   Create a virtual environment and install the required packages:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**

   Copy `.env.example` to `.env` and fill in your SMTP credentials. At a minimum, set:

   * `EMAIL_HOST`: SES SMTP host (e.g. `email-smtp.us-east-1.amazonaws.com`).
   * `EMAIL_PORT`: usually `587` for TLS.
   * `EMAIL_HOST_USER`: SES SMTP username.
   * `EMAIL_HOST_PASSWORD`: SES SMTP password.
   * `DEFAULT_FROM_EMAIL`: the address from which coupon emails will be sent.

   You can also adjust `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS`.

3. **Run Migrations**

   ```bash
   python manage.py migrate
   ```

4. **Start the Development Server**

   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000/api/coupons/`.

## API Usage

Send a `POST` request to `/api/coupons/` with JSON containing the user's email and the website name:

```
POST /api/coupons/
Content-Type: application/json

{
  "email": "user@example.com",
  "website": "example.com"
}
```

Response:

```
HTTP/1.1 201 Created
{
  "email": "user@example.com",
  "website": "example.com",
  "code": "ABC12345",
  "expires_at": "2025-11-17T13:45:00Z"
}
```

If a coupon already exists for the email and website and has not expired, the existing code will be returned. Otherwise a new code is generated and stored.

## Customising Coupon Expiry

By default, coupons expire 30 days after issuance. You can change the expiry duration by setting the `COUPON_EXPIRY_DAYS` variable in your Django settings or environment. For example:

```
export COUPON_EXPIRY_DAYS=14  # two weeks expiry
```

## Development Notes

* The project uses SQLite for ease of setup. For production, configure `DATABASES` in `coupon_project/settings.py` to use PostgreSQL or another database backend.
* To avoid sending real emails in development, you can set:

  ```bash
  export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
  ```

  This will print outgoing emails to the terminal instead of sending them via SMTP.

* This backend is designed to be consumed by a frontend popup script that can be embedded on any website. See the `frontend/` directory for an example implementation.