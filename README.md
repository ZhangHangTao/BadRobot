
<h1 align='center' style="text-align:center; font-weight:bold; font-size:2.0em;letter-spacing:2.0px;"> BadRobot: Jailbreaking Embodied LLMs in the Physical World </h1>



<p align='center';>
ICLR 2025<br>
</p>
<!-- <p align='center' style="text-align:center;font-size:2.5 em;">
<b>
    <a href="https://drive.google.com/file/d/1z8G-XWQOw9H5v4iP_2-ccSO1ZdznIOBP/view?usp=sharing" target="_blank" style="text-decoration: none;">[arXiv]</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://embodied-ai-safety.github.io/" target="_blank" style="text-decoration: none;">[Project Page]
    </a> 
</b>
</p> -->


------------

$${\color{red}\text{\textbf{!!! Warning !!!}}}$$

$${\color{red}\text{\textbf{This paper contains potentially harmful}}}$$

$${\color{red}\text{\textbf{AI-generated language and aggressive actions.}}}$$


Please be patient, I will continue to update the repository in the near future.

## Code Structure

- **`Jailbreak_Prompts.xlsx`**: 100 recent in-the-wild jailbreak prompts targeting LLMs cover disguised intent, role play, structured responses, virtual AI simulation, and hybrid strategies, used to test their effectiveness in embodied LLMs.

- **`Physical_Word_Malicious_Queries.xlsx`**: Our benchmark of queries for malicious actions against embodied LLMs, containing 277 requests covering physical harm, privacy violations, pornography, fraud, illegal activities, hateful conduct, and sabotage.

- **`digital_evaluation`**: Three distinct attack methods implemented for BadRobot, used for validation in the digital world.

### Running Demo in the Digital World
Demo code is at `digital_evaluation/main.py`.

To run the digital evaluation, use the following command in your terminal:

```bash
python digital_evaluation/main.py --api_key YOUR_API_KEY --base_url BASE_URL --model MODEL_NAME --user_input USER_INPUT --attack_method ATTACK_METHOD --load_malicious_queries True/False
```
#### Available Attack Methods

To select an attack method, use the `--attack_method` argument. You can choose from the following attack methods as described in our paper:

- `none`: No attack is applied.
- `contextual jailbreak`: Bypasses model safety mechanisms by manipulating the input context.
- `safety misalignment`: Exploits misalignment between the model’s responses and safety guidelines.
- `conceptual deception`: Tries to deceive the model by introducing misleading or subtly incorrect concepts.

---

We develop a prototype of the minimal embodied LLM system on two robotic arms in the physical world (`ER Mycobot 280 PI` manipulator and `UR3e` manipulator), sharing consistent core code but differing in movement control, tool interface, I/O, and processing units. Specifically, the `ER Mycobot 280 PI` is controlled by a `Raspberry Pi 4` as its processing unit, while the `UR3e` manipulator uses an `NVIDIA Jetson AGX Orin` as its processing unit. That is to say, we’ve provided implementations on two different processing platforms, allowing the community to more easily adapt and reuse the system for further development.


Next, we will analyze the code structure using the `UR3e Robot manipulator` distance.

- **`check`**: Check the functionality of the microphone, RGB-D camera, speakers, and other devices before running.
- **`pyorbbecsdk`**: RGB-D camera Orbbec driver and configuration files; see details at https://github.com/orbbec/pyorbbecsdk.
- **`temp`**: Temporary storage for captured images and recognized audio results.
- **`API_KEY.py`**: APIs for speech recognition (ASR) and text-to-speech (TTS) modules. We use the [Baidu AI Cloud Qianfan Platform's ASR interface](https://intl.cloud.baidu.com/) and [ChatTTS's TTS model](https://github.com/2noise/ChatTTS) for voice interaction within our embodied LLM system.
- **`agent_go.py`**: Entry point for execution, containing the core logic that drives the entire system.
- **`depth_estimate.py`**: depth data from the depth camera.
- **`utils_agent.py`**: System prompts that enable LLM to serve as a robot agent.
- **`utils_asr.py`**: Speech recognition module. `record_auto()` supports automatic pause detection for seamless conversation flow.
- **`utils_camera.py`**: Used to invoke the camera.
- **`utils_llm.py`**: calling various LLM APIs; please enter the correct API KEY.
- **`utils_robot.py`**: Encapsulates the motion commands for the robotic arm (such as `movel()`, `movej()`) and defines some basic atomic actions.
- **`utils_tts.py`**: Convert the robot's response into sound.
- **`utils_vlm.py`**: prompting the MLLM to complete visual localization, returning pixel coordinates that are then converted to spatial coordinates for the robotic arm.
- **`utils_vlm_move.py`**: Visualization of recognition results; if inaccurate, supports re-invoking the model for recognition.
- **`utils_vlm_vqa.py`**: visual question and answer on the visual scene.

---
### Running the Physical World System
To launch the entire system in the physical world, the main entry point can be found at `UR3e-Robot-manipulator/agent_go.py`, `ER-Mycobot-280-PI-manipulator/agent_go.py`.
To start the system, simply run the following command in your terminal. Make sure that all necessary dependencies are installed before running the script.
```bash
cd UR3e-Robot-manipulator
python agent_go.py
```
```bash
cd ER-Mycobot-280-PI-manipulator
python agent_go.py
```






## Hardware setup
For the `ER Mycobot 280 PI`, we use a Mycobot USB camera flange, a Mycobot vertical suction pump, and a Raspberry Pi 4.

For the `UR3e`, we use an Orbbec Gemini 335L RGB-D camera, a vertical suction pump, an adaptive gripper, and a Jetson AGX Orin with 64GB of memory.


## Physical World Manipulator Setup Instructions
- Create a conda environment:
```Shell
conda create -n embodied-safety python=3.10
conda activate embodied-safety
```

- Enable audio support:
```Shell
sudo apt-get install portaudio19-dev
```


- See [Instructions](https://github.com/orbbec/pyorbbecsdk) to install Orbbec camera driver (Note: install these inside the created conda environment).

- Install other dependencies:
```Shell
pip install -r requirements.txt
```

- Obtain an [OpenAI API](https://openai.com/blog/openai-api) key, and put it inside the `UR3e Robot manipulator/utils_llm.py`.


<br><br>




