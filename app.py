from flask import Flask, render_template, request, send_file, redirect, url_for, session
from stegano import lsb
from encryption import encrypt_data, decrypt_data
from database import init_db, get_user, add_user
from auth import hash_password, verify_password
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

init_db()

def embed_message(input_image_path, text, password):
    output_image_path = os.path.join(app.config['DOWNLOAD_FOLDER'], 'embedded_image.png')
    encrypted_text = encrypt_data(text, password)
    print(f"Embedding encrypted text: {encrypted_text}")
    secret_message = lsb.hide(input_image_path, encrypted_text)
    secret_message.save(output_image_path)
    return output_image_path

def extract_message(image_path, password):
    try:
        encrypted_message = lsb.reveal(image_path)
        if not encrypted_message:
            return ""
        print(f"Extracted encrypted message: {encrypted_message}")
        decrypted_message = decrypt_data(encrypted_message, password)
        return decrypted_message
    except (IndexError, ValueError) as e:
        print(f"Extraction error: {str(e)}")
        return ""

def is_logged_in():
    return 'user' in session

@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt - Username: {username}, Password: {password}")
        user = get_user(username)
        if user and verify_password(user[2], password):
            session['user'] = username
            print("Login successful")
            return redirect(url_for('index'))
        else:
            print("Invalid credentials")
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Register attempt - Username: {username}, Password: {password}")
        if get_user(username):
            print("Username already exists")
            return render_template('register.html', error="Username already exists")
        try:
            hashed_password = hash_password(password)
            add_user(username, hashed_password)
            print("Registration successful")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return render_template('register.html', error=str(e))
    return render_template('register.html')

@app.route('/embed', methods=['GET', 'POST'])
def embed():
    if not is_logged_in():
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('embed.html')

    if request.method == 'POST':
        uploaded_file = request.files.get('image_file')
        text = request.form.get('secret_message')
        password = request.form.get('password')

        if not uploaded_file or not text or not password:
            return render_template('embed.html', error="Image, secret message, and password are required")

        filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(filename)
        print(f"Saved image to: {filename}")

        try:
            embedded_image = embed_message(filename, text, password)
            print(f"Embedded image saved at: {embedded_image}")
            return send_file(embedded_image, as_attachment=True)
        except Exception as e:
            print(f"Embedding error: {str(e)}")
            return render_template('embed.html', error="Error embedding message")

@app.route('/extract', methods=['GET', 'POST'])
def extract():
    if not is_logged_in():
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('extract.html')

    if request.method == 'POST':
        uploaded_file = request.files.get('image_file')
        password = request.form.get('password')

        if not uploaded_file or not password:
            return render_template('extract.html', error="Image and password are required")

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(image_path)
        print(f"Saved stego image to: {image_path}")

        extracted_message = extract_message(image_path, password)
        if not extracted_message or not extracted_message.isprintable():
            return render_template('extract.html', error="No valid message found or incorrect password")
        
        return render_template('extract.html', extracted_message=extracted_message)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)