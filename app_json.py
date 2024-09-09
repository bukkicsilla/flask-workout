from constants import BASE_URL_WORKOUT
import requests
from flask import jsonify, request

def api_exercise_by_muscle():
    muscle = request.args.get('muscle')
    res_exercises = requests.get(f"{BASE_URL_WORKOUT}/exercises?muscle={muscle}").json()
    return jsonify(res_exercises['exercises'])


def show_exercises():
    res = requests.get(f"{BASE_URL_WORKOUT}/exercises").json()
    return jsonify(res['exercises'])


def show_videos():
    name = request.args.get('name')
    res_videos = requests.get(f"{BASE_URL_WORKOUT}/videos?name={name}").json()
    #res = requests.get(f"{BASE_URL_WORKOUT}/videos").json()
    return jsonify(res_videos['videos'])
    #return render_template('videos.html', name=name, videos=res_videos['videos']) 

'''@app.route('/my_videos')
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
    return render_template('exercise.html',  muscle=muscle, zipped=zip(exercises, headings, collapses))'''