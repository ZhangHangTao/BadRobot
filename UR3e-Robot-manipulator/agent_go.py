# agent_go.py


from utils_asr import *
from utils_robot import *
from utils_llm import *
from utils_camera import *
from utils_robot import *
from utils_pump import *
from utils_vlm_move import *
from utils_agent import *
from utils_tts import *
from utils_vlm_vqa import *
pump_off()
# back_zero()
#play_wav('asset/welcome.wav')

message=[]
message.append({"role":"system","content":AGENT_SYS_PROMPT})


def detect_wake_word(text):
    return True
    
def process_command(order):
    message.append({"role":"user","content":order})
    # 智能体Agent编排动作
    output=eval(agent_plan(message))
    print(output)
    response = output['response']
    tts(response)
    play_wav('temp/tts.wav')
    output_other=''
    for each in output['function']:
        print('action', each)
        ret = eval(each)
        if ret != None:
            output_other = ret

    output['response']+='.'+ output_other
    message.append({"role":"assistant","content":str(output)})
    back_zero()
    #time.sleep(3)
    
def agent_play():


    back_zero()

    #check_camera()


    QUITE_DB=7000
    #if str.isnumeric(QUITE_DB)==False:
    	#QUITE_DB=8000
    working_mode = False
    start_record_ok = "1"
    #start_record_ok = "1"
    while True:    
    	if str.isnumeric(start_record_ok):
            working_mode = record_auto(working_mode, int(QUITE_DB))
            text = speech_recognition()

            if working_mode:
                if text.strip():
                    process_command(text)
            else:
                if detect_wake_word(text):
                    #play_wav('temp/tts_welcome.wav')
                    working_mode = True
            #time.sleep(0.01)
            
            
            
    	elif start_record_ok == 'k':
            order = input('input command')
            process_command(order)

        
    

if __name__ == '__main__':

    while True:
        agent_play()

