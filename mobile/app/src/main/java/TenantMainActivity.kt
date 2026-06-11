package com.example.quanlyphongtro

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity

class TenantMainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_tenant_main)

        val btnPayNow = findViewById<Button>(R.id.btnPayNow)
        val btnMessage = findViewById<Button>(R.id.btnMessage)
        val btnCall = findViewById<Button>(R.id.btnCall)
        val navHome = findViewById<LinearLayout>(R.id.navHome)
        val navManage = findViewById<LinearLayout>(R.id.navManage)
        val navNotify = findViewById<LinearLayout>(R.id.navNotify)
        val navSettings = findViewById<LinearLayout>(R.id.navSettings)

        // Thanh toán ngay
        btnPayNow.setOnClickListener {
            // TODO: Mở màn hình thanh toán
        }

        // Nhắn tin cho chủ nhà
        btnMessage.setOnClickListener {
            val phone = "0901234567"
            val smsIntent = Intent(Intent.ACTION_SENDTO).apply {
                data = Uri.parse("smsto:$phone")
            }
            startActivity(smsIntent)
        }

        // Gọi cho chủ nhà
        btnCall.setOnClickListener {
            val phone = "0901234567"
            val callIntent = Intent(Intent.ACTION_DIAL).apply {
                data = Uri.parse("tel:$phone")
            }
            startActivity(callIntent)
        }

        // Bottom Navigation
        navHome.setOnClickListener { /* Đang ở trang chủ */ }
        navManage.setOnClickListener {
            startActivity(Intent(this, ContractActivity::class.java))
        }
        navNotify.setOnClickListener {
            // TODO: startActivity(Intent(this, NotifyActivity::class.java))
        }
        navSettings.setOnClickListener {
            // TODO: startActivity(Intent(this, SettingsActivity::class.java))
        }
    }
}
