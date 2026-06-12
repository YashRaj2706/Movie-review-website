from flask import Flask, render_template, request, redirect, url_for,flash,session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'your_secret_key'
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    reviews = db.relationship('Review',backref='movie')
    # backref creates a movie attribute on Review

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(128))
    confirm_password = db.Column(db.String(128))

posts = db.relationship('Post')

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
        if request.method == 'POST' :
            name=request.form.get('username')
            password=request.form.get('password')

            user = User.query.filter_by(user_name=name).first()

            if user and user.password == password:
                session['user_id'] = user.id
                session['name'] = user.user_name

                print('Successfully Login')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password')
                return render_template('login.html')
        
        return render_template('login.html')
        
@app.route('/register',methods=['GET','POST'])
def register():
        if request.method=='POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if confirm_password != password:
                flash("Password doesn't match")
                return render_template('register.html')

            new_user = User(user_name=username, email=email, password=password)
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
            except Exception:
                flash('User already exists')
                return render_template('register.html')
           
        return render_template('register.html')
    

    

@app.route('/index',methods=['GET'])
def index():
    search = request.args.get('search')
    if search:
        movies = Movie.query.filter(Movie.title.contains(search)).all()
        if not movies:
            flash('Movie not found!')
            
            #used flash to show a message when no movies are found
    else:
        movies = Movie.query.all()
        
    return render_template('index.html', movies=movies)

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        new_movie = Movie(title=request.form['title'], description=request.form['description'])
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_movie.html')

@app.route('/movie/<int:id>')
def view_movie(id):
    movie = Movie.query.get(id)
    return render_template('movie.html', movie=movie, reviews=movie.reviews)

@app.route('/movie/<int:movie_id>/add_review', methods=['POST'])
def add_review(movie_id):
    new_review = Review(
        rating=int(request.form['rating']),
        content=request.form['content'],
        movie_id=movie_id
    )
    db.session.add(new_review)
    db.session.commit()
    return redirect(url_for('view_movie', id=movie_id))

@app.route('/edit_review/<int:id>', methods=['GET', 'POST'])
def edit_review(id):
    review = Review.query.get(id)
    if request.method == 'POST':
        review.rating = int(request.form['rating'])
        review.content = request.form['content']
        db.session.commit()
        return redirect(url_for('view_movie', id=review.movie_id))
    return render_template('edit_review.html', review=review)

@app.route('/delete_review/<int:id>')
def delete_review(id):
    review = Review.query.get(id)
    m_id = review.movie_id
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for('view_movie', id=m_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
