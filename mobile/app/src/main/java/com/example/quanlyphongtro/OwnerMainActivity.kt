package com.example.quanlyphongtro

import android.content.Intent
import android.os.Bundle
import androidx.activity.result.contract.ActivityResultContracts
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.quanlyphongtro.network.RetrofitClient
import com.example.quanlyphongtro.network.SessionManager
import com.example.quanlyphongtro.network.RoomResponse
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Locale

class OwnerMainActivity : AppCompatActivity() {

    private lateinit var session: SessionManager
    private lateinit var roomAdapter: RoomAdapter

    private val addRoomLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            loadRoomsData()
        }
    }

    private lateinit var tvTotalRooms: TextView
    private lateinit var tvRentedRooms: TextView
    private lateinit var tvEmptyRooms: TextView
    private lateinit var tvRevenue: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_owner_main)

        session = SessionManager(this)

        // Ánh xạ các TextView Thống kê
        tvTotalRooms = findViewById(R.id.tvTotalRooms)
        tvRentedRooms = findViewById(R.id.tvRentedRooms)
        tvEmptyRooms = findViewById(R.id.tvEmptyRooms)
        tvRevenue = findViewById(R.id.tvRevenue)

        // Set tên Chủ trọ đăng nhập
        val tvOwnerName = findViewById<TextView>(R.id.tvOwnerName)
        tvOwnerName.text = "Xin chào, ${session.getUsername() ?: "Chủ trọ"}"

        // Xử lý nút Đăng xuất / Đổi vai trò
        val btnSwitchRole = findViewById<android.view.View>(R.id.btnSwitchRole)
        val cardAvatar = findViewById<android.view.View>(R.id.cardAvatar)

        val logoutAction = {
            session.clearSession()
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()
            Toast.makeText(this, "Đã đăng xuất", Toast.LENGTH_SHORT).show()
        }
        btnSwitchRole.setOnClickListener { logoutAction() }
        cardAvatar.setOnClickListener { logoutAction() }

        // Setup RecyclerView
        val rvRooms = findViewById<RecyclerView>(R.id.rvRooms)
        rvRooms.layoutManager = LinearLayoutManager(this)
        roomAdapter = RoomAdapter(emptyList()) { room ->
            val intent = Intent(this, RoomDetailActivity::class.java).apply {
                putExtra("ROOM_ID", room.id)
            }
            addRoomLauncher.launch(intent)
            overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)
        }
        rvRooms.adapter = roomAdapter

        // Bắt sự kiện các nút chức năng
        findViewById<Button>(R.id.btnAddRoom).setOnClickListener {
            val intent = Intent(this, AddRoomActivity::class.java)
            addRoomLauncher.launch(intent)
            overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)
        }
        findViewById<Button>(R.id.btnCreateInvoice).setOnClickListener {
            val intent = Intent(this, InvoiceListActivity::class.java)
            startActivity(intent)
            overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)
        }
        // Tab Quản lý → mở màn Hóa đơn
        findViewById<android.view.View>(R.id.navManage).setOnClickListener {
            val intent = Intent(this, InvoiceListActivity::class.java)
            startActivity(intent)
            overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)
        }
        findViewById<android.view.View>(R.id.navNotify).setOnClickListener {
            android.widget.Toast.makeText(this, "Tính năng Thông báo", android.widget.Toast.LENGTH_SHORT).show()
        }

        // Tải danh sách phòng từ database
        loadRoomsData()
    }

    private fun loadRoomsData() {
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.api.getRooms(session.bearerToken())
                if (response.isSuccessful && response.body() != null) {
                    val roomsList = response.body()!!
                    
                    // Cập nhật danh sách lên RecyclerView
                    roomAdapter.updateRooms(roomsList)

                    // Tính toán thống kê động
                    updateStatistics(roomsList)
                } else {
                    if (response.code() == 401) {
                        Toast.makeText(
                            this@OwnerMainActivity,
                            "Phiên đăng nhập hết hạn hoặc tài khoản không tồn tại. Vui lòng đăng nhập lại!",
                            Toast.LENGTH_LONG
                        ).show()
                        session.clearSession()
                        val intent = Intent(this@OwnerMainActivity, LoginActivity::class.java)
                        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                        startActivity(intent)
                        finish()
                    } else {
                        Toast.makeText(
                            this@OwnerMainActivity,
                            "Lấy danh sách phòng thất bại!",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(
                    this@OwnerMainActivity,
                    "Lỗi kết nối máy chủ!",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    private fun updateStatistics(rooms: List<RoomResponse>) {
        val total = rooms.size
        val rented = rooms.count { it.status == "occupied" }
        val empty = total - rented

        // Tính tổng doanh thu dự kiến (tổng tiền các phòng đã cho thuê)
        var totalRevenue = 0L
        for (room in rooms) {
            if (room.status == "occupied") {
                totalRevenue += room.price.toDoubleOrNull()?.toLong() ?: 0L
            }
        }

        // Convert sang định dạng triệu đồng (Ví dụ: 45.5M)
        val revenueText = if (totalRevenue >= 1_000_000) {
            val millions = totalRevenue.toDouble() / 1_000_000.0
            String.format(Locale.US, "%.1fM", millions)
        } else {
            val format = NumberFormat.getCurrencyInstance(Locale("vi", "VN"))
            format.format(totalRevenue)
        }

        // Ghi dữ liệu lên UI
        tvTotalRooms.text = total.toString()
        tvRentedRooms.text = rented.toString()
        tvEmptyRooms.text = empty.toString()
        tvRevenue.text = revenueText
    }
}
