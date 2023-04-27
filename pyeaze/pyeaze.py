import time
try: from pygame import time as pygame_time
except ImportError: pass

import numpy
from scipy.optimize import root_scalar, _zeros_py
from typing import Union, Tuple, Literal, List, Any


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
                       reverse: bool = False,
                       accurate_duration: bool = False,):
        
        self.duration = duration
        self.fps = fps
        self.wait_time = round(1 / fps, 4)
        # self.wait_time = int(1 / fps * 1000)  # converted to milliseconds
        self._reverse = reverse
        self._value_type = None
        self._animators: List[Animator] = []
        self._accurate_duration = accurate_duration

        # store values
        if isinstance(current_value, (int, float)) and isinstance(target_value, (int, float)):  # number values
            self.current_value = current_value
            self.target_value = target_value
            self._value_type = _NUMBER

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
                self._value_type = _COLOR

            else:  # string values
                pass
        
        else:
            raise ValueError("The argument passed to the current_value or target_value is invalid.")

        # set easing property
        match easing:
            case ((p1, p2), (p3, p4), (p5, p6), (p7, p8)):
                self.easing = ((p1, p2), (p3, p4), (p5, p6), (p7, p8))
            case ((p3, p4), (p5, p6)) | (p3, p4, p5, p6):
                self.easing = ((0, 0), (p3, p4), (p5, p6), (1, 1))
            case 'ease':
                self.easing = ((0, 0), (0.25, 0.1), (0.25, 1), (1, 1))
            case 'linear' | None:
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

        if self._value_type is _NUMBER:
            values_to_change = self.target_value - self.current_value
            self.values = [(self._animation_value(t/self.total_frames, *self.easing) * values_to_change) + self.current_value for t in range(self.total_frames+1)]
            values_to_change = self.current_value - self.target_value
            self._reversed_values = [(self._animation_value(t/self.total_frames, *self.easing) * values_to_change) + self.target_value for t in range(self.total_frames+1)]

        elif self._value_type is _COLOR:
            self.values = []
            self._reversed_values = []

            def float_to_hex(value):
                if value is None:
                    return ''
                value = str(hex(round(value)))[2:]
                if len(value) == 1:
                    value = '0' + value
                return value

            for frame in range(self.total_frames+1):
                values = [None] * 4
                r_values = [None] * 4 # for reversed values
                for color in range(4):
                    if self.current_value[color] is None or self.target_value[color] is None:
                        continue
                    values_to_change = self.target_value[color] - self.current_value[color]
                    values[color] = self._animation_value(frame/self.total_frames, *self.easing) * values_to_change + self.current_value[color]
                    values_to_change = self.current_value[color] - self.target_value[color]
                    r_values[color] = self._animation_value(frame/self.total_frames, *self.easing) * values_to_change + self.target_value[color]

                values = '#' + float_to_hex(values[0]) + float_to_hex(values[1]) + float_to_hex(values[2]) + float_to_hex(values[3])
                r_values = '#' + float_to_hex(r_values[0]) + float_to_hex(r_values[1]) + float_to_hex(r_values[2]) + float_to_hex(r_values[3])

                self.values.append(values)
                self._reversed_values.append(r_values)

        if self._reverse:
            self.reverse()

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return self

    def __next__(self) -> Union[Union[int, float, str], List[Union[int, float, str]]]:
        self.frame_count += 1
        if self.frame_count <= self.total_frames:
            if self._accurate_duration:
                s = time.time()
                while time.time() - s < self.wait_time: pass
            else:
                time.sleep(self.wait_time)
            # s = time.monotonic()
            # while time.monotonic() - s < self.wait_time: time.sleep(self.wait_time/4)  # uses seconds
            # pygame_time.wait(self.wait_time)  # uses milliseconds
            # pygame_time.delay(int(self.wait_time*1000))  # uses milliseconds
            # pygame_time.Clock().tick(self.fps)
            self.current_value = self.values[self.frame_count]

            if self._animators:
                self.current_value = [self.current_value]
                for animator in self._animators:
                    self.current_value.append(animator.values[self.frame_count])
                    
            return self.current_value
        else:
            raise StopIteration
        
    def _animation_value(self, time, p0, p1, p2, p3) -> float:
        time_value: _zeros_py.RootResults = root_scalar(lambda x: self._cubic_bezier(x, p0, p1, p2, p3)[1] - time, bracket=[0, 1])
        return self._cubic_bezier(time_value.root, p0, p1, p2, p3)[0]

    def _cubic_bezier(self, t, p0, p1, p2, p3) -> Tuple[float]:
        t = numpy.array(t)

        c0 = (1 - t)**3
        c1 = 3 * (1 - t)**2 * t
        c2 = 3 * (1 - t) * t**2
        c3 = t**3

        time = p0[0] * c0 + p1[0] * c1 + p2[0] * c2 + p3[0] * c3
        value = p0[1] * c0 + p1[1] * c1 + p2[1] * c2 + p3[1] * c3

        return float(value), float(time)

    def reset(self) -> None:
        self.frame_count = 0

    def reverse(self) -> None:
        self.values, self._reversed_values = self._reversed_values, self.values
        for animator in self._animators:
            animator.reverse()

    def add_animator(self, current_value: Union[int, float, str],
                       target_value: Union[int, float, str],
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
        animator = Animator(current_value, target_value, self.duration, self.fps, easing, reverse)
        self._animators.append(animator)
        return animator

    def accurate_duration(self, state: bool = True):
        self._accurate_duration = state