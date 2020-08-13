# Generated by Django 2.2.7 on 2020-01-21 21:17

from django.db import migrations, IntegrityError, transaction
from django.utils.text import slugify


def set_slugs_from_name(apps, schema):
    Account = apps.get_model('accounts', 'Account')

    for account in Account.objects.filter(slug__isnull=True) | Account.objects.filter(slug=''):
        if account.name:
            slug = slugify(account.name)[:50]
        else:
            slug = 'account-{}'.format(account.pk)

        generated_slug = slug

        slug_number = 2

        while True:
            if slug_number == 100:
                raise RuntimeError(
                    '{} iterations of trying to generate a slug for Account {}'.format(slug_number, account.pk))

            account.slug = slug
            try:
                with transaction.atomic():
                    account.save()
                break
            except IntegrityError:
                slug = '{}-{}'.format(generated_slug, slug_number)
                slug_number += 1


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0011_auto_20200107_1723'),
    ]

    operations = [
        migrations.RunPython(set_slugs_from_name),
    ]