from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from collections import defaultdict

from .models import Expense
from .serializers import ExpenseSerializer
from dotenv import load_dotenv
import json
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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

        # 🧠 Prepare structured input for AI
        ai_input = {
            "total_spend": float(total),
            "category_breakdown": category_percentages
        }

        # 🧠 Prompt (VERY IMPORTANT)
        prompt = f"""
            You are a financial assistant.

            The currency is Indian Rupees (₹).

            Given the user's expense summary:
            {ai_input}

            Generate:
            1. A short summary (1 sentence and avoid the word 'user' in it and instead use 'You')
            2. 2-3 key insights
            3. 2 actionable recommendations

            Respond strictly in JSON format:
            {{
            "summary": "...",
            "insights": ["...", "..."],
            "recommendations": ["...", "..."]
            }}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )

            content = response.choices[0].message.content
            try:
                parsed = json.loads(content)
            except Exception:
                parsed = {
                    "summary": content,
                    "insights": [],
                    "recommendations": []
                }

            return Response(parsed)

        except Exception as e:
            # Fallback (VERY IMPORTANT)
            return Response({
                "summary": "Unable to generate AI insights right now.",
                "insights": [],
                "recommendations": [],
                "error": str(e)
            }, status=500)