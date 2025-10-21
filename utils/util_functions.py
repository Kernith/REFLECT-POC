import time
import os, sys


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_current_time(self):
        current_time = time.time() - self.start_time
        return round(current_time, 1)
