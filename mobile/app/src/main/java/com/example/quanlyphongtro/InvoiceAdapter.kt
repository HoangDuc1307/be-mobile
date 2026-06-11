package com.example.quanlyphongtro

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import java.text.NumberFormat
import java.util.Locale

class InvoiceAdapter(
    private var invoices: List<InvoiceItem>,
    private val onMoreClick: (InvoiceItem) -> Unit = {}
) : RecyclerView.Adapter<InvoiceAdapter.InvoiceViewHolder>() {

    class InvoiceViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvRoomNumber: TextView = view.findViewById(R.id.tvRoomNumber)
        val tvInvoiceTitle: TextView = view.findViewById(R.id.tvInvoiceTitle)
        val tvInvoiceDate: TextView = view.findViewById(R.id.tvInvoiceDate)
        val tvAmount: TextView = view.findViewById(R.id.tvAmount)
        val tvPaymentStatus: TextView = view.findViewById(R.id.tvPaymentStatus)
        val btnMore: ImageView = view.findViewById(R.id.btnMore)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): InvoiceViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_invoice, parent, false)
        return InvoiceViewHolder(view)
    }

    override fun onBindViewHolder(holder: InvoiceViewHolder, position: Int) {
        val invoice = invoices[position]
        val context = holder.itemView.context

        holder.tvRoomNumber.text = invoice.roomNumber
        holder.tvInvoiceTitle.text = "${invoice.roomName} - ${invoice.tenantName}"
        holder.tvInvoiceDate.text = invoice.dateLabel

        val formattedAmount = NumberFormat.getNumberInstance(Locale("vi", "VN"))
            .format(invoice.amount) + " đ"
        holder.tvAmount.text = formattedAmount

        holder.tvRoomNumber.setBackgroundResource(R.drawable.bg_room_number)
        holder.tvPaymentStatus.setBackgroundResource(R.drawable.bg_badge_blue)

        if (invoice.isPaid) {
            holder.tvRoomNumber.backgroundTintList =
                ContextCompat.getColorStateList(context, R.color.room_paid_bg)
            holder.tvRoomNumber.setTextColor(ContextCompat.getColor(context, R.color.room_paid_text))
            holder.tvPaymentStatus.text = "Đã thanh toán"
            holder.tvPaymentStatus.backgroundTintList =
                ContextCompat.getColorStateList(context, R.color.badge_occupied_bg)
            holder.tvPaymentStatus.setTextColor(
                ContextCompat.getColor(context, R.color.badge_occupied_text)
            )
        } else {
            holder.tvRoomNumber.backgroundTintList =
                ContextCompat.getColorStateList(context, R.color.room_unpaid_bg)
            holder.tvRoomNumber.setTextColor(ContextCompat.getColor(context, R.color.room_unpaid_text))
            holder.tvPaymentStatus.text = "Chưa thanh toán"
            holder.tvPaymentStatus.backgroundTintList =
                ContextCompat.getColorStateList(context, R.color.badge_unpaid_bg)
            holder.tvPaymentStatus.setTextColor(
                ContextCompat.getColor(context, R.color.badge_unpaid_text)
            )
        }

        holder.btnMore.setOnClickListener { onMoreClick(invoice) }
    }

    override fun getItemCount(): Int = invoices.size

    fun updateInvoices(newInvoices: List<InvoiceItem>) {
        invoices = newInvoices
        notifyDataSetChanged()
    }
}
