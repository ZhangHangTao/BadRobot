# utils_asr.py


import pyaudio
import wave
import numpy as np
import os
import sys
from API_KEY import *
#os.close(sys.stderr.fileno())


# import sounddevice as sd
# print(sd.query_devices())

def play_wav(wav_file='asset/welcome.wav'):

    prompt = 'aplay -t wav {} -q'.format(wav_file)
    os.system(prompt)
    
def record(MIC_INDEX=2, DURATION=5):
    '''
    '''
    os.system('arecord -D "plughw:{}" -f dat -c 1 -r 16000 -d {} temp/speech_record.wav'.format(MIC_INDEX, DURATION))



def record_auto(working_mode, QUIET_DB=6000):

    
    CHUNK = 1024
    RATE = 16000
    

    delay_time = 1
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK
                   )
    
    frames = []
    
    flag = False
    quiet_flag = False
    
    temp_time = 0
    last_ok_time = 0
    START_TIME = 0
    END_TIME = 0
    

    while True:
        

        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        temp_volume = np.max(np.frombuffer(data, dtype=np.short))

        if temp_volume > QUIET_DB and flag==False:

            flag =True
            START_TIME = temp_time
            last_ok_time = temp_time
    
        if flag: # 录音中的各种情况
    
            if(temp_volume < QUIET_DB and quiet_flag==False):

                quiet_flag = True
                last_ok_time = temp_time
                
            if(temp_volume > QUIET_DB):

                quiet_flag = False
                last_ok_time = temp_time
    
            if(temp_time > last_ok_time + delay_time*15 and quiet_flag==True):

                if(quiet_flag and temp_volume < QUIET_DB):

                    END_TIME = temp_time
                    break
                else:

                    quiet_flag = False
                    last_ok_time = temp_time
                    

        temp_time += 1
        if quiet_flag==True and working_mode and temp_time > 200:
            END_TIME = temp_time
            play_wav('temp/tts_end.wav')
            working_mode=False
            break

    stream.stop_stream()
    stream.close()
    p.terminate()
    


    output_path = 'temp/speech_record.wav'
    wf = wave.open(output_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames[START_TIME-2:END_TIME]))
    wf.close()
    return working_mode


import appbuilder

os.environ["APPBUILDER_TOKEN"] = APPBUILDER_TOKEN
asr = appbuilder.ASR()



def speech_recognition(audio_path='temp/speech_record.wav'):


    try:

        with wave.open(audio_path, 'rb') as wav_file:
            

            num_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            num_frames = wav_file.getnframes()
            

            frames = wav_file.readframes(num_frames)
        

        content_data = {"audio_format": "wav", "raw_audio": frames, "rate": 16000}
        message = appbuilder.Message(content_data)
        

        speech_result = asr.run(message).content['result'][0]
        print('ASR result：', speech_result)
        return speech_result
    
    except Exception as e:
        return ""


