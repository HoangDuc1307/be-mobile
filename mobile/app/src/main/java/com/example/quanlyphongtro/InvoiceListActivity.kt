package com.example.quanlyphongtro

import android.content.Intent
import android.os.Bundle
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.quanlyphongtro.network.SessionManager
import com.google.android.material.floatingactionbutton.FloatingActionButton
import java.text.NumberFormat
import java.util.Calendar
import java.util.Locale

class InvoiceListActivity : AppCompatActivity() {

    private lateinit var session: SessionManager
    private lateinit var invoiceAdapter: InvoiceAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_invoice_list)

        session = SessionManager(this)

        setupHeader()
        setupRecyclerView()
        setupFilters()
        setupBottomNav()
        bindUiData()
    }

    private fun setupHeader() {
        val logoutAction = {
            session.clearSession()
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()
            Toast.makeText(this, "Đã đăng xuất", Toast.LENGTH_SHORT).show()
        }
        findViewById<android.view.View>(R.id.btnSwitchRole).setOnClickListener { logoutAction() }
        findViewById<android.view.View>(R.id.cardAvatar).setOnClickListener { logoutAction() }

        findViewById<FloatingActionButton>(R.id.fabCreateInvoice).setOnClickListener {
            Toast.makeText(this, "Tính năng Tạo hóa đơn", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupRecyclerView() {
        val rvInvoices = findViewById<RecyclerView>(R.id.rvInvoices)
        rvInvoices.layoutManager = LinearLayoutManager(this)
        invoiceAdapter = InvoiceAdapter(emptyList()) { invoice ->
            Toast.makeText(this, "Hóa đơn ${invoice.roomName}", Toast.LENGTH_SHORT).show()
        }
        rvInvoices.adapter = invoiceAdapter
    }

    private fun setupFilters() {
        val month = Calendar.getInstance().get(Calendar.MONTH) + 1
        findViewById<TextView>(R.id.tvMonthFilter).text = "Tháng $month"

        findViewById<android.view.View>(R.id.btnMonthFilter).setOnClickListener {
            Toast.makeText(this, "Chọn tháng", Toast.LENGTH_SHORT).show()
        }
        findViewById<android.view.View>(R.id.btnFilter).setOnClickListener {
            Toast.makeText(this, "Bộ lọc", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupBottomNav() {
        findViewById<android.view.View>(R.id.navHome).setOnClickListener {
            startActivity(Intent(this, OwnerMainActivity::class.java))
            finish()
        }
        findViewById<android.view.View>(R.id.navManage).setOnClickListener {
            Toast.makeText(this, "Tính năng Quản lý", Toast.LENGTH_SHORT).show()
        }
        findViewById<android.view.View>(R.id.navSettings).setOnClickListener {
            Toast.makeText(this, "Tính năng Cài đặt", Toast.LENGTH_SHORT).show()
        }
    }

    private fun bindUiData() {
        val invoices = listOf(
            InvoiceItem("101", "Phòng 101", "Nguyễn Văn A", 1_200_000, false, "Hạn: 05/12/2025"),
            InvoiceItem("102", "Phòng 102", "Trần Thị B", 1_500_000, true, "Thanh toán: 02/12/2025"),
            InvoiceItem("201", "Phòng 201", "Lê Văn C", 1_100_000, false, "Hạn: 08/12/2025"),
            InvoiceItem("202", "Phòng 202", "Phạm Thị D", 1_800_000, true, "Thanh toán: 01/12/2025"),
        )
        invoiceAdapter.updateInvoices(invoices)

        val formatter = NumberFormat.getNumberInstance(Locale("vi", "VN"))
        findViewById<TextView>(R.id.tvTotalInvoices).text = "15"
        findViewById<TextView>(R.id.tvCollectedAmount).text = "${formatter.format(12_500_000)} đ"
        findViewById<TextView>(R.id.tvCollectedCount).text = "10 hóa đơn"
        findViewById<TextView>(R.id.tvUncollectedAmount).text = "${formatter.format(4_800_000)} đ"
        findViewById<TextView>(R.id.tvUncollectedCount).text = "5 hóa đơn"
    }
}
