from flask import Flask, render_template, jsonify, request, flash 
from models import connect_db, Exercise
from constants import BASE_URL_WORKOUT
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///workout_flask"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 10
app.config["SECRET_KEY"] = "Capstone projects are challenging."

connect_db(app)

@app.route('/')
def index():
    muscle = request.args.get('muscle')
    res_exercises = requests.get(f"{BASE_URL_WORKOUT}/exercises?muscle={muscle}").json()
    name = 'National Parks'
    print(name)
    videos = Exercise.query.filter(Exercise.name == name).first().videos
    print("videos", videos)
    return render_template('index.html', exercises=res_exercises['exercises'])

@app.route('/exercises')
def get_exercises():
    res = requests.get(f"{BASE_URL_WORKOUT}/exercises").json()
    return jsonify(res['exercises'])

@app.route('/videos')
def get_videos():
    name = request.args.get('name')
    res_videos = requests.get(f"{BASE_URL_WORKOUT}/videos?name={name}").json()
    #res = requests.get(f"{BASE_URL_WORKOUT}/videos").json()
    #return jsonify(res['videos'])
    return render_template('videos.html', name=name, videos=res_videos['videos']) 

@app.route('/my_videos')
def get_all():
    exercises = Exercise.query.all()
    flash('You can scroll left and right.', 'msguser')
    return render_template('myvideos.html', exercises=exercises)


@app.route('/exercise', methods=['GET'])
def exercise_by_muscle():
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
    return render_template('exercise.html',  muscle=muscle, zipped=zip(exercises, headings, collapses))
