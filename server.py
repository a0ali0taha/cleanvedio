from flask import Flask, render_template, request
import os
import requests
from main import start

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    youtube_url = request.form['youtube_url']
    output_folder = request.form['output_folder']
    is_playlist = 'playlist' in request.form
    upload_to_telegram = 'upload_to_telegram' in request.form
    start(youtube_url,is_playlist,output_folder,upload_to_telegram)
    # Process the inputs (e.g., download the video, extract audio, etc.)
    return f"URL: {youtube_url}<br>Folder: {output_folder}<br>Playlist: {is_playlist}<br>Upload: {upload_to_telegram}"
   
if __name__ == '__main__':
    app.run(debug=True)
