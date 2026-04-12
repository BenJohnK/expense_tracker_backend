from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Expense
from .serializers import ExpenseSerializer

class ExpenseView(APIView):

    def get(self, request):
        queryset = Expense.objects.all()

        # Filter by category
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        # Sort by date desc
        sort = request.query_params.get("sort")
        if sort == "date_desc":
            queryset = queryset.order_by("-date")

        serializer = ExpenseSerializer(queryset, many=True)

        # Calculate total
        total = sum(item["amount"] for item in serializer.data)

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