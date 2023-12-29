from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import validators

app = Flask(__name__)
connection = db.connect_to_database()
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"])
app.secret_key = "LAIHSG*^&*%&*^$&*6DOUgihasgdoihAIUDS&*^(A*&S^D(&*^A&(*D^oye091yoigsad)))"

@app.route('/')
def index():
    if 'username' in session:
        if session['username'] == 'admin':
            return redirect(url_for('uploadMovies'))
        else:
            return render_template("index.html",movies=db.get_all_movies(connection))
    return "You are not logged in."

@app.route('/home')
def search_movie():
    movie_name = request.args.get('movie_name')
    movies = db.movie_search(connection,movie_name=movie_name)
    return render_template('search_result.html', movies=movies, movie_name=movie_name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not utils.is_strong_password(password):
            flash("Enter a stronger password", "danger")
            return render_template('register.html')
        user = db.get_user(connection, username)
        if user:
            flash("Username Exists Choose a new one", "danger")
            return render_template('register.html')
        else:
            db.add_user(connection, username, password)
            flash("Account created successfully","success")
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.get_user(connection, username)
        if user:
            if utils.is_password_match(password, user[2]):
                session['username'] = user[1]
                session['id'] = user[0]
                return redirect(url_for('index'))
            else:
                flash("Invalid credentials", "danger")
                return render_template('login.html')
        else:
            flash("Invalid credentials", "danger")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/upload-movie', methods=['GET', 'POST'])
@limiter.limit("5 per minute") 
def uploadMovies():
     if not 'username' in session:
        flash("Login in first,Please","danger")
        return redirect(url_for('login'))
     if 'username' in session:
      if session['username'] !='admin':
        flash("You dont have access!","danger")
        return redirect(url_for('login'))
     if request.method=='POST':
       MovieImage = request.files['image']
       if not MovieImage or MovieImage.filename == '':
            flash("Insert image please", "danger")
            return render_template("upload-movies.html")
       
       if not validators.allowed_file(MovieImage.filename) or not validators.allowed_file_size(MovieImage):
            flash("Invalid File Uploaded", "danger")
            return render_template("upload-movies.html")
       flash("Movie added successfully",'success')
       title = request.form['title']
       description = request.form['description']
       MovieImage=request.files['image']
       image_url= f"uploads/{MovieImage.filename}"
       MovieImage.save("static/"+image_url)
       user_id=session['id']
       db.add_movie(connection,user_id,title,description,image_url)
       return redirect(url_for('index'))
     return render_template('upload-movies.html') 

@app.route('/movie/<movie_id>')
def getMovie(movie_id):
	movie = db.get_movie(connection, movie_id)
	comments = db.get_comments_for_movie(connection, movie[0])

	return render_template("movie.html", movie=movie, comments=comments)

@app.route('/movie')
def getMovies():
 return render_template("index.html",movies=db.get_all_movies(connection))


@app.route('/add-comment/<movie_id>', methods=['POST'])
def addComment(movie_id):
	text = request.form['comment']
	user_id = session['id']
	db.add_comment(connection, movie_id, user_id, text)
	return redirect(url_for("getMovie", movie_id=movie_id))

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))

if __name__ == '__main__':
    db.init_db(connection)
    db.seed_admin_user1(connection)
    db.init_movie_table(connection)
    db.init_comments_table(connection)
    app.run(debug=True)