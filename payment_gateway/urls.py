from django.urls import path,include

from .views import CreateOrderAPIView,TransactionAPIView

urlpatterns = [
      path('order/create/',CreateOrderAPIView.as_view(),name="create-order-api"),
      path('order/complete/',TransactionAPIView.as_view(),name="complete-order-api"),
]