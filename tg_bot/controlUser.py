class ControlUser:
    def __init__(self, tg_id):
        self.tg_id = tg_id
        self.button_new_fit = False
        self.number_fit = -1
        self.day = ''

    def set_button_new_fit(self):
        self.button_new_fit = not self.button_new_fit

    def get_button_new_fit(self):
        return self.button_new_fit

    def set_number_fit(self, number):
        self.number_fit = number

    def get_number_fit(self):
        return self.number_fit

    def set_day(self, day):
        self.day = day

    def get_day(self):
        return self.day

    def reboot(self):
        self.button_new_fit = False
        self.number_fit = -1
        self.day = ''