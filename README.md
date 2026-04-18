# SkillBridge Backend API

FastAPI backend for SkillBridge - A Freelance & Micro-Task Platform for Students

## Sprint 1 - Task Completion

This implementation includes all Sprint 1 backend tasks:

- **SKIL-7**: User Registration API
- **SKIL-8**: User Login API
- **SKIL-11**: Post Micro Task API
- **SKIL-12**: Browse Tasks API
- **SKIL-13**: Search Tasks API

## Sprint 2 - Task Completion

This implementation includes all Sprint 2 backend tasks:

- **SKIL-9**: User Logout API
- **SKIL-10**: Password Reset & Set New Password API
- **SKIL-14**: Mark Task Complete API
- **SKIL-15**: Apply/Bid on Task API
- **SKIL-16**: View Applicants API

## Sprint 3 - Task Completion

This implementation includes all Sprint 3 backend tasks:

- **SKIL-17**: Applicant Decision (Accept/Reject)
- **SKIL-18**: Create Skill Profile (Skills, Experience, Bio)
- **SKIL-19**: Edit User Profile
- **SKIL-20**: Portfolio Upload & Link Support

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
│       ├── auth_router.py      # Authentication endpoints
|       ├── tasks_router.py     # Task management endpoints
│       └── profile_router.py   # Profile management
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
   - `service_role` key (for SUPABASE_SERVICE_KEY)

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
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication (Sprint 1)

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
    "username": "johndoe"
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
    "email": "student@example.com"
  }
}
```

### Authentication (Sprint 2)

#### POST /auth/logout (SKIL-9)
Logout the currently authenticated user

**Headers:** `Authorization: Bearer <access-token>`

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

#### POST /auth/password-reset (SKIL-10)
Send password reset email to user

**Request Body:**
```json
{
  "email": "student@example.com"
}
```

**Response:**
```json
{
  "message": "Password reset email sent successfully"
}
```

#### POST /auth/set-new-password (SKIL-10)
Set new password after reset (requires authentication)

**Headers:** `Authorization: Bearer <access-token>`

**Request Body:**
```json
{
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password updated successfully"
}
```

### Profile & Task Management (Sprint 3)

#### POST /profile/me (SKIL-18)
Create/Save skill profile (Skills, Experience, Bio)

**Request Body:**
```json
{
  "skills": ["Python", "FastAPI"],
  "experience": "2 years of internship experience",
  "bio": "Passionate backend developer"
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "skills": ["Python", "FastAPI"],
  "experience": "2 years of internship experience",
  "bio": "Passionate backend developer"
}
```

#### PUT /profile/me (SKIL-19)
Update existing profile information

**Request Body:**
```json
{
  "skills": ["Python", "FastAPI", "SQL"],
  "experience": "3 years of experience",
  "bio": "Updated bio"
}
```

#### GET /profile/me
Retrieve authenticated user's profile

**Response:**
```json
{
  "id": "uuid-here",
  "email": "student@example.com",
  "full_name": "John Doe",
  "skills": ["Python", "FastAPI", "SQL"],
  "experience": "3 years of experience"
}
```

#### PATCH /tasks/{task_id}/decision (SKIL-17)
Accept or reject an applicant (only task creator)

**Request Body:**
```json
{
  "decision": "accepted"
}
```

**Response:**
```json
{
  "message": "Application status updated successfully",
  "status": "accepted"
}
```

### Tasks (Sprint 1)

#### POST /tasks/ (SKIL-11)
Create a new micro-task (requires authentication)

**Headers:** `Authorization: Bearer <access-token>`

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
  "status": "open",
  "creator_id": "user-uuid",
  "budget": 50.00
}
```

#### GET /tasks/ (SKIL-12)
Browse all tasks

**Query Parameters:**
- `status_filter`: Filter by status (default: "open")
- `limit`: Max results (1-100, default: 50)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "tasks": [...],
  "total": 25
}
```

### Tasks (Sprint 2)

#### POST /tasks/{task_id}/apply (SKIL-15)
Apply/Bid on a task (requires authentication)

**Headers:** `Authorization: Bearer <access-token>`

**Request Body:**
```json
{
  "message": "I can help with this task"
}
```

**Response:**
```json
{
  "message": "Application submitted successfully",
  "data": {
    "task_id": "uuid",
    "applicant_id": "uuid",
    "message": "I can help with this task",
    "status": "pending"
  }
}
```

#### GET /tasks/{task_id}/applicants (SKIL-16)
View all applicants for a task (only task creator)

**Headers:** `Authorization: Bearer <access-token>`

**Response:**
```json
{
  "task_id": "uuid",
  "total_applicants": 1,
  "applicants": [
    {
      "id": "uuid",
      "message": "I can help",
      "status": "pending",
      "profiles": {
        "full_name": "John Doe",
        "email": "john@example.com"
      }
    }
  ]
}
```

#### PATCH /tasks/{task_id}/complete (SKIL-14)
Mark a task as complete (only task creator)

**Headers:** `Authorization: Bearer <access-token>`

**Response:**
```json
{
  "message": "Task marked as complete",
  "data": {
    "status": "completed"
  }
}
```

### Tasks (Sprint 3)

#### PATCH /tasks/{task_id}/decision (SKIL-17)
Accept or reject an applicant (only for the task creator)

**Headers:** `Authorization: Bearer <access-token>`

**Request Body:**
```json
{
  "decision": "accepted"
}
```

**Response:**
```json
{
  "message": "Application status updated successfully",
  "application_id": "uuid",
  "task_id": "uuid",
  "applicant_id": "uuid",
  "status": "accepted"
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

# Logout
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Apply for Task
curl -X POST http://localhost:8000/tasks/TASK_ID/apply \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"message":"I can help with this task"}'

# Mark Task Complete
curl -X PATCH http://localhost:8000/tasks/TASK_ID/complete \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
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

## Sprint 2 Completion Checklist

- [x] SKIL-9: User Logout API
- [x] SKIL-10: Password Reset API
- [x] SKIL-10: Set New Password API
- [x] SKIL-14: Mark Task Complete API
- [x] SKIL-15: Apply/Bid on Task API
- [x] SKIL-16: View Applicants API
- [x] JWT Authentication on all protected routes
- [x] Input Validation
- [x] Error Handling
- [x] API Documentation

## Sprint 3 Completion Checklist

- [x] SKIL-17: Applicant Decision (Accept/Reject) API
- [x] SKIL-18: Create Skill Profile API
- [x] SKIL-19: Edit Profile API
- [x] SKIL-20: Portfolio Upload & Link Support API
- [x] Database Schema Migration for Profiles
- [x] Storage Bucket configuration for Portfolios
- [x] JWT Authentication on all protected routes
- [x] Input Validation
- [x] Error Handling
- [x] API Documentation

## Next Steps (Future Sprints)

- View Ratings
- Give Rating
- View All Users
- Remove Content

## Contributors

- Backend Developer + QA: Maheen
- Scrum Master: Aniqa Saba
- Product Owner: Nosheen
- Frontend Developer: Ujala Kiran


## License

This project is part of an academic course on Software Engineering.
