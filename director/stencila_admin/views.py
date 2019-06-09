from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from projects.session_models import Session, SessionStatus


class SessionStatusView(View):
    @method_decorator(staff_member_required)
    def get(self, request):
        sessions = Session.objects.filter_status(SessionStatus.RUNNING)
        return render(request, 'stencila-admin/session-list.html', {
            'sessions': sessions
        })
