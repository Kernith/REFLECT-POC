from gui.pyqt6.pages.observation.base_observation_page import BaseObservationPage
from gui.pyqt6.pages.observation.components.button_behaviors import ClickButtonBehavior

class ObservationTimepointPage(BaseObservationPage):
    def __init__(self, switch_page, app_state):
        super().__init__(switch_page, app_state)

    def get_button_behavior(self):
        """Return click button behavior for timepoint observations"""
        return ClickButtonBehavior()
