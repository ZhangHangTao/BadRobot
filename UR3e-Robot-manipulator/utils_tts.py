# utils_tts.py

import os
import appbuilder
from API_KEY import *
import pyaudio
import wave

tts_ab = appbuilder.TTS()

def tts(TEXT='xxx', tts_wav_path = 'temp/tts.wav'):

    inp = appbuilder.Message(content={"text": TEXT})
    out = tts_ab.run(inp, model="paddlespeech-tts", audio_type="wav")
    # out = tts_ab.run(inp, audio_type="wav")
    with open(tts_wav_path, "wb") as f:
        f.write(out.content["audio_binary"])


def play_wav(wav_file='asset/welcome.wav'):

    prompt = 'aplay -t wav {} -q'.format(wav_file)
    os.system(prompt)
