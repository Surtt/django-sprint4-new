from django.views.generic import TemplateView


class AboutPage(TemplateView):
    template_name = 'pages/about.html'
    extra_context = {'title': 'О проекте'}


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'
    extra_context = {'title': 'Наши правила'}
