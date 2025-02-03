print('Import recording and speech recognition modules.')

import pyaudio
import wave
import numpy as np
import os
import sys
from API_KEY import *

# Determine the microphone index number.
# import sounddevice as sd
# print(sd.query_devices())

def record(MIC_INDEX=4, DURATION=5):
    '''
    Call the microphone recording, use the 'arecord -l' command to get the microphone ID.
    DURATION，Recording duration.
    '''
    print('Start recording for {} seconds.'.format(DURATION))
    os.system('sudo arecord -D "plughw:{}" -f dat -c 1 -r 16000 -d {} temp/speech_record.wav'.format(MIC_INDEX, DURATION))
    print('Recording finished.')

def record_auto(MIC_INDEX=4):
    '''
    Activate microphone recording and save to 'temp/speech_record.wav' audio file.
    Start recording automatically when the volume exceeds the threshold, and stop recording automatically after the volume falls below the threshold for a certain period.
    MIC_INDEX: Microphone device index number.
    '''
    
    CHUNK = 1024               # Sampling width.
    RATE = 16000               # Sampling rate.
    
    QUIET_DB = 2000            # Decibel threshold, start recording if exceeded, otherwise stop.
    delay_time = 1             # How long to wait before automatically stopping the recording after the sound drops below the decibel threshold.
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1  # Number of sampling channels.
    
    # Initialize recording.
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=MIC_INDEX
                   )
    
    frames = []             # All audio frames.
    
    flag = False            # Has the recording started
    quiet_flag = False      # Current volume is below the threshold.
    
    temp_time = 0           # What is the current frame number
    last_ok_time = 0        # What was the last normal frame number
    START_TIME = 0          # What was the frame number when recording started?
    END_TIME = 0            # What was the frame number when recording stopped?
    
    print('You could speak now')
    
    while True:
        
        # Get the sound of the current chunk.
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        # Get the decibel value of the current chunk's volume.
        temp_volume = np.max(np.frombuffer(data, dtype=np.short))
        
        if temp_volume > QUIET_DB and flag==False:
            print("Volume is above the threshold, start recording.")
            flag =True
            START_TIME = temp_time
            last_ok_time = temp_time
    
        if flag: # Get the decibel value of the current chunk's volume.
    
            if(temp_volume < QUIET_DB and quiet_flag==False):
                print("Recording in progress, current volume is below the threshold.")
                quiet_flag = True
                last_ok_time = temp_time
                
            if(temp_volume > QUIET_DB):
                quiet_flag = False
                last_ok_time = temp_time
    
            if(temp_time > last_ok_time + delay_time*15 and quiet_flag==True):
                print("After the volume is below the threshold for {:.2f} seconds, check the current volume.".format(delay_time))
                if(quiet_flag and temp_volume < QUIET_DB):
                    print("The current volume is still below the threshold, recording stopped.")
                    END_TIME = temp_time
                    break
                else:
                    print("The current volume is above the threshold again, continuing recording.")
                    quiet_flag = False
                    last_ok_time = temp_time

        temp_time += 1
        if temp_time > 150:
            END_TIME = temp_time
            print('Timeout, recording stopped.')
            break
    
    # Stop recording
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Export WAV audio file.
    output_path = 'temp/speech_record.wav'
    wf = wave.open(output_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames[START_TIME-2:END_TIME]))
    wf.close()
    print('Save the recording file.', output_path)

import appbuilder
os.environ["APPBUILDER_TOKEN"] = APPBUILDER_TOKEN
asr = appbuilder.ASR()

def speech_recognition(audio_path='temp/speech_record.wav'):
    print('Begin speech recognition.')
    # Load WAV audio file.
    with wave.open(audio_path, 'rb') as wav_file:
        
        # Get basic information about the audio file.
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        
        # Get audio data.
        frames = wav_file.readframes(num_frames)
        
    # Make a request to the API.
    content_data = {"audio_format": "wav", "raw_audio": frames, "rate": 16000}
    message = appbuilder.Message(content_data)
    speech_result = asr.run(message).content['result'][0]
    print('Speech recognition result:', speech_result)
    return speech_result
