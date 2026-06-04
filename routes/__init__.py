from fastapi import APIRouter

from .auth import router as auth
from .dashboard import router as dashboard
from .system import router as system
from .users import router as users
from .departments import router as departments
from .status import router as status
from .projects import router as projects
from .tickets import router as tickets
from .tickets_attachments import router as tickets_attachments
from .roles import router as roles
from .companies import router as companies
from .ticket_comments import router as ticket_comments
from .ticket_comments_attachments import router as ticket_comments_attachments
from .today_ticket_work import router as today_ticket_work
from .reports import route as reports

router = APIRouter()

router.include_router(auth.router)
router.include_router(dashboard.router)
router.include_router(system.router)
router.include_router(users.router)
router.include_router(departments.router)
router.include_router(status.router)
router.include_router(projects.router)
router.include_router(tickets.router)
router.include_router(tickets_attachments.router)
router.include_router(roles.router)
router.include_router(companies.router)
router.include_router(ticket_comments.router)
router.include_router(ticket_comments_attachments.router)
router.include_router(today_ticket_work.router)
router.include_router(reports.router)


