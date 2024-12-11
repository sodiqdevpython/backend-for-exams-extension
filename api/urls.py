from django.urls import path
from .views import FindBestMatchAPIView

urlpatterns = [
	path('find-match/', FindBestMatchAPIView.as_view())
]
