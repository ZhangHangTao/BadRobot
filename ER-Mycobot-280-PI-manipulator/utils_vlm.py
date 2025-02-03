VLM_MODEL = 'gpt-4-turbo'
print('Importing visual large model module')
import cv2
import numpy as np
from openai import OpenAI
from PIL import Image
from PIL import ImageFont, ImageDraw
from utils_tts import *  # Speech synthesis module

# Import Chinese font, specify font size
font = ImageFont.truetype('asset/SimHei.ttf', 26)

from API_KEY import *

OUTPUT_VLM = ''

# System prompt for object extraction
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

    # OUTPUT_VLM = str(completion.choices[0].message.content.strip())
    # Parse the result returned by the large model
    if vlm_option == 0:
        result = eval(completion.choices[0].message.content.strip())
    elif vlm_option == 1:
        result = completion.choices[0].message.content.strip()
        tts(result)  # Speech synthesis, export wav audio file
        play_wav('temp/tts.wav')  # Play synthesized speech audio file

    return result


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def vlm(image_path, prompt, vlm_option=0, vlm_model=VLM_MODEL):
    '''
    Use UIUI transfer API to call the GPT-4 large model (image understanding)
    '''
    client = OpenAI(
        api_key='sk-FBePIPeDcsi2gIu853F4F6E5432f498bAbD83cBc892dA1B2',
        base_url="https://uiuiapi.com/v1"
    )

    # Select the system prompt based on the option
    if vlm_option == 0:
        system_prompt = SYSTEM_PROMPT_CATCH
    elif vlm_option == 1:
        system_prompt = SYSTEM_PROMPT_VQA

    base64_image = encode_image(image_path)

    # Construct the message with the image
    message=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": system_prompt + prompt
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
              }
            },
          ],
        }
      ]

    # Call the GPT-4 API
    completion = client.chat.completions.create(
        model=vlm_model,
        messages=message,
        max_tokens=150
    )

    # Get the response result
    result = completion.choices[0].message.content
    # Process the returned result
    if vlm_option == 0:
        result = eval(result)
    elif vlm_option == 1:
        tts(result)  # Speech synthesis, export wav audio file
        play_wav('temp/tts.wav')  # Play synthesized speech audio file

    return result


def post_processing_viz(result, img_path, check=False):
    '''
    Post-processing and visualization of visual large model output results
    check: Whether to require manual screen confirmation of successful visualization, press key to continue or exit
    '''

    # Post-processing
    img_bgr = cv2.imread(img_path)
    img_h = img_bgr.shape[0]
    img_w = img_bgr.shape[1]
    # Scaling factor
    FACTOR = 999
    # Starting object name
    START_NAME = result['start']
    # Ending object name
    END_NAME = result['end']
    # Starting point, top-left pixel coordinates
    START_X_MIN = int(result['start_xyxy'][0][0] * img_w / FACTOR)
    START_Y_MIN = int(result['start_xyxy'][0][1] * img_h / FACTOR)
    # Starting point, bottom-right pixel coordinates
    START_X_MAX = int(result['start_xyxy'][1][0] * img_w / FACTOR)
    START_Y_MAX = int(result['start_xyxy'][1][1] * img_h / FACTOR)
    # Starting point, center pixel coordinates
    START_X_CENTER = int((START_X_MIN + START_X_MAX) / 2)
    START_Y_CENTER = int((START_Y_MIN + START_Y_MAX) / 2)
    # Ending point, top-left pixel coordinates
    END_X_MIN = int(result['end_xyxy'][0][0] * img_w / FACTOR)
    END_Y_MIN = int(result['end_xyxy'][0][1] * img_h / FACTOR)
    # Ending point, bottom-right pixel coordinates
    END_X_MAX = int(result['end_xyxy'][1][0] * img_w / FACTOR)
    END_Y_MAX = int(result['end_xyxy'][1][1] * img_h / FACTOR)
    # Ending point, center pixel coordinates
    END_X_CENTER = int((END_X_MIN + END_X_MAX) / 2)
    END_Y_CENTER = int((END_Y_MIN + END_Y_MAX) / 2)

    # Visualization
    # Draw starting object box
    img_bgr = cv2.rectangle(img_bgr, (START_X_MIN, START_Y_MIN), (START_X_MAX, START_Y_MAX), [0, 0, 255], thickness=3)
    # Draw starting center point
    img_bgr = cv2.circle(img_bgr, [START_X_CENTER, START_Y_CENTER], 6, [0, 0, 255], thickness=-1)
    # Draw ending object box
    img_bgr = cv2.rectangle(img_bgr, (END_X_MIN, END_Y_MIN), (END_X_MAX, END_Y_MAX), [255, 0, 0], thickness=3)
    # Draw ending center point
    img_bgr = cv2.circle(img_bgr, [END_X_CENTER, END_Y_CENTER], 6, [255, 0, 0], thickness=-1)
    # Write Chinese object names
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)  # BGR to RGB
    img_pil = Image.fromarray(img_rgb)  # array to PIL
    draw = ImageDraw.Draw(img_pil)
    # Write starting object Chinese name
    draw.text((START_X_MIN, START_Y_MIN - 32), START_NAME, font=font, fill=(255, 0, 0, 1))  # Text coordinates, Chinese string, font, rgba color
    # Write ending object Chinese name
    draw.text((END_X_MIN, END_Y_MIN - 32), END_NAME, font=font, fill=(0, 0, 255, 1))  # Text coordinates, Chinese string, font, rgba color
    img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)  # RGB to BGR
    # Save the visualization effect picture
    cv2.imwrite('temp/vl_now_viz.jpg', img_bgr)

    # Display the visualization effect picture on the screen
    cv2.imshow('vlm', img_bgr)

    if check:
        print('    Please confirm successful visualization, press c to continue, press q to quit')
        while (True):
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'):  # Press c to continue
                break
            if key == ord('q'):  # Press q to quit
                # exit()
                cv2.destroyAllWindows()  # Close all OpenCV windows
                raise NameError('Pressed q to quit')
    else:
        if cv2.waitKey(1) & 0xFF == None:
            pass
    return START_X_CENTER, START_Y_CENTER, END_X_CENTER, END_Y_CENTER
