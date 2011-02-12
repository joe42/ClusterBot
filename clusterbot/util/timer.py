import time

class Timer():
    def __init__(self, duration=0):
        self.refreshTimer(duration)
    def refreshTimer(self, duration):
        self.duration = duration;
        self.timeStamp = time.time(); 
    def rings(self):
        return self.timeStamp + self.duration < time.time();
