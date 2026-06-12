from django.urls import path
from .views import UnitPriceView, InvoiceListCreateView

urlpatterns = [
    path('unit-price/', UnitPriceView.as_view(), name='unit-price'),
    path('', InvoiceListCreateView.as_view(), name='invoice-list-create'),
]
