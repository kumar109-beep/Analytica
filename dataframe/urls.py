from django.urls import path, re_path
from . views import DataframeList, DataframeDetail, Frame_edit_requestList, Frame_edit_requestDetail


# import .views
urlpatterns = [
    path('frames/',  DataframeList.as_view()),
    path('frame/<int:pk>/', DataframeDetail.as_view()),


    path('edits/',  Frame_edit_requestList.as_view()),
    path('edit/<int:pk>/', Frame_edit_requestDetail.as_view()),
]