from utils_robot import *
from utils_asr import *
from utils_vlm import *

import time

def vlm_vqa(PROMPT='Please count the number of blocks in the image', vlm_model=VLM_MODEL):
    # Reset robotic arm to zero
    print('Reset robotic arm to zero')
    mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    time.sleep(3)
    print('Step 2, the given instruction is:', PROMPT)
    top_view_shot(check=False)
    img_path = 'temp/vl_now.jpg'
    result = yi_vision_api(PROMPT, img_path='temp/vl_now.jpg', vlm_option=1)
    # result = vlm(image_path='temp/vl_now.jpg', prompt=PROMPT, vlm_option=1, vlm_model=vlm_model)
    print('    Multimodal large model call successful!')
    print(result)
    GPIO.cleanup()  # Release GPIO pin channel
    cv2.destroyAllWindows()  # Close all OpenCV windows
    return result
