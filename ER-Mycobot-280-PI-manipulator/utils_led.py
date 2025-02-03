from utils_llm import llm_qianfan, llm_yi
from utils_robot import mc

print('Import the LED control module.')

SYS_PROMPT = 'I am about to say a sentence that contains a target object. Please help me return one possible color of this object in the form of an RGB pixel value ranging from 0-255, arranged in a tuple format, such as (255, 30, 60). Reply with the tuple itself, starting with parentheses, and do not include any Chinese characters. Here is the sentence:'

def llm_led(PROMPT_LED='Help me change the color of the LED light to the color of Lake Baikal.'):
    PROMPT = SYS_PROMPT + PROMPT_LED
    
    n = 1
    while n < 5:
        try:
            response = llm_yi(PROMPT)
            rgb_tuple = eval(response)
            mc.set_color(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
            print('LED light color changed successfully.', rgb_tuple)

            break
            
        except Exception as e:
            print('The large model returned a JSON structure error. Please try again.', e)
            n += 1