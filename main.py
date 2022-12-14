import os
import spidev
import RPi.GPIO as GPIO

from datetime import datetime
from time import sleep


#os.environ['DISPLAY'] = ":0.0"
#os.environ['KIVY_WINDOW'] = 'egl_rpi'

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.clock import Clock

from pidev.stepper import stepper
from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton


from Slush.Devices import L6470Registers

time = datetime
spi = spidev.SpiDev()

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White

s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=200, speed=2)


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    s0_rotation_direction = 0
    clock_control = 0
    position = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        """Things that are actually happening when the MainScreen class is called
        These variables are only defined here so they can be altered later.
        s0_rotation_dierction controls the rotation direction and stays between 1 and 0.
        clock_control helps control the clock, as if the_dance() has been called the variable should update
        and cancel the clock until the value is returned to 0, which the_dance function does when it is finished running
        """

        Clock.schedule_interval(self.speed_change, 0.5)
        Clock.schedule_interval(self.position_update, 0.5)
    def motor_on(self):
        if not s0.is_busy():
            s0.go_until_press(self.s0_rotation_direction, self.ids.slidervalue.value)
            print("moving!")

        else:
            s0.free()
            print("s0: I'm free!!")


    def motor_off(self):
        s0.softStop()
        s0.free()

    def position_update(self, dt):

        self.position = float(s0.get_position_in_units())

    def speed_change(self, dt):
        if self.clock_control == 0:
            if s0.is_busy():
                s0.go_until_press(self.s0_rotation_direction, self.ids.speed_slider.value)

    def motor_show(self):

        s0.free()
        s0.set_as_home()
        sleep(.1)
        self.clock_control += 1
        print(str(s0.get_position_in_units()))

        s0.start_relative_move(15)
        s0.wait_move_finish()
        print(str(s0.get_position_in_units()))

        sleep(10)
        s0.start_relative_move(10)
        print(str(s0.get_position_in_units()))

        sleep(8)
        s0.goHome()
        sleep(30)
        print(str(s0.get_position_in_units()))

        s0.start_relative_move(-100)
        print(str(s0.get_position_in_units()))

        sleep(10)
        s0.goHome()
        print(str(s0.get_position_in_units()))

        s0.free()
        self.clock_control -= 1
        print("THE END")


    def change_motor_direction(self):

        if s0.is_busy():
            if self.s0_rotation_direction == 0:
                self.s0_rotation_direction += 1
                print("Direction " + str(self.s0_rotation_direction))

            else:
                self.s0_rotation_direction -= 1
                print("Direction " + str(self.s0_rotation_direction))

            s0.go_until_press(self.s0_rotation_direction, self.ids.slidervalue.value)




class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()
