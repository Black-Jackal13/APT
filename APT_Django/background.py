import time
from .toolbox.update_tools import full_refresh


def full_update_and_refresh():
    while True:
        print("Refreshing and Updating Server...")
        full_refresh()
        time.sleep(300)  # 5 minutes between updates.
