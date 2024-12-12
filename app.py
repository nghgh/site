import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_url_path='')
app.secret_key = os.urandom(24)  # MUST BE STRONGER FOR PRODUCTION
app.config['UPLOAD_FOLDER'] = 'uploads'  # Create this folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024  # 16 MB limit


#
users = {}
user_uploads = {}

@app.route("/")
def index():
    if 'user' in session:
        return render_template("index.html", username=session['user'])
    return render_template("index.html")


@app.route("/авторизация", methods=['GET', 'POST'])
def авторизация():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username]['password'], password):
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template("about.html", error="Неверный логин или пароль")
    return render_template("about.html")


@app.route("/регистрация", methods=['GET', 'POST'])
def регистрация():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return render_template("registration.html", error="Пользователь уже существует")
        hashed_password = generate_password_hash(password)
        users[username] = {'password': hashed_password}
        return redirect(url_for('авторизация'))
    return render_template("registration.html")


@app.route("/профиль")
def профиль():
    if 'user' in session:
        username = session['user']
        user_images = user_uploads.get(username, []) # Get user's images
        return render_template("user.html", username=username, user_images=user_images)
    return redirect(url_for('авторизация'))





@app.route("/работы")
def работы():
    if 'user' not in session:
        return redirect(url_for('авторизация'))
    # Show all images for simplicity (Replace with user-specific logic in production)
    uploaded_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return render_template("works.html", uploaded_files=uploaded_files)



@app.route("/выход")
def выход():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route("/загрузка", methods=['GET', 'POST'])
def загрузка():
    if 'user' not in session:
        return redirect(url_for('авторизация'))
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template("upload.html", error="Файл не выбран")
        file = request.files['file']
        if file.filename == '':
            return render_template("upload.html", error="Файл не выбран")
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            username = session['user']
            if username not in user_uploads:
                user_uploads[username] = []
            user_uploads[username].append(filename)  # Associate file with user
            return redirect(url_for('index'))
    return render_template("upload.html")


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
