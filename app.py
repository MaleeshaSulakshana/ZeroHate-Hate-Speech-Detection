import os
import sys
import hashlib
import mysql.connector
from flask import Flask, render_template, redirect, jsonify, url_for, request, session

sys.path.append(os.path.abspath('detection/'))
import prediction as pd

# Initialize flask app
app = Flask(__name__)

app.secret_key = "ZeroHate"
app.static_folder = "static"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# For crate database connection
def connector():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="zerohate"
    )

    return conn


# For load login
@app.route('/login')
def login():
    if 'user' in session:
        return redirect('index')

    return render_template('login.html')


# For load registration
@app.route('/registration')
def registration():
    if 'user' in session:
        return redirect('index')

    return render_template('registration.html')


# For load index page
@app.route('/')
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect('login')

    conn = connector()
    query = ''' SELECT comments.id, users.name, comments.comment FROM comments
                INNER JOIN users ON users.id = comments.user ORDER BY comments.id DESC '''

    cur = conn.cursor()
    cur.execute(query)
    comments = cur.fetchall()

    return render_template('index.html', comments=comments)


# For login
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():

    if request.method == "POST":

        if 'user' in session:
            return jsonify({'redirect': url_for('index')})

        else:
            email = request.form.get('email')
            psw = request.form.get('psw')

            if len(email) == 0 or len(psw) == 0:
                return jsonify({'error': "Fields are empty!"})

            else:

                psw = hashlib.md5(psw.encode()).hexdigest()

                conn = connector()
                query = ''' SELECT id, name, email FROM users WHERE email = %s AND psw = %s '''
                values = (str(email), str(psw))

                cur = conn.cursor()
                cur.execute(query, values)
                details = cur.fetchall()

                if len(details) < 1:
                    return jsonify({'error': "Email or password incorrect!"})

                else:
                    session['user'] = str(details[0][0])
                    return jsonify({'redirect': url_for('index')})

    return jsonify({'redirect': url_for('login')})


# For user registration
@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():

    if request.method == "POST":

        if 'user' in session:
            return jsonify({'redirect': url_for('index')})

        else:
            name = request.form.get('name')
            email = request.form.get('email')
            psw = request.form.get('psw')
            psw = hashlib.md5(psw.encode()).hexdigest()

            conn = connector()

            query = ''' SELECT id, name, email FROM users WHERE email = %s '''
            values = (str(email),)

            cur = conn.cursor()
            cur.execute(query, values)
            details = cur.fetchall()

            if len(details) > 0:
                return jsonify({'error': "This email already exist!"})

            else:
                query = ''' INSERT INTO users (name, email, psw) VALUES (%s, %s, %s)'''
                values = (str(name), str(email), str(psw))

                cur = conn.cursor()
                cur.execute(query, values)
                conn.commit()
                result = cur.rowcount

            if result < 1:
                return jsonify({'error': "Account created not successfully!"})

            else:
                return jsonify({'success': "Account created successfully!"})

    return jsonify({'redirect': url_for('registration')})


# For logout
@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user', None)

    return redirect("login")


# For add comment
@app.route('/add_comment', methods=['GET', 'POST'])
def add_comment():

    if request.method == "POST":

        if 'user' not in session:
            return jsonify({'redirect': url_for('login')})

        else:
            comment = request.form.get('comment')

            if len(comment) == 0:
                return jsonify({'error': "Fields are empty!"})

            else:

                pred_result = pd.get_prediction(comment)

                if pred_result == "yes":
                    return jsonify({'error': "Your comment has hate speech!"})

                else:
                    conn = connector()
                    query = ''' INSERT INTO comments (user, comment) VALUES (%s, %s)'''
                    values = (int(session['user']), str(comment))

                    cur = conn.cursor()
                    cur.execute(query, values)
                    conn.commit()
                    result = cur.rowcount

                    if result < 1:
                        return jsonify({'error': "Comment not added!"})

                    else:
                        return jsonify({'success': "Comment added!"})

    return jsonify({'redirect': url_for('index')})


# Run
if __name__ == '__main__':

    port = "5000"
    host = "0.0.0.0"
    app.run(host=host, port=port, debug=True)
