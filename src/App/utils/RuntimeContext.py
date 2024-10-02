from collections import UserDict


class RuntimeContext(UserDict):

    def init_app(self, app):
        if len(self.data) > 0:
            raise RuntimeError("Cannot call `init_app()' more than once.")

        for key, val in app.config.items():
            self.data[key] = val
