import time
import numpy as np
from scipy.optimize import root_scalar


COLOR = 'color'
NUMBER = 'number'


class Animator:
    def __init__(self, current_value, target_value, duration, fps, easing=None, reverse: bool = False):
        self.duration = duration
        self.fps = fps
        self._reverse = reverse
        self.wait_time = 1 / fps
        self.value_type = None

        # get value type
        if not type(current_value) == type(target_value):
            raise ValueError("current_value and target_value must be of the same type")

        if isinstance(current_value, (int, float)):
            self.current_value = current_value
            self.target_value = target_value
            self.value_type = NUMBER

        elif isinstance(current_value, str):
            if '#' in current_value:  # hex color values
                if len(current_value) == 7:
                    _, redc1, redc2, greenc1, greenc2, bluec1, bluec2 = current_value
                    _, redt1, redt2, greent1, greent2, bluet1, bluet2 = target_value
                    alphac = None
                    alphat = None
                    
                elif len(current_value) == 9:  # with alpha
                    _, redc1, redc2, greenc1, greenc2, bluec1, bluec2, alphac1, alphac2 = current_value
                    _, redt1, redt2, greent1, greent2, bluet1, bluet2, alphat1, alphat2 = target_value
                    alphac = int('0x' + alphac1 + alphac2, 16)
                    alphat = int('0x' + alphat1 + alphat2, 16)

                redc = int('0x' + redc1 + redc2, 16)
                redt = int('0x' + redt1 + redt2, 16)
                greenc = int('0x' + greenc1 + greenc2, 16)
                greent = int('0x' + greent1 + greent2, 16)
                bluec = int('0x' + bluec1 + bluec2, 16)
                bluet = int('0x' + bluet1 + bluet2, 16)

                self.current_value = [redc, greenc, bluec, alphac]
                self.target_value = [redt, greent, bluet, alphat]
                self.value_type = COLOR

            else:
                raise ValueError("The argument passed to the current_value or target_value is invalid.")

        # set easing property
        if easing is None:
            self.easing = ((0, 0), (0, 0), (0, 0), (1, 1))
        elif isinstance(easing, tuple):  # looking for curve points
            if isinstance(easing[0], tuple):
                if len(easing) == 2:
                    self.easing = ((0, 0), easing[0], easing[1], (1, 1))
                elif len(easing) == 4:
                    self.easing = (easing[0], easing[1], easing[2], easing[3])
            elif isinstance(easing[0], (str, float, int)):
                self.easing = ((0, 0), (float(easing[0]), float(easing[1])), (float(easing[2]), float(easing[3])), (1, 1))
            else:
                raise ValueError("The argument passed to the function is not valid. The valid values for the 'easing' variable are: tuple(tuple, tuple, tuple, tuple) | tuple(str|int|float, str|int|float, str|int|float, str|int|float) | tuple(tuple,tuple) | 'ease' | 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out'")
        elif isinstance(easing, str):
            if easing.lower() == 'ease':
                self.easing = ((0, 0), (0.25, 0.1), (0.25, 1), (1, 1))
            elif easing.lower() == 'linear':
                self.easing = ((0, 0), (0, 0), (1, 1), (1, 1))
            elif easing.lower() == 'ease-in':
                self.easing = ((0, 0), (.42, 0), (1, 1), (1, 1))
            elif easing.lower() == 'ease-out':
                self.easing = ((0, 0), (0, 0), (.58, 1), (1, 1))
            elif easing.lower() == 'ease-in-out':
                self.easing = ((0, 0), (.42, 0), (.58, 1), (1, 1))
            else:
                raise ValueError("The argument passed to the function is not valid. The valid values for the 'easing' variable are: tuple(tuple, tuple, tuple, tuple) | tuple(str|int|float, str|int|float, str|int|float, str|int|float) | tuple(tuple,tuple) | 'ease' | 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out'")
        else:
            raise ValueError("The argument passed to the function is not valid. The valid values for the 'easing' variable are: tuple(tuple, tuple, tuple, tuple) | tuple(str|int|float, str|int|float, str|int|float, str|int|float) | tuple(tuple,tuple) | 'ease' | 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out'")

        self.total_frames = int(duration * fps)

        self.frame_count = 0
        if self.value_type == NUMBER:
            values_to_change = self.target_value - self.current_value
            self.values = [(self._animation_value(t/self.total_frames, *self.easing) * values_to_change) + self.current_value for t in range(self.total_frames+1)]

        elif self.value_type == COLOR:
            self.values = []

            def float_to_hex(value):
                if value is None:
                    return ''
                value = str(hex(round(value)))[2:]
                if len(value) == 1:
                    value = '0' + value
                return value

            for frame in range(self.total_frames+1):
                if frame == 208:
                    pass
                values = [None] * 4
                for color in range(4):
                    if self.current_value[color] is None or self.target_value[color] is None:
                        continue
                    values_to_change = self.target_value[color] - self.current_value[color]
                    values[color] = self._animation_value(frame/self.total_frames, *self.easing) * values_to_change + self.current_value[color]
                values = '#' + float_to_hex(values[0]) + float_to_hex(values[1]) + float_to_hex(values[2]) + float_to_hex(values[3])
                self.values.append(values)

        if self._reverse:
            self.reverse()
        self.__len__()

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return self

    def __next__(self):
        if self.frame_count <= self.total_frames:
            time.sleep(self.wait_time)

            self.current_value = self.values[self.frame_count]

            self.frame_count += 1

            return self.current_value

        else:
            raise StopIteration
        
    def _return_value(self):
        pass


    def _animation_value(self, time, p0, p1, p2, p3):
        time_value = root_scalar(lambda x: self._cubic_bezier(x, p0, p1, p2, p3)[1] - time, bracket=[0, 1])
        return self._cubic_bezier(time_value.root, p0, p1, p2, p3)[0]

    def _cubic_bezier(self, t, p0, p1, p2, p3):
        t = np.array(t)

        c0 = (1 - t)**3
        c1 = 3 * (1 - t)**2 * t
        c2 = 3 * (1 - t) * t**2
        c3 = t**3

        time = p0[0] * c0 + p1[0] * c1 + p2[0] * c2 + p3[0] * c3
        value = p0[1] * c0 + p1[1] * c1 + p2[1] * c2 + p3[1] * c3

        return value, time

    def reset(self):
        self.frame_count = 0

    def reverse(self):
        self.values[::-1]


# for testing purposes
if __name__ == '__main__':
    import customtkinter
    import threading

    def show_graph():
        import matplotlib.pyplot as plt

        def ease_in(t):
            return t * t

        x_values = []
        y_values = []
        cg = .99, 0, 0, .3
        cg = (0, 0), (cg[0], cg[1]), (cg[2], cg[3]), (1, 1)
        anim = Animator(-1, -2, 1, 100, cg, True)
        for t, i in enumerate(anim):
            x_values.append(t)
            y_values.append(i)

        plt.plot(x_values, y_values)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title('Ease-In Easing Function')
        plt.show()

        quit()

    def button_action_move(reverse=False):
        if reverse: st, en = 200, 0
        else: st, en = 0, 200

        if entry.get():
            cg = entry.get().split(',')
            cg = [float(i) for i in cg]
        else:
            cg = .98, .01, .02, .98
        
        cg = (0, 0), (cg[0], cg[1]), (cg[2], cg[3]), (1, 1)
        anim = Animator(st, en, 1, 60, 'ease', False)
        for t, value in enumerate(anim):
            box.pack(padx=(value, 0))
            root.update()
        if not reverse: root.after(1500, button_action_move(True))
        quit()

    def button_action_color(reverse=False):
        c1, c2 =  '#00ff0000', '#ff001100'
        if reverse: st, en = c2, c1
        else: st, en = c1, c2
        anim = Animator(st, en, 1, 60, 'ease')
        for t, value in enumerate(anim):
            value = value[:-(len(value)-7)]
            box.configure(fg_color=value)
            root.update()
        if not reverse: root.after(1500, button_action_color(True))
        quit()

    root = customtkinter.CTk()

    entry = customtkinter.CTkEntry(root)
    entry.pack(pady=10)

    def button_action():
        threading.Thread(target=button_action_move).start()
        threading.Thread(target=button_action_color).start()

    button = customtkinter.CTkButton(root, command=button_action, text='start')
    button.pack(pady=10)

    box_frame = customtkinter.CTkFrame(root, 240, 40)
    box_frame.pack_propagate(False)
    box_frame.pack(pady=10, padx=10)

    box = customtkinter.CTkFrame(box_frame, 40, 40, fg_color='#e01a6d')
    box.pack(side='left')

    button2 = customtkinter.CTkButton(root, command=lambda: threading.Thread(target=show_graph).start())
    button2.pack(padx=10, pady=10)

    root.attributes('-topmost', True)
    root.mainloop()
