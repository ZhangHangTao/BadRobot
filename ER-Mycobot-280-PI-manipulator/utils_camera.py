import cv2
import numpy as np

def check_camera():
    '''
    Turn on the camera, display the real-time footage from the camera, and exit by pressing the 'q' key.
    '''
    print('Turn on the camera')
    cap = cv2.VideoCapture(0)
    
    while(True):
        ret, frame = cap.read()
    
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()