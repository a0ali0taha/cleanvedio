"""Map raw errors and exceptions to stable, user-facing messages."""


def friendly_failure_message(raw) -> str:
    text = str(raw or "").strip()
    lower = text.lower()
    if "ffmpeg" in lower:
        return (
            "FFmpeg is missing or not configured correctly. "
            "Reinstall the app bundle and try again."
        )
    if "spleeter" in lower or "separator" in lower or "2stems" in lower:
        return (
            "The vocal separation runtime is missing or misconfigured. "
            "Reinstall the app bundle and try again."
        )
    if "permission denied" in lower:
        return (
            "The app cannot access a required file or folder. "
            "Try running from a writable location."
        )
    if "file not found" in lower:
        return (
            "A required input file is missing. Please select the file again and retry."
        )
    if text:
        return text
    return "Processing failed due to an unexpected error."
