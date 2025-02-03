import numpy as np
from pyorbbecsdk import Config, OBSensorType, Pipeline

MIN_DEPTH = 300  # 10cm
MAX_DEPTH = 700  # 50cm

class AreaDepthMeasurement:
    def __init__(self):
        self.config = Config()
        self.pipeline = Pipeline()
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
            print(e)
            return

    def measure_area_depth(self, x1, y1, x2, y2):
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

            # Ensure coordinates are within frame bounds
            x1 = max(0, min(x1, width - 1))
            y1 = max(0, min(y1, height - 1))
            x2 = max(0, min(x2, width))
            y2 = max(0, min(y2, height))

            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_data = depth_data.reshape((height, width))

            # Extract the region of interest
            roi = depth_data[y1:y2, x1:x2]

            # Convert to millimeters and filter depths
            roi_mm = roi.astype(np.float32) * scale
            valid_depths = roi_mm[(roi_mm >= MIN_DEPTH) & (roi_mm <= MAX_DEPTH)]

            if len(valid_depths) == 0:
                return None

            average_depth = np.mean(valid_depths)
            return average_depth

        finally:
            self.pipeline.stop()

def main():
    measurement = AreaDepthMeasurement()
    
    # Example: Measure depth in a 100x100 pixel area at the center of the frame
    x1, y1 = 270, 190  # Assuming a 640x480 resolution, adjust if different
    x2, y2 = 370, 290

    avg_depth = measurement.measure_area_depth(x1, y1, x2, y2)
    if avg_depth is not None:
        print(f"Average depth in the specified area: {avg_depth:.2f} mm")
    else:
        print("Failed to measure depth in the specified area.")

if __name__ == "__main__":
    main()

