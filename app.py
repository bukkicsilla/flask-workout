from flask import Flask, render_template, jsonify, request, flash, redirect, session
from models import db, connect_db, Exercise, Video, User
from forms import RegisterForm, LoginForm, DeleteForm
from sqlalchemy.exc import IntegrityError
from constants import BASE_URL_WORKOUT
import app_json
import requests
import flask_cors
import re


app = Flask(__name__)

app.add_url_rule('/api/fitness/exercises/<muscle>', view_func=app_json.api_exercise_by_muscle)
app.add_url_rule('/api/fitness/allexercises', view_func=app_json.show_all_exercises)
app.add_url_rule('/api/fitness/videos', view_func=app_json.show_videos)

flask_cors.CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///workout_flask"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 10
app.config["SECRET_KEY"] = "Capstone projects are challenging."

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
    if "user_id" not in session:
        flash("Please login first!", "msguser")
        return True
    return False

@app.route('/')
def index():
    muscle = request.args.get('muscle')
    res_exercises = requests.get(f"{BASE_URL_WORKOUT}/exercises?muscle={muscle}").json()
    #name = 'National Parks'
    #print(name)
    #videos = Exercise.query.filter(Exercise.name == name).first().videos
    #print("videos", videos)
    return render_template('index.html', exercises=res_exercises['exercises'])


@app.route('/exercises')
def get_exercises():
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


@app.route('/my_videos')
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
    
    #flash('You can scroll left and right.', 'msguser')
    #print("Grouped exercises by muscle:", muscle_groups)
    return render_template('myvideos3.html', muscle_groups=muscle_groups)


@app.route('/videos/add/<name>/<videoid>')
def save_video(name, videoid):
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


@app.route('/videos/delete/<int:id>')
def delete_video(id):
    video = Video.query.get_or_404(id)
    db.session.delete(video)
    db.session.commit()
    return redirect('/my_videos')


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


#With User
@app.route('/auth')
def login_or_register():
    return render_template('auth.html') 

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
        print("new_user", new_user)
        db.session.add(new_user)
        '''try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)'''
        db.session.commit()
        session['user_id'] = new_user.id
        #flash('Welcome new user!', "success")
        return redirect('/my_videos')
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
            #flash(f"Welcome Back, {user.username}!", "primary")
            session['user_id'] = user.id
            #return redirect('/secret')
            #return redirect(f'/users/{user.username}')
            return redirect('/my_videos')
        #else:
            #form.username.errors = ['Invalid username or']
            #form.password.errors = ['Invalid password']
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    """Logout user"""
    session.pop('user_id')
    #flash("Goodbye!", "success")
    return redirect('/')

