"""
Web dashboard routes for the Code Review Assistant.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

router = APIRouter(tags=["dashboard"])

# Set up templates directory
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """
    Serve the main dashboard page.
    
    Returns:
        HTML response with the dashboard interface
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """
    Alternative route for the dashboard page.
    
    Returns:
        HTML response with the dashboard interface
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})