from flask import Flask, render_template, jsonify, request, flash, redirect, session, url_for
from models import db, connect_db, Exercise, Video, User, UserVideo, Playlist, PlaylistVideo
from forms import RegisterForm, LoginForm, PlaylistForm, RequestResetForm, ResetPasswordForm
from sqlalchemy.exc import IntegrityError
from constants import BASE_URL_WORKOUT, SECRET_KEY
import app_json
import requests
import flask_cors
import re
import os
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

app = Flask(__name__)

#API endpoints for React
app.add_url_rule('/api/fitness/exercises/<muscle>', view_func=app_json.api_exercise_by_muscle)
app.add_url_rule('/api/fitness/allexercises', view_func=app_json.show_all_exercises)
app.add_url_rule('/api/fitness/videos', view_func=app_json.show_videos)

flask_cors.CORS(app, resources={r"/api/*": {"origins": "*"}})
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///workout_flask"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.jljzqisclorjmtmwcnog:FlaskW0rk0ut42.@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 10
app.config["SECRET_KEY"] = SECRET_KEY

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
#app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
app.config['MAIL_USERNAME'] = 'csilla.bukki@gmail.com'
app.config['MAIL_PASSWORD'] = 'ohgy ibdq hktx tlsj'
mail = Mail(app)

connect_db(app)
MUSCLES = ['abdominals', 'abductors', 'adductors', 'biceps', 'calves', 'chest', 'forearms', 'glutes', 'hamstrings', 'lats', 'lower_back', 'middle_back', 'neck', 'quadriceps', 'traps', 'triceps']
#@app.route('/api/fitness/exercises/<muscle>', methods=['GET'])
#def api_exercise_by_muscle(muscle):
#    res_exercises = requests.get(f"{BASE_URL_WORKOUT}/exercises?muscle={muscle}").json()
#    return jsonify(res_exercises['exercises'])

def transform_word(word):
    # Case 1: Capitalize a single word (e.g., "abdominals" -> "Abdominals")
    if '_' not in word:
        return word.capitalize()
    
    # Case 2: Replace underscore with space and capitalize each word (e.g., "lower_back" -> "Lower Back")
    else:
        # Split by underscore, capitalize each part, and join them with a space
        return ' '.join([w.capitalize() for w in word.split('_')])

def not_authorized():
    '''User is not authorized to view the page.'''
    if "user_id" not in session:
        flash("Please login first!", "msguser")
        return True
    return False

@app.route('/')
def index():
    '''User can search exercises by muscle group.'''
    muscle = request.args.get('muscle')
    res_exercises = requests.get(f"{BASE_URL_WORKOUT}/exercises?muscle={muscle}").json()
    return render_template('index.html', exercises=res_exercises['exercises'])


@app.route('/exercises')
def get_exercises():
    '''Get the 156 exercises from the workout API and add them to the database. For only development purposes.'''
    res = requests.get(f"{BASE_URL_WORKOUT}/exercises/all").json()
    exercises = res['exercises']
    '''for j in range(len(exercises)):
            new_exercise = Exercise(name=exercises[j]['name'], 
                                    exercise_type=exercises[j]['exercise_type'], 
                                    muscle=exercises[j]['muscle'], 
                                    equipment=exercises[j]['equipment'], 
                                    difficulty=exercises[j]['difficulty'],
                                    instructions=exercises[j]['instructions'])
            db.session.add(new_exercise)
            db.session.commit()'''
    return jsonify(res['exercises'])


@app.route('/videos')
def get_videos():
    '''Get YoutTube videos with a specific exercise name from the workout API.'''
    if not_authorized():
        return redirect('/auth')
    name = request.args.get('name')
    res_videos = requests.get(f"{BASE_URL_WORKOUT}/videos?name={name}").json()
    #res = requests.get(f"{BASE_URL_WORKOUT}/videos").json()
    #return jsonify(res['videos'])
    return render_template('videos.html', name=name, videos=res_videos['videos']) 


'''@app.route('/my_videos')
def get_my_videos():
    exercises = Exercise.query.all()
    my_exercises = []
    for exercise in exercises:
        if len(exercise.videos):
            my_exercises.append(exercise)
    flash('You can scroll left and right.', 'msguser')
    print("exercises in my_videos", my_exercises)
    return render_template('myvideos.html', exercises=my_exercises)'''


'''@app.route('/my_videos')
def get_my_videos():
    if not_authorized():
        return redirect('/auth')
    exercises = Exercise.query.all()
    muscle_groups = {}

    # Group exercises by muscle
    for exercise in exercises:
        if len(exercise.videos):
            transformed_muscle = transform_word(exercise.muscle)
            if transformed_muscle not in muscle_groups:
                muscle_groups[transformed_muscle] = []
            muscle_groups[transformed_muscle].append(exercise)
    #print("Grouped exercises by muscle:", muscle_groups)
    return render_template('myvideos3.html', muscle_groups=muscle_groups)'''

#change this to /auth/my_videos
@app.route("/auth/my_videos", methods=["GET"])
def loading():
    '''Show looading message while the videos are being loaded.'''
    if not_authorized():
        return redirect('/auth')
    return render_template("loading.html")

#change this to /auth/my_videos_done 
@app.route('/auth/my_videos_loaded')
def auth_get_my_videos():
    '''Show added videos grouped by muscle groups.'''
    if not_authorized():
        return redirect('/auth')
    
    uservideos = UserVideo.query.filter(UserVideo.user_id==session['user_id']).all()
    uv_ids = [uservideo.video_id for uservideo in uservideos]
    s1 = set(uv_ids)
    exercises = Exercise.query.all()
    muscle_groups = {}

    # Group exercises by muscle
    for exercise in exercises:
        video_ids = [video.id for video in exercise.videos]
        s2 = set(video_ids)
        if len(exercise.videos) and (s1 & s2):
            transformed_muscle = transform_word(exercise.muscle)
            if transformed_muscle not in muscle_groups:
                muscle_groups[transformed_muscle] = []
            muscle_groups[transformed_muscle].append(exercise)
    
    #flash('You can scroll left and right.', 'msguser')
    #print("Grouped exercises by muscle:", muscle_groups)
    return render_template('myvideos5.html', muscle_groups=muscle_groups, ids=uv_ids)


@app.route('/videos/add/<name>/<videoid>')
def save_video(name, videoid):
    '''Save a video to the database without authentication.'''
    local_video = Video.query.filter(Video.videoid==videoid, Video.exercise_name == name).first()
    if not local_video:
        videos = requests.get(f"{BASE_URL_WORKOUT}/videos/videoid?videoid={videoid}").json()
        video = videos['videos'][0]
        new_video = Video(videoid=video['videoid'], 
                      title=video['title'], 
                      rating=video['rating'],
                      exercise_name=video['exercise_name'])
        db.session.add(new_video)
        db.session.commit()
        return redirect('/my_videos')
    flash('Video already added', 'msguser')
    return redirect("/")

@app.route('/auth/videos/add/<name>/<videoid>')
def auth_save_video(name, videoid):
    '''Save a video to the database with authentication.'''
    local_video = Video.query.filter(Video.videoid==videoid, Video.exercise_name == name).first()
    if not local_video:
        videos = requests.get(f"{BASE_URL_WORKOUT}/videos/videoid?videoid={videoid}").json()
        video = videos['videos'][0]
        new_video = Video(videoid=video['videoid'], 
                      title=video['title'], 
                      rating=video['rating'],
                      exercise_name=video['exercise_name'])
        db.session.add(new_video)
        db.session.commit()
        uv = UserVideo(user_id=session['user_id'], video_id=new_video.id)
        db.session.add(uv)
        db.session.commit()
        return redirect('/auth/my_videos')
    user_video = UserVideo.query.filter(UserVideo.user_id==session['user_id'], UserVideo.video_id == local_video.id).first()
    if not user_video:
        uv = UserVideo(user_id=session['user_id'], video_id=local_video.id)
        db.session.add(uv)
        db.session.commit()
        return redirect('/auth/my_videos')
    flash('Video already added', 'msguser')
    return redirect("/")


@app.route('/videos/delete/<int:id>')
def delete_video(id):
    '''Delete a video to the database without authentication.'''
    video = Video.query.get_or_404(id)
    db.session.delete(video)
    db.session.commit()
    return redirect('/my_videos')


@app.route('/auth/videos/delete/<int:id>')
def auth_delete_video(id):
    '''Delete a video to the database with authentication.'''
    user_video = UserVideo.query.filter(UserVideo.user_id==session['user_id'], UserVideo.video_id == id).first()
    db.session.delete(user_video)
    db.session.commit()
    return redirect('/auth/my_videos')

@app.route('/auth/playlists/add/<int:video_id>', methods=['GET', 'POST'])
def add_to_playlist(video_id):
    '''Add a video to a playlist.'''
    #duplicate video warning ... !!!
    form = PlaylistForm()
    if form.validate_on_submit():
        name = form.name.data
        existing_playlist = Playlist.query.filter(Playlist.name==name, Playlist.user_id==session['user_id']).first()
        if not existing_playlist:
            playlist = Playlist(name=name, user_id=session['user_id'])  
            db.session.add(playlist)
            db.session.commit()
            pl = Playlist.query.filter(Playlist.name==name, Playlist.user_id==session['user_id']).first()
            pv = PlaylistVideo(playlist_id=pl.id, video_id=video_id)
            db.session.add(pv)
            db.session.commit()
            return redirect('/auth/playlists')
        existing_pv = PlaylistVideo.query.filter(PlaylistVideo.playlist_id==existing_playlist.id, PlaylistVideo.video_id==video_id).first()
        if existing_pv:
            print("existing_pv", existing_pv)
            flash('Video already added to the playlist', 'msguser')
            return redirect('/auth/playlists')
        pv = PlaylistVideo(playlist_id=existing_playlist.id, video_id=video_id)
        db.session.add(pv)
        db.session.commit()
        return redirect('/auth/playlists')
    else:
        return render_template('add_to_playlist.html', form=form)
    
@app.route('/auth/playlists/<playlist_name>/delete/<int:video_id>')
def delete_from_playlist(playlist_name, video_id):
    '''Delete a video from a playlist.'''
    playlist = Playlist.query.filter(Playlist.name==playlist_name, Playlist.user_id==session['user_id']).first()
    le = len(playlist.videos)
    pv = PlaylistVideo.query.filter(PlaylistVideo.playlist_id==playlist.id, PlaylistVideo.video_id==video_id).first()
    db.session.delete(pv)
    db.session.commit()
    if le > 1:
        return redirect('/auth/playlists')
    db.session.delete(playlist)
    db.session.commit()
    return redirect('/auth/playlists')


@app.route('/auth/playlists')
def get_playlists():
    '''Show playlists of the user.'''
    if not_authorized():
        return redirect('/auth')
    #user = User.query.get_or_404(userid)
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    playlists = Playlist.query.filter(Playlist.user_id==user.id).all()
    #print("playlists", playlists)
    return render_template('playlists.html',  playlists=playlists)


@app.route('/exercise', methods=['GET'])
def exercise_by_muscle():
    """Display exercises in accordion by muscle group."""
    #muscle = request.form['muscle']
    muscle = request.args.get('muscle')
    if not muscle:
        print("no muscle group")
        muscle = 'triceps'
    res = requests.get(f"{BASE_URL_WORKOUT}/exercises?muscle={muscle}").json()
    exercises = res['exercises']
    nums = list(range(1, len(exercises) + 1))
    headings = ["heading"+str(num) for num in nums]
    collapses = ["collapse"+str(num) for num in nums]
    transformed_muscle = transform_word(muscle)
    return render_template('exercise.html',  muscle=transformed_muscle, zipped=zip(exercises, headings, collapses))

@app.route('/rating/<int:video_id>', methods=['POST'])
def rate_video(video_id):
    '''Rate a video.'''
    rating = request.form['rating']
    uv_to_update = UserVideo.query.filter(UserVideo.user_id==session['user_id'], UserVideo.video_id==video_id).first()
    uv_to_update.rating = rating
    db.session.commit()
    uvs = UserVideo.query.filter(UserVideo.video_id==video_id).all()
    ratings = [uv.rating for uv in uvs]
    avr_rating = round(sum(ratings) / len(ratings), 1)
    video = Video.query.get_or_404(video_id)
    video.rating = avr_rating
    db.session.commit()
    return redirect('/auth/my_videos')

@app.route('/auth')
def login_or_register():
    '''Tell user to sign in or register.'''
    return render_template('auth.html') 

@app.route('/profile/<username>')
def show_profile(username):
    '''Show user profile.'''
    if "user_id" not in session:
        flash("Please login first!", "msguser")
        return redirect('/auth')
    #user = User.query.get_or_404(user_id)
    user = User.query.filter(User.username == username).first()
    return render_template('profile.html', user=user)


@app.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    '''Delete a user.'''
    if "user_id" not in session:
        flash("Please login first!", "msguser")
        return redirect('/auth')
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id')
    return redirect('/')

@app.route('/users/update/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    '''Update user information.'''
    if "user_id" not in session:
        flash("Please login first!", "msguser")
        return redirect('/auth')
    user = User.query.get_or_404(user_id)
    form = RegisterForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        db.session.commit()
        return redirect(f'/profile/{user.username}')
    return render_template('update_user.html', form=form, user=user)

#authorization
@app.route("/register", methods=['GET', 'POST'])
def register_user():
    """Register user"""
    if "user_id" in session:
        return redirect(f"/profile/{session['user_id']}")
    
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            #form.username.errors.append('Username taken. Sign up again.')
            #form.email.errors.append('Or Email taken. Sign up again.')
            flash('Username or Email taken. Sign up again.', 'msgerror')
            return render_template('register.html', form=form)
        db.session.commit()
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        #flash(f"Welcome {new_user.username}", "success")
        return redirect('/')
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login_user():
    """Login user"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "success")
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/')
        else:
            #form.username.errors = ['Invalid username or']
            #form.password.errors = ['Invalid password']
            flash('Invalid username or password', 'msgerror')
            return redirect('/login')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    """Logout user"""
    session.pop('user_id')
    session.pop('username')
    #flash("Goodbye!", "success")
    return redirect('/')

#password reset
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    '''Request a password reset.'''
    if "user_id" in session:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'msguser')
        return redirect(url_for('login_user'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    '''Reset password.'''
    if "user_id" in session:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'msguser')
        return redirect(url_for('login_user'))
    return render_template('reset_token.html', title='Reset Password', form=form)

#credit for password reset: https://www.youtube.com/watch?v=vutyTx7IaAI&t=36s
#https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog/10-Password-Reset-Email

