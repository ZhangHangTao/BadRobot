# utils_vlm.py

import cv2
import numpy as np
from pyorbbecsdk import Config, OBSensorType, Pipeline
from PIL import Image, ImageDraw, ImageFont
import time
import os


MIN_DEPTH = 20  # 20mm
MAX_DEPTH = 1000  # 10000mm


from utils_tts import *

font = ImageFont.truetype('asset/SimHei.ttf', 26)

from API_KEY import *

OUTPUT_VLM = ''

# 系统提示词
SYSTEM_PROMPT_CATCH = '''
I am about to give an instruction to the robotic arm. Please help me extract the starting object and the target object from the instruction, and find the pixel coordinates of the top-left and bottom-right corners of these objects in the image. Ensure the precision of the localization, outputting JSON data structure.

For example, if my instruction is: Please help me place the red block on the house sketch.
You should output the following format:
{
 "start":"red block",
 "start_xyxy":[[102,505],[324,860]],
 "end":"house sketch",
 "end_xyxy":[[300,150],[476,310]]
}
Only reply with the JSON itself, do not include any other content.

My current instruction is:
'''

SYSTEM_PROMPT_VQA = '''
Tell me the name, category, and function of each object in the image. Describe each object in one sentence.

For example:
Capsules, medicine, treat colds.
Plate, household item, holds things.
Loratadine Tablets, medicine, treat allergies.

My current instruction is:
'''


import openai
from openai import OpenAI
import base64
def yi_vision_api(PROMPT='Please help me place the red block on the pen', img_path='temp/vl_now.jpg', vlm_option=0):
    '''
    Lingyiwanwu large model open platform, yi-vision visual language multimodal large model API
    '''
    if vlm_option == 0:
        SYSTEM_PROMPT = SYSTEM_PROMPT_CATCH
    elif vlm_option == 1:
        SYSTEM_PROMPT = SYSTEM_PROMPT_VQA

    client = OpenAI(
        api_key=YI_KEY,
        base_url="https://api.lingyiwanwu.com/v1"
    )

    # Encode as base64 data
    with open(img_path, 'rb') as image_file:
        image = 'data:image/jpeg;base64,' + base64.b64encode(image_file.read()).decode('utf-8')

    # Make a request to the large model
    completion = client.chat.completions.create(
        model="yi-vision",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT + PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image
                        }
                    }
                ]
            },
        ]
    )
    

    if vlm_option == 0:
        result = eval(completion.choices[0].message.content.strip())
    elif vlm_option==1:
        result=completion.choices[0].message.content.strip()
        print(result)
        tts(result)
        play_wav('temp/tts.wav')
    
    return result
   

class TemporalFilter:
    def __init__(self, alpha):
        self.alpha = alpha
        self.previous_frame = None

    def process(self, frame):
        if self.previous_frame is None:
            result = frame
        else:
            result = cv2.addWeighted(frame, self.alpha, self.previous_frame, 1 - self.alpha, 0)
        self.previous_frame = result
        return result

class DepthMeasurement:
    def __init__(self):
        self.config = Config()
        self.pipeline = Pipeline()
        self.temporal_filter = TemporalFilter(alpha=0.5)
        self.setup_pipeline()

    def setup_pipeline(self):
        try:
            profile_list = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
            assert profile_list is not None
            depth_profile = profile_list.get_default_video_stream_profile()
            assert depth_profile is not None
            print("depth profile: ", depth_profile)
            self.config.enable_stream(depth_profile)
        except Exception as e:
            print(f"Setup pipeline error: {e}")

    def measure_depth(self, x1, y1, x2, y2):
        self.pipeline.start(self.config)
        try:
            frames = self.pipeline.wait_for_frames(500)
            if frames is None:
                return None

            depth_frame = frames.get_depth_frame()
            if depth_frame is None:
                return None

            width = depth_frame.get_width()
            height = depth_frame.get_height()
            scale = depth_frame.get_depth_scale()
		
            x1 = max(0, min(x1, width - 1))
            y1 = max(0, min(y1, height - 1))
            x2 = max(0, min(x2, width))
            y2 = max(0, min(y2, height))
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_data = depth_data.reshape((height, width))
            
            #roi = depth_data[y1:y2, x1:x2]

            depth_data = depth_data.astype(np.float32) * scale
            depth_data = np.where((depth_data > MIN_DEPTH) & (depth_data < MAX_DEPTH), depth_data, 0)
            depth_data = depth_data.astype(np.uint16)
            
            # Apply temporal filtering
            depth_data = self.temporal_filter.process(depth_data)
            depth_data = depth_data[y1:y2, x1:x2]

            return np.median(depth_data[depth_data > 0])



        finally:
            self.pipeline.stop()

    def get_depth_image(self):
        self.pipeline.start(self.config)
        try:
            frames = self.pipeline.wait_for_frames(100)
            if frames is None:
                return None

            depth_frame = frames.get_depth_frame()
            if depth_frame is None:
                return None

            width = depth_frame.get_width()
            height = depth_frame.get_height()
            scale = depth_frame.get_depth_scale()

            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_data = depth_data.reshape((height, width))

            depth_data = depth_data.astype(np.float32) * scale
            depth_data = np.where((depth_data > MIN_DEPTH) & (depth_data < MAX_DEPTH), depth_data, 0)
            depth_data = depth_data.astype(np.uint16)
            
            # Apply temporal filtering
            depth_data = self.temporal_filter.process(depth_data)

            depth_image = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            depth_image = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)

            return depth_image

        finally:
            self.pipeline.stop()



def post_processing_viz(result, img_path, check=False):


    img_bgr = cv2.imread(img_path)
    img_h = img_bgr.shape[0]
    img_w = img_bgr.shape[1]

    FACTOR = 999

    START_NAME = result['start']

    END_NAME = result['end']

    START_X_MIN = int(result['start_xyxy'][0][0] * img_w / FACTOR)
    START_Y_MIN = int(result['start_xyxy'][0][1] * img_h / FACTOR)

    START_X_MAX = int(result['start_xyxy'][1][0] * img_w / FACTOR)
    START_Y_MAX = int(result['start_xyxy'][1][1] * img_h / FACTOR)

    START_X_CENTER = int((START_X_MIN + START_X_MAX) / 2)
    START_Y_CENTER = int((START_Y_MIN + START_Y_MAX) / 2)

    END_X_MIN = int(result['end_xyxy'][0][0] * img_w / FACTOR)
    END_Y_MIN = int(result['end_xyxy'][0][1] * img_h / FACTOR)

    END_X_MAX = int(result['end_xyxy'][1][0] * img_w / FACTOR)
    END_Y_MAX = int(result['end_xyxy'][1][1] * img_h / FACTOR)

    END_X_CENTER = int((END_X_MIN + END_X_MAX) / 2)
    END_Y_CENTER = int((END_Y_MIN + END_Y_MAX) / 2)
    START_X_MIN_DEPTH = int(START_X_MIN * 848 / 1280)
    START_Y_MIN_DEPTH = int(START_Y_MIN * 480 / 720)
    START_X_MAX_DEPTH = int(START_X_MAX * 848 / 1280)
    START_Y_MAX_DEPTH = int(START_Y_MAX * 480 / 720)
    END_X_MIN_DEPTH = int(END_X_MIN * 848 / 1280)
    END_Y_MIN_DEPTH = int(END_Y_MIN * 480 / 720)
    END_X_MAX_DEPTH = int(END_X_MAX * 848 / 1280)
    END_Y_MAX_DEPTH = int(END_Y_MAX * 480 / 720)


    depth_measurer = DepthMeasurement()
    start_depth = depth_measurer.measure_depth(
    int(START_X_MIN_DEPTH + (START_X_MAX_DEPTH - START_X_MIN_DEPTH) * 0.25),
    int(START_Y_MIN_DEPTH + (START_Y_MAX_DEPTH - START_Y_MIN_DEPTH) * 0.25),
    int(START_X_MAX_DEPTH - (START_X_MAX_DEPTH - START_X_MIN_DEPTH) * 0.25),
    int(START_Y_MAX_DEPTH - (START_Y_MAX_DEPTH - START_Y_MIN_DEPTH) * 0.25)
)

    end_depth = depth_measurer.measure_depth(
    int(END_X_MIN_DEPTH + (END_X_MAX_DEPTH - END_X_MIN_DEPTH) * 0.25),
    int(END_Y_MIN_DEPTH + (END_Y_MAX_DEPTH - END_Y_MIN_DEPTH) * 0.25),
    int(END_X_MAX_DEPTH - (END_X_MAX_DEPTH - END_X_MIN_DEPTH) * 0.25),
    int(END_Y_MAX_DEPTH - (END_Y_MAX_DEPTH - END_Y_MIN_DEPTH) * 0.25)
)

    depth_image = depth_measurer.get_depth_image()
    cv2.rectangle(depth_image, (START_X_MIN_DEPTH, START_Y_MIN_DEPTH), 
                  (START_X_MAX_DEPTH, START_Y_MAX_DEPTH), [0, 0, 255], 2)
    cv2.rectangle(depth_image, (END_X_MIN_DEPTH, END_Y_MIN_DEPTH), 
                  (END_X_MAX_DEPTH, END_Y_MAX_DEPTH), [255, 0, 0], 2)
    if depth_image is not None:
        cv2.imshow("Depth Image", depth_image)
        cv2.moveWindow('Depth Image', 1800, 100) 
        cv2.waitKey(1)

    img_bgr = cv2.rectangle(img_bgr, (START_X_MIN, START_Y_MIN), (START_X_MAX, START_Y_MAX), [0, 0, 255], thickness=3)

    img_bgr = cv2.circle(img_bgr, [START_X_CENTER, START_Y_CENTER], 6, [0, 0, 255], thickness=-1)

    img_bgr = cv2.rectangle(img_bgr, (END_X_MIN, END_Y_MIN), (END_X_MAX, END_Y_MAX), [255, 0, 0], thickness=3)

    img_bgr = cv2.circle(img_bgr, [END_X_CENTER, END_Y_CENTER], 6, [255, 0, 0], thickness=-1)

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(img_pil)

    draw.text((START_X_MIN, START_Y_MIN-32), START_NAME, font=font, fill=(255, 0, 0, 1))

    draw.text((END_X_MIN, END_Y_MIN-32), END_NAME, font=font, fill=(0, 0, 255, 1))


    if start_depth is not None:
        start_depth_text = f"Depth: {start_depth:.2f} mm"
        draw.text((START_X_MIN, START_Y_MAX+5), start_depth_text, font=font, fill=(255, 0, 0, 1))
    
    if end_depth is not None:
        end_depth_text = f"Depth: {end_depth:.2f} mm"
        draw.text((END_X_MIN, END_Y_MAX+5), end_depth_text, font=font, fill=(0, 0, 255, 1))

    img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    cv2.imwrite('temp/vl_now_viz.jpg', img_bgr)
    
    formatted_time = time.strftime("%Y%m%d%H%M", time.localtime())
    cv2.imwrite('visualizations/{}.jpg'.format(formatted_time), img_bgr)

    cv2.imshow('vlm', img_bgr)
    cv2.moveWindow('vlm_start', 100, 100)
    print(START_X_CENTER)
    print(START_Y_CENTER)
    if check:

        while(True):
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'):
                break
            if key == ord('q'):
                cv2.destroyAllWindows()
                return -1,-1,-1,-1
    else:
        if cv2.waitKey(1) & 0xFF == None:
            pass
    #start_depth, end_depth
    return START_X_CENTER, START_Y_CENTER, END_X_CENTER, END_Y_CENTER , start_depth , end_depth

