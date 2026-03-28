import os
import re
import time
import uuid
import unicodedata
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple

import jobs as _jobs
from jobs import JobInfo, JobQueue, JobStatus, job_queue
from paths import get_data_root
from user_messages import friendly_failure_message
from services.mylogger import logger


@dataclass
class PipelineResult:
    success: bool
    output_path: str = ""
    error: str = ""
    duration_seconds: float = 0


def _run_detach_if_needed(video: Any) -> None:
    from services.detach import detach_audio

    if not os.path.exists(video.detached_mp3):
        detach_audio(video)


def _run_split(video: Any) -> None:
    from services.audio_split import split_video

    split_video(video)


def _run_separate(video: Any) -> None:
    from services.separator import create_vocals

    create_vocals(video)


def _run_merge(video: Any) -> None:
    from services.audio_merge import combine_audio_segments

    combine_audio_segments(video)


def _run_attach(video: Any) -> None:
    from services.attach import attach_audio

    attach_audio(video)


PipelineStep = Tuple[JobStatus, str, Callable[[Any], None]]


def default_pipeline_steps() -> List[PipelineStep]:
    return [
        (JobStatus.EXTRACTING_AUDIO, "Extracting audio from video", _run_detach_if_needed),
        (JobStatus.SPLITTING, "Splitting audio into segments", _run_split),
        (JobStatus.SEPARATING_VOCALS, "Separating vocals with Spleeter", _run_separate),
        (JobStatus.MERGING, "Merging vocal segments", _run_merge),
        (JobStatus.ATTACHING, "Attaching clean audio to video", _run_attach),
    ]


class Pipeline:
    def __init__(
        self,
        job_id: Optional[str] = None,
        job_queue: Optional[JobQueue] = None,
        steps: Optional[List[PipelineStep]] = None,
    ):
        self.job_id = job_id
        self._job_queue = job_queue if job_queue is not None else _jobs.job_queue
        self._steps = steps if steps is not None else default_pipeline_steps()

    def _update(self, status: JobStatus, progress: str = ""):
        if self.job_id:
            self._job_queue.update(self.job_id, status, progress)
        logger.info(f"[{self.job_id or 'cli'}] {status.value}: {progress}")

    @staticmethod
    def _sanitize_filename(name):
        normalized = unicodedata.normalize("NFKC", name)
        return re.sub(r'[<>:"|?*]', "_", normalized)

    def _init_dirs(self, video):
        os.makedirs(video.processing_input_folder, exist_ok=True)
        video.detached_mp3 = os.path.join(video.processing_input_folder, "det.mp3")
        video_file_name = self._sanitize_filename(os.path.basename(video.input_video_path))
        final_dir = os.path.join(get_data_root(), "final")
        os.makedirs(final_dir, exist_ok=True)
        video.output_video_path = os.path.join(final_dir, video_file_name)

    def process(self, video) -> PipelineResult:
        t0 = time.time()
        try:
            self._init_dirs(video)

            for status, progress, step_fn in self._steps:
                self._update(status, progress)
                step_fn(video)

            elapsed = time.time() - t0
            if self.job_id:
                self._job_queue.complete(self.job_id, video.output_video_path)
            return PipelineResult(
                success=True,
                output_path=video.output_video_path,
                duration_seconds=elapsed,
            )
        except Exception as e:
            elapsed = time.time() - t0
            msg = friendly_failure_message(e)
            if self.job_id:
                self._job_queue.fail(self.job_id, msg)
            logger.error(f"Pipeline failed: {e}")
            return PipelineResult(success=False, error=msg, duration_seconds=elapsed)

    def process_youtube(self, url, output_path, is_playlist=False):
        from services.youtube_downloader_with_jdownloader import download_playlist, download_video
        from video import Video

        self._update(JobStatus.DOWNLOADING, "Downloading from YouTube")
        os.makedirs(output_path, exist_ok=True)

        job_tag = self.job_id or uuid.uuid4().hex[:8]

        results = []
        if is_playlist:
            video_paths = download_playlist(url, output_path, use_jdownloader=False)
            for i, (title, file_path) in enumerate(video_paths.items(), 1):
                if not file_path or not os.path.exists(file_path):
                    continue
                self._update(JobStatus.DOWNLOADING, f"Downloaded: {title}")
                video = Video(
                    processing_input_folder=os.path.join(output_path, f"{job_tag}_{i}"),
                    input_video_path=file_path,
                    url=url,
                )
                results.append(self.process(video))
        else:
            _title, video_path = download_video(url, output_path, use_jdownloader=False)
            if not video_path or not os.path.exists(video_path):
                err = f"Download failed for {url}"
                detail = friendly_failure_message(err)
                if self.job_id:
                    self._job_queue.fail(self.job_id, detail)
                return [PipelineResult(success=False, error=detail)]
            video = Video(
                processing_input_folder=os.path.join(output_path, job_tag),
                input_video_path=video_path,
                url=url,
            )
            results.append(self.process(video))

        return results

    def process_file(self, video_path):
        from video import Video

        if not os.path.exists(video_path):
            err = f"File not found: {video_path}"
            detail = friendly_failure_message(err)
            if self.job_id:
                self._job_queue.fail(self.job_id, detail)
            return PipelineResult(success=False, error=detail)

        processing_folder = os.path.splitext(video_path)[0]
        os.makedirs(processing_folder, exist_ok=True)
        video = Video(
            processing_input_folder=processing_folder,
            input_video_path=video_path,
        )
        return self.process(video)


__all__ = [
    "Pipeline",
    "PipelineResult",
    "JobStatus",
    "JobInfo",
    "JobQueue",
    "job_queue",
    "default_pipeline_steps",
]
