from rest_framework import routers

from search import views


router = routers.SimpleRouter()
router.register("query", views.QueryViewSet)
urlpatterns = router.urls
