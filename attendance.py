from db_connection import get_db_connection
import datetime
from mail import send_email

def present_marked(roll_no, section_id, teacher_id):
    con = get_db_connection()
    cur = con.cursor()

    # Fetch student_id based on roll_no
    cur.execute('''SELECT student_id 
                   FROM students 
                   WHERE roll_no = %s;''', (roll_no,))
    student = cur.fetchone()

    if student is None:
        print(f"No student found with roll_no {roll_no}")
        con.close()
        return

    student_id = student[0]

    # Fetch subject_id based on teacher_id and section_id
    cur.execute('''SELECT subject_ids AS subject_id
                   FROM section_subject 
                   WHERE teacher_ids = %s 
                   AND section_ids = %s;''', (teacher_id, section_id))
    subject = cur.fetchone()

    if subject is None:
        print(f"No subject found for teacher_id {teacher_id} and section_id {section_id}")
        con.close()
        return

    subject_id = subject[0]

    # Get today's date
    attendance_date = datetime.date.today()

    # Mark student as present
    is_present = 1

    # Check if the section is an optional section
    cur.execute('''SELECT DISTINCT optional_section_id 
                   FROM students 
                   WHERE optional_section_id IS NOT NULL;''')
    optional_sub = cur.fetchall()
    optional_section_ids = [item[0] for item in optional_sub]

    # Determine the actual section_id to compare
    if section_id in optional_section_ids:
        cur.execute('''SELECT optional_section_id 
                       FROM students 
                       WHERE student_id = %s;''', (student_id,))
        section = cur.fetchone()
        actual_section_id = section[0]
    else:
        cur.execute('''SELECT section_id 
                       FROM students 
                       WHERE student_id = %s;''', (student_id,))
        section = cur.fetchone()
        actual_section_id = section[0]

    # Insert attendance if the section_id matches
    if actual_section_id == section_id:
        cur.execute(
            '''INSERT IGNORE INTO attendance (student_id, section_id, subject_id, teacher_id, attendance_date, is_present) 
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (student_id, section_id, subject_id, teacher_id, attendance_date, is_present)
        )
        con.commit()

        if cur.rowcount > 0:
            print(f"{roll_no} , Attendance marked successfully")
            cur.execute(
                '''SELECT subject_name FROM subjects WHERE subject_id = %s''',
                (subject_id,)
            )
            sub = cur.fetchone()
            subj = sub[0]

            cur.execute(
                '''SELECT first_name FROM students WHERE student_id = %s''',
                (student_id,)
            )
            na = cur.fetchone()
            name = na[0]

            # Sending mail
            subject = f"{subj} Attendance "
            message_body = f"Hello {name},\n\n{roll_no}, has been marked present in {subj}.\n\nBest regards,\nBayan Kumar Sahu"
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT gmail FROM students WHERE roll_no = %s"
            cursor.execute(query, (roll_no,))
            mails = cursor.fetchone()
            con.commit()
            if mails:
                # Extract the email address
                gmail = mails['gmail']
                send_email(gmail, subject, message_body)

    con.commit()
    con.close()
