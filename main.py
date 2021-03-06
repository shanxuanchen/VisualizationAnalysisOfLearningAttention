

import cv2
import dlib
import numpy as np
from imutils import face_utils
import utils
import math


face_landmark_path = './shape_predictor_68_face_landmarks.dat'

K = [6.5308391993466671e+002, 0.0, 3.1950000000000000e+002,
     0.0, 6.5308391993466671e+002, 2.3950000000000000e+002,
     0.0, 0.0, 1.0]
D = [7.0834633684407095e-002, 6.9140193737175351e-002, 0.0, 0.0, -1.3073460323689292e+000]

cam_matrix = np.array(K).reshape(3, 3).astype(np.float32)
dist_coeffs = np.array(D).reshape(5, 1).astype(np.float32)

object_pts = np.float32([[6.825897, 6.760612, 4.402142],
                         [1.330353, 7.122144, 6.903745],
                         [-1.330353, 7.122144, 6.903745],
                         [-6.825897, 6.760612, 4.402142],
                         [5.311432, 5.485328, 3.987654],
                         [1.789930, 5.393625, 4.413414],
                         [-1.789930, 5.393625, 4.413414],
                         [-5.311432, 5.485328, 3.987654],
                         [2.005628, 1.409845, 6.165652],
                         [-2.005628, 1.409845, 6.165652],
                         [2.774015, -2.080775, 5.048531],
                         [-2.774015, -2.080775, 5.048531],
                         [0.000000, -3.116408, 6.097667],
                         [0.000000, -7.415691, 4.070434]])

reprojectsrc = np.float32([[10.0, 10.0, 10.0],
                           [10.0, 10.0, -10.0],
                           [10.0, -10.0, -10.0],
                           [10.0, -10.0, 10.0],
                           [-10.0, 10.0, 10.0],
                           [-10.0, 10.0, -10.0],
                           [-10.0, -10.0, -10.0],
                           [-10.0, -10.0, 10.0]])

line_pairs = [[0, 1], [1, 2], [2, 3], [3, 0],
              [4, 5], [5, 6], [6, 7], [7, 4],
              [0, 4], [1, 5], [2, 6], [3, 7]]

def draw_text(coordinates, image_array, text, color, x_offset=0, y_offset=0,
                                                font_scale=2, thickness=2):
    x, y = coordinates[:2]
    cv2.putText(image_array, text, (x + x_offset, y + y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, color, thickness, cv2.LINE_AA)



def get_head_pose(shape):
    image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                            shape[39], shape[42], shape[45], shape[31], shape[35],
                            shape[48], shape[54], shape[57], shape[8]])

    _, rotation_vec, translation_vec = cv2.solvePnP(object_pts, image_pts, cam_matrix, dist_coeffs)

    reprojectdst, _ = cv2.projectPoints(reprojectsrc, rotation_vec, translation_vec, cam_matrix,
                                        dist_coeffs)

    reprojectdst = tuple(map(tuple, reprojectdst.reshape(8, 2)))

    # calc euler angle
    rotation_mat, _ = cv2.Rodrigues(rotation_vec)
    pose_mat = cv2.hconcat((rotation_mat, translation_vec))
    _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)

    return reprojectdst, euler_angle


def drawLine(frame, Point1, Point2, Color=(0,255,255)):
    cv2.line(frame, Point1, Point2, color=Color, thickness=2)


def main():
    # return
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Unable to connect to camera.")
        return
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(face_landmark_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            face_rects = detector(frame, 0)

            if len(face_rects) > 0:

                for face in face_rects:
                    shape = predictor(frame, face)

                    shape = face_utils.shape_to_np(shape)
                    reprojectdst, euler_angle = get_head_pose(shape)

                    for idx, (x, y) in enumerate(shape):
                        # cv2.putText(frame, str(idx), (x,y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)
                        cv2.circle(frame, (x, y), 1, (0, 0, 255), 5)


                    # 视线检测
                    RightEys = (int((shape[36][0] + shape[39][0]) / 2), int((shape[36][1] + shape[39][1]) / 2))
                    LeftEys = (int((shape[42][0] + shape[45][0]) / 2), int((shape[42][1] + shape[45][1]) / 2))


                    pitch = euler_angle[0, 0]
                    yaw = euler_angle[1, 0]
                    roll = euler_angle[2,0]


                    euler_angle[1,0] = euler_angle[1,0] - 25.0



                    cv2.circle(frame, LeftEys, 1, (0, 0, 255), -1)
                    cv2.putText(frame, 'left eye', LeftEys, cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

                    cv2.circle(frame, RightEys, 1, (0, 0, 255), -1)
                    cv2.putText(frame, 'right eye', RightEys, cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

                    LeftTopFacePoint = (shape[0][0], shape[19][1])
                    RightTopFacePoint = (shape[26][0], shape[19][1])
                    LeftDownFacePoint = (shape[0][0], shape[8][1])
                    RightDownFacePoint = (shape[26][0], shape[8][1])

                    # Lip Angle

                    LeftMousePoint = (shape[48][0], shape[48][1])
                    RightMousePoint = (shape[54][0], shape[54][1])
                    TopMousePoint = (shape[51][0], shape[51][1])
                    DownMousePoint = (shape[57][0], shape[57][1])
                    drawLine(frame, LeftMousePoint, TopMousePoint, (220, 255, 110))
                    drawLine(frame, LeftMousePoint, DownMousePoint, (220, 255, 110))
                    drawLine(frame, LeftMousePoint, RightMousePoint, (220, 255, 110))

                    L1 = [TopMousePoint[0] - LeftMousePoint[0], TopMousePoint[1] - LeftMousePoint[1]]
                    L2 = [RightMousePoint[0] - LeftMousePoint[0], RightMousePoint[1] - LeftMousePoint[1]]
                    L3 = [DownMousePoint[0] - LeftMousePoint[1], DownMousePoint[1] - LeftMousePoint[1]]
                    MouseTopAngle = utils.angle(L1, L2)
                    MouseDownAngle = utils.angle(L3, L2)
                    LipAngle = MouseDownAngle - MouseTopAngle


                    utils.draw_axis(frame, yaw, pitch, roll, tdx=shape[30][0], tdy=shape[30][1], size=200)


                    # 检测失效
                    if yaw > 30.0 or yaw < -30.0:
                        Point = -1
                    elif LipAngle > 60.0:
                        Point = math.cos(yaw * math.pi / 180.0 )
                    else:
                        Point = 0.8 * math.cos(yaw * math.pi / 180.0 ) + 0.2 * math.sin(LipAngle * math.pi / 180.0)

                    print("Point is : %.2lf, yaw: %.2lf, LipAngle : %.2lf"%(Point, yaw, LipAngle))

                    if Point > 0.8:
                        LineColor = (255, 255, 0)
                        ResString = 'engagement'
                    elif Point > 0.6:
                        LineColor = (0, 255, 255)
                        ResString = 'attention'
                    else:
                        LineColor = (0, 0, 255)
                        ResString = 'disregard'

                    font_scale = 2
                    thickness = 2
                    x_offset = 1
                    y_offset = 1

                    drawLine(frame, LeftTopFacePoint, RightTopFacePoint, LineColor)
                    drawLine(frame, LeftTopFacePoint, LeftDownFacePoint, LineColor)
                    drawLine(frame, RightTopFacePoint, RightDownFacePoint, LineColor)
                    drawLine(frame, LeftDownFacePoint, RightDownFacePoint, LineColor)
                    cv2.putText(frame, ResString, (LeftTopFacePoint[0] + x_offset, LeftTopFacePoint[1] + y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale, LineColor, thickness, cv2.LINE_AA)

                cv2.imshow("demo", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


if __name__ == '__main__':
    main()
