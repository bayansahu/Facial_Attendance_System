from flask import Flask, render_template, request, redirect, url_for, Response
import mysql.connector
from dataset import dataframe
from training import train_classifier
from detector import detector
from db_connection import get_db_connection
from mail import send_email


app = Flask(__name__)

@app.route('/')
@app.route("/login", methods=['POST', 'GET'])
def login():
    connection = get_db_connection()
    if request.method == 'POST':
        user_type = request.form['user-type']
        user_id = request.form['username']
        password = request.form['password']
        if user_type == 'teacher':
            cursor = connection.cursor(dictionary=True)
            query = "SELECT password, first_name FROM teachers WHERE teacher_id = %s"
            cursor.execute(query, (user_id,))
            record = cursor.fetchone()
            if record:
                stored_password = record['password']
                name = record['first_name']
                if stored_password == password:
                    print(name)
                    return redirect(url_for('home',user_id=user_id))
                else:
                    msg = "Password is incorrect"
                    return render_template('login.html', msg=msg)
            else:
                msg = "User not found"
                return render_template('login.html', msg=msg)

        elif user_type == 'student':
            cursor = connection.cursor(dictionary=True)
            query = "SELECT password ,first_name FROM students WHERE roll_no = %s"
            cursor.execute(query, (user_id,))
            record = cursor.fetchone()
            if record:
                stored_password = record['password']
                name = record['first_name']

                if stored_password == password:
                    print(name)
                    return redirect(url_for('home',user_id=user_id))
                else:
                    msg = "Password is incorrect"
                    return render_template('login.html', msg=msg)
            else:
                msg = "User not found"
                return render_template('login.html', msg=msg)

        elif user_type == 'admin':
            if user_id == '21052655' and password == 'Bayan@12345':
                return redirect(url_for('admin'))
    return render_template('login.html')

@app.route("/admin", methods=['POST', 'GET'])
def admin():
    #connection = get_db_connection()
    return render_template('admin.html')

@app.route("/home/<int:user_id>", methods=['POST', 'GET'])
def home(user_id):
    connection = get_db_connection()
    section = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('''SELECT sec.section_id, sec.section_name FROM sections sec
                JOIN 
                    section_subject ss ON sec.section_id = ss.section_ids
                JOIN 
                    teachers t ON ss.teacher_ids = t.teacher_id
                WHERE 
                    t.teacher_id = %s;
                    ''', (user_id,))
            section = cursor.fetchall()
            cursor.close()
        except mysql.connector.Error as err:
            print(f"Error fetching data: {err}")
        finally:
            connection.close()
    return render_template('home.html', section=section, user_id=user_id)

@app.route('/abc', methods=['POST', 'GET'])
def abc():
    return render_template('registration.html')

@app.route('/teachers', methods=['POST', 'GET'])
def teachers():
    msg = ''
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gmail = request.form['gmail']

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    '''INSERT INTO teachers (first_name, last_name, gmail) VALUES (%s, %s, %s)''',
                    (first_name, last_name, gmail)
                )
                connection.commit()
                cursor.execute(
                    '''UPDATE teachers 
                       SET password = SUBSTRING(SHA2(RAND(), 256), 1, 8)
                       WHERE first_name = %s
                       AND last_name = %s
                       AND gmail = %s''',
                    (first_name, last_name, gmail)
                )
                connection.commit()
                if cursor.rowcount > 0:
                    msg = 'Successfully Registered'
                    cursor.execute(
                        '''SELECT teacher_id, password FROM teachers 
                           WHERE first_name = %s AND gmail = %s''',
                        (first_name, gmail)
                    )
                    record = cursor.fetchall()
                    if record:
                        teacher_id, password = record[0]
                        subject = 'Attendance Portal Credential'
                        message_body = f'Hello {first_name},\n\nYour Login Credential for Attendance Portal are,\nID : {teacher_id}\nPassword : {password}\n\nBest regards,\nBayan Kumar Sahu'
                        send_email(gmail, subject, message_body)

                else:
                    msg = 'Sorry, Unable to Register'
                cursor.close()
            except mysql.connector.Error as err:
                msg = f'Sorry, Unable to Register : Error inserting data: {err}'
                print(f"Error inserting data: {err}")
            finally:
                connection.close()
    return render_template('teachers_form.html', msg=msg)

@app.route('/student')
def students():
    connection = get_db_connection()
    students = []

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            cursor.close()
        except mysql.connector.Error as err:
            print(f"Error fetching data: {err}")
        finally:
            connection.close()

    return render_template('students.html', students=students)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    output = request.form.to_dict()
    roll = output["roll_no"]
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        roll_no = request.form['roll_no']
        section_id = request.form['section_id']
        optional_subject_id = request.form['optional_subject_id']
        optional_section_id = request.form['optional_section_id']
        gmail = request.form['gmail']

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO students (first_name, last_name, roll_no, section_id, optional_subject_id, optional_section_id, gmail) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (first_name, last_name, roll_no, section_id, optional_subject_id, optional_section_id, gmail)
                )
                connection.commit()
                cursor.execute(
                    '''UPDATE students 
                       SET password = SUBSTRING(SHA2(RAND(), 256), 1, 8)
                       WHERE first_name = %s
                       AND last_name = %s
                       AND gmail = %s''',
                    (first_name, last_name, gmail)
                )
                connection.commit()
                if cursor.rowcount > 0:
                    msg = 'Successfully Registered'
                    cursor.execute(
                        '''SELECT roll_no , password FROM teachers 
                           WHERE first_name = %s AND gmail = %s''',
                        (first_name, gmail)
                    )
                    record = cursor.fetchall()
                    if record:
                        user_id, password = record[0]
                        subject = 'Attendance Portal Credential'
                        message_body = f'Hello {first_name},\n\nYour Login Credential for Attendance Portal are,\nID : {user_id}\nPassword : {password}\n\nBest regards,\nBayan Kumar Sahu'
                        send_email(gmail, subject, message_body)

                else:
                    msg = 'Sorry, Unable to Register'
                cursor.close()
            except mysql.connector.Error as err:
                print(f"Error inserting data: {err}")
            finally:
                connection.close()
            # return redirect(url_for('students'))
    return render_template("registration.html", start_video=True, roll=roll)

@app.route("/video/<roll>")
def video(roll):
    return Response(dataframe(roll), mimetype='multipart/x-mixed-replace; boundary=frame')


from datetime import date


@app.route('/attendance/<int:section_id>/<int:user_id>')
def attendance(section_id, user_id):
    connection = get_db_connection()
    students = []
    today_date = date.today()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            # Get the subject_id for the teacher and section
            cursor.execute('''SELECT subject_ids AS subject_id
                               FROM section_subject 
                               WHERE teacher_ids = %s 
                               AND section_ids = %s;''', (user_id, section_id))
            subject = cursor.fetchone()
            subject_id = subject['subject_id']

            cursor.execute('''
                SELECT DISTINCT optional_section_id FROM students;
            ''')
            optional_sub = cursor.fetchall()
            optional_section_ids = [item['optional_section_id'] for item in optional_sub]

            if section_id not in optional_section_ids:
                cursor.execute('''
                    SELECT 
                        s.first_name, 
                        s.roll_no,
                        a.is_present
                    FROM 
                        students s
                        JOIN sections sec ON s.section_id = sec.section_id
                        JOIN section_subject ss ON sec.section_id = ss.section_ids
                        JOIN teachers t ON ss.teacher_ids = t.teacher_id
                        LEFT JOIN attendance a ON s.student_id = a.student_id
                            AND a.subject_id = %s
                            AND a.attendance_date = %s
                    WHERE 
                        t.teacher_id = %s
                        AND sec.section_id = %s;
                ''', (subject_id, today_date, user_id, section_id,))
            else:
                cursor.execute('''
                    SELECT 
                        s.first_name, 
                        s.roll_no,
                        a.is_present
                    FROM 
                        students s
                        JOIN section_subject ss ON s.optional_section_id = ss.section_ids
                        LEFT JOIN attendance a ON s.student_id = a.student_id
                            AND a.subject_id = %s
                            AND a.attendance_date = %s
                    WHERE 
                        ss.teacher_ids = %s 
                        AND s.optional_section_id = %s;
                ''', (subject_id, today_date, user_id, section_id,))

            students = cursor.fetchall()
            cursor.close()
        except mysql.connector.Error as err:
            print(f"Error fetching data: {err}")
        finally:
            connection.close()

    return render_template('attendance.html', students=students, section_id=section_id, user_id=user_id)


@app.route("/result/<int:section_id>/<int:user_id>", methods=['POST', 'GET'])
def result(section_id, user_id):
    train_classifier("data")
    detected_roll = detector(section_id, user_id)
    print(detected_roll)
    return redirect(url_for('attendance', section_id=section_id, user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True)
