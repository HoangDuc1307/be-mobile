package com.example.quanlyphongtro

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.example.quanlyphongtro.network.RetrofitClient
import com.example.quanlyphongtro.network.RoomRequest
import com.example.quanlyphongtro.network.SessionManager
import com.example.quanlyphongtro.network.RoomResponse
import com.google.android.material.card.MaterialCardView
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.launch

class EditRoomActivity : AppCompatActivity() {

    private lateinit var session: SessionManager
    private var roomId: Int = -1

    // Trạng thái hiện tại khi user chọn toggle
    private var currentStatus: String = "available"

    // Dữ liệu thực từ DB
    private var dbStatus: String = "available"       // status từ API
    private var hasTenantInDb: Boolean = false        // phòng có người thuê thực sự trong DB
    private var tenantPhone: String? = null

    // Views
    private lateinit var btnBack: ImageView
    private lateinit var etRoomName: TextInputEditText
    private lateinit var etPrice: TextInputEditText
    private lateinit var etElecPrice: TextInputEditText
    private lateinit var etWaterPrice: TextInputEditText

    private lateinit var btnStatusAvailable: Button
    private lateinit var btnStatusOccupied: Button

    private lateinit var cardTenantManage: MaterialCardView
    private lateinit var tvTenantAvatar: TextView
    private lateinit var tvTenantName: TextView
    private lateinit var tvTenantPhone: TextView
    private lateinit var btnTenantInfo: MaterialCardView
    private lateinit var btnRemoveTenant: MaterialCardView

    private lateinit var btnDeleteRoom: MaterialCardView
    private lateinit var btnSave: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_edit_room)

        session = SessionManager(this)
        roomId = intent.getIntExtra("ROOM_ID", -1)

        if (roomId == -1) {
            Toast.makeText(this, "Lỗi: Không tìm thấy ID phòng!", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        bindViews()
        setupListeners()
        loadRoomData()
    }

    private fun bindViews() {
        btnBack             = findViewById(R.id.btnBack)
        etRoomName          = findViewById(R.id.etRoomName)
        etPrice             = findViewById(R.id.etPrice)
        etElecPrice         = findViewById(R.id.etElecPrice)
        etWaterPrice        = findViewById(R.id.etWaterPrice)

        btnStatusAvailable  = findViewById(R.id.btnStatusAvailable)
        btnStatusOccupied   = findViewById(R.id.btnStatusOccupied)

        cardTenantManage    = findViewById(R.id.cardTenantManage)
        tvTenantAvatar      = findViewById(R.id.tvTenantAvatar)
        tvTenantName        = findViewById(R.id.tvTenantName)
        tvTenantPhone       = findViewById(R.id.tvTenantPhone)
        btnTenantInfo       = findViewById(R.id.btnTenantInfo)
        btnRemoveTenant     = findViewById(R.id.btnRemoveTenant)

        btnDeleteRoom       = findViewById(R.id.btnDeleteRoom)
        btnSave             = findViewById(R.id.btnSave)
    }

    private fun setupListeners() {
        btnBack.setOnClickListener { finish() }

        // ── Toggle trạng thái ──────────────────────────────────────
        btnStatusAvailable.setOnClickListener {
            applyToggle("available")
        }

        btnStatusOccupied.setOnClickListener {
            // Chỉ cho phép chuyển sang "occupied" nếu DB đang có người
            if (!hasTenantInDb) {
                Toast.makeText(
                    this,
                    "Phòng chưa có người thuê trong hệ thống.\nVui lòng thêm người thuê trước.",
                    Toast.LENGTH_LONG
                ).show()
                return@setOnClickListener
            }
            applyToggle("occupied")
        }

        // ── Lưu thông tin ─────────────────────────────────────────
        btnSave.setOnClickListener { handleSave() }

        // ── Xóa phòng ─────────────────────────────────────────────
        btnDeleteRoom.setOnClickListener { confirmDeleteRoom() }

        // ── Xóa người thuê / Trả phòng ───────────────────────────
        btnRemoveTenant.setOnClickListener { confirmRemoveTenant() }

        // ── Gọi điện cho người thuê ────────────────────────────────
        btnTenantInfo.setOnClickListener {
            val phone = tenantPhone
            if (!phone.isNullOrEmpty()) {
                startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phone")))
            } else {
                Toast.makeText(this, "Không có số điện thoại người thuê!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    // ── Cập nhật giao diện toggle ──────────────────────────────────
    private fun applyToggle(status: String) {
        currentStatus = status
        val density = resources.displayMetrics.density

        if (status == "available") {
            // Nút Trống → active (trắng, shadow)
            btnStatusAvailable.backgroundTintList =
                android.content.res.ColorStateList.valueOf(android.graphics.Color.WHITE)
            btnStatusAvailable.setTextColor(ContextCompat.getColor(this, R.color.navy_dark))
            btnStatusAvailable.elevation = 2 * density

            // Nút Đã có người → inactive (trong suốt)
            btnStatusOccupied.backgroundTintList =
                android.content.res.ColorStateList.valueOf(android.graphics.Color.TRANSPARENT)
            btnStatusOccupied.setTextColor(ContextCompat.getColor(this, R.color.gray_text))
            btnStatusOccupied.elevation = 0f

            // Ẩn card khách thuê
            cardTenantManage.visibility = View.GONE

        } else {
            // Nút Đã có người → active (xanh lá)
            btnStatusOccupied.backgroundTintList =
                ContextCompat.getColorStateList(this, R.color.badge_occupied_bg)
            btnStatusOccupied.setTextColor(ContextCompat.getColor(this, R.color.badge_occupied_text))
            btnStatusOccupied.elevation = 2 * density

            // Nút Trống → inactive
            btnStatusAvailable.backgroundTintList =
                android.content.res.ColorStateList.valueOf(android.graphics.Color.TRANSPARENT)
            btnStatusAvailable.setTextColor(ContextCompat.getColor(this, R.color.gray_text))
            btnStatusAvailable.elevation = 0f

            // Hiện card khách thuê CHỈ KHI DB có người thực
            if (hasTenantInDb) {
                cardTenantManage.visibility = View.VISIBLE
            }
        }
    }

    // ── Load dữ liệu phòng từ API ─────────────────────────────────
    private fun loadRoomData() {
        lifecycleScope.launch {
            try {
                val token = session.bearerToken()
                val response = RetrofitClient.api.getRoomDetail(token, roomId)
                if (response.isSuccessful && response.body() != null) {
                    fillForm(response.body()!!)
                } else {
                    if (response.code() == 401) handleSessionExpired()
                    else Toast.makeText(this@EditRoomActivity, "Lấy thông tin phòng thất bại!", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@EditRoomActivity, "Lỗi kết nối máy chủ!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun fillForm(room: RoomResponse) {
        // ── Lưu trạng thái DB ─────────────────────────────────────
        dbStatus        = room.status
        hasTenantInDb   = (room.status == "occupied" && room.tenant_name != null)
        tenantPhone     = room.tenant_phone

        // ── Fill form fields ───────────────────────────────────────
        etRoomName.setText(room.name)
        val priceClean = room.price.toDoubleOrNull()?.toLong()?.toString() ?: room.price
        etPrice.setText(priceClean)

        // ── Apply toggle theo DB ───────────────────────────────────
        applyToggle(room.status)

        // ── Điền thông tin người thuê nếu có ──────────────────────
        if (hasTenantInDb) {
            val name = room.tenant_name ?: "Người thuê"
            tvTenantName.text   = name
            tvTenantPhone.text  = room.tenant_phone ?: "Chưa có SĐT"
            tvTenantAvatar.text = if (name.isNotEmpty()) name.take(1).uppercase() else "N"
        }
    }

    // ── Lưu thông tin phòng ────────────────────────────────────────
    private fun handleSave() {
        val name      = etRoomName.text.toString().trim()
        val priceText = etPrice.text.toString().trim()

        if (name.isEmpty()) { etRoomName.error = "Vui lòng nhập số phòng"; return }
        if (priceText.isEmpty()) { etPrice.error = "Vui lòng nhập giá thuê"; return }

        btnSave.isEnabled = false
        btnSave.text = "Đang lưu..."

        lifecycleScope.launch {
            try {
                val token = session.bearerToken()

                // Lấy area & description hiện tại để không mất dữ liệu
                val currentResp = RetrofitClient.api.getRoomDetail(token, roomId)
                val area        = currentResp.body()?.area ?: 0.0
                val description = currentResp.body()?.description ?: ""

                val finalBody = RoomRequest(
                    name        = name,
                    price       = priceText,
                    area        = area,
                    status      = currentStatus,
                    description = description
                )

                val response = RetrofitClient.api.updateRoom(token, roomId, finalBody)
                if (response.isSuccessful) {
                    Toast.makeText(this@EditRoomActivity, "Cập nhật phòng thành công!", Toast.LENGTH_SHORT).show()
                    setResult(RESULT_OK)
                    finish()
                } else {
                    if (response.code() == 401) handleSessionExpired()
                    else { Toast.makeText(this@EditRoomActivity, "Cập nhật thất bại!", Toast.LENGTH_SHORT).show(); resetSaveButton() }
                }
            } catch (e: Exception) {
                Toast.makeText(this@EditRoomActivity, "Lỗi kết nối máy chủ!", Toast.LENGTH_SHORT).show()
                resetSaveButton()
            }
        }
    }

    private fun resetSaveButton() {
        btnSave.isEnabled = true
        btnSave.text = "Lưu thông tin"
    }

    // ── Xóa phòng ────────────────────────────────────────────────
    private fun confirmDeleteRoom() {
        val msg = if (hasTenantInDb)
            "Phòng này đang có người thuê!\n\nVui lòng trả phòng cho người thuê trước khi xóa."
        else
            "Bạn có chắc muốn xóa phòng này?\nHành động này không thể hoàn tác."

        AlertDialog.Builder(this)
            .setTitle("Xóa phòng")
            .setMessage(msg)
            .setPositiveButton(if (hasTenantInDb) "Đã hiểu" else "Xóa") { _, _ ->
                if (!hasTenantInDb) deleteRoom()
            }
            .setNegativeButton(if (hasTenantInDb) null else "Hủy", null)
            .setIcon(android.R.drawable.ic_dialog_alert)
            .show()
    }

    private fun deleteRoom() {
        lifecycleScope.launch {
            try {
                val token    = session.bearerToken()
                val response = RetrofitClient.api.deleteRoom(token, roomId)
                if (response.isSuccessful || response.code() == 204) {
                    Toast.makeText(this@EditRoomActivity, "Đã xóa phòng thành công!", Toast.LENGTH_SHORT).show()
                    setResult(RESULT_OK)
                    finish()
                } else {
                    when (response.code()) {
                        400  -> Toast.makeText(this@EditRoomActivity, "Không thể xóa phòng đang có người thuê!", Toast.LENGTH_LONG).show()
                        401  -> handleSessionExpired()
                        else -> Toast.makeText(this@EditRoomActivity, "Xóa phòng thất bại!", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@EditRoomActivity, "Lỗi kết nối máy chủ!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    // ── Trả phòng ────────────────────────────────────────────────
    private fun confirmRemoveTenant() {
        AlertDialog.Builder(this)
            .setTitle("Trả phòng")
            .setMessage("Bạn có chắc muốn cho người thuê trả phòng?\n\nThao tác này sẽ:\n• Kết thúc hợp đồng thuê\n• Chuyển trạng thái phòng về Trống")
            .setPositiveButton("Trả phòng") { _, _ -> removeTenant() }
            .setNegativeButton("Hủy", null)
            .show()
    }

    private fun removeTenant() {
        lifecycleScope.launch {
            try {
                val token    = session.bearerToken()
                val response = RetrofitClient.api.removeTenant(token, roomId)
                if (response.isSuccessful || response.code() == 200) {
                    Toast.makeText(this@EditRoomActivity, "Trả phòng thành công!", Toast.LENGTH_SHORT).show()
                    // Cập nhật state local
                    hasTenantInDb = false
                    tenantPhone   = null
                    dbStatus      = "available"
                    applyToggle("available")
                    setResult(RESULT_OK)
                } else {
                    when (response.code()) {
                        400  -> Toast.makeText(this@EditRoomActivity, "Phòng không có người thuê!", Toast.LENGTH_SHORT).show()
                        401  -> handleSessionExpired()
                        else -> Toast.makeText(this@EditRoomActivity, "Trả phòng thất bại!", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@EditRoomActivity, "Lỗi kết nối máy chủ!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun handleSessionExpired() {
        Toast.makeText(this, "Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại!", Toast.LENGTH_LONG).show()
        session.clearSession()
        val intent = Intent(this, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}
