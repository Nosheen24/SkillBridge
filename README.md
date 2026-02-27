# SkillBridge Backend API

FastAPI backend for SkillBridge - A Freelance & Micro-Task Platform for Students

## Sprint 1 - Task Completion

This implementation includes all Sprint 1 backend tasks:

- **SKIL-7**: User Registration API
- **SKIL-8**: User Login API
- **SKIL-11**: Post Micro Task API
- **SKIL-12**: Browse Tasks API
- **SKIL-13**: Search Tasks API

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth (JWT)
- **Validation**: Pydantic
- **Server**: Uvicorn

## Project Structure

```
se_project_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Supabase client initialization
│   ├── models.py            # Pydantic models for validation
│   ├── auth.py              # Authentication utilities
│   └── routers/
│       ├── __init__.py
│       ├── auth_router.py   # Authentication endpoints
│       └── tasks_router.py  # Task management endpoints
├── database/
│   └── schema.sql           # Supabase database schema
├── .env                     # Environment variables
├── .gitignore
├── Main.py                  # Application entry point
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or higher
- Supabase account and project
- Git

### 2. Clone Repository

```bash
git clone <repository-url>
cd se_project_backend
```

### 3. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Supabase

#### A. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Note your project URL and API keys

#### B. Run Database Schema
1. Go to Supabase Dashboard > SQL Editor
2. Copy the contents of `database/schema.sql`
3. Execute the SQL script to create all tables, indexes, and policies

#### C. Get API Keys
1. Go to Project Settings > API
2. Copy the following:
   - Project URL
   - `anon` `public` key (for SUPABASE_KEY)
   - `service_role` key (optional, for admin operations)

### 6. Configure Environment Variables

Update the `.env` file with your Supabase credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Application Configuration
APP_NAME=SkillBridge API
APP_VERSION=1.0.0
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 7. Run the Application

```bash
# Using Main.py
python Main.py

# OR using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

#### POST /auth/register (SKIL-7)
Register a new user account

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "username": "johndoe",
  "bio": "Computer Science Student",
  "skills": ["Python", "FastAPI", "React"],
  "student_id": "CS2024001",
  "university": "ABC University"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "uuid-here",
  "user": {
    "id": "uuid-here",
    "email": "student@example.com",
    "full_name": "John Doe",
    "username": "johndoe",
    ...
  }
}
```

#### POST /auth/login (SKIL-8)
Authenticate user and get access token

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "jwt-token-here",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-here",
    "email": "student@example.com",
    ...
  }
}
```

### Tasks

#### POST /tasks/ (SKIL-11)
Create a new micro-task (requires authentication)

**Headers:**
```
Authorization: Bearer <access-token>
```

**Request Body:**
```json
{
  "title": "Build a React Component",
  "description": "Need a reusable React component for user profiles",
  "category": "Frontend Development",
  "budget": 50.00,
  "deadline": "2024-04-01T10:00:00Z",
  "tags": ["React", "JavaScript", "UI"]
}
```

**Response:**
```json
{
  "id": "task-uuid",
  "title": "Build a React Component",
  "description": "Need a reusable React component for user profiles",
  "category": "Frontend Development",
  "budget": 50.00,
  "status": "open",
  "creator_id": "user-uuid",
  "deadline": "2024-04-01T10:00:00Z",
  "tags": ["React", "JavaScript", "UI"],
  "created_at": "2024-03-01T10:00:00Z",
  "creator": {
    "id": "user-uuid",
    "full_name": "John Doe",
    "username": "johndoe",
    "email": "student@example.com"
  }
}
```

#### GET /tasks/ (SKIL-12)
Browse all tasks

**Query Parameters:**
- `status_filter`: Filter by status (default: "open")
- `limit`: Max results (1-100, default: 50)
- `offset`: Pagination offset (default: 0)

**Example:**
```
GET /tasks/?status_filter=open&limit=10&offset=0
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "task-uuid",
      "title": "Build a React Component",
      ...
      "creator": {
        "id": "user-uuid",
        "full_name": "John Doe",
        ...
      }
    }
  ],
  "total": 25
}
```

#### GET /tasks/search (SKIL-13)
Search tasks by keyword and filters

**Query Parameters:**
- `keyword`: Search in title/description
- `category`: Filter by category
- `min_budget`: Minimum budget
- `max_budget`: Maximum budget
- `status_filter`: Filter by status (default: "open")
- `limit`: Max results (1-100, default: 50)
- `offset`: Pagination offset (default: 0)

**Example:**
```
GET /tasks/search?keyword=react&category=Frontend%20Development&min_budget=20&max_budget=100
```

**Response:**
```json
{
  "tasks": [...],
  "total": 5
}
```

#### GET /tasks/{task_id}
Get detailed information about a specific task

**Response:**
```json
{
  "id": "task-uuid",
  "title": "Build a React Component",
  ...
  "creator": {...}
}
```

## Authentication Flow

### For Protected Endpoints

1. Register or login to get an access token
2. Include the token in the Authorization header:
   ```
   Authorization: Bearer <your-access-token>
   ```
3. The token is valid for the duration specified in `expires_in`

### Example using cURL

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User","username":"testuser"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Create Task (with token)
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"title":"Test Task","description":"This is a test task","category":"Testing","budget":25.50}'
```

## Database Schema

The database includes the following tables:

- **profiles**: User profile information (extends Supabase Auth)
- **tasks**: Micro-task listings
- **task_applications**: Applications from users to work on tasks
- **ratings**: Task completion ratings (for future sprints)

All tables include:
- Row Level Security (RLS) policies
- Automatic timestamp management
- Proper foreign key relationships
- Indexes for performance

See `database/schema.sql` for complete schema definition.

## Testing

### Using Interactive Docs

1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the required parameters
5. Click "Execute"

### Using Postman or Thunder Client

Import the following base URL:
```
http://localhost:8000
```

Create requests for each endpoint following the API documentation above.

## Development

### Adding New Endpoints

1. Create or modify router files in `app/routers/`
2. Define Pydantic models in `app/models.py`
3. Include router in `app/main.py`
4. Update this README with endpoint documentation

### Code Structure

- **Models**: Define in `app/models.py` using Pydantic
- **Routes**: Create in `app/routers/` as separate modules
- **Database**: Use `app/database.py` Supabase client
- **Auth**: Protect routes using `Depends(get_current_user)`

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure virtual environment is activated
2. **Supabase Connection Error**: Check SUPABASE_URL and SUPABASE_KEY in .env
3. **Authentication Error**: Ensure you're using the correct token format
4. **CORS Error**: Add your frontend URL to ALLOWED_ORIGINS in .env

### Logs

Enable debug mode in `.env`:
```env
DEBUG=True
```

This will show detailed error messages and auto-reload on code changes.

## Sprint 1 Completion Checklist

- [x] SKIL-7: User Registration API
- [x] SKIL-8: User Login API
- [x] SKIL-11: Post Micro Task API
- [x] SKIL-12: Browse Tasks API
- [x] SKIL-13: Search Tasks API
- [x] Supabase Database Schema
- [x] JWT Authentication
- [x] Input Validation
- [x] Error Handling
- [x] API Documentation

## Next Steps (Future Sprints)

- Task assignment workflow
- Real-time chat integration
- File upload for task attachments
- Rating and review system
- Payment integration
- Notification system

## Contributors

- Backend Developer: [Your Name]
- Scrum Master: [Name]
- Product Owner: [Name]
- Frontend Developer: [Name]

## License

This project is part of an academic course on Software Engineering.
