package com.example.quanlyphongtro

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.example.quanlyphongtro.network.RoomResponse
import java.text.NumberFormat
import java.util.Locale

class RoomAdapter(
    private var rooms: List<RoomResponse>,
    private val onRoomClick: (RoomResponse) -> Unit
) : RecyclerView.Adapter<RoomAdapter.RoomViewHolder>() {

    class RoomViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvRoomName: TextView = view.findViewById(R.id.tvRoomName)
        val tvDescription: TextView = view.findViewById(R.id.tvDescription)
        val tvStatusBadge: TextView = view.findViewById(R.id.tvStatusBadge)
        val tvTenantName: TextView = view.findViewById(R.id.tvTenantName)
        val ivStatusIcon: ImageView = view.findViewById(R.id.ivStatusIcon)
        val ivPriceIcon: ImageView = view.findViewById(R.id.ivPriceIcon)
        val tvPrice: TextView = view.findViewById(R.id.tvPrice)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RoomViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_room, parent, false)
        return RoomViewHolder(view)
    }

    override fun onBindViewHolder(holder: RoomViewHolder, position: Int) {
        val room = rooms[position]
        val context = holder.itemView.context

        holder.tvRoomName.text = room.name

        val digits = room.name.filter { it.isDigit() }
        val floorText = if (digits.length >= 3) {
            "Tầng ${digits[0]}"
        } else {
            room.description.ifEmpty { "Tầng 1" }
        }
        holder.tvDescription.text = floorText

        val priceLong = room.price.toDoubleOrNull()?.toLong() ?: 0L
        val formattedPrice = NumberFormat.getCurrencyInstance(Locale("vi", "VN")).format(priceLong)
        holder.tvPrice.text = "$formattedPrice/tháng"

        if (room.status == "occupied") {
            holder.tvStatusBadge.text = "Đã cho thuê"
            holder.tvStatusBadge.setBackgroundResource(R.drawable.bg_badge_blue)
            holder.tvStatusBadge.backgroundTintList =
                ContextCompat.getColorStateList(context, R.color.badge_occupied_bg)
            holder.tvStatusBadge.setTextColor(
                ContextCompat.getColor(context, R.color.badge_occupied_text)
            )

            holder.ivStatusIcon.setImageResource(R.drawable.ic_tenant)
            holder.ivStatusIcon.setColorFilter(ContextCompat.getColor(context, R.color.gray_text))
            holder.tvTenantName.text = room.tenant_name ?: "Người thuê ẩn danh"

            holder.ivPriceIcon.setImageResource(R.drawable.ic_money)
        } else {
            val isRepair = room.description.contains("sửa", ignoreCase = true)
                    || room.description.contains("repair", ignoreCase = true)

            if (isRepair) {
                holder.tvStatusBadge.text = "Đang sửa"
                holder.ivStatusIcon.setImageResource(R.drawable.ic_wrench)
                holder.tvTenantName.text = "Đang sửa chữa"
            } else {
                holder.tvStatusBadge.text = "Trống"
                holder.ivStatusIcon.setImageResource(R.drawable.ic_clock)
                holder.tvTenantName.text = "Đang tìm khách"
            }

            holder.tvStatusBadge.setBackgroundResource(R.drawable.bg_badge_blue)
            holder.tvStatusBadge.backgroundTintList =
                ContextCompat.getColorStateList(context, R.color.badge_available_bg)
            holder.tvStatusBadge.setTextColor(
                ContextCompat.getColor(context, R.color.badge_available_text)
            )
            holder.ivStatusIcon.setColorFilter(ContextCompat.getColor(context, R.color.gray_text))
            holder.ivPriceIcon.setImageResource(R.drawable.ic_price)
        }

        holder.ivPriceIcon.setColorFilter(ContextCompat.getColor(context, R.color.gray_text))
        holder.itemView.setOnClickListener { onRoomClick(room) }
    }

    override fun getItemCount(): Int = rooms.size

    fun updateRooms(newRooms: List<RoomResponse>) {
        this.rooms = newRooms
        notifyDataSetChanged()
    }
}
