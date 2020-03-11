from rest_framework import routers

from search import views


app_name = "search"


router = routers.SimpleRouter()
router.register("query", views.QueryViewSet)
urlpatterns = router.urls
