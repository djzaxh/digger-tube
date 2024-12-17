from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import json
import os

app = Flask(__name__)
app.secret_key = 'abc123'

# JSON file management
VIDEO_FILE = 'videos.json'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'm4v'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_mime_type(filename):
    extension = filename.rsplit('.', 1)[1].lower()
    mime_types = {
        'mp4': 'video/mp4',
        'mov': 'video/quicktime',
        'avi': 'video/x-msvideo',
        'm4v': 'video/x-m4v'
    }
    return mime_types.get(extension, 'video/m4v')

def load_videos():
    """Load videos from a JSON file."""
    if os.path.exists(VIDEO_FILE):
        with open(VIDEO_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_videos(videos):
    """Save the videos to the JSON file."""
    with open(VIDEO_FILE, 'w') as f:
        json.dump(videos, f)

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

@app.route("/")
def home():
    videos = load_videos()
    return render_template("index.html", videos=videos)

@app.route("/admin", methods=['GET', 'POST'])
def adminpanel():
    if not session.get('logged_in'):  # Check if user is logged in
        flash('You need to log in first', 'warning')
        return redirect(url_for('login'))

    # Load the videos from the JSON file
    videos = load_videos()

    # Ensure the route returns the admin template with videos
    return render_template("admin.html", videos=videos)

@app.route('/add-video', methods=['POST'])
def add_video():
    name = request.form.get('name')
    src = request.form.get('src')
    video_file = request.files.get('video_file')
    error_message = None

    # Initialize a variable to store the video source (either URL or file path)
    video_source = None
    mime_type = 'video/mp4'  # Default MIME type

    # Check if a URL is provided
    if src:
        video_source = src
        mime_type = 'video/mp4'  # Assume mp4 for URL; adjust as needed

    # Check if a file is uploaded and valid
    elif video_file and allowed_file(video_file.filename):
        filename = video_file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(file_path)
        # Use the 'uploaded_file' endpoint with the 'filename' argument
        video_source = url_for('uploaded_file', filename=filename)  # Get MIME type based on file extension

    # Ensure a valid video source was provided
    if not video_source:
        error_message = 'Please provide either a video URL or upload a valid video file.'
        return render_template('admin.html', error_message=error_message)

    # Load current videos, add the new video, and save back to JSON
    video_data = {
        'name': name,
        'src': video_source,
        'type': 'file' if video_file else 'url',
        'mime_type': mime_type
    }
    videos = load_videos()
    videos.append(video_data)
    save_videos(videos)

    return redirect(url_for('adminpanel'))




@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if credentials are correct
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True  # Set session flag
            return redirect(url_for('adminpanel'))
        else:
            flash('Invalid credentials. Please try again.', category='danger')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove session
    flash('You were successfully logged out', 'success')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
