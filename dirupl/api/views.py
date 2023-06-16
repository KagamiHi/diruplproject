from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.renderers import JSONRenderer

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from braces.views import CsrfExemptMixin

from dirupl.address_directory.models import Guildinfo
from dirupl.address_directory.serializers import GuildinfoSerializer


class ServersSettingsApi(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    renderer_classes = [JSONRenderer]


    def get(self, request, format=None):
        guilds = Guildinfo.objects.select_related('server', 'notification_settings').filter(members=request.user).all()
        guildserializer = GuildinfoSerializer(instance=guilds, many=True)
        return Response(guildserializer.data)
    
    
    def post(self, request, *args, **kwargs):
        data = request.data
        guild = Guildinfo.objects.select_related('server', 'notification_settings').filter(members=request.user).get(id=data['guildinfo'])
        if not guild:
            return HttpResponse(status=204)
        settings = guild.notification_settings
        if data['setting_type'] == 'esl':
            settings.event_show_location = not settings.event_show_location
        elif data['setting_type'] == 'esd':
            settings.event_show_distance = not settings.event_show_distance
        elif data['setting_type'] == 'vsl':
            settings.vend_show_location = not settings.vend_show_location
        elif data['setting_type'] == 'vsd':
            settings.vend_show_distance = not settings.vend_show_distance
        settings.save()
        return HttpResponse(status=204)
    

    

