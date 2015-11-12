from django.contrib import admin

from users.models import UserDetails, UserToken


class UserDetailsAdmin(admin.ModelAdmin):

    list_display = ('id',)

admin.site.register(UserDetails, UserDetailsAdmin)


class UserTokenAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'issued', 'expires')

admin.site.register(UserToken, UserTokenAdmin)
