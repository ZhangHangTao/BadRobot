print('Importing speech synthesis module')

import os
import appbuilder
from API_KEY import *
import pyaudio
import wave

tts_ab = appbuilder.TTS()

def tts(TEXT='I am a robot', tts_wav_path='temp/tts.wav'):
    '''
    Speech synthesis TTS, generate wav audio file
    '''
    inp = appbuilder.Message(content={"text": TEXT})
    out = tts_ab.run(inp, model="paddlespeech-tts", audio_type="wav")
    # out = tts_ab.run(inp, audio_type="wav")
    with open(tts_wav_path, "wb") as f:
        f.write(out.content["audio_binary"])
    # print("TTS speech synthesis, export wav audio file to: {}".format(tts_wav_path))

def play_wav(wav_file='asset/welcome.wav'):
    '''
    Play wav audio file
    '''
    prompt = 'aplay -t wav {} -q'.format(wav_file)
    os.system(prompt)