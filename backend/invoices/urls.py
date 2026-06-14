from django.urls import path
from .views import UnitPriceView, InvoiceListCreateView, InvoiceCurrentUnpaidView

urlpatterns = [
    path('unit-price/',     UnitPriceView.as_view(),           name='unit-price'),
    path('current-unpaid/', InvoiceCurrentUnpaidView.as_view(), name='invoice-current-unpaid'),
    path('',                InvoiceListCreateView.as_view(),   name='invoice-list-create'),
]
