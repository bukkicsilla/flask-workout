from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

class Exercise(db.Model):
    __tablename__ = "exercises"

    name = db.Column(db.String(50), primary_key=True, nullable=False,  unique=True)
    exercise_type = db.Column(db.Text, nullable=True)
    muscle = db.Column(db.String(20), nullable=False, default="abdominals")
    equipment = db.Column(db.Text, nullable=False, default="body_only")
    difficulty = db.Column(db.Text, nullable=False, default="beginner")
    instructions = db.Column(db.Text, nullable=True)

    videos = db.relationship("Video", backref="exercise", cascade="all,delete")

    def serialize(self):
        """Returns a dict representation of exercise which we can turn into JSON"""
        return {
            'name': self.name,
            'exercise_type': self.exercise_type,
            'muscle': self.muscle,
            'equipment': self.equipment,
            'difficulty': self.difficulty,
            'instructions': self.instructions
        }
    
    def __repr__(self):
        return f"<Exercise name={self.name} exercise_type={self.exercise_type} muscle={self.muscle} equipment={self.equipment} difficulty={self.difficulty}>"


class Video(db.Model):
    __tablename__ = "videos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    videoid = db.Column(db.String(20), nullable=False, default="onLTHQ1KE50")
    title = db.Column(db.Text, nullable=False, default="YouTube video")
    rating = db.Column(db.Float, db.CheckConstraint('rating >= 1.0 AND rating <= 10.0'), nullable=False, default=5.0)
    exercise_name = db.Column(db.String(50), db.ForeignKey('exercises.name'), nullable=False)
    
    '''user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )'''

    def serialize(self):
        """Returns a dict representation of video which we can turn into JSON"""
        return {
            'videoid': self.videoid,
            'title': self.title,
            'rating': self.rating,
            'exercise_name': self.exercise_name
        }

    def __repr__(self):
        return f"<Video videoid={self.videoid} title={self.title} rating={self.rating} exercise_name={self.exercise_name}>"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    videos = db.relationship('Video', secondary='users_videos', backref='users')
    #ratings = db.relationship('UserVideo', backref='user')

    def serialize(self):
        """Returns a dict representation of user which we can turn into JSON"""
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
        
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register user with username, hashed password, email, first_name, last_name and return user."""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
    
    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists and password is correct.
        Return user if valid, else return False.
        """
        user = User.query.filter_by(username=username).first()
        #print("Authenticate user", user)
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
    
class UserVideo(db.Model):
    __tablename__ = "users_videos"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), primary_key=True)
    rating = db.Column(db.Integer, db.CheckConstraint('rating >= 1 AND rating <= 10'), nullable=False, default=5)

class Playlist(db.Model):
    __tablename__ = "playlists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    videos = db.relationship('Video', secondary='playlists_videos', backref='playlists') 

class PlaylistVideo(db.Model):
    __tablename__ = "playlists_videos"

    playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.id"), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), primary_key=True)