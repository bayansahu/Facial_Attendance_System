from db_connection import get_db_connection
import cv2
from attendance import present_marked

def detector(section_id, user_id):
    def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf):
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = classifier.detectMultiScale(gray_image, scaleFactor, minNeighbors)

        for (x, y, w, h) in features:
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
            id, pred = clf.predict(gray_image[y:y+h, x:x+w])
            confidence = int(100 * (1 - pred/300))

            if confidence > 80:
                con = get_db_connection()
                cur = con.cursor()
                cur.execute("SELECT roll_no, first_name FROM students WHERE roll_no = %s", (id,))
                student = cur.fetchone()
                con.close()

                if student:
                    name = student[1]
                    cv2.putText(img, name, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
                    present_marked(id,section_id, user_id)
                    return id
            else:
                cv2.putText(img, "Unknown", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, cv2.LINE_AA)

    def recognize(img, clf, faceCascade):
        name = draw_boundary(img, faceCascade, 1.1, 10, (255, 255, 255), "Face", clf)
        return name, img

    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.read("classifier.xml")

    url = 'http://192.168.126.63:8080/video'
    video_capture = cv2.VideoCapture(0)
    detected_id = None

    while True:
        ret, img = video_capture.read()
        if not ret:
            break
        name, img = recognize(img, clf, faceCascade)
        cv2.imshow("Face detection", img)

        if name is not None:
            detected_id = name

        if cv2.waitKey(1) == 13:
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return detected_id
