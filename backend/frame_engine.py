import settings
import backend.constants as const


# -----------------------------------------------------------------------------
# This class loads html files from the "template" directory and formats them using Python.
# If you are unsure how this is working, just


class FrameEngine:
    def __init__(self,
                 template_path=settings.TEMPLATE_FILE,
                 template_extension=".html",
                 **kwargs):
        self.template_path = template_path
        self.template_extension = template_extension
        self.global_renders = kwargs

    def load_template(self, filename):
        path = self.template_path + filename + self.template_extension
        text = ""
        with open(path) as f:
            for line in f:
                text += line
        return text

    @staticmethod
    def simple_render(template, **kwargs):
        template = template.format(**kwargs)
        return template

    def render(self, template, **kwargs):
        keys = {**self.global_renders, **kwargs}
        keys.update(kwargs)
        template = self.simple_render(template, **keys)
        return template

    def load_and_render(self, filename, header="header", header_buttons=const.LOGIN_HEAD + const.REGISTER_HEAD,
                        tailer="tailer", **kwargs):
        main_template = self.load_template(filename)
        header_template = self.load_template(header)
        rendered_main = self.render(main_template, **kwargs)
        rendered_header = self.simple_render(header_template, buttons=header_buttons)
        rendered_template = rendered_header + rendered_main + self.load_template(tailer)
        return rendered_template
