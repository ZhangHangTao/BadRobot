from utils_asr import *
from utils_robot import *
from utils_llm import *
from utils_led import *
from utils_camera import *
from utils_robot import *
from utils_pump import *
from utils_vlm_move import *
from utils_drag_teaching import *
from utils_agent import *
from utils_tts import *
from utils_vlm_vqa import *

pump_off()
message=[]
message.append({"role":"system","content":AGENT_SYS_PROMPT})

def agent_play():
    '''
    This main function is to control the robotic arm intelligent agent through voice commands to arrange actions.
    '''
    back_zero()
    # Enter command.
    start_record_ok = input('Input the number to record for a specified duration, press k to type input, press c to input default instructions.\n')
    if str.isnumeric(start_record_ok):
        DURATION = int(start_record_ok)
        record(DURATION=DURATION)   # Recording.
        #record_auto()
        order = speech_recognition() # Speech recognition.
    elif start_record_ok == 'k':
        order = input('Please enter instructions.')
    elif start_record_ok == 'c':
        order = 'Return to zero first, then shake your head, then place the green square on the basketball'
    else:
        print('No instructions, exit.')
        # exit()
        raise NameError('No instructions, exit.')
    message.append({"role":"user","content":order})
    
    output=eval(agent_plan(message))

    print(output)
    response = output['response'] # Get what the robot wants to say to me.
    print('Begin speech synthesis.')
    tts(response)                     # Speech synthesis, export WAV audio file.
    play_wav('temp/tts.wav')          # Play the speech synthesis audio file.
    output_other=''
    for each in output['function']: # Run each function orchestrated by the Embodied intelligent.
        print('Begin executing actions.', each)
        ret = eval(each)
        if ret != None:
            output_other = ret

    output['response']+='.'+ output_other
    message.append({"role":"assistant","content":str(output)})
    #print(message)

# agent_play()
if __name__ == '__main__':
    while True:
        agent_play()

