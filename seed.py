from models import db, Exercise, Video
from app import app
import requests
from constants import BASE_URL_WORKOUT

db.drop_all()
db.create_all()

'''res = requests.get(f"{BASE_URL_WORKOUT}/exercises/all").json()
exercises = len(res['exercises'])
for j in range(len(exercises)):
    new_exercise = Exercise(name=exercises[j]['name'], 
                            exercise_type=exercises[j]['exercise_type'], 
                            muscle=exercises[j]['muscle'], 
                            equipment=exercises[j]['equipment'], 
                            difficulty=exercises[j]['difficulty'],
                            instructions=exercises[j]['instructions'])
db.session.add(new_exercise)
db.session.commit()'''

'''e1 = Exercise(name="Plank", exercise_type="yoga")
db.session.add(e1)
db.session.commit()
v11 = Video(videoid="pvIjsG5Svck", title="Core Exercise: Plank", rating=6, exercise_name="Plank")
v12 = Video(videoid="yeKv5oX_6GY", title="Basic Forward Plank", rating=8, exercise_name="Plank")
db.session.add(v11)
db.session.add(v12)
db.session.commit()

e2 = Exercise(name="National Parks", exercise_type="hike")
db.session.add(e2)
db.session.commit()
v21 = Video(videoid="bHlf2T6mIRo", title="Yellowstone National Park", rating=7, exercise_name="National Parks")
v22 = Video(videoid="KS7yNH5UYfM", title="Lake Clark National Park", rating=8, exercise_name="National Parks")
v23 = Video(videoid="1kxySVKiWfU", title="Lake Tahoe", rating=6, exercise_name="National Parks")
v24 = Video(videoid="OkrEfJzQxfM", title="Yosemite National Park", rating=10, exercise_name="National Parks")
v25 = Video(videoid="OZKH0abyRSE", title="Great Smokey National Park", exercise_name="National Parks")
v26 = Video(videoid="QVwKL_YzGlU", title="Grand Canyon", exercise_name="National Parks")
v27 = Video(videoid="wgDKpEczAmY", title="Road to Hana", exercise_name="National Parks")
v28 = Video(videoid="wOsZTRDvb2s", title="Long Island Montauk", exercise_name="National Parks")
db.session.add(v21)
db.session.add(v22)
db.session.add(v23)
db.session.add(v24)
db.session.add(v25)
db.session.add(v26)
db.session.add(v27)
db.session.add(v28)
db.session.commit()

e3 = Exercise(name="Pilates", exercise_type="pilates")
db.session.add(e3)
db.session.commit()
v31 = Video(videoid="toFOWvqOjDY", title="Pilates 1", rating=7, exercise_name="Pilates")
v32 = Video(videoid="xMyW3jbg0y0", title="Pilates 2", rating=8, exercise_name="Pilates")
v33 = Video(videoid="UyoqRHklKjc", title="Pilates 3", rating=6, exercise_name="Pilates")
v34 = Video(videoid="ecZ09liTiFI", title="Pilates 4", rating=10, exercise_name="Pilates")
v35 = Video(videoid="hgPPy_zNtlU", title="Pilates 5", exercise_name="Pilates")
v36 = Video(videoid="_y39T5jQfFM", title="Pilates 6", exercise_name="Pilates")
v37 = Video(videoid="efxKEO9H1A8", title="Pilates 7", exercise_name="Pilates")
v38 = Video(videoid="U5LwQW_IQOc", title="Pilates 8", exercise_name="Pilates")
db.session.add(v31)
db.session.add(v32)
db.session.add(v33)
db.session.add(v34)
db.session.add(v35)
db.session.add(v36)
db.session.add(v37)
db.session.add(v38)
db.session.commit()'''
