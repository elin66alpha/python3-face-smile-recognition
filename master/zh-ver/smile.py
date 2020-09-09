# -*- coding: UTF-8 -*-
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import numpy as np
import time
import dlib
import cv2
import face_recognition
import sys

font = cv2.FONT_HERSHEY_SIMPLEX

def smile(mouth):
    A = dist.euclidean(mouth[3], mouth[9])
    B = dist.euclidean(mouth[2], mouth[10])
    C = dist.euclidean(mouth[4], mouth[8])
    avg = (A+B+C)/3
    D = dist.euclidean(mouth[0], mouth[6])
    mar=avg/D
    return mar



def main():
    names = []
    with open('names.txt','r') as f:
        names = [line.strip() for line in f]
    known_face_encodings = []
    for w in names:
        s1 = face_recognition.load_image_file("./image/"+w+".jpg")
        s2 = face_recognition.face_encodings(s1)[0]
        known_face_encodings.append(s2)
    print(known_face_encodings)
    known_face_names = names
    known_names = names
    print (known_face_names)
    


    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True   

    shape_predictor= "./shape_predictor_68_face_landmarks.dat" #dace_landmark
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(shape_predictor)
    (mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

    print("starting video ")
    vs = VideoStream(src=0).start()
    fileStream = False
    time.sleep(1.0)



    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    #convert color to rgb
        rgb_small_frame = small_frame[:, :, ::-1]

        if process_this_frame:
        # Find faces and face encodings in cap
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            #if True in matches:
                #first_match_index = matches.index(True)
                #name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                face_names.append(name)

        process_this_frame = not process_this_frame


    # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

        # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        # Draw a label with a name below the face
        #cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, name, (left, bottom + 35), font, 1.0, (0, 0, 255), 1)


        rects = detector(gray, 0)
        for (i, rect) in enumerate(rects):
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            mouth= shape[mStart:mEnd]
            mar= smile(mouth)
            mouthHull = cv2.convexHull(mouth)
            cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)
            
            if mar <= .27 or mar > .5 :
                cv2.putText(frame, "smile", (100, 100), font , 0.5, (0, 255, 255), 2)
                for i in known_names:
                    if i == name:
                        cv2.putText(frame, "open", (0, 300), font , 1, (0, 255, 255), 3)
                    else:
                        cv2.putText(frame, "close", (0, 300), font , 1, (0, 255, 255), 3)
            else:
                cv2.putText(frame, "normal", (100, 100), font , 0.5, (0, 255, 255), 2)

            cv2.putText(frame, "MAR: {}".format(mar), (10, 30), font , 0.5, (0, 0, 255), 2)

        cv2.imshow("Frame", frame)

        key2 = cv2.waitKey(1) & 0xFF
        if key2 == ord('q'):
            break


    cv2.destroyAllWindows()
    vs.stop()
