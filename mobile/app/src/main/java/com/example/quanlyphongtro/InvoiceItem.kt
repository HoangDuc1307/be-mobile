package com.example.quanlyphongtro

data class InvoiceItem(
    val roomNumber: String,
    val roomName: String,
    val tenantName: String,
    val amount: Long,
    val isPaid: Boolean,
    val dateLabel: String
)
