from flask import Flask, send_from_directory, jsonify, request, abort, Response
from flask_cors import CORS
import os
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow CORS for all routes

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Path to the music directory
MUSIC_DIR = os.path.join(os.getcwd(), 'music')

# Ensure the music directory exists
if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)
    logger.warning(f"Created music directory at {MUSIC_DIR}")

@app.route('/')
def home():
    """Home route to check if the server is running."""
    return jsonify({"message": "Music streaming server is running!"})

@app.route('/stream/<filename>')
def stream(filename):
    try:
        file_path = os.path.join(MUSIC_DIR, filename)
        if not os.path.exists(file_path):
            logger.error(f"File not found: {filename}")
            abort(404, description="File not found")

        logger.debug(f"Streaming file: {filename}")
        return stream_file(file_path)  # Use the range request handler
    except Exception as e:
        logger.error(f"Error streaming file: {e}")
        abort(500, description="Internal server error")

@app.route('/search')
def search():
    """Search for songs matching the query."""
    query = request.args.get('q', '').lower()
    logger.debug(f"Search query: {query}")
    
    try:
        songs = [f for f in os.listdir(MUSIC_DIR) if query in f.lower()]
        logger.debug(f"Found {len(songs)} songs matching the query")
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error during search: {e}")
        abort(500, description="Internal server error")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Allow access from other devices