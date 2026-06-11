package com.example.quanlyphongtro

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.quanlyphongtro.network.RetrofitClient
import com.example.quanlyphongtro.network.RoomRequest
import com.example.quanlyphongtro.network.SessionManager
import kotlinx.coroutines.launch

class AddRoomActivity : AppCompatActivity() {

    private lateinit var session: SessionManager
    private var roomId: Int = -1
    private var isEditMode = false

    private lateinit var tvTitle: TextView
    private lateinit var etRoomName: EditText
    private lateinit var etPrice: EditText
    private lateinit var etArea: EditText
    private lateinit var rgStatus: RadioGroup
    private lateinit var rbAvailable: RadioButton
    private lateinit var rbOccupied: RadioButton
    private lateinit var etDescription: EditText
    private lateinit var btnSubmit: Button
    private lateinit var btnBack: ImageView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_add_room)

        session = SessionManager(this)

        // Ánh xạ views
        tvTitle = findViewById(R.id.tvTitle)
        etRoomName = findViewById(R.id.etRoomName)
        etPrice = findViewById(R.id.etPrice)
        etArea = findViewById(R.id.etArea)
        rgStatus = findViewById(R.id.rgStatus)
        rbAvailable = findViewById(R.id.rbAvailable)
        rbOccupied = findViewById(R.id.rbOccupied)
        etDescription = findViewById(R.id.etDescription)
        btnSubmit = findViewById(R.id.btnSubmit)
        btnBack = findViewById(R.id.btnBack)

        // Nhận dữ liệu Intent để check chế độ Thêm hay Sửa
        roomId = intent.getIntExtra("ROOM_ID", -1)
        isEditMode = roomId != -1

        if (isEditMode) {
            setupEditMode()
        }

        btnBack.setOnClickListener {
            finish()
        }

        btnSubmit.setOnClickListener {
            handleSubmit()
        }
    }

    private fun setupEditMode() {
        tvTitle.text = "Sửa thông tin phòng"
        btnSubmit.text = "CẬP NHẬT"

        // Tải thông tin phòng hiện tại để fill vào form
        lifecycleScope.launch {
            try {
                val token = session.bearerToken()
                val response = RetrofitClient.api.getRoomDetail(token, roomId)
                if (response.isSuccessful && response.body() != null) {
                    val room = response.body()!!
                    etRoomName.setText(room.name)
                    // Loại bỏ phần thập phân của giá nếu là số chẵn
                    val priceClean = room.price.toDoubleOrNull()?.toLong()?.toString() ?: room.price
                    etPrice.setText(priceClean)
                    etArea.setText(room.area.toString())
                    etDescription.setText(room.description)

                    if (room.status == "occupied") {
                        rbOccupied.isChecked = true
                    } else {
                        rbAvailable.isChecked = true
                    }
                } else {
                    if (response.code() == 401) {
                        Toast.makeText(
                            this@AddRoomActivity,
                            "Phiên đăng nhập hết hạn hoặc tài khoản không tồn tại. Vui lòng đăng nhập lại!",
                            Toast.LENGTH_LONG
                        ).show()
                        session.clearSession()
                        val intent = android.content.Intent(this@AddRoomActivity, LoginActivity::class.java)
                        intent.flags = android.content.Intent.FLAG_ACTIVITY_NEW_TASK or android.content.Intent.FLAG_ACTIVITY_CLEAR_TASK
                        startActivity(intent)
                        finish()
                    } else {
                        Toast.makeText(this@AddRoomActivity, "Lấy thông tin phòng thất bại!", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@AddRoomActivity, "Lỗi kết nối máy chủ!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun handleSubmit() {
        val name = etRoomName.text.toString().trim()
        val priceText = etPrice.text.toString().trim()
        val areaText = etArea.text.toString().trim()
        val description = etDescription.text.toString().trim()

        // Validate
        if (name.isEmpty()) {
            etRoomName.error = "Vui lòng nhập số phòng"
            return
        }
        if (priceText.isEmpty()) {
            etPrice.error = "Vui lòng nhập giá thuê"
            return
        }
        if (areaText.isEmpty()) {
            etArea.error = "Vui lòng nhập diện tích"
            return
        }

        val price = priceText
        val area = areaText.toDoubleOrNull() ?: 0.0

        val status = if (rgStatus.checkedRadioButtonId == R.id.rbOccupied) {
            "occupied"
        } else {
            "available"
        }

        val requestBody = RoomRequest(
            name = name,
            price = price,
            area = area,
            status = status,
            description = description
        )

        btnSubmit.isEnabled = false
        btnSubmit.text = if (isEditMode) "ĐANG CẬP NHẬT..." else "ĐANG TẠO..."

        lifecycleScope.launch {
            try {
                val token = session.bearerToken()
                val response = if (isEditMode) {
                    RetrofitClient.api.updateRoom(token, roomId, requestBody)
                } else {
                    RetrofitClient.api.createRoom(token, requestBody)
                }

                if (response.isSuccessful) {
                    val msg = if (isEditMode) "Cập nhật phòng thành công!" else "Thêm phòng mới thành công!"
                    Toast.makeText(this@AddRoomActivity, msg, Toast.LENGTH_SHORT).show()
                    setResult(RESULT_OK) // Báo về OwnerMainActivity để reload danh sách
                    finish()
                } else {
                    if (response.code() == 401) {
                        Toast.makeText(
                            this@AddRoomActivity,
                            "Phiên đăng nhập hết hạn hoặc tài khoản không tồn tại. Vui lòng đăng nhập lại!",
                            Toast.LENGTH_LONG
                        ).show()
                        session.clearSession()
                        val intent = android.content.Intent(this@AddRoomActivity, LoginActivity::class.java)
                        intent.flags = android.content.Intent.FLAG_ACTIVITY_NEW_TASK or android.content.Intent.FLAG_ACTIVITY_CLEAR_TASK
                        startActivity(intent)
                        finish()
                    } else {
                        val errorMsg = if (isEditMode) "Cập nhật thất bại!" else "Thêm phòng thất bại!"
                        Toast.makeText(this@AddRoomActivity, errorMsg, Toast.LENGTH_SHORT).show()
                        btnSubmit.isEnabled = true
                        btnSubmit.text = if (isEditMode) "CẬP NHẬT" else "TẠO PHÒNG"
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@AddRoomActivity, "Lỗi kết nối máy chủ!", Toast.LENGTH_SHORT).show()
                btnSubmit.isEnabled = true
                btnSubmit.text = if (isEditMode) "CẬP NHẬT" else "TẠO PHÒNG"
            }
        }
    }
}
