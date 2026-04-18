from django.urls import path
from .views import ExpenseView, ExpenseInsightsView

urlpatterns = [
    path("expenses/", ExpenseView.as_view(), name="expenses"),
    path("expenses/insights/", ExpenseInsightsView.as_view(), name="expense-insights")
]