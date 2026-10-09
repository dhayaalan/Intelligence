from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.search import router as search_router
from app.api.v1.investigations import router as investigations_router
from app.api.v1.cases import router as cases_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.entities import router as entities_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.findings import router as findings_router
from app.api.v1.reports import router as reports_router
from app.api.v1.modules import router as modules_router
from app.api.v1.tenants import router as tenants_router
from app.api.v1.users import router as users_router
from app.api.v1.audit import router as audit_router
from app.api.v1.providers import router as providers_router
from app.api.v1.platform import router as platform_router
from app.api.v1.tools import router as tools_router
from app.api.v1.news import router as news_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(platform_router)
api_v1_router.include_router(tools_router)
api_v1_router.include_router(news_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(cases_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(investigations_router)
api_v1_router.include_router(entities_router)
api_v1_router.include_router(evidence_router)
api_v1_router.include_router(findings_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(modules_router)
api_v1_router.include_router(providers_router)
api_v1_router.include_router(tenants_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(audit_router)


