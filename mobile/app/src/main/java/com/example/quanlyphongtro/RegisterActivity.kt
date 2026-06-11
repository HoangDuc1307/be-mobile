package com.example.quanlyphongtro

import android.content.Intent
import android.os.Bundle
import android.text.method.PasswordTransformationMethod
import android.text.method.SingleLineTransformationMethod
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class RegisterActivity : AppCompatActivity() {

    private var isPasswordVisible = false
    private var isConfirmPasswordVisible = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        val etFullName = findViewById<EditText>(R.id.etFullName)
        val etPhone = findViewById<EditText>(R.id.etPhone)
        val etEmail = findViewById<EditText>(R.id.etEmail)
        val etPassword = findViewById<EditText>(R.id.etPassword)
        val etConfirmPassword = findViewById<EditText>(R.id.etConfirmPassword)
        val ivTogglePassword = findViewById<ImageView>(R.id.ivTogglePassword)
        val ivToggleConfirmPassword = findViewById<ImageView>(R.id.ivToggleConfirmPassword)
        val btnRegister = findViewById<Button>(R.id.btnRegister)
        val tvLoginLink = findViewById<TextView>(R.id.tvLoginLink)

        // Toggle hiện/ẩn mật khẩu
        ivTogglePassword.setOnClickListener {
            isPasswordVisible = !isPasswordVisible
            etPassword.transformationMethod = if (isPasswordVisible)
                SingleLineTransformationMethod.getInstance()
            else
                PasswordTransformationMethod.getInstance()
            ivTogglePassword.setImageResource(
                if (isPasswordVisible) R.drawable.ic_eye_off else R.drawable.ic_eye
            )
            etPassword.setSelection(etPassword.text?.length ?: 0)
        }

        // Toggle hiện/ẩn xác nhận mật khẩu
        ivToggleConfirmPassword.setOnClickListener {
            isConfirmPasswordVisible = !isConfirmPasswordVisible
            etConfirmPassword.transformationMethod = if (isConfirmPasswordVisible)
                SingleLineTransformationMethod.getInstance()
            else
                PasswordTransformationMethod.getInstance()
            ivToggleConfirmPassword.setImageResource(
                if (isConfirmPasswordVisible) R.drawable.ic_eye_off else R.drawable.ic_eye
            )
            etConfirmPassword.setSelection(etConfirmPassword.text?.length ?: 0)
        }

        // Nút Đăng ký
        btnRegister.setOnClickListener {
            val fullName = etFullName.text.toString().trim()
            val phone = etPhone.text.toString().trim()
            val email = etEmail.text.toString().trim()
            val password = etPassword.text.toString().trim()
            val confirmPassword = etConfirmPassword.text.toString().trim()

            // Validate
            if (fullName.isEmpty()) {
                etFullName.error = "Vui lòng nhập họ tên"
                return@setOnClickListener
            }
            if (phone.isEmpty()) {
                etPhone.error = "Vui lòng nhập số điện thoại"
                return@setOnClickListener
            }
            if (email.isEmpty()) {
                etEmail.error = "Vui lòng nhập email"
                return@setOnClickListener
            }
            if (password.isEmpty()) {
                etPassword.error = "Vui lòng nhập mật khẩu"
                return@setOnClickListener
            }
            if (password.length < 6) {
                etPassword.error = "Mật khẩu tối thiểu 6 ký tự"
                return@setOnClickListener
            }
            if (password != confirmPassword) {
                etConfirmPassword.error = "Mật khẩu xác nhận không khớp"
                return@setOnClickListener
            }

            // TODO: Gọi API đăng ký ở đây
            // Sau khi đăng ký thành công:
            // startActivity(Intent(this, LoginActivity::class.java))
            // finish()
        }

        // Link quay về đăng nhập
        tvLoginLink.setOnClickListener {
            finish() // Quay về LoginActivity
        }
    }
}
