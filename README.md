# **pyeaze**

**pyeaze** is a Python package for animating values with easing functions. It supports float, int, and hex color values (specified as strings), and can animate multiple values at the same time.

# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pyeaze.

```bash
pip install pyeaze
```

# Usage

Animating single value,
```python
import pyeaze

anim = Animator(current_value=0, target_value=100, duration=1, fps=60, easing='ease', reverse=False)

for value in anim:
    print(value)
```

Animating multiple values,
```python
anim.add_animator(current_value='#e01a6d', target_value='#ffffff', easing='ease')
anim.add_animator(current_value='#006effff', target_value='#ffffff00', easing='ease')

for value, color1, color2 in anim:
    print(value, color1, color2)
```

## Arguments
| Parameters  | Type | Description |
| ---------: | :--------- | --------- |
| current_value | `int` \| `float` \| `str` | The initial value to start the animation from. |
| target_value | `int` \| `float` \| `str` | The value to animate towards. |
| duration | `float` | The duration of the animation in seconds. |
| fps | `int` | The number of frames per second to use when animating. |
| easing | `str` \| [points](#easing-functions) | The easing function to use when animating. Look [here](#easing-functions) for more details. |
| reverse | `bool` | Reverse the direction of the animation. but will use the same easing function. |
| accurate_duration | `bool` | Method makes the duration of each frame little more accurately, but uses more resources. |

## Additional Methods

Animator also includes the following methods:

| Methods  | Description |
| --------- | --------- |
| `.reset()` | The `reset()` method resets the frame count, so the animation starts from the beginning.
| `.reverse()` | The `reverse()` method reverses the direction of the animation.
| `.accurate_duration(True)` | The `accurate_duration()` method makes the duration of each frame little more accurately, but uses more resources.

# Easing Functions
Animator uses cubic Bezier curves to define the easing function used during the animation.

Easing should be one of these options. `"linear"`, `"ease-in"`, `"ease-out"`, `"ease-in-out"` or points.

## Cubic Bezier **points**

| Predefined Easing | cubic bezier points |
| ---------: | --------- |
| ease | ((0, 0), (0.25, 0.1), (0.25, 1), (1, 1)) |
| linear | ((0, 0), (0, 0), (1, 1), (1, 1)) |
| ease-in | ((0, 0), (.42, 0), (1, 1), (1, 1)) |
| ease-out | ((0, 0), (0, 0), (.58, 1), (1, 1)) |
| ease-in-out | ((0, 0), (.42, 0), (.58, 1), (1, 1)) |

Cubic Bezier curves are a type of mathematical curve that are commonly used in computer graphics to define the shape of a curve between two points.

The easing function in Animator is defined by four control points that specify the shape of the curve. The first and last control points are fixed and represent the start and end points of the animation. The second and third control points are adjustable and determine the shape of the curve between the start and end points.

By default, Animator uses a pre-defined set of cubic Bezier curves to provide a range of built-in easing functions that can be selected using a string parameter. These easing functions include options like "linear", "ease-in", "ease-out", and "ease-in-out".

Alternatively, you can also define your own custom easing functions using points.

By using cubic Bezier easing functions, Animator provides a flexible and powerful way to customize the animation's timing and transition effects.

# Timing
Because of some limitations `time.sleep` is not precise enough for smooth animations. I have tried some approaches to make this better. but no luck 😔. If anyone have any better ideas, please feel free to contribute. it's appreciate 💝.

Additionally, Animator provides an `accurate_duration` parameter that can help to improve the accuracy of the animation's timing. However, as you noted, this may come at the cost of additional system resources and may not be entirely precise in all cases.

# Contributing
I'm having trouble with the timing. The `time.sleep` function is not accurate enough for smooth transitions. Is there a better way to control the frame rate and the duration of each frame?

Pull requests are welcome. For significant changes, please open an issue first
to discuss what you would like to change.

# License

[MIT](https://choosealicense.com/licenses/mit/)