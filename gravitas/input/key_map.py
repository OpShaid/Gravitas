
import glfw


class KeyMap:
    

    UNKNOWN = -1
    SPACE = glfw.KEY_SPACE
    APOSTROPHE = glfw.KEY_APOSTROPHE
    COMMA = glfw.KEY_COMMA
    MINUS = glfw.KEY_MINUS
    PERIOD = glfw.KEY_PERIOD
    SLASH = glfw.KEY_SLASH
    SEMICOLON = glfw.KEY_SEMICOLON
    EQUAL = glfw.KEY_EQUAL

    _0 = glfw.KEY_0
    _1 = glfw.KEY_1
    _2 = glfw.KEY_2
    _3 = glfw.KEY_3
    _4 = glfw.KEY_4
    _5 = glfw.KEY_5
    _6 = glfw.KEY_6
    _7 = glfw.KEY_7
    _8 = glfw.KEY_8
    _9 = glfw.KEY_9

    A = glfw.KEY_A
    B = glfw.KEY_B
    C = glfw.KEY_C
    D = glfw.KEY_D
    E = glfw.KEY_E
    F = glfw.KEY_F
    G = glfw.KEY_G
    H = glfw.KEY_H
    I = glfw.KEY_I
    J = glfw.KEY_J
    K = glfw.KEY_K
    L = glfw.KEY_L
    M = glfw.KEY_M
    N = glfw.KEY_N
    O = glfw.KEY_O
    P = glfw.KEY_P
    Q = glfw.KEY_Q
    R = glfw.KEY_R
    S = glfw.KEY_S
    T = glfw.KEY_T
    U = glfw.KEY_U
    V = glfw.KEY_V
    W = glfw.KEY_W
    X = glfw.KEY_X
    Y = glfw.KEY_Y
    Z = glfw.KEY_Z

    F1 = glfw.KEY_F1
    F2 = glfw.KEY_F2
    F3 = glfw.KEY_F3
    F4 = glfw.KEY_F4
    F5 = glfw.KEY_F5
    F6 = glfw.KEY_F6
    F7 = glfw.KEY_F7
    F8 = glfw.KEY_F8
    F9 = glfw.KEY_F9
    F10 = glfw.KEY_F10
    F11 = glfw.KEY_F11
    F12 = glfw.KEY_F12

    UP = glfw.KEY_UP
    DOWN = glfw.KEY_DOWN
    LEFT = glfw.KEY_LEFT
    RIGHT = glfw.KEY_RIGHT

    LEFT_SHIFT = glfw.KEY_LEFT_SHIFT
    RIGHT_SHIFT = glfw.KEY_RIGHT_SHIFT
    LEFT_CONTROL = glfw.KEY_LEFT_CONTROL
    RIGHT_CONTROL = glfw.KEY_RIGHT_CONTROL
    LEFT_ALT = glfw.KEY_LEFT_ALT
    RIGHT_ALT = glfw.KEY_RIGHT_ALT
    LEFT_SUPER = glfw.KEY_LEFT_SUPER
    RIGHT_SUPER = glfw.KEY_RIGHT_SUPER
    TAB = glfw.KEY_TAB
    ENTER = glfw.KEY_ENTER
    BACKSPACE = glfw.KEY_BACKSPACE
    INSERT = glfw.KEY_INSERT
    DELETE = glfw.KEY_DELETE
    PAGE_UP = glfw.KEY_PAGE_UP
    PAGE_DOWN = glfw.KEY_PAGE_DOWN
    HOME = glfw.KEY_HOME
    END = glfw.KEY_END
    CAPS_LOCK = glfw.KEY_CAPS_LOCK
    SCROLL_LOCK = glfw.KEY_SCROLL_LOCK
    NUM_LOCK = glfw.KEY_NUM_LOCK
    PRINT_SCREEN = glfw.KEY_PRINT_SCREEN
    PAUSE = glfw.KEY_PAUSE
    ESCAPE = glfw.KEY_ESCAPE

    KP_0 = glfw.KEY_KP_0
    KP_1 = glfw.KEY_KP_1
    KP_2 = glfw.KEY_KP_2
    KP_3 = glfw.KEY_KP_3
    KP_4 = glfw.KEY_KP_4
    KP_5 = glfw.KEY_KP_5
    KP_6 = glfw.KEY_KP_6
    KP_7 = glfw.KEY_KP_7
    KP_8 = glfw.KEY_KP_8
    KP_9 = glfw.KEY_KP_9
    KP_DECIMAL = glfw.KEY_KP_DECIMAL
    KP_DIVIDE = glfw.KEY_KP_DIVIDE
    KP_MULTIPLY = glfw.KEY_KP_MULTIPLY
    KP_SUBTRACT = glfw.KEY_KP_SUBTRACT
    KP_ADD = glfw.KEY_KP_ADD
    KP_ENTER = glfw.KEY_KP_ENTER
    KP_EQUAL = glfw.KEY_KP_EQUAL

    MOD_SHIFT = glfw.MOD_SHIFT
    MOD_CONTROL = glfw.MOD_CONTROL
    MOD_ALT = glfw.MOD_ALT
    MOD_SUPER = glfw.MOD_SUPER

    @staticmethod
    def get_key_name(key: int) -> str:
        
        key_names = {
            KeyMap.SPACE: "Space",
            KeyMap.APOSTROPHE: "'",
            KeyMap.COMMA: ",",
            KeyMap.MINUS: "-",
            KeyMap.PERIOD: ".",
            KeyMap.SLASH: "/",
            KeyMap.SEMICOLON: ";",
            KeyMap.EQUAL: "=",
            KeyMap._0: "0",
            KeyMap._1: "1",
            KeyMap._2: "2",
            KeyMap._3: "3",
            KeyMap._4: "4",
            KeyMap._5: "5",
            KeyMap._6: "6",
            KeyMap._7: "7",
            KeyMap._8: "8",
            KeyMap._9: "9",
            KeyMap.A: "A",
            KeyMap.B: "B",
            KeyMap.C: "C",
            KeyMap.D: "D",
            KeyMap.E: "E",
            KeyMap.F: "F",
            KeyMap.G: "G",
            KeyMap.H: "H",
            KeyMap.I: "I",
            KeyMap.J: "J",
            KeyMap.K: "K",
            KeyMap.L: "L",
            KeyMap.M: "M",
            KeyMap.N: "N",
            KeyMap.O: "O",
            KeyMap.P: "P",
            KeyMap.Q: "Q",
            KeyMap.R: "R",
            KeyMap.S: "S",
            KeyMap.T: "T",
            KeyMap.U: "U",
            KeyMap.V: "V",
            KeyMap.W: "W",
            KeyMap.X: "X",
            KeyMap.Y: "Y",
            KeyMap.Z: "Z",
            KeyMap.F1: "F1",
            KeyMap.F2: "F2",
            KeyMap.F3: "F3",
            KeyMap.F4: "F4",
            KeyMap.F5: "F5",
            KeyMap.F6: "F6",
            KeyMap.F7: "F7",
            KeyMap.F8: "F8",
            KeyMap.F9: "F9",
            KeyMap.F10: "F10",
            KeyMap.F11: "F11",
            KeyMap.F12: "F12",
            KeyMap.UP: "Up",
            KeyMap.DOWN: "Down",
            KeyMap.LEFT: "Left",
            KeyMap.RIGHT: "Right",
            KeyMap.LEFT_SHIFT: "Left Shift",
            KeyMap.RIGHT_SHIFT: "Right Shift",
            KeyMap.LEFT_CONTROL: "Left Control",
            KeyMap.RIGHT_CONTROL: "Right Control",
            KeyMap.LEFT_ALT: "Left Alt",
            KeyMap.RIGHT_ALT: "Right Alt",
            KeyMap.LEFT_SUPER: "Left Super",
            KeyMap.RIGHT_SUPER: "Right Super",
            KeyMap.TAB: "Tab",
            KeyMap.ENTER: "Enter",
            KeyMap.BACKSPACE: "Backspace",
            KeyMap.INSERT: "Insert",
            KeyMap.DELETE: "Delete",
            KeyMap.PAGE_UP: "Page Up",
            KeyMap.PAGE_DOWN: "Page Down",
            KeyMap.HOME: "Home",
            KeyMap.END: "End",
            KeyMap.CAPS_LOCK: "Caps Lock",
            KeyMap.SCROLL_LOCK: "Scroll Lock",
            KeyMap.NUM_LOCK: "Num Lock",
            KeyMap.PRINT_SCREEN: "Print Screen",
            KeyMap.PAUSE: "Pause",
            KeyMap.ESCAPE: "Escape",
            KeyMap.KP_0: "Keypad 0",
            KeyMap.KP_1: "Keypad 1",
            KeyMap.KP_2: "Keypad 2",
            KeyMap.KP_3: "Keypad 3",
            KeyMap.KP_4: "Keypad 4",
            KeyMap.KP_5: "Keypad 5",
            KeyMap.KP_6: "Keypad 6",
            KeyMap.KP_7: "Keypad 7",
            KeyMap.KP_8: "Keypad 8",
            KeyMap.KP_9: "Keypad 9",
            KeyMap.KP_DECIMAL: "Keypad Decimal",
            KeyMap.KP_DIVIDE: "Keypad Divide",
            KeyMap.KP_MULTIPLY: "Keypad Multiply",
            KeyMap.KP_SUBTRACT: "Keypad Subtract",
            KeyMap.KP_ADD: "Keypad Add",
            KeyMap.KP_ENTER: "Keypad Enter",
            KeyMap.KP_EQUAL: "Keypad Equal"
        }
        return key_names.get(key, "Unknown")
