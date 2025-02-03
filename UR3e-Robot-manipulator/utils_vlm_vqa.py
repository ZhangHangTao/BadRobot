from utils_robot import *
from utils_asr import *
from utils_vlm import *

import time

def vlm_vqa(PROMPT='xxx', input_way='keyboard'):
    #mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    time.sleep(3)

    top_view_shot(check=False)
    img_path = 'temp/vl_now.jpg'
    result = yi_vision_api(PROMPT, img_path='temp/vl_now.jpg', vlm_option=1)

    # print(result)
    GPIO.cleanup()
    cv2.destroyAllWindows()
    return result

