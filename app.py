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

def stream_file(file_path):
    """Stream a file in chunks using range requests."""
    range_header = request.headers.get('Range')
    if not range_header:
        # If no range header, send the entire file
        return send_from_directory(MUSIC_DIR, os.path.basename(file_path))

    # Parse the range header
    size = os.path.getsize(file_path)
    start, end = 0, size - 1

    range_ = range_header.split('=')[1]
    if '-' in range_:
        start, end = range_.split('-')
        start = int(start)
        end = int(end) if end else size - 1

    # Ensure the range is valid
    if start >= size or end >= size or start > end:
        abort(416, description="Requested Range Not Satisfiable")

    # Calculate the chunk length
    chunk_length = end - start + 1

    # Open the file and seek to the start position
    with open(file_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(chunk_length)

    # Create a response with status code 206 (Partial Content)
    response = Response(
        chunk,
        206,  # Partial Content
        mimetype='audio/mpeg',  # Adjust based on file type
        content_type='audio/mpeg',  # Adjust based on file type
        direct_passthrough=True,
    )

    # Set headers for range support
    response.headers.add(
        'Content-Range',
        f'bytes {start}-{end}/{size}'
    )
    response.headers.add(
        'Accept-Ranges',
        'bytes'
    )
    response.headers.add(
        'Content-Length',
        str(chunk_length)
    )

    return response

@app.route('/stream/<filename>')
def stream(filename):
    """Stream a music file with range request support."""
    try:
        file_path = os.path.join(MUSIC_DIR, filename)
        if not os.path.exists(file_path):
            logger.error(f"File not found: {filename}")
            abort(404, description="File not found")

        logger.debug(f"Streaming file: {filename}")
        return stream_file(file_path)

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