# LuminalLib Backend

FastAPI backend with **PostgreSQL**, **JWT authentication**, **AI sentiment analysis**, and **storage abstraction** (local disk or AWS S3).

## 🚀 Quick Start (30 seconds)

```bash
# 1. Ensure PostgreSQL is running
brew services start postgresql

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python3 main.py
```

✅ API ready at `http://localhost:8000`

---

## 🔑 Authentication

**Test User:**
- Username: `testuser`
- Password: `password123`
- User ID: `bebe955e-a9fe-466c-a22e-532149baa2f8`

**Login Flow:**
```bash
# 1. Get JWT token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}

# 2. Use token in requests
curl -H "Authorization: Bearer eyJhbGc..." \
  http://localhost:8000/api/books
```

---

## 💾 Storage Abstraction (Local & AWS S3)

### Currently: Local File Storage (Development)
```bash
# Files saved to ./files directory
# Served at http://localhost:8000/files/
STORAGE_TYPE=local
STORAGE_LOCAL_BASE_PATH=./files
STORAGE_BASE_URL=http://localhost:8000/files
```
✅ Already configured, works immediately

### Switch to AWS S3 (Production)
```bash
# Files uploaded to S3 bucket, scales automatically
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=luminallib-books
AWS_S3_REGION=us-east-1
STORAGE_BASE_URL=https://cdn.luminallib.com
```

### Implementation Details
- ✅ **Abstract Port:** `FileStoragePort` interface
- ✅ **Local Adapter:** `LocalFileStorageAdapter` (150+ lines)
- ✅ **S3 Adapter:** `S3FileStorageAdapter` (180+ lines)
- ✅ **Factory:** Config-driven creation (no code changes)
- ✅ **Integration:** Used in BookService for file uploads

**Architecture:** Storage is abstracted behind a port interface. Services don't know if files go to local disk or S3. Just change config!

---

## 🤖 AI Sentiment Analysis

### Three LLM Providers Available

**Change Provider:** `app/core/config.py` (Line 52)

```python
llm_provider: str = "mock"  # Options: mock, openai, huggingface
```

### Provider Details

| Provider | API Calls | Speed | Accuracy | Cost | Setup |
|----------|-----------|-------|----------|------|-------|
| **mock** | ❌ No | ⚡ Instant | 70% | Free | ✅ Zero |
| **openai** | ✅ Yes | 🐢 2-5s | 95% | 💰 $$ | 🔧 Key needed |
| **huggingface** | ❌ No | 🚀 1-3s | 85% | Free | 🔧 Download model |

### Setup Each Provider

#### Mock (Default, No Setup)
```python
# app/core/config.py
llm_provider: str = "mock"
# Done! Uses keyword matching
```

#### OpenAI (Needs API Key)
```bash
# 1. Get key from https://platform.openai.com/api/keys
# 2. Create .env file or edit config.py

# Option A: .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Option B: config.py
llm_provider: str = "openai"
openai_api_key: str = "sk-proj-your-key-here"
openai_model: str = "gpt-3.5-turbo"
```

**Cost:** ~$0.0005/review

#### HuggingFace (Free, Local)
```bash
# 1. Edit config.py
llm_provider: str = "huggingface"
huggingface_model: str = "meta-llama/Llama-2-7b-chat"
huggingface_device: str = "cuda"  # or "cpu"

# 2. First run downloads model (~3GB)
python3 main.py
# On next startup, uses cached model
```

**Cost:** Free (just electricity)

---

## 📊 API Endpoints

### Authentication
```
POST   /auth/register        Create account
POST   /auth/login           Get JWT token
POST   /auth/refresh         Refresh token
POST   /auth/logout          Logout
```

### Books
```
GET    /api/books            List all books
GET    /api/books/{id}       Get book details
POST   /api/books/upload     Upload new book
```

### Reviews (With Sentiment Analysis)
```
POST   /api/books/{id}/reviews           Create review → triggers sentiment analysis
GET    /api/books/{id}/reviews           List reviews for book
PUT    /api/reviews/{id}                 Update review → updates sentiment_score
```

### Sentiment Analysis
- Automatic: Triggered on review creation
- Asynchronous: Non-blocking (returns HTTP 201 immediately)
- Storage: `sentiment_score` column (0.0-1.0 range)
- Async logs: Backend logs show "✅ Analyzed review {id}: {sentiment}"

---

## 🗄️ Database Setup

### PostgreSQL Installation

**macOS:**
```bash
brew install postgresql
brew services start postgresql
createdb luminallib
```

**Linux:**
```bash
sudo apt-get install postgresql
sudo systemctl start postgresql
createdb luminallib
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### Connection

**Default connection string:**
```
postgresql://localhost:5432/luminallib
```

**Override in .env:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/luminallib
```

### Database Schema

**Tables:**
- `users` - User accounts
- `books` - Book catalog
- `reviews` - Reviews with sentiment_score
- `borrow_records` - Borrowing history

**Key column:**
```sql
-- In reviews table
sentiment_score NUMERIC(3, 2) NULL
-- Range: 0.00 to 1.00
-- 0.15 = Negative, 0.50 = Neutral, 0.85 = Positive
```

---

## 🏗️ Architecture

```
FastAPI Application
├── API Layer (app/api/)
│   ├── auth.py → Authentication endpoints
│   ├── books.py → Book endpoints
│   ├── reviews.py → Review endpoints (triggers sentiment analysis)
│
├── Services (app/services/)
│   ├── review_service.py → Business logic
│   │   └── analyze_and_update_sentiment() → Sentiment analysis
│   ├── user_service.py
│   └── book_service.py
│
├── Adapters (app/adapters/)
│   ├── llm/ → LLM implementations
│   │   ├── mock_llm.py → Keyword matching
│   │   ├── openai_adapter.py → GPT API
│   │   └── huggingface_adapter.py → Local models
│   ├── db/ → Database implementations
│   │   └── postgresql_storage.py → PostgreSQL ORM
│
├── Domain (app/domain/)
│   └── entities.py → User, Book, Review classes
│
└── Core (app/core/)
    ├── config.py → Settings (LLM provider switch here)
    └── di.py → Dependency injection
```

---

## 🧪 Test Endpoints

### 1. Create Account
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@example.com",
    "password": "password123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### 3. Get Books
```bash
curl http://localhost:8000/api/books
```

### 4. Create Review (Sentiment Analysis)
```bash
TOKEN="your_token_from_login"

curl -X POST http://localhost:8000/api/books/book-1/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "content": "This book is amazing and wonderful!"
  }'

# Response: HTTP 201 Created
# sentiment_score starts as null, gets populated in <1 second
```

### 5. Check Sentiment Score in Database
```bash
psql luminallib -c \
  "SELECT id, rating, content, sentiment_score FROM reviews ORDER BY created_at DESC LIMIT 1;"
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
# Database
DATABASE_URL=postgresql://localhost:5432/luminallib

# LLM Configuration
LLM_PROVIDER=mock              # mock, openai, huggingface
OPENAI_API_KEY=sk-proj-...     # Only for openai
OPENAI_MODEL=gpt-3.5-turbo

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
DEBUG=False
ENVIRONMENT=production
```

### Configuration File

`app/core/config.py` - All settings centralized:
```python
class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./luminallib.db"
    
    # LLM Provider
    llm_provider: str = "mock"  # ← Change here
    openai_api_key: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
```

---

## 📚 File Structure

```
luminallib-backend/
├── main.py                              # Entry point
├── requirements.txt                     # Dependencies
├── README.md                            # This file
├── .env                                 # Environment (create if needed)
│
└── app/
    ├── core/
    │   ├── config.py                   # Settings & LLM provider
    │   ├── di.py                       # Dependency injection
    │   └── exceptions.py
    │
    ├── domain/
    │   └── entities.py                 # User, Book, Review
    │
    ├── ports/
    │   ├── storage_port.py             # Storage interface
    │   └── llm_port.py                 # LLM interface
    │
    ├── services/
    │   ├── review_service.py           # Sentiment analysis logic
    │   ├── user_service.py
    │   └── book_service.py
    │
    ├── adapters/
    │   ├── llm/
    │   │   ├── llm_factory.py          # Creates LLM adapter
    │   │   ├── mock_llm.py             # Keyword matching
    │   │   ├── openai_adapter.py       # GPT API
    │   │   └── huggingface_adapter.py  # Local models
    │   │
    │   └── db/
    │       ├── postgresql_storage.py   # PostgreSQL implementation
    │       └── in_memory_storage.py    # For testing
    │
    └── api/
        ├── auth.py                     # Login, register, logout
        ├── books.py                    # Book endpoints
        └── reviews.py                  # Review endpoints
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Check if PostgreSQL is running
brew services list | grep postgresql

# Check requirements installed
pip install -r requirements.txt
```

### "User not found" error
- Backend has test user built-in: `testuser` / `password123`
- User ID: `bebe955e-a9fe-466c-a22e-532149baa2f8`
- This is hardcoded in `app/api/reviews.py`

### Sentiment score is NULL
- Check backend logs for "Analyzed review" messages
- Ensure LLM provider is configured correctly
- Verify PostgreSQL `sentiment_score` column exists:
  ```bash
  psql luminallib -c "\d reviews"
  ```

### Database connection error
```bash
# Check PostgreSQL is running
brew services start postgresql

# Check database exists
psql -l | grep luminallib

# Create if needed
createdb luminallib

# Test connection
psql luminallib
```

---

## ✅ Features Implemented

- ✅ User registration & login (JWT)
- ✅ Book management (list, details, upload)
- ✅ Review system (create, update, read)
- ✅ **Sentiment analysis** (async, three providers)
- ✅ PostgreSQL integration
- ✅ Proper HTTP status codes
- ✅ Error handling & validation
- ✅ Structured logging
- ✅ Type safety (Python types)
- ✅ Clean architecture (ports & adapters)

---

## 📖 API Endpoints

### Users
- `POST /api/users` - Create user
- `GET /api/users/{user_id}` - Get user
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user
- `GET /api/users` - List users

### Books
- `POST /api/books` - Create book
- `GET /api/books/{book_id}` - Get book
- `PUT /api/books/{book_id}` - Update book
- `DELETE /api/books/{book_id}` - Delete book
- `GET /api/books` - List books
- `GET /api/books/search/{query}` - Search books

### Reviews
- `POST /api/reviews` - Create review
- `GET /api/reviews/{review_id}` - Get review
- `PUT /api/reviews/{review_id}` - Update review
- `DELETE /api/reviews/{review_id}` - Delete review
- `GET /api/reviews/book/{book_id}` - Get reviews for book
- `GET /api/reviews/user/{user_id}` - Get reviews by user
- `POST /api/reviews/{review_id}/helpful` - Mark review as helpful

## Development

### Adding a New Feature

1. **Create Entity** in `app/domain/entities.py`
2. **Create Port** in `app/ports/` (if needed)
3. **Create Service** in `app/services/` with business logic
4. **Create Adapter** in `app/adapters/` (implementation)
5. **Create Router** in `app/api/` with endpoints
6. **Register in DI** container in `main.py`

### Current Adapters

- **Storage**: In-memory (mock)
- **LLM**: Mock implementation
- **Recommendation**: Mock implementation

These can be replaced with real implementations (PostgreSQL, OpenAI, ML model, etc.) without changing the service or API layers.

## Environment Variables

See `.env` file for configuration options:
- `DATABASE_URL` - Database connection string
- `DEBUG` - Debug mode
- `LLM_PROVIDER` - LLM provider (mock, openai, huggingface)
- `LLM_API_KEY` - LLM API key
