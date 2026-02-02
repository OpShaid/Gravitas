
import glfw


class MouseMap:
    

    LEFT = glfw.MOUSE_BUTTON_LEFT
    RIGHT = glfw.MOUSE_BUTTON_RIGHT
    MIDDLE = glfw.MOUSE_BUTTON_MIDDLE
    _4 = glfw.MOUSE_BUTTON_4
    _5 = glfw.MOUSE_BUTTON_5
    _6 = glfw.MOUSE_BUTTON_6
    _7 = glfw.MOUSE_BUTTON_7
    _8 = glfw.MOUSE_BUTTON_8

    PRESS = glfw.PRESS
    RELEASE = glfw.RELEASE
    REPEAT = glfw.REPEAT

    @staticmethod
    def get_button_name(button: int) -> str:
        
        button_names = {
            MouseMap.LEFT: "Left Button",
            MouseMap.RIGHT: "Right Button",
            MouseMap.MIDDLE: "Middle Button",
            MouseMap._4: "Button 4",
            MouseMap._5: "Button 5",
            MouseMap._6: "Button 6",
            MouseMap._7: "Button 7",
            MouseMap._8: "Button 8"
        }
        return button_names.get(button, "Unknown Button")

    @staticmethod
    def get_action_name(action: int) -> str:
        
        action_names = {
            MouseMap.PRESS: "Press",
            MouseMap.RELEASE: "Release",
            MouseMap.REPEAT: "Repeat"
        }
        return action_names.get(action, "Unknown Action")
