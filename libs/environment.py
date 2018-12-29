# __author__ = itsneo1990
import os


class ENV(object):
    def __init__(self):
        env = os.environ.get("oa_env", "local")
        file_name = env + "_settings"
        base_settings = __import__("ldap_server", fromlist=[file_name])
        self.settings = getattr(base_settings, file_name)

    def get_config(self, value):
        return getattr(self.settings, value)
