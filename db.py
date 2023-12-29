import utils

def connect_to_database(name='database.db'):
	import sqlite3
	return sqlite3.connect(name, check_same_thread=False)

def init_db(connection):
	cursor = connection.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL
		)
	''')
     
	connection.commit()

def init_movie_table(connection):
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    connection.commit()

def movie_search(connection, movie_name):
    query = '''SELECT * FROM movies WHERE title = ?'''
    try:
        result = connection.execute(query,(movie_name,))
        movies_dicts = []
        for row in result.fetchall():
            columns = [column[0] for column in result.description]
            movies = dict(zip(columns, row))
            movies_dicts.append(movies)
        return movies_dicts
    except Exception as e:
        return e
   
        
        

def add_movie(connection, user_id, title, description, image_url=None):
    cursor = connection.cursor()
    query = '''INSERT INTO movies (user_id, title, description, image_url) VALUES (?, ?, ?, ?)'''
    cursor.execute(query, (user_id, title, description, image_url))
    connection.commit()

def add_user(connection, username, password):
    cursor = connection.cursor()
    hashed_password = utils.hash_password(password)
    query = '''INSERT INTO users (username, password) VALUES (?, ?)'''
    cursor.execute(query, (username, hashed_password))
    connection.commit()

def get_user(connection, username):
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE username = ?'''
    cursor.execute(query, (username,))
    return cursor.fetchone()

def get_movie(connection, movie_id):
    cursor = connection.cursor()
    query = '''SELECT * FROM movies WHERE id = ?'''
    cursor.execute(query, (movie_id,))
    return cursor.fetchone()

def get_all_movies(connection):
    cursor = connection.cursor()
    query = '''SELECT * FROM movies'''
    cursor.execute(query)
    return cursor.fetchall()

def get_all_users(connection):
	cursor = connection.cursor()
	query = 'SELECT * FROM users'
	cursor.execute(query)
	return cursor.fetchall()

def seed_admin_user1(connection):
    admin_username = 'admin'
    admin_pass = 'admin'
    admin_user = get_user(connection, admin_username)
    if not admin_user:
        add_user(connection, admin_username, admin_pass)
        print("Admin seeded successfully.")

def init_comments_table(connection):
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (movie_id) REFERENCES movies (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    connection.commit()

def add_comment(connection, movie_id, user_id, text):
    cursor = connection.cursor()
    query = '''INSERT INTO comments (movie_id, user_id, text) VALUES (?, ?, ?)'''
    cursor.execute(query, (movie_id, user_id, text))
    connection.commit()

def get_comments_for_movie(connection, movie_id):
    cursor = connection.cursor()
    query = '''
        SELECT  users.username, comments.text, comments.timestamp
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.movie_id = ?
    '''
    cursor.execute(query, (movie_id,))
    return cursor.fetchall()