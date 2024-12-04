from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, send_from_directory, url_for, \
    abort, session
from Security import check_password, add_user, is_user_pass_empty, users_pass, delete_user, edit_user
from pyzbar.pyzbar import decode
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import qrcode
import base64
import json
import cv2
import os

app = Flask(__name__)

app.secret_key = b'_3#y9L"O4Q8z\n\xec]78/'

app.static_folder = 'File/static'
app.template_folder = 'File/templates'

# Path to the JSON file
user_data_file = 'File/data/user_data.json'

# Load existing user data from JSON file
users = {}
if os.path.exists(user_data_file):
    try:
        with open(user_data_file, 'r') as file:
            users = json.load(file)
            # print(users)
    except json.JSONDecodeError:
        users = {}


def is_logged_in():
    return "user" in session


@app.route('/')
def home():
    global days_left
    if is_logged_in():
        session.pop('random_number', None)
        # Calculate next payment date based on registration date
        for username, user_info in users.items():
            last_pay = datetime.strptime(user_info['last_pay_date'], '%d-%m-%Y')
            next_pay_date = last_pay + timedelta(days=30)
            days_left = (next_pay_date - datetime.now()).days
            user_info['next_pay_date'] = next_pay_date.strftime('%d-%m-%Y')
            user_info['days_left'] = days_left
            # max_day = max(days_left, 0)
            # user_info['active'] = days_left > 0
            user_info['payment'] = days_left > 0
        # Always save to JSON file
        with open(user_data_file, 'w') as f:
            json.dump(users, f, indent=2)

        return render_template('Index.html', users=users)
    else:
        return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if is_user_pass_empty():
        if request.method == 'POST':
            # Fetching form data
            fullname = request.form.get('fullname')
            ph = request.form.get('ph')
            password = request.form.get('password')
            # us_password = request.form.get('us_password')

            if ph.startswith('0') and len(ph) > 1:
                phone = ph[1:]  # Return the number without the first character ('0')
            else:
                phone = ph

            # Get the first four characters of the username
            username_prefix = fullname[:5]
            # Get the last four digits of the phone number
            phone_suffix = phone[-4:]
            # Generate unique user ID
            user_id = str(username_prefix + "" + phone_suffix)

            add_user(user_id, fullname, password)

            # Redirect to a success page or perform other actions as needed
            return redirect(url_for('login'))

            # If it's a GET request, render the signup form
        return render_template('signup.html')
    else:
        if is_logged_in():
            session.pop('random_number', None)
            if request.method == 'POST':
                # Fetching form data
                fullname = request.form.get('fullname')
                ph = request.form.get('ph')
                password = request.form.get('password')
                # us_password = request.form.get('us_password')

                if ph.startswith('0') and len(ph) > 1:
                    phone = ph[1:]  # Return the number without the first character ('0')
                else:
                    phone = ph

                # Get the first four characters of the username
                username_prefix = fullname[:5]
                # Get the last four digits of the phone number
                phone_suffix = phone[-4:]
                # Generate unique user ID
                user_id = str(username_prefix + "" + phone_suffix)

                add_user(user_id, fullname, password)

                # Redirect to a success page or perform other actions as needed
                return redirect(url_for('login'))

            # If it's a GET request, render the signup form
            return render_template('signup.html')

        else:
            return redirect(url_for('login'))


@app.route('/generate_user_id', methods=['POST'])
def generate_user_id():
    fullname = request.form.get('fullname')
    ph = request.form.get('ph')

    if fullname and ph:
        if ph.startswith('0') and len(ph) > 1:
            phone = ph[1:]  # Return the number without the first character ('0')
        else:
            phone = ph

        # Get the first five characters of the fullname
        username_prefix = fullname[:5]
        # Get the last four digits of the phone number
        phone_suffix = phone[-4:]
        # Generate unique user ID
        user_id = str(username_prefix + phone_suffix)

        return jsonify({'user_id': user_id})

    return jsonify({'error': 'Invalid input'}), 400


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        session.pop('random_number', None)
        return redirect(url_for('home'))

    show_signup_link = is_user_pass_empty()
    next_url = request.args.get('next', '/')  # Set default value to home page
    # print("GET next_url:", next_url)  # Debugging line

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        next_url = request.form.get('next', '/')
        # print("POST next_url:", next_url)  # Debugging line

        if check_password(username, password):
            session["user"] = username
            flash('Logged in successfully', 'success')
            return redirect(next_url)
        else:
            return render_template("Login.html", error="Invalid username or password. Try Again!",
                                   show_signup_link=show_signup_link, next=next_url)

    return render_template("Login.html", show_signup_link=show_signup_link, next=next_url)


@app.route('/logout')
def logout():
    session.pop("user", None)
    # flash('Logged out successfully', 'success')
    return redirect("/")


@app.route('/users')
def user_management():
    if is_logged_in():
        if is_user_pass_empty():
            return redirect(url_for('logout'))
        else:
            session.pop('random_number', None)
            return render_template('usermanage.html', users=users_pass['users'])
    else:
        return redirect(url_for('login'))


@app.route('/edit_user', methods=['POST'])
def Edit_user():
    if is_logged_in():
        session.pop('random_number', None)
        user_id = request.form['id']
        username = request.form['username']
        password = request.form['password']
        edit_user(user_id, new_username=username, new_password=password)
        flash('Edit is successful', 'success')
        return redirect(url_for('user_management'))
    else:
        return redirect(url_for('login'))


@app.route('/delete_user', methods=['POST'])
def Delete_user():
    if is_logged_in():
        session.pop('random_number', None)
        user_id = request.form['id']
        password = request.form['password']
        user_to_delete = next(
            (user for user in users_pass['users'] if user['Id'] == user_id and user['password'] == password), None)
        if user_to_delete:
            delete_user(user_id)
            if is_user_pass_empty():
                pass
            else:
                flash('Delete is successful', 'error')
        else:
            flash('User ID or password is incorrect', 'error')

        return redirect(url_for('user_management'))
    else:
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        session.pop('random_number', None)
        if request.method == 'POST':
            username = request.form['username']
            ph = request.form['phone']
            email = request.form['email']
            pay = request.form['pay']

            if ph.startswith('0') and len(ph) > 1:
                phone = ph[1:]  # Return the number without the first character ('0')
            else:
                phone = ph

            # Extracting phone numbers from user dictionaries
            phone_numbers = [user['phone'] for user in users.values()]

            # Check if the phone number already exists in the list of phone numbers
            if phone in phone_numbers:
                flash("User with this phone number already exists!", 'error')
                return redirect(url_for('home'))
            else:
                # Get the first four characters of the username
                username_prefix = username[:5]
                # Get the last four digits of the phone number
                phone_suffix = phone[-5:]
                # Generate unique user ID
                user_id = str(username_prefix + "" + phone_suffix)

                if pay == 'paid':
                    payment_status = True
                else:
                    payment_status = False

                # next_pay = datetime.now() + timedelta(days=30)
                # Save user and generate QR code
                users[username] = {
                    'id': user_id,
                    'phone': phone,
                    'email': email,
                    'reg_date': datetime.now().strftime("%d-%m-%Y"),
                    'last_pay_date': datetime.now().strftime("%d-%m-%Y"),
                    # 'next_pay_date': next_pay,
                    'active': True,
                    'payment': payment_status,
                    'attendance': []
                }
                generate_qr(username, user_id)

                # Save to JSON file
                with open(user_data_file, 'w') as File:
                    json.dump(users, File, indent=2)

                flash(f'{username} registered successfully!', 'success')
                return redirect(url_for('home'))
        return render_template('Index.html')
    else:
        return redirect(url_for('login'))


def generate_qr(username, user_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(user_id)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save(f'File/static/qrcodes/{username}_Qr.png')


@app.route('/download_qr/<username>', methods=['GET'])
def download_qr(username):
    if is_logged_in():
        session.pop('random_number', None)
        qr_directory = os.path.abspath('File/static/qrcodes')
        qr_filename = f'{username}_Qr.png'
        if os.path.exists(os.path.join(qr_directory, qr_filename)):
            return send_from_directory(qr_directory, qr_filename, as_attachment=True)
        flash('QR code not found!', 'error')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/delete/<username>', methods=['GET'])
def delete(username):
    if is_logged_in():
        session.pop('random_number', None)
        if username in users:
            # Remove the user's QR code file if it exists
            qr_path = os.path.abspath(f'File/static/qrcodes/{username}_Qr.png')
            if os.path.exists(qr_path):
                os.remove(qr_path)

            # Remove the user from the dictionary
            del users[username]

            # Save the updated users dictionary to the JSON file
            with open(user_data_file, 'w') as files:
                json.dump(users, files, indent=2)

            flash(f'{username} is deleted!', 'error')
            return redirect(url_for('home'))
        flash('User not found!', 'error')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/activate/<username>', methods=['GET'])
def activate(username):
    if is_logged_in():
        session.pop('random_number', None)
        if username in users:
            if not users[username].get('payment', False):  # Check if payment is pending
                flash(f'{username} cannot be activated. Payment is pending.', 'error')
                return redirect(url_for('home'))

            users[username]['active'] = True

            # Save to JSON file
            with open(user_data_file, 'w') as Js_file:
                json.dump(users, Js_file, indent=2)

            flash(f'{username} is activated!', 'success')
            return redirect(url_for('home'))
        flash('User not found!', 'error')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/deactivate/<username>', methods=['GET'])
def deactivate(username):
    if is_logged_in():
        session.pop('random_number', None)
        if username in users:
            users[username]['active'] = False

            # Save to JSON file
            with open(user_data_file, 'w') as f:
                json.dump(users, f, indent=2)

            flash(f'{username} is deactivated!', 'error')
            return redirect(url_for('home'))
        flash('User not found!', 'error')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/paid/<username>', methods=['GET'])
def paid(username):
    if is_logged_in():
        session.pop('random_number', None)
        if username in users:
            users[username]['payment'] = True
            users[username]['last_pay_date'] = datetime.now().strftime("%d-%m-%Y")
            # Save to JSON file
            with open(user_data_file, 'w') as F:
                json.dump(users, F, indent=2)

            flash(f'{username} marked as paid!', 'success')
            return redirect(url_for('home'))
        flash('User not found!', 'error')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/unpaid/<username>', methods=['GET'])
def unpaid(username):
    if is_logged_in():
        session.pop('random_number', None)
        if username in users:
            users[username]['payment'] = False

            # Save to JSON file
            with open(user_data_file, 'w') as Files:
                json.dump(users, Files, indent=2)

            flash(f'{username} marked as unpaid!', 'error')
            return redirect(url_for('home'))
        flash('User not found!', 'error')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/download', methods=['GET'])
def download():
    # Convert users dictionary to a DataFrame
    data = []
    for username, details in users.items():
        for timestamp in details['attendance']:
            data.append({
                'User ID': details['id'],
                'User Name': username,
                'User Phone': details['phone'],
                'Date': timestamp.split(' ')[0],
                'Time': timestamp.split(' ')[1],
                'Payment': 'Paid' if details['payment'] else 'Unpaid',
                'Status': 'Active' if details['active'] else 'Inactive'
            })
    df = pd.DataFrame(data)

    # Save DataFrame to CSV
    csv_filename = 'export_data.csv'
    csv_file_path = os.path.join('File', 'database', 'all_user_file', csv_filename)
    df.to_csv(csv_file_path, index=False)

    # Get the absolute path of the CSV file
    csv_file_abs_path = os.path.abspath(csv_file_path)

    # Send the file as an attachment
    response = send_file(csv_file_abs_path, as_attachment=True)

    # Return the file as an attachment
    return response


@app.route('/download_user/<username>', methods=['GET'])
def download_user(username):
    if username not in users:
        abort(404, description="User not found")

    # Convert selected user's attendance details to DataFrame
    details = users[username]
    data = []
    for timestamp in details['attendance']:
        data.append({
            'User ID': details['id'],
            'User Name': username,
            'User Phone': details['phone'],
            'Date': timestamp.split(' ')[0],
            'Time': timestamp.split(' ')[1],
            'Payment': 'Paid' if details['payment'] else 'Unpaid',
            'Status': 'Active' if details['active'] else 'Inactive'
        })
    df = pd.DataFrame(data)

    csv_directory = 'File/database/user_csv_file'
    for All_file in os.listdir(csv_directory):
        file_path = os.path.join(csv_directory, All_file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted existing file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    # Save DataFrame to CSV
    csv_filename = f'{username}_data.csv'
    csv_file_path = os.path.join('File', 'database', 'user_csv_file', csv_filename)
    df.to_csv(csv_file_path, index=False)

    # Get the absolute path of the CSV file
    csv_file_abs_path = os.path.abspath(csv_file_path)

    # Send the file as an attachment
    response = send_file(csv_file_abs_path, as_attachment=True)

    # Delete the file after sending
    # os.remove(csv_file_abs_path)

    return response


@app.route('/scanqr', methods=['GET'])
def scanBtn():
    if is_logged_in():
        session.pop('random_number', None)
        return render_template('Scan_QR.html')
    else:
        return redirect(url_for('login', next=request.url))


def decode_barcode_from_image(image):
    barcodes = decode(image)
    for barcode in barcodes:
        data = barcode.data.decode('utf-8')
        if data:
            return data
    return None


@app.route('/scan', methods=['POST'])
def scan():
    try:
        user_found = False
        data_url = request.json.get('image')

        if data_url:
            # Convert data URL to OpenCV image
            header, encoded = data_url.split(",", 1)
            img_data = base64.b64decode(encoded)
            np_arr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if image is None:
                return jsonify({'status': 'error', 'message': 'Camera access issue. Unable to capture image.'})

            user_id = decode_barcode_from_image(image)
            if user_id:
                for username, data in users.items():
                    if data['id'] == user_id:
                        user_found = True

                        if not data['payment']:
                            return jsonify(
                                {'status': 'error', 'message': 'Payment due, you cannot access! Contact Now'})
                        if not data['active']:
                            return jsonify({'status': 'error',
                                            'message': 'Your ID is deactivated, you cannot access! Contact Now'})

                        timestamp = datetime.now().strftime('%d-%m-%Y %I:%M:%p')
                        users[username]['attendance'].append(timestamp)

                        # Save to JSON file
                        with open(user_data_file, 'w') as js_file:
                            json.dump(users, js_file, indent=2)

                        return jsonify({'status': 'success',
                                        'message': f'Dear {username}, checked into the GYM successfully at {timestamp}!'})

                if not user_found:
                    return jsonify({'status': 'error', 'message': 'Invalid QR, you cannot access!'})

            else:
                return jsonify({'status': 'error', 'message': 'No valid barcode detected in the image.'})

        else:
            return jsonify({'status': 'error', 'message': 'No image data received. Please try again.'})

    except Exception as e:
        # return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'})
        return jsonify({'status': 'error', 'message': 'Camera access issue. Unable to capture image.'})


if __name__ == '__main__':
    if not os.path.exists('File/static/qrcodes'):
        os.makedirs('File/static/qrcodes')
    app.run(host="0.0.0.0", debug=True)
