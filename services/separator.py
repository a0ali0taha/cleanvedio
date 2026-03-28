import os
import sys


def _app_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _has_em_runtime():
    root = _app_root()
    em_exe = os.path.join(root, "runtime", "em", "SpleeterExe.exe")
    model_dir = os.path.join(root, "runtime", "em", "models", "2stems")
    return os.path.exists(em_exe) and os.path.exists(model_dir)


def get_separator_backend():
    configured = str(os.environ.get("CLEANVEDIO_SEPARATOR_BACKEND", "em")).strip().lower()
    if configured in {"spleeter", "em"}:
        return configured
    if _has_em_runtime():
        return "em"
    return "spleeter"


def create_vocals(video):
    backend = get_separator_backend()
    if backend == "em":
        from services.separator_em import create_vocals as create_vocals_em

        return create_vocals_em(video)

    from services.spleeter import create_vocals as create_vocals_spleeter

    return create_vocals_spleeter(video)


def missing_separator_dependencies():
    backend = get_separator_backend()
    if backend == "em":
        from services.separator_em import missing_dependencies

        return missing_dependencies()

    missing = []
    import shutil
    import subprocess

    spleeter_bin = shutil.which("spleeter")
    if not spleeter_bin:
        missing.append("spleeter")
    else:
        try:
            result = subprocess.run(
                [spleeter_bin, "--help"], capture_output=True, timeout=10, check=False
            )
            if result.returncode != 0:
                missing.append("spleeter")
        except Exception:
            missing.append("spleeter")
    return missing
