import pyautogui
from PIL import Image
import io
import base64
import time
import platform
from datetime import datetime

# copy from https://github.com/suitedaces/computer-agent
class ComputerControl:

    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        pyautogui.PAUSE = 0.5
        self.last_click_position = None

    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        # resize
        screenshot = screenshot.resize((1000, 1000), Image.LANCZOS)

        # save
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG") 
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def map_from_ai_space(self, x, y):
        ai_width, ai_height = 1000, 1000
        return (x * self.screen_width / ai_width, y * self.screen_height / ai_height)
    
    def map_to_ai_space(self, x, y):
        ai_width, ai_height = 1000, 1000
        return (x * ai_width / self.screen_width, y * ai_height / self.screen_height)
    
    def action(self, action):
        action_type = action['action']

        if action_type == 'click':
            x, y = self.map_from_ai_space(action["start_box"][0], action["start_box"][1])
            # pyautogui.moveTo(x, y)
            # time.sleep(0.2)  # Wait for move to complete
            pyautogui.click(x, y)
            time.sleep(0.2)
            # pyautogui.click()

        elif action_type == 'type':
            print(f"Typing content: {action['content']}")
            pyautogui.write(action['content'], interval=0.1)
            time.sleep(0.2)

        elif action_type == 'hotkey':
            pyautogui.click()   # Ensure the window is focused
            time.sleep(0.2)
            convert_keys = []
            for key in action['key'].split():
                if key == 'space':
                    key = ' '
                elif key == 'ctrl' and platform.system() == "Darwin":
                    key = 'command'  # macOS uses 'command' instead of 'ctrl'
                convert_keys.append(key)
            pyautogui.hotkey(convert_keys)
            time.sleep(0.2)

        elif action_type == 'wait':
            time.sleep(2)
        
        elif action_type == 'left_double':
            x, y = self.map_from_ai_space(action["start_box"][0], action["start_box"][1])
            pyautogui.doubleClick(x, y)
            time.sleep(0.2)

        elif action_type == 'right_single':
            x, y = self.map_from_ai_space(action["start_box"][0], action["start_box"][1])
            pyautogui.moveTo(x, y)
            time.sleep(0.2)  # Wait for move to complete
            pyautogui.rightClick()
            time.sleep(0.2)

        elif action_type == 'drag':
            start_x, start_y = self.map_from_ai_space(action["start_box"][0], action["start_box"][1])
            end_x, end_y = self.map_from_ai_space(action["end_box"][0], action["end_box"][1])
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, button='left', duration=0.5)
            time.sleep(0.2)
        else:
            raise Exception(action_type)
