import numpy as np
import cv2
import pyautogui


class Capturer:

    def __init__(self, width, height, fps, resolution='1080p'):
        if resolution == '1080p':
            self.monitor = {
                'top': 1080 - height,
                'left': 1920 - width,
                'width': width,
                'height': height
            }

        elif resolution == '1440p':
            self.monitor = {
                'top': 1440 - height,
                'left': 2560 - width,
                'width': width,
                'height': height
            }

        else:
            raise ValueError('Unsupported monitor resolution')
        self.vid = cv2.VideoWriter(
            'output.avi',
            cv2.VideoWriter_fourcc(*'XVID'),
            fps=fps,
            frameSize=(
                self.monitor['width'],
                self.monitor['height']
            )
        )

    def mainloop(self):
        while True:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(
                np.array(img),
                cv2.COLOR_BGR2RGB
            )
            self.vid.write(frame)


if __name__ == '__main__':
    w = int(input("Width = "))
    h = int(input("Height = "))
    capt = Capturer(w, h, 20.0)
    try:
        print('TO EXIT PRESS Ctrl+C')
        capt.mainloop()
    except KeyboardInterrupt:
        input('Successfully')
