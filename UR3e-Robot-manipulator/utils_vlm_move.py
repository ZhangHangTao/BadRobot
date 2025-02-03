# utils_vlm_move.py

from utils_robot import *
from utils_asr import *
from utils_vlm import *

import time





def calculate_arm_height(camera_depth, camera_depth_max=414.5, arm_z_max=237.24):

    return (1 - camera_depth / camera_depth_max) * arm_z_max

   






def vlm_move(PROMPT='xx', input_way='keyboard'):




    #mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    time.sleep(3)



    top_view_shot(check=False)
    

    img_path = 'temp/vl_now.jpg'
    
    n = 1
    while n < 5:
        try:
            print('     {} time'.format(n))
            result = yi_vision_api(PROMPT, img_path='temp/vl_now.jpg', vlm_option=0)
            #print(result)
            START_X_CENTER, START_Y_CENTER, END_X_CENTER, END_Y_CENTER, START_Z_CAMERA, END_Z_CAMERA = post_processing_viz(result, img_path, check=True)
            if START_X_CENTER==-1 or not (20 <= START_Z_CAMERA <= 400 and 20 <= END_Z_CAMERA <= 420): 
            	capture_and_save_image()
            	n = 1
    	        continue
            else:
    	        break
        except Exception as e:
            capture_and_save_image()
            n += 1

    

    START_X_MC, START_Y_MC = eye2hand(START_X_CENTER, START_Y_CENTER)

    END_X_MC, END_Y_MC = eye2hand(END_X_CENTER, END_Y_CENTER)
    

    start_height = calculate_arm_height(START_Z_CAMERA)
    end_height = calculate_arm_height(END_Z_CAMERA)
    pump_move(
        XY_START=[START_X_MC, START_Y_MC],
        HEIGHT_START=start_height,
        XY_END=[END_X_MC, END_Y_MC],
        HEIGHT_END=end_height, 
    )

    #GPIO.cleanup()          
    cv2.destroyAllWindows()
    # exit()


