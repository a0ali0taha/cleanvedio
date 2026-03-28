import json
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from paths import ensure_data_root
from services.mylogger import logger


class JobStatus(Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    EXTRACTING_AUDIO = "extracting_audio"
    SPLITTING = "splitting"
    SEPARATING_VOCALS = "separating_vocals"
    MERGING = "merging"
    ATTACHING = "attaching"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JobInfo:
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    progress: str = ""
    source: str = ""
    filename: str = ""
    error: str = ""
    output_path: str = ""
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0
    is_playlist: bool = False

    def to_dict(self):
        now = time.time()
        elapsed = (self.completed_at or now) - self.created_at
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "progress": self.progress,
            "source": self.source,
            "filename": self.filename,
            "error": self.error,
            "output_path": self.output_path,
            "elapsed": round(elapsed, 1),
        }


_DATA_ROOT = ensure_data_root()
JOBS_FILE = os.path.join(_DATA_ROOT, "jobs.json")


class JobQueue:
    def __init__(self):
        self._jobs: Dict[str, JobInfo] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        if not os.path.exists(JOBS_FILE):
            return
        try:
            with open(JOBS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for d in data:
                job = JobInfo(
                    job_id=d["job_id"],
                    status=JobStatus(d["status"]),
                    progress=d.get("progress", ""),
                    source=d.get("source", ""),
                    filename=d.get("filename", ""),
                    error=d.get("error", ""),
                    output_path=d.get("output_path", ""),
                    created_at=d.get("created_at", 0),
                    completed_at=d.get("completed_at", 0),
                    is_playlist=d.get("is_playlist", False),
                )
                if job.status not in (JobStatus.COMPLETED, JobStatus.FAILED):
                    job.status = JobStatus.FAILED
                    job.error = "Interrupted by server restart"
                    job.completed_at = job.completed_at or time.time()
                self._jobs[job.job_id] = job
        except Exception as e:
            logger.error(f"Failed to load jobs: {e}")

    def _save(self):
        try:
            jobs = list(self._jobs.values())
            data = []
            for j in jobs:
                data.append(
                    {
                        "job_id": j.job_id,
                        "status": j.status.value,
                        "progress": j.progress,
                        "source": j.source,
                        "filename": j.filename,
                        "error": j.error,
                        "output_path": j.output_path,
                        "created_at": j.created_at,
                        "completed_at": j.completed_at,
                        "is_playlist": j.is_playlist,
                    }
                )
            with open(JOBS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save jobs: {e}")

    def create(
        self,
        source: str,
        filename: str,
        is_playlist: bool = False,
    ) -> str:
        job_id = uuid.uuid4().hex[:8]
        with self._lock:
            self._jobs[job_id] = JobInfo(
                job_id=job_id,
                source=source,
                filename=filename,
                is_playlist=is_playlist,
            )
            self._save()
        return job_id

    def get(self, job_id: str) -> Optional[JobInfo]:
        return self._jobs.get(job_id)

    def update(self, job_id: str, status: JobStatus, progress: str = ""):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = status
                job.progress = progress
                self._save()

    def complete(self, job_id: str, output_path: str = ""):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.COMPLETED
                job.output_path = output_path
                job.completed_at = time.time()
                self._save()

    def fail(self, job_id: str, error: str):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.FAILED
                job.error = error
                job.completed_at = time.time()
                self._save()

    def list_all(self) -> list:
        with self._lock:
            return [j.to_dict() for j in reversed(list(self._jobs.values()))]


job_queue = JobQueue()
