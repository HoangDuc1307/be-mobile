package com.example.quanlyphongtro

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.example.quanlyphongtro.network.RetrofitClient
import com.example.quanlyphongtro.network.SessionManager
import com.example.quanlyphongtro.network.RoomResponse
import com.google.android.material.card.MaterialCardView
import com.google.android.material.floatingactionbutton.FloatingActionButton
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Locale

class RoomDetailActivity : AppCompatActivity() {

    private lateinit var session: SessionManager
    private var roomId: Int = -1
    private var isModified = false

    // ── Header ──────────────────────────────────────────────────────
    private lateinit var btnBack: ImageView
    private lateinit var tvTitle: TextView

    // ── Thông tin phòng ─────────────────────────────────────────────
    private lateinit var tvStatusBadge: TextView
    private lateinit var tvRoomNameLarge: TextView
    private lateinit var tvAreaValue: TextView
    private lateinit var tvPriceValue: TextView
    private lateinit var layoutAmenities: LinearLayout

    // ── Người thuê ───────────────────────────────────────────────────
    private lateinit var cardTenantInfo: MaterialCardView
    private lateinit var tvTenantAvatar: TextView
    private lateinit var tvTenantNameDetail: TextView
    private lateinit var tvTenantPhoneDetail: TextView
    private lateinit var btnCallTenant: MaterialCardView
    private lateinit var tvMoveInDate: TextView
    private lateinit var tvDepositValue: TextView

    // ── Nút chức năng ────────────────────────────────────────────────
    private lateinit var btnContract: MaterialCardView
    private lateinit var btnInvoice: MaterialCardView
    private lateinit var fabEditRoom: FloatingActionButton

    private val editRoomLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            isModified = true
            loadRoomDetail()   // Reload dữ liệu sau khi chỉnh sửa
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_room_detail)

        session = SessionManager(this)
        roomId  = intent.getIntExtra("ROOM_ID", -1)

        if (roomId == -1) {
            Toast.makeText(this, "Lỗi: Không tìm thấy ID phòng!", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        bindViews()
        setupListeners()

        // Hiện loading ngay khi vào màn hình
        tvTitle.text          = "Đang tải..."
        tvRoomNameLarge.text  = "..."
        tvAreaValue.text      = "--"
        tvPriceValue.text     = "--"
        cardTenantInfo.visibility = View.GONE

        loadRoomDetail()
    }

    private fun bindViews() {
        btnBack              = findViewById(R.id.btnBack)
        tvTitle              = findViewById(R.id.tvTitle)
        tvStatusBadge        = findViewById(R.id.tvStatusBadge)
        tvRoomNameLarge      = findViewById(R.id.tvRoomNameLarge)
        tvAreaValue          = findViewById(R.id.tvAreaValue)
        tvPriceValue         = findViewById(R.id.tvPriceValue)
        layoutAmenities      = findViewById(R.id.layoutAmenities)

        cardTenantInfo       = findViewById(R.id.cardTenantInfo)
        tvTenantAvatar       = findViewById(R.id.tvTenantAvatar)
        tvTenantNameDetail   = findViewById(R.id.tvTenantNameDetail)
        tvTenantPhoneDetail  = findViewById(R.id.tvTenantPhoneDetail)
        btnCallTenant        = findViewById(R.id.btnCallTenant)
        tvMoveInDate         = findViewById(R.id.tvMoveInDate)
        tvDepositValue       = findViewById(R.id.tvDepositValue)

        btnContract          = findViewById(R.id.btnContract)
        btnInvoice           = findViewById(R.id.btnInvoice)
        fabEditRoom          = findViewById(R.id.fabEditRoom)
    }

    private fun setupListeners() {
        btnBack.setOnClickListener {
            onBackPressedDispatcher.onBackPressed()
        }

        fabEditRoom.setOnClickListener {
            val intent = Intent(this, EditRoomActivity::class.java).apply {
                putExtra("ROOM_ID", roomId)
            }
            editRoomLauncher.launch(intent)
            overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)
        }
    }

    override fun finish() {
        if (isModified) setResult(RESULT_OK)
        super.finish()
        overridePendingTransition(R.anim.slide_in_left, R.anim.slide_out_right)
    }

    // ── Gọi API lấy chi tiết phòng ───────────────────────────────────
    private fun loadRoomDetail() {
        lifecycleScope.launch {
            try {
                val token    = session.bearerToken()
                val response = RetrofitClient.api.getRoomDetail(token, roomId)

                if (response.isSuccessful && response.body() != null) {
                    bindRoomData(response.body()!!)
                } else {
                    when (response.code()) {
                        401 -> {
                            Toast.makeText(
                                this@RoomDetailActivity,
                                "Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại!",
                                Toast.LENGTH_LONG
                            ).show()
                            session.clearSession()
                            val intent = Intent(this@RoomDetailActivity, LoginActivity::class.java)
                            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                            startActivity(intent)
                            finish()
                        }
                        else -> {
                            Toast.makeText(
                                this@RoomDetailActivity,
                                "Lấy thông tin phòng thất bại! (${response.code()})",
                                Toast.LENGTH_SHORT
                            ).show()
                            tvTitle.text = "Chi tiết phòng"
                        }
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@RoomDetailActivity, "Lỗi kết nối máy chủ!", Toast.LENGTH_SHORT).show()
                tvTitle.text = "Chi tiết phòng"
            }
        }
    }

    // ── Bind dữ liệu thật lên UI ─────────────────────────────────────
    private fun bindRoomData(room: RoomResponse) {
        // Header
        tvTitle.text         = "Chi tiết ${room.name}"
        tvRoomNameLarge.text = room.name

        // Diện tích
        val areaStr = room.area.toLong().toString()
        tvAreaValue.text = "$areaStr m²"

        // Giá phòng
        val priceLong      = room.price.toDoubleOrNull()?.toLong() ?: 0L
        val formattedPrice = NumberFormat.getCurrencyInstance(Locale("vi", "VN")).format(priceLong)
        tvPriceValue.text  = formattedPrice

        // ── Trạng thái ──────────────────────────────────────────────
        if (room.status == "occupied") {
            tvStatusBadge.text = "✔ Đang cho thuê"
            tvStatusBadge.backgroundTintList =
                ContextCompat.getColorStateList(this, R.color.badge_occupied_bg)
            tvStatusBadge.setTextColor(ContextCompat.getColor(this, R.color.badge_occupied_text))

            // Hiện card người thuê CHỈ KHI có dữ liệu thật từ DB
            if (room.tenant_name != null) {
                cardTenantInfo.visibility = View.VISIBLE

                val tenantName = room.tenant_name
                tvTenantNameDetail.text  = tenantName
                tvTenantPhoneDetail.text = room.tenant_phone ?: "Chưa cập nhật SĐT"
                tvTenantAvatar.text      = tenantName.take(1).uppercase()

                // Ngày vào
                val rawMoveIn = room.move_in ?: "--"
                tvMoveInDate.text = try {
                    val parts = rawMoveIn.split("T")[0].split("-")
                    if (parts.size == 3) "${parts[2]}/${parts[1]}/${parts[0]}" else rawMoveIn
                } catch (e: Exception) { rawMoveIn }

                // Tiền cọc
                val depositLong     = room.deposit?.toDoubleOrNull()?.toLong() ?: 0L
                val formattedDeposit = NumberFormat.getCurrencyInstance(Locale("vi", "VN")).format(depositLong)
                tvDepositValue.text  = formattedDeposit

                // Gọi điện
                btnCallTenant.setOnClickListener {
                    val phone = room.tenant_phone
                    if (!phone.isNullOrEmpty()) {
                        startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phone")))
                    } else {
                        Toast.makeText(this, "Không có số điện thoại người thuê!", Toast.LENGTH_SHORT).show()
                    }
                }
            } else {
                // Phòng có trạng thái occupied nhưng DB chưa có tenant record
                cardTenantInfo.visibility = View.GONE
            }
        } else {
            // Phòng trống
            tvStatusBadge.text = "✔ Còn trống"
            tvStatusBadge.backgroundTintList =
                ContextCompat.getColorStateList(this, R.color.badge_available_bg)
            tvStatusBadge.setTextColor(ContextCompat.getColor(this, R.color.badge_available_text))

            cardTenantInfo.visibility = View.GONE
        }

        // ── Tiện ích ─────────────────────────────────────────────────
        bindAmenities(room.description)

        // ── Nút Hợp đồng / Hóa đơn ──────────────────────────────────
        btnContract.setOnClickListener {
            Toast.makeText(this, "Hợp đồng phòng ${room.name}", Toast.LENGTH_SHORT).show()
        }
        btnInvoice.setOnClickListener {
            Toast.makeText(this, "Hóa đơn phòng ${room.name}", Toast.LENGTH_SHORT).show()
        }
    }

    // ── Bind tiện ích dạng chip ───────────────────────────────────────
    private fun bindAmenities(description: String) {
        layoutAmenities.removeAllViews()

        val list = description
            .split(Regex("[,;\n]"))
            .map { it.trim() }
            .filter { it.isNotEmpty() }

        if (list.isEmpty()) {
            val tvEmpty = TextView(this).apply {
                text = "Chưa cập nhật tiện ích"
                setTextColor(ContextCompat.getColor(this@RoomDetailActivity, R.color.gray_light))
                textSize = 13f
            }
            layoutAmenities.addView(tvEmpty)
        } else {
            val density       = resources.displayMetrics.density
            val padH          = (12 * density).toInt()
            val padV          = (6 * density).toInt()
            val rightMarginPx = (8 * density).toInt()

            for (amenity in list) {
                val tv = TextView(this).apply {
                    text = amenity
                    setBackgroundResource(R.drawable.bg_badge_gray)
                    setPadding(padH, padV, padH, padV)
                    setTextColor(ContextCompat.getColor(this@RoomDetailActivity, R.color.badge_available_text))
                    textSize     = 12f
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    ).apply { rightMargin = rightMarginPx }
                }
                layoutAmenities.addView(tv)
            }
        }
    }
}
