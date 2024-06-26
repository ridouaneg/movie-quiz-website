from flask import Flask, render_template, request, redirect, url_for, session
import csv
import re
import numpy as np

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed to use sessions

def read_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['video_path'] = row['video_path'].replace('watch?v=', 'embed/')
            video_id = re.search(r"embed/([a-zA-Z0-9_-]+)", row['video_path']).group(1)
            row['thumbnail'] = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            data.append(row)
    return data

def save_answer(pseudo, gender, age, video_id, question_id, selected_option, watched, visual_only):
    with open('answers.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([pseudo, gender, age, video_id, question_id, selected_option, watched, visual_only])

def get_unique_movies(movies):
    unique_movies = {}
    for movie in movies:
        if movie['video_id'] not in unique_movies:
            unique_movies[movie['video_id']] = movie
    return list(unique_movies.values())

movies = read_csv('data.csv')
unique_movies = get_unique_movies(movies)

@app.route('/', methods=['GET', 'POST'])
def pseudo():
    if request.method == 'POST':
        pseudo = request.form.get('pseudo')
        gender = request.form.get('gender')
        age = request.form.get('age')
        muted_version = request.form.get('muted_version') == 'on'
        session['pseudo'] = pseudo
        session['gender'] = gender
        session['age'] = age
        session['muted_version'] = muted_version
        return redirect(url_for('index'))
    return render_template('pseudo.html')

@app.route('/index')
def index():
    if 'pseudo' not in session:
        return redirect(url_for('pseudo'))
    random_movies = np.random.choice(unique_movies, 6, replace=False).tolist()
    return render_template('index.html', movies=random_movies)

@app.route('/quiz/<video_id>', methods=['GET', 'POST'])
def quiz(video_id):
    if 'pseudo' not in session:
        return redirect(url_for('pseudo'))

    questions = [movie for movie in movies if movie['video_id'] == video_id]
    movie_title = questions[0]['movie_title'] if questions else 'Unknown Title'
    muted_version = session.get('muted_version', False)

    if request.method == 'POST':
        pseudo = session['pseudo']
        gender = session['gender']
        age = session['age']
        for question in questions:
            question_id = question['question_id']
            selected_option = request.form.get(f'option_{question_id}')
            visual_only = request.form.get(f'visual_only_{question_id}') == 'on'
            if selected_option:
                save_answer(pseudo, gender, age, video_id, question_id, selected_option, watched=False, visual_only=visual_only)
        return redirect(url_for('full_quiz', video_id=video_id))

    return render_template('quiz.html', questions=questions, movie_title=movie_title, muted_version=muted_version)

@app.route('/full_quiz/<video_id>', methods=['GET', 'POST'])
def full_quiz(video_id):
    if 'pseudo' not in session:
        return redirect(url_for('pseudo'))

    questions = [movie for movie in movies if movie['video_id'] == video_id]
    movie_title = questions[0]['movie_title'] if questions else 'Unknown Title'
    muted_version = session.get('muted_version', False)

    if request.method == 'POST':
        pseudo = session['pseudo']
        gender = session['gender']
        age = session['age']
        for question in questions:
            question_id = question['question_id']
            selected_option = request.form.get(f'option_{question_id}')
            visual_only = request.form.get(f'visual_only_{question_id}') == 'on'
            if selected_option:
                save_answer(pseudo, gender, age, video_id, question_id, selected_option, watched=True, visual_only=visual_only)
        return redirect(url_for('index'))

    return render_template('full_quiz.html', questions=questions, movie_title=movie_title, muted_version=muted_version)

if __name__ == '__main__':
    app.run(debug=True)
