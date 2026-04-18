from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from collections import defaultdict

from .models import Expense
from .serializers import ExpenseSerializer

class ExpenseView(APIView):

    def get(self, request):
        queryset = Expense.objects.all()

        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        sort = request.query_params.get("sort")
        if sort == "date_desc":
            queryset = queryset.order_by("-date")

        serializer = ExpenseSerializer(queryset, many=True)

        total = queryset.aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "data": serializer.data,
            "total": total
        })

    def post(self, request):
        serializer = ExpenseSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            expense = serializer.save()
            return Response(
                ExpenseSerializer(expense).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseInsightsView(APIView):

    def get(self, request):
        expenses = Expense.objects.all()

        if not expenses.exists():
            return Response({
                "summary": "No expenses found.",
                "insights": [],
                "recommendations": []
            })

        total = expenses.aggregate(total=Sum("amount"))["total"] or 0

        category_totals = defaultdict(float)

        for exp in expenses:
            category_totals[exp.category] += float(exp.amount)

        # Convert to percentages
        category_percentages = {
            cat: (amt / float(total)) * 100
            for cat, amt in category_totals.items()
        }

        # --- MOCK AI LOGIC (for now) ---

        # Top category
        top_category = max(category_totals, key=category_totals.get)

        summary = f"You spent most on {top_category}."

        insights = []

        for cat, percent in category_percentages.items():
            insights.append(f"{cat} accounts for {percent:.1f}% of your spending.")

        recommendations = []

        if category_percentages.get("FOOD", 0) > 40:
            recommendations.append("Consider reducing eating out expenses.")

        if category_percentages.get("TRAVEL", 0) > 30:
            recommendations.append("Plan trips in advance to save costs.")

        if not recommendations:
            recommendations.append("Your spending looks balanced. Keep it up!")

        return Response({
            "summary": summary,
            "insights": insights,
            "recommendations": recommendations
        })