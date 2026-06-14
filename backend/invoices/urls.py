from django.urls import path
from .views import (
    UnitPriceView, InvoiceListCreateView, InvoiceCurrentUnpaidView,
    SubmitPaymentView, PendingPaymentsView, ApprovePaymentView, RejectPaymentView,
)

urlpatterns = [
    path('unit-price/',                         UnitPriceView.as_view(),            name='unit-price'),
    path('current-unpaid/',                     InvoiceCurrentUnpaidView.as_view(), name='invoice-current-unpaid'),
    path('pending-payments/',                   PendingPaymentsView.as_view(),      name='pending-payments'),
    path('<int:invoice_id>/submit-payment/',    SubmitPaymentView.as_view(),        name='submit-payment'),
    path('<int:invoice_id>/approve/',           ApprovePaymentView.as_view(),       name='approve-payment'),
    path('<int:invoice_id>/reject/',            RejectPaymentView.as_view(),        name='reject-payment'),
    path('',                                    InvoiceListCreateView.as_view(),    name='invoice-list-create'),
]
