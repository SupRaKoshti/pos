from django.views.generic import TemplateView

class FrontendAppView(TemplateView):
    template_name = "index.html"

    def get_template_names(self):
        return [self.template_name]
