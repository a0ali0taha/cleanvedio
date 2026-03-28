import os
import shutil
import subprocess
import math
import sys


DEFAULT_EM_EXE = "SpleeterExe.exe"

# ffmpeg emits stereo f32le @ 44100 Hz; SpleeterExe duration must match actual PCM bytes.
_F32LE_STEREO_44100_BYTES_PER_SEC = 44100 * 2 * 4


def _project_root():
    env_root = os.environ.get("CLEANVEDIO_DATA_DIR", "").strip()
    if env_root:
        return os.path.abspath(env_root)
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _candidate_model_dirs():
    project_root = _project_root()
    return [
        os.environ.get("CLEANVEDIO_EM_MODEL_DIR", "").strip(),
        os.path.join(project_root, "runtime", "em", "models", "2stems"),
        os.path.join(project_root, "runtime", "models", "2stems"),
        os.path.join(project_root, "models", "2stems"),
    ]


def resolve_em_executable():
    configured = os.environ.get("CLEANVEDIO_EM_EXE", "").strip()
    if configured:
        if os.path.isabs(configured) and os.path.exists(configured):
            return configured
        in_path = shutil.which(configured)
        return in_path or configured

    root = _project_root()
    bundled = os.path.join(root, "runtime", DEFAULT_EM_EXE)
    if os.path.exists(bundled):
        return bundled

    from_path = shutil.which(DEFAULT_EM_EXE)
    return from_path or DEFAULT_EM_EXE


def resolve_model_dir():
    for candidate in _candidate_model_dirs():
        if candidate and os.path.exists(candidate):
            return os.path.abspath(candidate)
    return ""


def missing_dependencies():
    missing = []

    exe = resolve_em_executable()
    if not exe:
        missing.append("em_exe")
        return missing

    if not (os.path.isabs(exe) and os.path.exists(exe)):
        if not shutil.which(exe):
            missing.append("em_exe")

    model_dir = resolve_model_dir()
    if not model_dir:
        missing.append("em_models")

    return missing


def _probe_duration_seconds(input_audio_path):
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nk=1:nw=1",
                input_audio_path,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return 30
        duration = float(str(result.stdout).strip() or "0")
        return max(1, int(math.ceil(duration)))
    except Exception:
        return 30


def _duration_seconds_for_em_pcm(pcm_path):
    """Whole seconds implied by PCM file size (must match ffmpeg output, not ffprobe ceil)."""
    try:
        size = os.path.getsize(pcm_path)
    except OSError:
        return None
    if size <= 0:
        return None
    return max(1, size // _F32LE_STEREO_44100_BYTES_PER_SEC)


def _run_em_for_segment(input_audio_path, output_file):
    exe = resolve_em_executable()
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    chunk_seconds = int(os.environ.get("CLEANVEDIO_EM_CHUNK_SECONDS", "10"))
    input_pcm = os.path.join(output_dir, "_input_f32le.pcm")
    output_pcm_base = os.path.join(output_dir, "_vocals_f32le")
    output_pcm = output_pcm_base + ".pcm"   

    try:
        # Em splitter expects float32 PCM input and writes float32 PCM output.
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_audio_path,
                "-f",
                "f32le",
                "-ac",
                "2",
                "-ar",
                "44100",
                input_pcm,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        file_duration = _duration_seconds_for_em_pcm(input_pcm)
        if file_duration is None:
            file_duration = _probe_duration_seconds(input_audio_path)

        subprocess.run(
            [exe, input_pcm, output_pcm_base, str(file_duration), str(chunk_seconds)],
            check=True,
            capture_output=True,
            text=True,
        )

        if not os.path.exists(output_pcm):
            return False

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "f32le",
                "-ac",
                "2",
                "-ar",
                "44100",
                "-i",
                output_pcm,
                output_file,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as exc:
        print(f"Error while calling Em separator: {exc}")
        print(f"Em stdout: {exc.stdout}")
        print(f"Em stderr: {exc.stderr}")
        return False
    except Exception as exc:
        print(f"Unexpected Em error: {exc}")
        return False
    finally:
        for temp_path in (input_pcm, output_pcm):
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass


def create_vocals(video):
    vocals_folder = os.path.join(video.processing_input_folder, "vocals")
    if not os.path.exists(vocals_folder):
        os.makedirs(vocals_folder)

    vocal_files = []
    for mp3_file in video.audio_segments_paths:
        segment_name = os.path.basename(mp3_file).replace(".mp3", "")
        output_file = os.path.join(vocals_folder, segment_name, "vocals.mp3")

        if not os.path.exists(output_file):
            success = _run_em_for_segment(mp3_file, output_file)
            if not success:
                print(f"Failed Em separation for {mp3_file}")
                # stop the process and return the error
                raise RuntimeError(f"Failed Em separation for {mp3_file}")

        if os.path.exists(output_file):
            vocal_files.append(output_file)
        else:
            print(f"Warning: Expected vocals file not found: {output_file}")

    if len(vocal_files) == 0:
        raise RuntimeError(
            "No vocals files were produced by Em backend. "
            "Check CLEANVEDIO_EM_EXE and CLEANVEDIO_EM_MODEL_DIR."
        )

    video.vocals_paths = vocal_files
