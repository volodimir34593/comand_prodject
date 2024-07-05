from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import os
import json
import uuid
import sqlite3
import base64
import io
from PIL import Image
import traceback
from flask import Flask, render_template, request, redirect, url_for
from models import get_db_connection, add_user, add_topic, add_post


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit, for example
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def connect_db():
    conn = sqlite3.connect('auction.db')
    conn.execute('PRAGMA busy_timeout = 30000')
    return conn

def get_all_topics():
    conn = get_db_connection()
    topics = conn.execute('''
        SELECT topics.*, users.username
        FROM topics
        JOIN users ON topics.user_id = users.username
        ORDER BY topics.date_posted DESC
    ''').fetchall()
    conn.close()
    return [dict(topic) for topic in topics]

def get_topic(topic_id):
    conn = get_db_connection()
    topic = conn.execute('''
        SELECT topics.*, users.username
        FROM topics
        JOIN users ON topics.user_id = users.username
        WHERE topics.id = ?
    ''', (topic_id,)).fetchone()
    conn.close()
    if topic:
        return dict(topic)  # Конвертуємо Row об'єкт в словник
    return None

def get_posts(topic_id):
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT posts.*, users.username
        FROM posts
        JOIN users ON posts.user_id = users.username
        WHERE posts.topic_id = ?
        ORDER BY posts.date_posted
    ''', (topic_id,)).fetchall()
    conn.close()
    return posts

def create_topic(title, content, user_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO lots (name, description, owner, created_at) VALUES (?, ?, ?, ?)',
                 (title, content, user_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def create_post(content, user_id, topic_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO posts (content, user_id, topic_id, date_posted)
    VALUES (?, ?, ?, ?)
    ''', (content, user_id, topic_id, datetime.utcnow()))
    conn.commit()
    conn.close()

def allowed_file(filename):
    print(f"Checking filename: {filename}")
    allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    print(f"Filename allowed: {allowed}")
    return allowed

def is_image_file(file_stream):
    print("Checking if file is an image")
    try:
        image = Image.open(file_stream)
        image.verify()
        file_stream.seek(0)  # Повернення до початку потоку після перевірки
        print("File is a valid image")
        return True
    except Exception as e:
        print(f"File is not a valid image: {e}")
        return False

def save_user_to_db(user):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (username, password, last_name, first_name, phone_number, email)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (user['username'], user['password'], user['last_name'], user['first_name'], user['phone_number'], user['email']))
    conn.commit()
    conn.close()

def update_user_in_db(user):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE users
    SET password = ?, last_name = ?, first_name = ?, phone_number = ?, email = ?, avatar = ?
    WHERE username = ?
    ''', (user['password'], user['last_name'], user['first_name'], user['phone_number'], user['email'], user.get('avatar'), user['username']))
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            'username': user[0],
            'password': user[1],
            'last_name': user[2],
            'first_name': user[3],
            'phone_number': user[4],
            'email': user[5],
            'avatar': user[6]
        }
    return None

def get_user_by_email(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            'username': user[0],
            'password': user[1],
            'last_name': user[2],
            'first_name': user[3],
            'phone_number': user[4],
            'email': user[5]
        }
    return None

def get_all_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT username, first_name, last_name, phone_number, email FROM users')
    users = cursor.fetchall()
    conn.close()
    return {user[0]: {'first_name': user[1], 'last_name': user[2], 'phone_number': user[3], 'email': user[4]} for user in users}

def get_lots_from_db():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lots')
        lots = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching lots: {e}")
        return []
    finally:
        conn.close()
    
    lots_list = []
    for lot in lots:
        image_urls = json.loads(lot[6]) if lot[6] else []
        
        lots_list.append({
            'id': lot[0],
            'name': lot[1],
            'description': lot[2],
            'start_price': lot[3],
            'created_at': lot[4],
            'owner': lot[5],
            'image_urls': image_urls,
            'user_ip': lot[7],
            'current_price': lot[8],
            'times': lot[9],
            'end_date': lot[10],
            'category_id' : lot[11]
        })
    
    return lots_list

def get_lot_by_id_from_db(lot_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lots WHERE id = ?', (str(lot_id),))
        lot = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error fetching lot by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

    if lot:
        # Парсимо JSON для обробки URL зображень
        image_urls = json.loads(lot[6]) if lot[6] else []
        lot_dict = {
            'id': lot[0],
            'name': lot[1],
            'description': lot[2],
            'start_price': lot[3],
            'created_at': lot[4],
            'owner': lot[5],
            'image_urls': image_urls,
            'user_ip': lot[7],
            'current_price': lot[8],
            'times': lot[9],  # Додавання тривалості до об'єкту лоту
            'end_date': lot[10],  # Додавання дати закінчення до об'єкту лоту
            'category_id': lot[11]
        }
        return lot_dict
    
    return None

def update_lot_in_db(lot_id, new_price=None, user_ip=None, lot=None):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Оновлення current_price, якщо задано new_price
        if new_price is not None:
            cursor.execute('UPDATE lots SET current_price = ? WHERE id = ?', (new_price, lot_id))
        
        # Оновлення user_ip, якщо задано user_ip
        if user_ip is not None:
            cursor.execute('UPDATE lots SET user_ip = ? WHERE id = ?', (user_ip, lot_id))
        
        # Оновлення інших полів лоту, якщо задано lot
        if lot is not None:
            image_urls_json = json.dumps(lot.get('image_urls', []))
            cursor.execute('''
                UPDATE lots
                SET name = ?,
                    description = ?,
                    start_price = ?,
                    current_price = ?,
                    image_urls = ?,
                    category_id = ?
                WHERE id = ?
            ''', (lot['name'], lot['description'], lot['start_price'], lot['current_price'], image_urls_json, lot['category_id'], lot_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")
        print(traceback.format_exc())
        conn.rollback()
        return False
    except Exception as e:
        print(f"Error updating lot: {e}")
        print(traceback.format_exc())
        conn.rollback()
        return False
    finally:
        conn.close()

def save_image_to_db(image_file):
    img = Image.open(image_file)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return base64.b64encode(img_byte_arr).decode('utf-8')

def calculate_end_date(created_at, days):
    created_at_datetime = datetime.fromisoformat(created_at)
    end_date = created_at_datetime + timedelta(days=days)
    return end_date.isoformat()

def save_lot_to_db(lot):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Check if lot with the same id already exists
        existing_lot = get_lot_by_id_from_db(lot['id'])
        if existing_lot:
            lot['id'] = str(uuid.uuid4())

        image_urls_json = json.dumps(lot['image_urls'])
        created_at = datetime.now()
        end_date = created_at + timedelta(days=lot['times'])

        cursor.execute('''
        INSERT INTO lots (id, name, description, start_price, created_at, owner, image_urls, current_price, user_ip, times, end_date, category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lot['id'], lot['name'], lot['description'], lot['start_price'], created_at.isoformat(), lot['owner'], image_urls_json, lot['current_price'], lot['user_ip'], lot['times'], end_date.isoformat(), lot['category_id']))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"IntegrityError: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Error saving lot: {e}")
    finally:
        conn.close()

@app.route('/')
def index():
    lots = get_lots_from_db()
    users = get_all_users()
    return render_template('index.html', lots=lots, users=users)

@app.route('/create_lot', methods=['GET', 'POST'])
def create_lot():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            lot_name = request.form['lot_name']
            lot_description = request.form['lot_description']
            lot_start_price = float(request.form['lot_start_price'])
            lot_images = request.files.getlist('lot_images[]')
            lot_images = lot_images[:-1]
            print(f"Number of uploaded files: {len(lot_images)}")
            user_ip = request.remote_addr
            times = int(request.form['lot_times'])
            category_id = request.form['category_id']

            print(f"Received data: {lot_name}, {lot_description}, {lot_start_price}, {times}, {category_id}")

            image_urls = []
            
            if not lot_images or len(lot_images) == 0 or lot_images[0].filename == '':
                print("No image file uploaded")
                return render_template('create_lot.html', error='Потрібно завантажити хоча б одне зображення')
            
            for lot_image in lot_images:
                print(f"Processing image: {lot_image.filename}")
                if lot_image and allowed_file(lot_image.filename) and is_image_file(lot_image.stream):
                    image_data = save_image_to_db(lot_image)
                    image_urls.append(f"data:image/png;base64,{image_data}")
                else:
                    print(f"Invalid image file: {lot_image} {lot_image.filename}")
                    return render_template('create_lot.html', error=f'Неприпустимий файл зображення: {lot_image.filename}')

            created_at = datetime.now().isoformat()
            end_date = calculate_end_date(created_at, times)

            new_lot = {
                'id': str(uuid.uuid4()),
                'name': lot_name,
                'description': lot_description,
                'start_price': lot_start_price,
                'created_at': created_at,
                'owner': session['username'],
                'image_urls': image_urls,
                'current_price': lot_start_price,
                'user_ip': user_ip,
                'times': times,
                'end_date': end_date,
                'category_id': category_id
            }
            print(f"New lot data: {new_lot}")
            save_lot_to_db(new_lot)
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error creating lot: {str(e)}")
            return render_template('create_lot.html', error=f'Error creating lot: {str(e)}')

    return render_template('create_lot.html')

@app.route('/edit_lot/<string:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    lot = get_lot_by_id_from_db(lot_id)
    if not lot:
        flash('Лот не знайдено', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        lot_name = request.form['lot_name']
        lot_description = request.form['lot_description']
        new_start_price = float(request.form['lot_start_price'])
        lot_images = request.files.getlist('lot_images[]')
        category_id = request.form['category_id']

        # Перевірка, чи можна змінити стартову ціну
        if lot['current_price'] != lot['start_price']:
            flash('Неможливо змінити стартову ціну, оскільки на лот вже були ставки.', 'error')
            return render_template('edit_lot.html', lot=lot)

        image_urls = lot['image_urls']
        new_images_uploaded = False

        for lot_image in lot_images:
            if lot_image and lot_image.filename != '':
                if allowed_file(lot_image.filename) and is_image_file(lot_image.stream):
                    image_data = save_image_to_db(lot_image)
                    image_urls.append(f"data:image/png;base64,{image_data}")
                    new_images_uploaded = True
                else:
                    flash('Невірний формат файлу. Будь ласка, завантажте зображення.', 'error')
                    return render_template('edit_lot.html', lot=lot)

        if not image_urls and not new_images_uploaded:
            flash('Будь ласка, завантажте принаймні одне зображення.', 'error')
            return render_template('edit_lot.html', lot=lot)

        updated_lot = {
            'id': lot_id,
            'name': lot_name,
            'description': lot_description,
            'start_price': new_start_price,
            'image_urls': image_urls,
            'current_price': new_start_price,  # Оновлюємо і поточну ціну, якщо стартова була змінена
            'user_ip': lot['user_ip'],
            'category_id': category_id
        }

        try:
            if update_lot_in_db(lot_id, lot=updated_lot):
                flash('Лот успішно оновлено', 'success')
                return redirect(url_for('item_page', item_id=lot_id))
            else:
                flash('Не вдалося оновити лот.', 'error')
                return render_template('edit_lot.html', lot=lot)
        except Exception as e:
            flash(f'Помилка при оновленні лота: {str(e)}', 'error')
            return render_template('edit_lot.html', lot=lot)

    return render_template('edit_lot.html', lot=lot)

@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Видаляємо всі лоти користувача
        cursor.execute("DELETE FROM lots WHERE owner = ?", (username,))
        # Видаляємо користувача
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"Помилка при видаленні акаунта: {e}", "error")
    finally:
        conn.close()
    
    session.clear()
    flash("Ваш акаунт та всі ваші лоти було успішно видалено.", "success")
    return redirect(url_for("index"))

@app.route('/item/<uuid:item_id>')
def item_page(item_id):
    lot = get_lot_by_id_from_db(item_id)
    if lot:
        users = get_all_users()  # Fetch all users
        return render_template('lots.html', lots=[lot], users=users)
    else:
        return "Товар не знайдено", 404

@app.route('/search')
def search():
    query = request.args.get('query', '')
    category_id = request.args.get('category_id', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    lots = get_lots_from_db()
    
    filtered_lots = [lot for lot in lots if 
                     (query.lower() in lot['name'].lower() or query.lower() in lot['description'].lower()) and
                     (not category_id or lot['category_id'] == category_id) and
                     (min_price is None or lot['current_price'] >= min_price) and
                     (max_price is None or lot['current_price'] <= max_price)]
    
    return render_template('search_results.html', 
                           lots=filtered_lots, 
                           query=query, 
                           category=category_id, 
                           min_price=min_price, 
                           max_price=max_price)

@app.route('/place_bid', methods=['POST'])
def place_bid():
    try:
        print("Received POST request to /place_bid")
        
        # Спроба отримати необхідні дані з форми
        item_id = request.form.get('item_id')
        bid_amount = request.form.get('bid_amount')
        end_time = request.form.get('end_time')  # Переконайтеся, що 'end_time' включено в форму

        print(f"Received data - item_id: {item_id}, bid_amount: {bid_amount}, end_time: {end_time}")

        if not item_id or not bid_amount or not end_time:
            print("Missing required form data")
            return jsonify({'success': False, 'error': 'Сталася помилка при відправці ставки. Не вистачає необхідних даних'}), 400

        bid_amount = float(bid_amount)
        
        username = session.get('username')
        
        if not username:
            return jsonify({'success': False, 'error': 'Ви повинні увійти, щоб ставити ставки.'}), 403

        # Отримання лоту з бази даних
        lot = get_lot_by_id_from_db(item_id)

        if not lot:
            return jsonify({'success': False, 'error': 'Лот не знайдено.'}), 404

        # Перевірка на завершення таймера
        if datetime.now() >= datetime.fromisoformat(lot['end_date']):
            return jsonify({'success': False, 'error': 'Час для ставок на цей лот завершився.'}), 400

        if bid_amount <= lot['current_price']:
            return jsonify({'success': False, 'error': 'Ставка повинна бути вищою за поточну ціну.'}), 400

        # Оновлення лоту з новою ставкою
        if update_lot_in_db(item_id, bid_amount, request.remote_addr):
            #return jsonify({'success': True, 'bid_amount': bid_amount, 'lot_id': item_id}), 200
            return redirect(url_for(item_page.__name__, item_id=item_id))
        else:
            return jsonify({'success': False, 'error': 'Не вдалося оновити лот.'}), 500
    except KeyError as e:
        print(f"Missing form data: {e}")
        return jsonify({'success': False, 'error': 'Сталася помилка при відправці ставки. Не вистачає необхідних даних'}), 400
    except ValueError as e:
        print(f"Invalid data: {e}")
        return jsonify({'success': False, 'error': 'Сталася помилка при відправці ставки. Неправильні дані'}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'success': False, 'error': 'Сталася помилка при відправці ставки. Внутрішня помилка сервера'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)
        if user and user['password'] == password:
            session['logged_in'] = True
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неправильний email або пароль')
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = get_user_by_username(username)
    return render_template('profile.html', user=user)

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user = get_user_by_username(username)

    if request.method == "POST":
        user["first_name"] = request.form["first_name"]
        user["last_name"] = request.form["last_name"]
        user["phone_number"] = request.form["phone_number"]
        user["email"] = request.form["email"]

        # Обробка завантаження аватарки
        if "avatar" in request.files:
            avatar_file = request.files["avatar"]
            if avatar_file.filename != "":
                if allowed_file(avatar_file.filename):
                    # Зберігаємо аватар як base64-encoded рядок
                    avatar_data = save_image_to_db(avatar_file)
                    user["avatar"] = avatar_data
                else:
                    return render_template("edit_profile.html", user=user, error="Недопустимий формат файлу")

        update_user_in_db(user)
        return redirect(url_for("profile"))

    # Завантаження аватара з бази даних
    if user.get("avatar"):
        user["avatar_url"] = f"data:image/png;base64,{user['avatar']}"
    else:
        user["avatar_url"] = url_for('static', filename='default_avatar.png')  # Шлях до стандартного аватара

    return render_template("edit_profile.html", user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['email']  # Використовуємо email як ім'я користувача
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        phone_number = request.form['phone_number']
        email = request.form['email']

        error = None  # Початкове значення помилки

        if password != password_confirm:
            error = 'Паролі не співпадають'

        elif get_user_by_email(email):
            error = 'Цей email вже зареєстрований'

        if error:  # Якщо є помилка, поверніть сторінку реєстрації з помилкою
            return render_template('register.html', error=error)

        full_phone_number = f'{phone_number}'

        new_user = {
            'username': username,
            'password': password,
            'last_name': last_name,
            'first_name': first_name,
            'phone_number': full_phone_number,
            'email': email
        }
        save_user_to_db(new_user)
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/delete_lot/<item_id>', methods=['POST'])
def delete_lot(item_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    lot = get_lot_by_id_from_db(item_id)
    if lot and lot['owner'] == session['username']:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM lots WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route("/user_lots")
def user_lots():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    user_lots = [lot for lot in get_lots_from_db() if lot["owner"] == username]
    return render_template("user_lots.html", lots=user_lots, users=get_all_users())

@app.route('/delete_images/<lot_id>', methods=['POST'])
def delete_images(lot_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    lot = get_lot_by_id_from_db(lot_id)
    if lot and lot['owner'] == session['username']:
        # Obtain the list of image URLs from the lot
        image_urls = lot['image_urls']

        # Delete physical image files on the server (if necessary)
        for url in image_urls:
            # Assuming the image path looks like '/static/uploads/'
            image_path = os.path.join('static', url.lstrip('/'))
            if os.path.exists(image_path):
                os.remove(image_path)

        # Clear image URLs in the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE lots SET image_urls = ? WHERE id = ?', (json.dumps([]), lot_id))
        conn.commit()
        conn.close()

    # Redirect to the edit_lot page with the correct lot_id parameter
    return redirect(url_for('edit_lot', lot_id=lot_id))

@app.route('/delete_image', methods=['POST'])
def delete_image():
    try:
        data = request.json
        lot_id = data['lot_id']
        image_url = data['image_url']
        
        # Retrieve lot from the database
        lot = get_lot_by_id_from_db(lot_id)
        if not lot:
            return jsonify({'success': False, 'error': 'Lot not found'}), 404
        
        # Remove the image from the list of image_urls
        if image_url in lot['image_urls']:
            lot['image_urls'].remove(image_url)
            # Update the lot in the database
            if update_lot_in_db(lot_id, lot=lot):
                return jsonify({'success': True}), 200
            else:
                return jsonify({'success': False, 'error': 'Failed to update lot'}), 500
        else:
            return jsonify({'success': False, 'error': 'Image URL not found in lot'}), 400
    
    except Exception as e:
        print(f"Error deleting image: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/forum')
def forum():
    topics = get_all_topics()
    return render_template('forum.html', topics=topics)

@app.route('/topic/<int:topic_id>')
def topic(topic_id):
    topic = get_topic(topic_id)
    if topic is None:
        return render_template('topic.html', topic=None)
    posts = get_posts(topic_id)
    return render_template('topic.html', topic=topic, posts=posts)

@app.route('/create_topic', methods=['GET', 'POST'])
def create_topic():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('username')
        if user_id:
            topic_id = add_topic(title, content, user_id)
            return redirect(url_for('topic', topic_id=topic_id))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('create_topic.html')

@app.route('/create_post/<int:topic_id>', methods=['POST'])
def create_post_route(topic_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    create_post(content, session['username'], topic_id)
    return redirect(url_for('topic', topic_id=topic_id))


if __name__ == '__main__':
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            email TEXT NOT NULL,
            avatar TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS lots (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            start_price REAL NOT NULL,
            created_at TEXT NOT NULL,
            owner TEXT NOT NULL,
            image_urls TEXT,
            current_price REAL NOT NULL,
            user_ip TEXT
        )
        ''')
        conn.commit()
    app.run(debug=True)
