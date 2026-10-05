import asyncio
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional
from pydantic import BaseModel, Field
from app.core.logging import app_logger

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"

class JobLog(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = "info"
    message: str

class JobExecutionRecord(BaseModel):
    job_id: str
    tenant_id: str
    module_id: Optional[str] = None
    search_id: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    retry_count: int = 0
    max_retries: int = 1
    timeout_seconds: int = 30
    logs: List[JobLog] = Field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class JobManager:
    """Manages asynchronous isolated jobs with timeouts, retry policies, and tracking."""
    
    def __init__(self):
        self._jobs: Dict[str, JobExecutionRecord] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        
    def create_job(
        self,
        tenant_id: str,
        module_id: Optional[str] = None,
        search_id: Optional[str] = None,
        timeout_seconds: int = 30,
        max_retries: int = 0
    ) -> JobExecutionRecord:
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        job = JobExecutionRecord(
            job_id=job_id,
            tenant_id=tenant_id,
            module_id=module_id,
            search_id=search_id,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries
        )
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[JobExecutionRecord]:
        return self._jobs.get(job_id)

    def list_jobs(self, tenant_id: Optional[str] = None, search_id: Optional[str] = None) -> List[JobExecutionRecord]:
        jobs = list(self._jobs.values())
        if tenant_id:
            jobs = [j for j in jobs if j.tenant_id == tenant_id]
        if search_id:
            jobs = [j for j in jobs if j.search_id == search_id]
        return sorted(jobs, key=lambda x: x.started_at or datetime.min, reverse=True)

    def add_log(self, job_id: str, message: str, level: str = "info"):
        job = self._jobs.get(job_id)
        if job:
            job.logs.append(JobLog(message=message, level=level))

    async def run_async_job(
        self,
        job_id: str,
        target_coro_fn: Callable[[], Coroutine[Any, Any, Any]]
    ) -> JobExecutionRecord:
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
            
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        self.add_log(job_id, f"Job started for module '{job.module_id}'")
        
        start_time = time.time()
        
        try:
            # Wrap execution with strict timeout isolation
            result = await asyncio.wait_for(target_coro_fn(), timeout=float(job.timeout_seconds))
            job.status = JobStatus.COMPLETED
            if isinstance(result, dict):
                job.result = result
            elif hasattr(result, "dict"):
                job.result = result.dict()
            else:
                job.result = {"data": result}
            job.completed_at = datetime.utcnow()
            self.add_log(job_id, "Job finished successfully")
        except asyncio.TimeoutError:
            job.status = JobStatus.TIMED_OUT
            job.error = f"Job exceeded execution timeout of {job.timeout_seconds}s"
            job.completed_at = datetime.utcnow()
            self.add_log(job_id, job.error, level="warning")
            app_logger.warning(f"Job {job_id} timed out", extra={"job_id": job_id, "module_id": job.module_id})
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            self.add_log(job_id, f"Execution failed: {str(e)}", level="error")
            app_logger.error(f"Job {job_id} failed: {e}", extra={"job_id": job_id, "module_id": job.module_id})
        finally:
            job.duration_ms = round((time.time() - start_time) * 1000, 2)
            
        return job

# Singleton job manager
job_manager = JobManager()
