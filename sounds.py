from playsound import playsound
from os.path import isdir, exists, join

class SoundHandler:
    is_enabled = True
    sound_path = ""
    def __init__(self, sound_path:str="sound/", default_enable:bool=True):
        SoundHandler.is_enabled = default_enable
        if exists(sound_path) and isdir(sound_path):
            SoundHandler.sound_path = sound_path
            return
        raise TypeError("Hangok mappája nem találva!")
    
    @classmethod
    def play(self, sound: str):
        if SoundHandler.is_enabled:
            f = SoundHandler.sound_path + f"{sound}"
            if exists(join(SoundHandler.sound_path, f"{sound}.mp3")):
                playsound(join(SoundHandler.sound_path, f"{sound}.mp3"))

