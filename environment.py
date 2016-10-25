"""
This file will handle opening the java source files
so that they're easy to read for the TA, opening the
info files displaying the information contained
within so that it's convenient for the TA, and
potentially in the future compiling the source files
and checking for errors or problems with the output,
though this would likely be contained in its own
file.
"""


from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
import sys


class MainMenu(Screen):
    message = StringProperty("You will be TA-inated.")


class StudentScreen(Screen):
    code = StringProperty("")
    info = StringProperty("")
    requirements = StringProperty("")
    font_size = NumericProperty(10)


class MainFrame(ScreenManager):
    current_position = NumericProperty()

    def __init__(self, attempts=None):
        super(MainFrame, self).__init__()
        MainFrame.current_position = 0
        self.attempts = attempts
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        # content = FileChooserIconView()
        # p = Popup(title="File Manager",
        #           content=FileChooserIconView(),
        #           size_hint=(None, None), size=(400, 400))
        # content.bind(on_press=p.dismiss)
        # p.open()

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'a':
            self.previous_student()
        elif keycode[1] == 'd':
            self.next_student()
        elif keycode[1] == 'left':
            self.previous_student()
        elif keycode[1] == 'right':
            self.next_student()
        elif keycode[1] == 'escape' or keycode[1] == 'q':
            sys.exit(0)
        return True

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def load_attempts(self):
        for attempt in self.attempts:
            name = attempt.student_name
            keys = attempt.source.keys()
            code = ""
            for key in keys:
                code += "// ----- File Name: " + key + " ----- //\n" +\
                        attempt.source[key].strip().lstrip() +\
                        "\n// ----- End of file: " + key + " ----- //\n"
            code = code.strip()
            info = attempt.info.strip().lstrip()
            requirements = attempt.requirements.strip().lstrip()
            student_screen = StudentScreen(name=name,
                                           code=code,
                                           info=info,
                                           requirements=requirements)
            # self.ids.menu.message = "Submission Loaded: " + name
            self.add_widget(student_screen)
        self.ids.menu.message = "Loading complete.\nSwitching to review screen..."
        self.current = self.attempts[MainFrame.current_position].student_name

    def previous_student(self):
        self.transition.direction = 'right'
        if MainFrame.current_position > 0:
            MainFrame.current_position -= 1
            self.current = self.attempts[MainFrame.current_position].student_name

    def next_student(self):
        self.transition.direction = 'left'
        if MainFrame.current_position < len(self.attempts)-1:
            MainFrame.current_position += 1
            self.current = self.attempts[MainFrame.current_position].student_name


class TAinator(App):
    def __init__(self, attempts):
        super(TAinator, self).__init__()
        self.attempts = attempts

    def build(self):
        return MainFrame(self.attempts)
