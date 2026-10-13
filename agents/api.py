"""FastAPI REST server: Ottawa decision support plus legacy demonstration endpoints."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from clinical_rules import evaluate
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Ottawa Ankle, Midfoot and Knee Rules API",
    description="Adult clinical radiography decision support. Legacy /api/audit routes are nonclinical demonstrations.",
    version="3.1.0",
)


class ClinicalAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    site: str
    age: StrictInt = Field(ge=0, le=120)
    pain_present: StrictBool
    acute_blunt_trauma: StrictBool
    reliable_exam: StrictBool
    posterior_lateral_malleolus_tenderness: StrictBool | None = None
    posterior_medial_malleolus_tenderness: StrictBool | None = None
    navicular_tenderness: StrictBool | None = None
    fifth_metatarsal_base_tenderness: StrictBool | None = None
    fibular_head_tenderness: StrictBool | None = None
    isolated_patellar_tenderness: StrictBool | None = None
    cannot_flex_90: StrictBool | None = None
    unable_four_steps_immediately: StrictBool | None = None
    unable_four_steps_at_assessment: StrictBool | None = None


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "ottawa-ankle-knee-rules", "version": "3.1.0"}


@app.post("/api/clinical")
def clinical(payload: ClinicalAssessment):
    try:
        return evaluate(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL",
    }


@app.post("/api/audit", deprecated=True)
def api_audit(payload: SystemTaskPayload):
    """Legacy threshold-based demo; not an Ottawa clinical decision."""
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat", deprecated=True)
def api_chat(req: ChatRequest):
    try:
        return {"response": supervisor.query_supervisory_chat(req.query)}
    except SecurityException:
        raise HTTPException(status_code=400, detail="Input contains a potentially identifying field")


@app.get("/api/audit/logs", deprecated=True)
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


# Registered last so API routes take precedence over the static application.
app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent.parent / "web", html=True), name="web")
