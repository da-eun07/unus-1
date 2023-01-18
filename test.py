# VIDEO RECORDING - NOT FINISHED

import cv2

cap = cv2.VideoCapture(2)
if cap.isOpened:
    file_path = './video/record.mp4'
    fps = 25.40
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')  # 인코딩 포맷 문자
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    size = (int(width), int(height))  # 프레임 크기

    # out = cv2.VideoWriter(file_path, fourcc, fps, size)  # VideoWriter 객체 생성
    out = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('camera-recording', frame)
            out.write(frame)  # 파일 저장
            if cv2.waitKey(int(1000 / fps)) != -1:
                break
        else:
            print('no file!')
            break
    out.release()  # 파일 닫기
else:
    print("Can`t open camera!")
cap.release()
cv2.destroyAllWindows()
