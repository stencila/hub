from dois.api.views import DoisViewSet
from manager.api.routers import OptionalSlashRouter

dois = OptionalSlashRouter()
dois.register("dois", DoisViewSet, "api-dois")

urlpatterns = dois.urls
