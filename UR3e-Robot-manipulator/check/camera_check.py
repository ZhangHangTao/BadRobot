import os
import cv2
import numpy as np
from pyorbbecsdk import *
from utils import frame_to_bgr_image

def save_one_color_frame(frame: ColorFrame):
    if frame is None:
        return
    image = frame_to_bgr_image(frame)
    if image is None:
        print("Failed to convert frame to image")
        return
    cv2.imwrite("tmp.png", image)

def main():
    pipeline = Pipeline()
    config = Config()

    try:
        profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        if profile_list is not None:
            color_profile: VideoStreamProfile = profile_list.get_default_video_stream_profile()
            config.enable_stream(color_profile)
    except OBError as e:
        print(e)
        return

    pipeline.start(config)
    
    try:
        frames = pipeline.wait_for_frames(700)
        if frames is not None:
            color_frame = frames.get_color_frame()
            if color_frame is not None:
                save_one_color_frame(color_frame)
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.stop()

if __name__ == "__main__":
    main()


