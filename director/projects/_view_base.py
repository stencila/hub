import typing

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

T = typing.TypeVar('T')


def owner_access_check(request: HttpRequest, instance: typing.Any, ownership_attribute: str = "owner"):
    """
    Check if request user has access to an object (1request.user == instance.<ownership_attribute>`, assume staff users
    are allowed to access any instnce.
    ."""
    if request.user.is_staff:
        return True

    return getattr(instance, ownership_attribute, None) == request.user


class DetailView(View):
    model: typing.Type[T]
    create_form_class: typing.Type[forms.Form]
    edit_form_class: typing.Type[forms.Form]
    is_model_form: bool = False
    template: str
    save_redirect_reverse: str
    model_name = 'Item'

    def check_instance_ownership(self, instance: T) -> None:
        """Subclasses should override this to raise exceptions if the ownership is not correct."""
        pass

    def get_instance(self, pk: typing.Optional[int]) -> typing.Optional[T]:
        """
        Fetch an instance of `model` using its pk, and perfom the instance ownership check.
        Returns None is pk is None, raises 404 exception is instance is not found. The check_instance_ownership may
        raise other exceptions.
        """
        if pk is None:
            return None

        instance = get_object_or_404(self.model, pk=pk)

        self.check_instance_ownership(instance)

        return instance

    def get_initial_instance(self, request: HttpRequest) -> T:
        """
        If creating a new instance, the subclass can override this to change the default values when creating the
        instance.
        """
        return self.model()

    def get_form_initial(self, request: HttpRequest, instance: typing.Optional[T] = None) -> typing.Optional[dict]:
        """
        Gets the initial value of a form, from an optional instance.
        """
        return None

    def get_create_form(self, data: typing.Optional[QueryDict] = None,
                        instance: typing.Optional[T] = None) -> forms.Form:
        if self.is_model_form:
            return self.create_form_class(data, instance=instance)
        else:
            return self.create_form_class(data)

    def get_edit_form(self, data: typing.Optional[QueryDict] = None, initial: typing.Optional[dict] = None,
                      instance: typing.Optional[T] = None):
        if self.is_model_form:
            return self.edit_form_class(data, initial=initial, instance=instance)
        else:
            return self.edit_form_class(data, initial=initial)

    def form_post_create(self, request: HttpRequest, form: forms.Form) -> None:
        """Called after the Form is instantiated, so subclasses can perform other setup operations on the Form."""
        pass

    def update_and_save_instance(self, instance: T, form: forms.Form):
        """Update the instance with the form data and save it, subclasses must implement this."""
        raise NotImplementedError("Subclasses must implement update_and_save_instance.")

    def get_post_save_redirect_url(self, instance: T, was_create: bool) -> str:
        """
        Subclasses may override this to change the behaviour, for example, to redirect to the instance detail view after
        create.
        """
        return reverse(self.save_redirect_reverse)

    def get(self, request: HttpRequest, pk: typing.Optional[int] = None) -> HttpResponse:
        instance = self.get_instance(pk)

        if pk is None:
            form = self.get_create_form()
        else:
            form = self.get_edit_form(initial=self.get_form_initial(request, instance), instance=instance)

        self.form_post_create(request, form)

        return render(request, self.template, {"form": form, "object": instance})

    def post(self, request: HttpRequest, pk: typing.Optional[int] = None) -> HttpResponse:
        instance = self.get_instance(pk)

        if instance is None:
            instance = self.get_initial_instance(request)

        if pk is None:
            form = self.get_create_form(data=request.POST, instance=instance)
        else:
            form = self.get_edit_form(data=request.POST, initial=self.get_form_initial(request, instance),
                                      instance=instance)

        self.form_post_create(request, form)

        if form.is_valid():
            self.update_and_save_instance(instance, form)
            action = "created" if pk is None else "updated"
            messages.success(request, "{} was {}.".format(self.model_name, action))
            return redirect(self.get_post_save_redirect_url(instance, pk is None))

        return render(request, self.template, {"form": form, "object": instance})
