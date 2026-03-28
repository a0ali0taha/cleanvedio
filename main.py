from pipeline import Pipeline


def start(url, is_playlist=True, output_path='videos'):
    """Download from YouTube and process. Used by scripts and the web server."""
    pipe = Pipeline()
    pipe.process_youtube(url, output_path, is_playlist)


def handle(video):
    """Process a ``Video`` through the full pipeline. Used by ``batch.py``."""
    pipe = Pipeline()
    pipe.process(video)
