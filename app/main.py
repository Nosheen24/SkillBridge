

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth_router, tasks_router, profile_router
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Load settings
settings = get_settings()


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router)
app.include_router(tasks_router.router)
app.include_router(profile_router.router)


@app.get("/", tags=["Root"])
async def root():

    return {
        "message": "Welcome to SkillBridge API",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }



app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/post-task")
def post_task_page(request: Request):
    return templates.TemplateResponse(request, "post_task.html")

@app.get("/search")
def search_page(request: Request):
    return templates.TemplateResponse(request, "search_task.html")

@app.get("/browse")
def browse_tasks_page(request: Request):
    return templates.TemplateResponse(request, "browse_task.html")

@app.get("/forgot_password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse(request, "forgot_password.html")

@app.get("/task_detail")
def task_detail_page(request: Request):
    return templates.TemplateResponse(request, "task_detail.html")

@app.get("/applicants")
def applicants_page(request: Request):
    return templates.TemplateResponse(request, "applicants.html")

@app.get("/profile")
def profile_page(request: Request):
    return templates.TemplateResponse(request, "profile.html")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

