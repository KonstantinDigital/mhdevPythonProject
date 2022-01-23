import numpy as np
import cv2
import pyautogui


class Capturer:

    def __init__(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = fps
        self.vid = cv2.VideoWriter(
            'output.avi',
            cv2.VideoWriter_fourcc(*'XVID'),
            fps=self.fps,
            frameSize=(
                self.width,
                self.height
            )
        )

    def mainloop(self):
        while True:
            img = pyautogui.screenshot()
            np_arr = np.array(img)
            frame = cv2.cvtColor(
                np_arr,
                cv2.COLOR_BGR2RGB
            )

            self.vid.write(frame)


if __name__ == '__main__':
    w = int(input("Width = "))
    h = int(input("Height = "))
    fps = float(input("FPS = "))
    capt = Capturer(w, h, fps=fps)
    try:
        print('TO EXIT PRESS Ctrl+C')
        capt.mainloop()
    except KeyboardInterrupt:
        input('Successfully')
