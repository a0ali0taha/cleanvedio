import os
import shutil
import socket
import subprocess
import sys
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort

from jobs import JobStatus, job_queue
from paths import get_app_root, get_data_root, get_resource_root
from pipeline import Pipeline
from services.separator import get_separator_backend, missing_separator_dependencies
from user_messages import friendly_failure_message


def _human_size(size_bytes):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def _is_truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _detect_local_ipv4():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if ip and not ip.startswith("127."):
                return ip
    except OSError:
        pass

    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip and not ip.startswith("127."):
                return ip
    except OSError:
        pass

    return "127.0.0.1"


def _resolve_server_binding():
    env_host = os.environ.get("CLEANVEDIO_HOST")
    env_port = os.environ.get("CLEANVEDIO_PORT")
    host = env_host if env_host else "127.0.0.1"
    default_port = 8787

    try:
        port = int(env_port) if env_port else default_port
    except ValueError:
        port = default_port

    return host, port


def _is_port_available(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return sock.connect_ex((host, port)) != 0
    except OSError:
        return False


def _find_available_port(host, start_port, max_attempts=30):
    for offset in range(max_attempts):
        candidate = start_port + offset
        if _is_port_available(host, candidate):
            return candidate
    return start_port


def _prepend_path_if_exists(path):
    if not path or not os.path.exists(path):
        return
    current = os.environ.get("PATH", "")
    parts = current.split(os.pathsep) if current else []
    if path not in parts:
        os.environ["PATH"] = path + (os.pathsep + current if current else "")


def _configure_packaged_runtime_env(app_root):
    if not getattr(sys, "frozen", False):
        return

    ffmpeg_bin = os.path.join(app_root, "runtime", "ffmpeg", "bin")
    em_root = os.path.join(app_root, "runtime", "em")
    em_exe = os.path.join(em_root, "SpleeterExe.exe")
    em_models = os.path.join(em_root, "models", "2stems")

    _prepend_path_if_exists(ffmpeg_bin)
    _prepend_path_if_exists(em_root)

    if os.path.exists(em_exe):
        os.environ.setdefault("CLEANVEDIO_EM_EXE", em_exe)
    if os.path.exists(em_models):
        os.environ.setdefault("CLEANVEDIO_EM_MODEL_DIR", em_models)

    if (
        "CLEANVEDIO_SEPARATOR_BACKEND" not in os.environ
        and os.path.exists(em_exe)
        and os.path.exists(em_models)
    ):
        os.environ["CLEANVEDIO_SEPARATOR_BACKEND"] = "em"


APP_ROOT = get_app_root()
RESOURCE_ROOT = get_resource_root()
DATA_ROOT = get_data_root()
_configure_packaged_runtime_env(APP_ROOT)
INPUT_DIR = os.path.join(DATA_ROOT, "input")
FINAL_DIR = os.path.join(DATA_ROOT, "final")
DOWNLOADS_DIR = os.path.join(DATA_ROOT, "downloads")
THUMBS_DIR = os.path.join(FINAL_DIR, ".thumbs")
TEMPLATE_DIR = os.path.join(RESOURCE_ROOT, "templates")
ASSETS_DIR = os.path.join(RESOURCE_ROOT, "assets")
SERVER_HOST, SERVER_PORT = _resolve_server_binding()
SERVER_DEBUG = _is_truthy(os.environ.get("CLEANVEDIO_DEBUG", "0"))

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(THUMBS_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FINAL_DIR, template_folder=TEMPLATE_DIR)


def _missing_dependencies():
    missing = []
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        missing.append("ffmpeg")
    else:
        try:
            ffmpeg_check = subprocess.run(
                [ffmpeg_bin, "-version"], capture_output=True, timeout=8, check=False
            )
            if ffmpeg_check.returncode != 0:
                missing.append("ffmpeg")
        except Exception:
            missing.append("ffmpeg")

    missing.extend(missing_separator_dependencies())
    return missing


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/assets/<path:filename>')
def assets(filename):
    safe_path = os.path.abspath(os.path.join(ASSETS_DIR, filename))
    if not safe_path.startswith(os.path.abspath(ASSETS_DIR) + os.sep):
        abort(404)
    if not os.path.exists(safe_path):
        abort(404)
    return send_file(safe_path)


@app.route('/final')
def show_final_videos():
    final_path = FINAL_DIR
    if not os.path.exists(final_path):
        return "Final directory does not exist"

    per_page = 6
    page = request.args.get('page', 1, type=int)

    all_videos = []
    for file in os.listdir(final_path):
        if file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            full = os.path.join(final_path, file)
            mtime = os.path.getmtime(full)
            all_videos.append({
                'name': file,
                'mtime': mtime,
                'date': datetime.fromtimestamp(mtime).strftime('%b %d, %Y %H:%M'),
                'size': _human_size(os.path.getsize(full)),
            })

    all_videos.sort(key=lambda v: v['mtime'], reverse=True)
    total = len(all_videos)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    videos = all_videos[(page - 1) * per_page : page * per_page]

    return render_template('videos.html', videos=videos,
                           page=page, total_pages=total_pages, total=total)


@app.route('/final/<filename>', methods=['DELETE'])
def delete_video(filename):
    file_path = os.path.join(FINAL_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    try:
        os.remove(file_path)
        thumb = os.path.join(THUMBS_DIR, filename + '.jpg')
        if os.path.exists(thumb):
            os.remove(thumb)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/final/<filename>/thumbnail')
def video_thumbnail(filename):
    video_path = os.path.join(FINAL_DIR, filename)
    if not os.path.exists(video_path):
        return jsonify({"error": "File not found"}), 404

    thumbs_dir = THUMBS_DIR
    os.makedirs(thumbs_dir, exist_ok=True)
    thumb_path = os.path.join(thumbs_dir, filename + '.jpg')

    if not os.path.exists(thumb_path):
        try:
            subprocess.run([
                'ffmpeg', '-i', video_path,
                '-ss', '00:00:02', '-frames:v', '1',
                '-vf', 'scale=480:-1',
                '-q:v', '4', '-y', thumb_path
            ], capture_output=True, timeout=15)
        except Exception:
            pass

    if os.path.exists(thumb_path):
        return send_file(thumb_path, mimetype='image/jpeg')

    return '', 204


@app.route('/health')
def health():
    missing = _missing_dependencies()
    backend = get_separator_backend()
    status = 503 if missing else 200
    return jsonify({
        "ok": not missing,
        "separator_backend": backend,
        "missing_dependencies": missing,
        "host": SERVER_HOST,
        "port": SERVER_PORT,
        "launch_url": f"http://{SERVER_HOST}:{SERVER_PORT}",
        "data_root": DATA_ROOT,
    }), status


@app.route('/process', methods=['POST'])
def process():
    source = request.form.get('source', 'youtube')
    output_folder = request.form.get('output_folder', '').strip()
    is_playlist = 'playlist' in request.form

    missing = _missing_dependencies()
    if missing:
        return jsonify({
            "error": "The app is not ready yet. Missing required components: " + ", ".join(missing)
        }), 503

    if not output_folder:
        output_folder = DOWNLOADS_DIR

    output_folder = os.path.abspath(output_folder)
    try:
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(FINAL_DIR, exist_ok=True)
    except OSError:
        return jsonify({
            "error": "Could not prepare app folders. Try choosing another output folder."
        }), 500

    if source == 'youtube':
        youtube_url = request.form.get('youtube_url', '').strip()
        if not youtube_url:
            return jsonify({"error": "YouTube URL is required"}), 400

        job_id = job_queue.create(source="youtube", filename=youtube_url,
                                   is_playlist=is_playlist)
        pipe = Pipeline(job_id=job_id)

        def run():
            pipe.process_youtube(youtube_url, output_folder, is_playlist)

        threading.Thread(target=run, daemon=True).start()
        return jsonify({"job_id": job_id})
    else:
        if 'video_file' not in request.files:
            return jsonify({"error": "No video file selected"}), 400

        video_file = request.files['video_file']
        if not video_file or video_file.filename == '':
            return jsonify({"error": "No video file selected"}), 400

        safe_name = os.path.basename(video_file.filename)
        file_path = os.path.join(INPUT_DIR, safe_name)
        try:
            video_file.save(file_path)
        except OSError:
            return jsonify({
                "error": "Could not save uploaded file. Please check folder permissions and retry."
            }), 500

        job_id = job_queue.create(source="local", filename=safe_name)
        pipe = Pipeline(job_id=job_id)

        def run():
            pipe.process_file(file_path)

        threading.Thread(target=run, daemon=True).start()
        return jsonify({"job_id": job_id})


@app.route('/jobs')
def list_jobs():
    return jsonify(job_queue.list_all())


@app.route('/jobs/<job_id>')
def get_job(job_id):
    job = job_queue.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    data = job.to_dict()
    if job.status == JobStatus.FAILED:
        data["error"] = friendly_failure_message(job.error)
    return jsonify(data)


@app.route('/jobs/<job_id>/retry', methods=['POST'])
def retry_job(job_id):
    old_job = job_queue.get(job_id)
    if not old_job:
        return jsonify({"error": "Job not found"}), 404
    if old_job.status != JobStatus.FAILED:
        return jsonify({"error": "Only failed jobs can be retried"}), 400

    output_folder = DOWNLOADS_DIR
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(FINAL_DIR, exist_ok=True)

    new_id = job_queue.create(
        source=old_job.source, filename=old_job.filename,
        is_playlist=old_job.is_playlist,
    )
    pipe = Pipeline(job_id=new_id)

    if old_job.source == 'youtube':
        def run():
            pipe.process_youtube(old_job.filename, output_folder,
                                 old_job.is_playlist)
        threading.Thread(target=run, daemon=True).start()
    else:
        file_path = os.path.join(INPUT_DIR, old_job.filename)
        if not os.path.exists(file_path):
            job_queue.fail(new_id, f"File not found: {file_path}")
            return jsonify({"error": "Original file no longer exists"}), 404

        def run():
            pipe.process_file(file_path)
        threading.Thread(target=run, daemon=True).start()

    return jsonify({"job_id": new_id})


@app.route('/open-output-folder', methods=['POST'])
def open_output_folder():
    try:
        path = os.path.abspath(FINAL_DIR)
        os.makedirs(path, exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return jsonify({"success": True, "path": path})
    except Exception:
        return jsonify({"error": "Could not open output folder."}), 500


@app.route('/diagnostics')
def diagnostics():
    jobs = job_queue.list_all()
    by_status = {
        "queued": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
    }
    for job in jobs:
        status = job.get("status")
        if status == "completed":
            by_status["completed"] += 1
        elif status == "failed":
            by_status["failed"] += 1
        elif status == "queued":
            by_status["queued"] += 1
        else:
            by_status["running"] += 1

    latest_failures = []
    for job in jobs:
        if job.get("status") == "failed":
            latest_failures.append({
                "job_id": job.get("job_id"),
                "filename": job.get("filename"),
                "error": friendly_failure_message(job.get("error")),
                "elapsed": job.get("elapsed"),
            })
        if len(latest_failures) >= 5:
            break

    return jsonify({
        "ok": True,
        "counts": by_status,
        "total_jobs": len(jobs),
        "separator_backend": get_separator_backend(),
        "latest_failures": latest_failures,
        "launch_url": f"http://{SERVER_HOST}:{SERVER_PORT}",
        "data_root": DATA_ROOT,
    })


def run_server():
    host = SERVER_HOST
    requested = SERVER_PORT
    chosen = requested

    if not _is_port_available(host, requested):
        chosen = _find_available_port(host, requested + 1)
        print(f"Port {requested} is busy. Using {chosen} instead.")

    if chosen != requested:
        os.environ["CLEANVEDIO_PORT"] = str(chosen)
    app.run(host=host, port=chosen, debug=SERVER_DEBUG)


if __name__ == '__main__':
    missing_deps = _missing_dependencies()
    if missing_deps:
        print("Missing required dependencies: " + ", ".join(missing_deps))
        print("Install the missing tools, then restart the app.")
    run_server()
