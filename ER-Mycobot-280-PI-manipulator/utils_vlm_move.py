from utils_robot import *
from utils_asr import *
from utils_vlm import *

import time

def vlm_move(PROMPT='Please help me place the green block on Peppa Pig', vlm_model=VLM_MODEL):
    '''
    Multimodal large model recognizes image, suction pump grabs and moves the object
    input_way: speech for speech input, keyboard for keyboard input
    '''

    print('Multimodal large model recognizes image, suction pump grabs and moves the object')

    # Reset robotic arm to zero
    print('Reset robotic arm to zero')
    mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    time.sleep(3)

    ## Step 1: Complete hand-eye calibration
    print('Step 1: Complete hand-eye calibration')

    ## Step 2: Issue instruction
    # PROMPT_BACKUP = 'Please help me place the green block on Peppa Pig' # Default instruction

    # if input_way == 'keyboard':
    #     PROMPT = input('Step 2: Input instruction')
    #     if PROMPT == '':
    #         PROMPT = PROMPT_BACKUP
    # elif input_way == 'speech':
    #     record() # Record
    #     PROMPT = speech_recognition() # Speech recognition
    print('Step 2, the given instruction is:', PROMPT)

    ## Step 3: Take a top view photo
    print('Step 3: Take a top view photo')
    top_view_shot(check=False)

    ## Step 4: Input the image to the multimodal visual large model
    print('Step 4: Input the image to the multimodal visual large model')
    img_path = 'temp/vl_now.jpg'

    result = None
    n = 1
    while n < 5:
        try:
            print('    Attempt {} to access the multimodal large model'.format(n))
            result = yi_vision_api(PROMPT, img_path='temp/vl_now.jpg', vlm_option=0)
            # result = vlm(image_path='temp/vl_now.jpg', prompt=PROMPT, vlm_option=0, vlm_model=vlm_model)
            print('    Multimodal large model call successful!')
            print(result)
            break
        except Exception as e:
            print('    Multimodal large model returned data structure error, try again', e)
            n += 1

    if result is None:
        raise ValueError("Multimodal LLM called failed")

    ## Step 5: Post-processing and visualization of the visual large model output
    print('Step 5: Post-processing and visualization of the visual large model output')
    START_X_CENTER, START_Y_CENTER, END_X_CENTER, END_Y_CENTER = post_processing_viz(result, img_path, check=True)

    ## Step 6: Convert hand-eye calibration to robotic arm coordinates
    print('Step 6: Convert hand-eye calibration, transform pixel coordinates to robotic arm coordinates')
    # Starting point, robotic arm coordinates
    START_X_MC, START_Y_MC = eye2hand(START_X_CENTER, START_Y_CENTER)
    # Ending point, robotic arm coordinates
    END_X_MC, END_Y_MC = eye2hand(END_X_CENTER, END_Y_CENTER)

    ## Step 7: Suction pump grabs and moves the object
    print('Step 7: Suction pump grabs and moves the object')
    pump_move(mc=mc, XY_START=[START_X_MC, START_Y_MC], XY_END=[END_X_MC, END_Y_MC])

    ## Step 8: Finish up
    print('Step 8: Task completed')
    GPIO.cleanup()  # Release GPIO pin channel
    cv2.destroyAllWindows()  # Close all OpenCV windows
    # exit()

def vlm_collision(PROMPT, vlm_model='gpt-4'):
    # Reset robotic arm to zero
    print('Reset robotic arm to zero')
    mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    time.sleep(3)

    ## Step 3: Take a top view photo
    print('Step 3: Take a top view photo')
    top_view_shot(check=False)

    ## Step 4: Input the image to the multimodal visual large model
    print('Step 4: Input the image to the multimodal visual large model')
    img_path = 'temp/vl_now.jpg'

    n = 1
    while n < 5:
        try:
            print('    Attempt {} to access the multimodal large model'.format(n))
            result = vlm(image_path='temp/vl_now.jpg', prompt=PROMPT, vlm_option=0, vlm_model=vlm_model)
            print('    Multimodal large model call successful!')
            print(result)
            break
        except Exception as e:
            print('    Multimodal large model returned data structure error, try again', e)
            n += 1

    ## Step 5: Post-processing and visualization of the visual large model output
    print('Step 5: Post-processing and visualization of the visual large model output')
    START_X_CENTER, START_Y_CENTER, END_X_CENTER, END_Y_CENTER = post_processing_viz(result, img_path, check=True)

    ## Step 6: Convert hand-eye calibration to robotic arm coordinates
    print('Step 6: Convert hand-eye calibration, transform pixel coordinates to robotic arm coordinates')
    # Starting point, robotic arm coordinates
    START_X_MC, START_Y_MC = eye2hand(START_X_CENTER, START_Y_CENTER)
    # Ending point, robotic arm coordinates
    END_X_MC, END_Y_MC = eye2hand(END_X_CENTER, END_Y_CENTER)

    ## Step 7: Suction pump grabs and moves the object
    print('Step 7: Suction pump grabs and moves the object')
    pump_move_collision(mc=mc, XY_START=[START_X_MC, START_Y_MC], XY_END=[END_X_MC, END_Y_MC])

    ## Step 8: Finish up
    print('Step 8: Task completed')
    GPIO.cleanup()  # Release GPIO pin channel
    cv2.destroyAllWindows()  # Close all OpenCV windows
