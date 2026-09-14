# main.py
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen

class MainScreen(Screen):
    """Logic for the main application screen goes here."""
    pass

class MainApp(MDApp):
    def build(self):
        # Configure application theming 
        self.theme_cls.theme_style = "Light"  # "Light" or "Dark"
        self.theme_cls.primary_palette = "Orange"  # Sets the dominant app color
        
        # Initialize and return the screen manager
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    MainApp().run()
