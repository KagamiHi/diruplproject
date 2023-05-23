from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status
from rest_framework.response import Response

class SpaView(LoginRequiredMixin, TemplateView):
    template_name = "spa/index.html"

