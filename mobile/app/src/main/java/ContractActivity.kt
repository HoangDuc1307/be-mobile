package com.example.quanlyphongtro

import android.content.Intent
import android.os.Bundle
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView

class ContractActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_contract)

        val btnBack = findViewById<ImageView>(R.id.btnBack)
        val fabDownload = findViewById<CardView>(R.id.fabDownload)
        val navHome = findViewById<LinearLayout>(R.id.navHome)
        val navContract = findViewById<LinearLayout>(R.id.navContract)
        val navNotify = findViewById<LinearLayout>(R.id.navNotify)
        val navSettings = findViewById<LinearLayout>(R.id.navSettings)

        // Nhận data từ Intent
        val signDate = intent.getStringExtra("sign_date") ?: "15/10/2023"
        val duration = intent.getStringExtra("duration") ?: "12 tháng"
        val landlordName = intent.getStringExtra("landlord_name") ?: "Nguyễn Văn A"
        val tenantName = intent.getStringExtra("tenant_name") ?: "Trần Thị B"

        // Set data
        findViewById<TextView>(R.id.tvSignDate).text = signDate
        findViewById<TextView>(R.id.tvDuration).text = duration
        findViewById<TextView>(R.id.tvLandlordName).text = landlordName
        findViewById<TextView>(R.id.tvTenantName).text = tenantName

        // Quay lại
        btnBack.setOnClickListener { finish() }

        // Tải hợp đồng
        fabDownload.setOnClickListener {
            // TODO: Tải file PDF hợp đồng về máy
        }

        // Bottom Navigation
        navHome.setOnClickListener {
            startActivity(Intent(this, TenantMainActivity::class.java))
            finish()
        }
        navContract.setOnClickListener {
            // Đang ở màn này rồi, không cần làm gì
        }
        navNotify.setOnClickListener {
            // TODO: startActivity(Intent(this, NotifyActivity::class.java))
        }
        navSettings.setOnClickListener {
            // TODO: startActivity(Intent(this, SettingsActivity::class.java))
        }
    }
}