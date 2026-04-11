# 📚 Pagely Backend — FastAPI Production-Ready Architecture

A modern, scalable backend system for a bookstore application built with **FastAPI**, designed to support a Flutter frontend.

This project started as a simple CRUD API and evolved into a **production-grade backend system** implementing authentication, background processing, email verification, role-based authorization, and more.

---

# 🚀 Overview

Pagely is a backend service that powers a bookstore platform. It provides:

- User authentication & authorization
- Book management
- Review system
- Email verification
- Background job processing
- Token-based security with revocation
- Clean architecture with service layer separation

---

# 🧠 Architecture Philosophy

This project follows key backend engineering principles:

- **Separation of Concerns**
  - Routers → HTTP layer
  - Services → Business logic
  - Models → Database layer
  - Dependencies → Wiring & injection

- **Async-first design**

- **Stateless APIs with JWT**

- **Background processing for heavy tasks**

- **Scalable modular structure**

---

# 🏗️ Tech Stack

| Layer               | Technology                        |
| ------------------- | --------------------------------- |
| Framework           | FastAPI                           |
| ORM                 | SQLModel                          |
| Database            | PostgreSQL (via SQLAlchemy async) |
| Migrations          | Alembic                           |
| Authentication      | JWT                               |
| Password Hashing    | Passlib (Argon2)                  |
| Cache / Broker      | Redis                             |
| Background Jobs     | Celery                            |
| Email Service       | FastAPI-Mail                      |
| Frontend (external) | Flutter                           |

---

# 📂 Project Structure

```
src/
├── auth/        # Authentication domain
├── books/       # Books domain
├── reviews/     # Reviews domain
├── db/          # Database & Redis config
├── middleware/  # Middleware logic
├── errors/      # Custom exception system
├── mail.py      # Email configuration
├── celery.py    # Background worker setup
├── config.py    # Environment settings
```

---

# 🔐 Authentication System

## Features

- JWT-based authentication
- Access & Refresh tokens
- Token revocation via Redis
- Email verification
- Role-based authorization

---

## JWT Flow

1. User signs in

2. Server returns:
   - Access token (short-lived)
   - Refresh token (long-lived)

3. Access token is used for API requests

4. Refresh token is used to generate new access tokens

---

## Token Structure

Each token contains:

- `sub` → user ID
- `jti` → unique token ID
- `iat` → issued at
- `exp` → expiration
- `type` → access / refresh

---

## Token Revocation (Redis)

Logout doesn't just delete tokens client-side.

Instead:

- Token `jti` is stored in Redis blacklist
- Every request checks:

  ```
  if jti in Redis → reject request
  ```

---

# 📧 Email Verification System

## Flow

1. User signs up
2. A **URL-safe token** is generated
3. Email sent with verification link
4. User clicks link → account verified

---

## Token Generation

Uses:

- `itsdangerous.URLSafeTimedSerializer`

Why?

- Safer for URLs than JWT
- Built-in expiration support

---

## Example Verification Link

```
http://DOMAIN/api/v1/auth/verify/<token>
```

---

# ⚙️ Background Processing with Celery

## Why Celery?

Sending emails during requests is slow and blocking.

Solution:

```
FastAPI → sends task → Redis → Celery worker executes
```

---

## Task Flow

1. API triggers:

```python
send_mail.delay(data)
```

2. Task sent to Redis
3. Worker picks it up
4. Email is sent asynchronously

---

## Important Detail

Celery is **synchronous**, but email sending is async.

Solution used:

```python
asgiref.sync.async_to_sync(async_func)
```

---

## Why this matters

- Prevents blocking requests
- Enables horizontal scaling
- Decouples heavy operations

---

# 🧩 Dependency Injection System

FastAPI's `Depends()` is used to:

- Inject services
- Inject database sessions
- Inject authenticated users

---

## Example

```python
async def endpoint(service: BookService = Depends(get_book_service)):
```

---

## Benefits

- Loose coupling
- Testability
- Clean architecture

---

# 🗂️ Database Design

## Entities

### User

- Authentication info
- Role system
- Email verification

### Book

- Created by a user
- Contains metadata

### Review

- Many-to-many (User ↔ Book)
- Composite primary key

---

## Relationships

- User → Books (1:N)
- User ↔ Book (M:N via Review)
- Book → Reviews (1:N)

---

## Advanced Design

- Composite primary key in reviews
- Relationship linking via `link_model`
- Lazy loading with `selectinload`

---

# 🔄 Migrations with Alembic

## Commands

```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```

---

## What it handles

- Schema evolution
- Table creation
- Indexes
- Constraints

---

# ⚡ Middleware System

## Custom Middleware

Logs:

- Request URL
- Method
- Execution time

Adds header:

```
X-Process-Time
```

---

## Built-in Middleware

### CORS

Allows cross-origin requests

### Trusted Host

Protects against host header attacks

---

# ❗ Error Handling System

Centralized error handling using custom exceptions.

---

## Base Class

```python
class AppError(Exception):
```

---

## Derived Errors

- InvalidTokenError
- UnauthorizedError
- ServerError

---

## Benefits

- Consistent API responses
- Cleaner code (no scattered HTTPException)
- Better debugging

---

# 🔐 Authorization System

## Role-Based Access

Supports:

- Admin-only routes
- Multi-role access

---

## Example

```python
RequireRoles(["ADMIN"])
```

---

## Benefit

Fine-grained access control without cluttering endpoints.

---

# 📬 Email System

Uses:

- FastAPI-Mail
- HTML templates
- Config-driven SMTP

---

## Features

- Styled HTML emails
- Configurable SMTP
- Background sending via Celery

---

# ⚙️ Environment Configuration

Managed via `pydantic-settings`

---

## Key Variables

- Database
- JWT settings
- Redis config
- Mail credentials
- Celery config

---

# 🧪 Key Engineering Decisions

## Why Service Layer?

Instead of:

```text
Router → DB directly
```

We use:

```text
Router → Service → DB
```

---

## Why Redis?

- Token blacklist
- Celery broker
- Fast access

---

## Why Async?

- Better concurrency
- Non-blocking I/O
- Scalability

---

# 🚀 Running the Project

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 2. Setup environment

Create `.env` based on `.env.example`

---

## 3. Run database

```bash
alembic upgrade head
```

---

## 4. Start FastAPI

```bash
uvicorn src:app --reload
```

---

## 5. Start Redis

```bash
redis-server
```

---

## 6. Start Celery Worker

```bash
celery -A src.celery.celery_app worker --loglevel=info
```

---

# 🔮 Future Improvements

- Retry logic for failed tasks
- Email queue monitoring
- Rate limiting
- Caching layer for books
- Search functionality
- Notification system

---

# 🧠 Key Takeaways

This project demonstrates:

- How to build a **production-ready FastAPI backend**
- How to design for **scalability early**
- How to separate concerns across layers
- How to handle **async + background jobs correctly**

---

# 🤝 Contribution

Feel free to fork, explore, or suggest improvements.

---

# 🔗 Repository

https://github.com/EslamKamel89/pagely

---

# 📌 Final Note

This is not just a CRUD API.

It’s a backend system designed with real-world constraints in mind:
performance, scalability, maintainability, and clean architecture.
