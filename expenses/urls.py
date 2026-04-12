from django.urls import path
from .views import ExpenseView

urlpatterns = [
    path("expenses/", ExpenseView.as_view(), name="expenses"),
]