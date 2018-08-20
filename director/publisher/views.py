from secrets import compare_digest
import typing

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View

from publisher.forms import SessionGroupForm, SessionTemplateForm

PUBLISHER_GROUP_NAME = 'Publisher'


def update_session_group_from_form_data(owner: typing.Optional[User], session_group: "SessionGroup",
                                        form_data: dict) -> None:
    """
    Updates a SessionGroup's attributes with data from a SessionGroupForm's cleaned_data. Assumes the form the data
    comes from has already been tested for validity.
    """

    if owner is not None:
        session_group.owner = owner
    elif session_group.owner is None:
        # owner should be None on update, so that it's not changed
        # however if it is None but owner was None before, raise Exception
        raise ValueError('SessionGroup can not have an owner that is None')

    session_group.max_sessions = form_data['max_sessions']
    session_group.max_concurrent = form_data['max_concurrent']
    session_group.template = form_data['template']

    if form_data['generate_key']:
        session_group.key = generate_project_key()
    else:
        session_group.key = form_data['key']


def session_group_initial_form_values(session_group) -> dict:
    """
    Extract values from a SessionGroup into a dictionary for initial values of SessionGroupForm. Returns empty
    dictionary if session_group is None.
    """
    if session_group is None:
        return {}

    return {
        'token': session_group.token,
        'key': session_group.key,
        'max_sessions': session_group.max_sessions,
        'max_concurrent': session_group.max_concurrent,
        'template': session_group.template
    }


class PublisherOrAdminMixin(UserPassesTestMixin):
    """A mixin that checks if a the request user is a superuser or is in the publisher group."""

    def test_func(self) -> bool:
        if self.request.user.is_superuser:
            return True

        user_groups = self.request.user.groups.values_list('name', flat=True)

        return PUBLISHER_GROUP_NAME in user_groups


class OwnerOrAdminListView(PublisherOrAdminMixin, ListView):
    paginate_by = 100

    def get_queryset(self) -> QuerySet:
        owner_kwargs = {}

        if not self.request.user.is_superuser:
            owner_kwargs['owner'] = self.request.user

        return self.model.objects.filter(**owner_kwargs).order_by('id')


class SessionGroupListView(OwnerOrAdminListView):
    model = None


T = typing.TypeVar('T')


class OwnerOrAdminView(PublisherOrAdminMixin, View):
    model: typing.Type[T]

    def get_model_instance(self, model_class: typing.Type[T], filter_kwargs: dict) -> typing.Optional[T]:
        instance = get_object_or_404(model_class, **filter_kwargs)

        if self.request.user.is_superuser:
            return instance

        if instance.owner != self.request.user:
            raise PermissionDenied

        return instance

    def get_class_model_instance_by_pk(self, pk: typing.Optional[int]) -> typing.Optional[T]:
        if pk is None:
            return None

        return self.get_model_instance(self.model, {'pk': pk})


class PublisherMainView(PublisherOrAdminMixin, View):
    def get(self, request: HttpRequest):
        return render(request, "publisher/main.html")


class SessionGroupDetail(OwnerOrAdminView):
    model = None

    @staticmethod
    def get_session_start_url(request: HttpRequest, session_group: typing.Optional):
        if session_group is None:
            return None

        return request.build_absolute_uri(reverse('session_token_start', args=(session_group.token,)))

    def get(self, request: HttpRequest, pk: typing.Optional[int] = None) -> HttpResponse:
        session_group = self.get_class_model_instance_by_pk(pk)
        form = self.get_form(session_group)

        return self.get_form_response(request, form, session_group)

    def post(self, request: HttpRequest, pk: typing.Optional[int] = None) -> HttpResponse:
        session_group = self.get_class_model_instance_by_pk(pk)
        form = self.get_form(session_group, request.POST)
        if form.is_valid():
            if session_group is None:
                new_owner = request.user
                session_group = SessionGroup()
            else:
                new_owner = None

            update_session_group_from_form_data(new_owner, session_group, form.cleaned_data)
            session_group.save()
            messages.success(request, 'Session Group Saved')
            return self.get_redirect_after_save_response()

        return self.get_form_response(request, form, session_group)

    def get_form(self, session_group: typing.Optional,
                 post_data: typing.Optional[dict] = None) -> SessionGroupForm:
        form = SessionGroupForm(post_data, initial=session_group_initial_form_values(session_group))
        form.fields['template'].queryset = SessionTemplate.objects.filter(owner=self.request.user)
        return form

    @staticmethod
    def get_redirect_after_save_response() -> HttpResponse:
        return redirect(reverse('session_group_list'))

    def get_form_response(self, request: HttpRequest, form: SessionGroupForm,
                          session_group: typing.Optional) -> HttpResponse:
        session_start_url = self.get_session_start_url(request, session_group)

        return render(request, 'publisher/sessiongroup_detail.html',
                      {'form': form, 'session_group': session_group, 'session_start_url': session_start_url})


class SessionTemplateListView(OwnerOrAdminListView):
    model = None


class SessionTemplateDetailView(OwnerOrAdminView):
    model = None

    def get(self, request: HttpRequest, pk: typing.Optional[int] = None) -> HttpResponse:
        session_template = self.get_class_model_instance_by_pk(pk)

        form = SessionTemplateForm(instance=session_template)

        return render(request, 'publisher/sessiontemplate_detail.html',
                      {'form': form, 'session_template': session_template})

    def post(self, request: HttpRequest, pk: typing.Optional[int] = None) -> HttpResponse:
        session_template = self.get_class_model_instance_by_pk(pk)

        form = SessionTemplateForm(request.POST, instance=session_template)

        if form.is_valid():
            session_template = form.save(commit=False)
            if session_template.owner is None:
                session_template.owner = request.user
            session_template.save()
            messages.success(request, 'Session Template saved.')
            return redirect(reverse('session_template_list'))

        return render(request, 'publisher/sessiontemplate_detail.html',
                      {'form': form, 'session_template': session_template})


class SessionListView(OwnerOrAdminView):
    model = None

    def get(self, request, session_group_pk: int) -> HttpResponse:
        session_group = self.get_model_instance(SessionGroup, {'pk': session_group_pk})
        return render(request, 'publisher/session_list.html',
                      {'sessions': session_group.sessions, 'session_group': session_group})


@method_decorator(csrf_exempt, name='dispatch')
class SessionStartView(View):
    def post(self, request: HttpRequest, token: str):
        session_group = get_object_or_404(SessionGroup, token=token)

        if session_group.key and not compare_digest(session_group.key, request.POST.get('key', '')):
            raise PermissionDenied

        return HttpResponse('Redirecting to session...')
