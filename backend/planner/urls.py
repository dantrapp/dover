from django.urls import path

from planner.views import api_root_view, options_view, planner_view

urlpatterns = [
    path('', api_root_view, name='planner-api-root'),
    path('options/', options_view, name='planner-options'),
    path('planner/', planner_view, name='planner-view'),
]
