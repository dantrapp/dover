from django.urls import path

from planner.views import options_view, planner_view

urlpatterns = [
    path('options/', options_view, name='planner-options'),
    path('planner/', planner_view, name='planner-view'),
]
