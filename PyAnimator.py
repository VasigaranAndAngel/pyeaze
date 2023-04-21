import time
import numpy as np
from scipy.optimize import root_scalar
from pygame import time as pygame_time
from typing import Union, Tuple, Literal


_COLOR = 'color'
_NUMBER = 'number'
_STRING = 'string'


class Animator:
    def __init__(self, current_value: Union[int, float, str],
                       target_value: Union[int, float, str],
                       duration: Union[int, float],
                       fps: int,
                       easing:Union[Literal['ease', 'linear', 'ease-in', 'ease-out', 'ease-in-out'],
                                    # for ((0, 0), (0.5, 0.5), (0.6, 0.6), (1, 1))
                                    Tuple[Tuple[Union[float, int], Union[float, int]],
                                          Tuple[Union[float, int], Union[float, int]],
                                          Tuple[Union[float, int], Union[float, int]],
                                          Tuple[Union[float, int], Union[float, int]]],
                                    # for ((0.5, 0.5), (0.6, 0.6,))
                                    Tuple[Tuple[Union[float, int], Union[float, int]],
                                          Tuple[Union[float, int], Union[float, int]]],
                                    # for (0.5, 0.5, 0.6, 0.6)
                                    Tuple[Union[float, int], Union[float, int], Union[float, int], Union[float, int]], None
                                    ]=None,
                       reverse: bool = False):
        
        self.duration = duration
        self.fps = fps
        # self.wait_time = 1 / fps
        self.wait_time = int(1 / fps * 1000)
        self._reverse = reverse
        self._value_type = None

        # get values
        if isinstance(current_value, (int, float)) and isinstance(target_value, (int, float)):  # number values
            self.current_value = current_value
            self.target_value = target_value
            self.value_type = _NUMBER

        elif isinstance(current_value, str) and isinstance(target_value, str):
            if '#' == current_value[0] == target_value[0]:  # hex color values
                if len(current_value) == 7:  # without alpha
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
                self.value_type = _COLOR

            else:  # string values
                pass
        
        else:
            raise ValueError("The argument passed to the current_value or target_value is invalid.")

        # set easing property
        match easing:
            case None:
                self.easing = ((0, 0), (0, 0), (0, 0), (1, 1))
            case ((p1, p2), (p3, p4), (p5, p6), (p7, p8)):
                self.easing = ((p1, p2), (p3, p4), (p5, p6), (p7, p8))
            case ((p3, p4), (p5, p6)) | (p3, p4, p5, p6):
                self.easing = ((0, 0), (p3, p4), (p5, p6), (1, 1))
            case 'ease':
                self.easing = ((0, 0), (0.25, 0.1), (0.25, 1), (1, 1))
            case 'linear':
                self.easing = ((0, 0), (0, 0), (1, 1), (1, 1))
            case 'ease-in':
                self.easing = ((0, 0), (.42, 0), (1, 1), (1, 1))
            case 'ease-out':
                self.easing = ((0, 0), (0, 0), (.58, 1), (1, 1))
            case 'ease-in-out':
                self.easing = ((0, 0), (.42, 0), (.58, 1), (1, 1))
            case _:
                raise ValueError(f"Invalid easing type: {easing}.")

        self.total_frames = int(duration * fps)

        self.frame_count = 0
        if self.value_type is _NUMBER:
            values_to_change = self.target_value - self.current_value
            self.values = [(self._animation_value(t/self.total_frames, *self.easing) * values_to_change) + self.current_value for t in range(self.total_frames+1)]

        elif self.value_type is _COLOR:
            self.values = []

            def float_to_hex(value):
                if value is None:
                    return ''
                value = str(hex(round(value)))[2:]
                if len(value) == 1:
                    value = '0' + value
                return value

            for frame in range(self.total_frames+1):
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

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return self

    def __next__(self):
        self.frame_count += 1
        if self.frame_count <= self.total_frames:
            # time.sleep(self.wait_time)
            # s = time.monotonic()
            # while time.monotonic() - s < self.wait_time: time.sleep(self.wait_time/4)
            pygame_time.wait(self.wait_time)
            # pygame_time.delay(int(self.wait_time*1000))
            # pygame_time.Clock().tick(self.fps)
            self.current_value = self.values[self.frame_count]
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
