import os
import subprocess

FFMPEG = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", "ffmpeg.exe")

def task_dir_Audio(taskName):
    os.makedirs("./audio/" + taskName, exist_ok=True)

def course_dir_Audio(taskName,untiName):
    os.makedirs("./audio/" + taskName + "/" + untiName, exist_ok=True)

def level_dir_Audio(taskName,untiName,levelName):
    os.makedirs("./audio/" + taskName + "/" + untiName + "/" + levelName, exist_ok=True)

def mp3_to_wav(mp3_path, wav_path=None):
    '''将 mp3 转成 16000Hz/单声道/16bit 的 wav，如wav_path缺省则同目录同名'''
    if wav_path is None:
        wav_path = os.path.splitext(mp3_path)[0] + ".wav"
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"找不到文件: {mp3_path}")
    subprocess.run(
        [FFMPEG, "-y", "-i", mp3_path, "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", wav_path],
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    )

def get_vbcable_device():
    '''寻找虚拟播放设备'''
    import sounddevice as sd
    for i , dev in enumerate(sd.query_devices()):
        if "CABLE Input" in dev['name']:
            return i
    raise RuntimeError("找不到虚拟播放设备")

def play_wav(wav_path, blocking=True):
    '''播放wav到虚拟声卡输入'''
    import wave
    import numpy as np
    import sounddevice as sd
    VB_DEVICE = get_vbcable_device()
    try:
        with wave.open(wav_path, 'rb') as wf:
            data = wf.readframes(wf.getnframes())
            samplerate = wf.getframerate()
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            dtype = {1: np.uint8, 2: np.int16, 4: np.int32}.get(width, np.int16)
        arr = np.frombuffer(data, dtype=dtype)
        if channels > 1:
            arr = arr.reshape(-1, channels).mean(axis=1).astype(dtype)
        sd.stop()
        sd.play(arr, samplerate=samplerate, device=VB_DEVICE, blocking=blocking)
    except Exception as e:
        print(f"  播放失败: {e}")