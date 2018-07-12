from django.db.models import (
    Model, ForeignKey,
    TextField,
    CASCADE, SET_NULL
)

class Checkout(Model):
    """
    A checkout of a project using a particular editor and
    execution host (if any).
    """

    #project = ForeignKey(
    #    'projects.Project',
    #    null=True,
    #    on_delete=SET_NULL
    #)

    #editor = ForeignKey(
    #    'editors.Editor',
    #    null=True,
    #    on_delete=SET_NULL
    #)

    #host

    creator = ForeignKey(
        'auth.User',
        null=True,  # Should only be null if the creator is deleted
        on_delete=SET_NULL,
        editable=False,
        related_name='checkouts_created',
        help_text='User who created the checkout'
    )

    #created_at

    #def __str__(self):
    #    return self.address if self.address else 'Checkout #{}'.format(self.id)

    def event(self, message, data=None):
        CheckoutEvent.objects.create(
            checkout=self,
            message=message
        )

    def launch(self):
        self.event('Foo')
        self.event('Bar')


class CheckoutEvent(Model):
    """
    A project
    """

    checkout = ForeignKey(
        Checkout,
        on_delete=CASCADE,
        related_name='events',
        help_text='Checkout that this event relates to'
    )

    # datetime
    
    message = TextField(

    )
    
    # data - json dict
