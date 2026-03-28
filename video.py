from dataclasses import dataclass, field
from typing import List


@dataclass
class Video:
    processing_input_folder: str
    url: str = ""
    input_video_path: str = ""
    output_video_path: str = ""
    detached_mp3: str = ""
    audio_segments_paths: List[str] = field(default_factory=list)
    vocals_paths: List[str] = field(default_factory=list)
    output_audio_path: str = ""
