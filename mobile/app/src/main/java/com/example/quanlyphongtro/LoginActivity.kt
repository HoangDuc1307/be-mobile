package com.example.quanlyphongtro

import android.content.Intent
import android.os.Bundle
import android.text.method.PasswordTransformationMethod
import android.text.method.SingleLineTransformationMethod
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.quanlyphongtro.network.LoginRequest
import com.example.quanlyphongtro.network.RetrofitClient
import com.example.quanlyphongtro.network.SessionManager
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {

    private var isPasswordVisible = false
    private lateinit var session: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        session = SessionManager(this)

        // Nếu đã đăng nhập rồi và là chủ trọ → vào thẳng OwnerMainActivity
        if (session.isLoggedIn()) {
            if (session.isOwner()) {
                navigateAfterLogin()
                return
            } else {
                session.clearSession()
            }
        }

        val etUsername       = findViewById<EditText>(R.id.etUsername)
        val etPassword       = findViewById<EditText>(R.id.etPassword)
        val ivTogglePassword = findViewById<ImageView>(R.id.ivTogglePassword)
        val btnLogin         = findViewById<Button>(R.id.btnLogin)
        val btnRegister      = findViewById<Button>(R.id.btnRegister)
        val tvForgotPassword = findViewById<TextView>(R.id.tvForgotPassword)

        // Toggle hiện/ẩn mật khẩu
        ivTogglePassword.setOnClickListener {
            isPasswordVisible = !isPasswordVisible
            if (isPasswordVisible) {
                etPassword.transformationMethod = SingleLineTransformationMethod.getInstance()
                ivTogglePassword.setImageResource(R.drawable.ic_eye_off)
            } else {
                etPassword.transformationMethod = PasswordTransformationMethod.getInstance()
                ivTogglePassword.setImageResource(R.drawable.ic_eye)
            }
            etPassword.setSelection(etPassword.text?.length ?: 0)
        }

        // Nút đăng nhập
        btnLogin.setOnClickListener {
            val username = etUsername.text.toString().trim()
            val password = etPassword.text.toString().trim()

            if (username.isEmpty()) {
                etUsername.error = "Vui lòng nhập tên đăng nhập"
                return@setOnClickListener
            }
            if (password.isEmpty()) {
                etPassword.error = "Vui lòng nhập mật khẩu"
                return@setOnClickListener
            }

            btnLogin.isEnabled = false
            btnLogin.text = "Đang đăng nhập..."

            lifecycleScope.launch {
                try {
                    val response = RetrofitClient.api.login(LoginRequest(username, password))
                    if (response.isSuccessful && response.body() != null) {
                        val authResponse = response.body()!!
                        if (authResponse.user.is_owner) {
                            session.saveSession(authResponse)
                            navigateAfterLogin()
                        } else {
                            Toast.makeText(
                                this@LoginActivity,
                                "Tài khoản không phải là Chủ trọ!",
                                Toast.LENGTH_LONG
                            ).show()
                            btnLogin.isEnabled = true
                            btnLogin.text = "Đăng nhập"
                        }
                    } else {
                        Toast.makeText(
                            this@LoginActivity,
                            "Sai tên đăng nhập hoặc mật khẩu",
                            Toast.LENGTH_SHORT
                        ).show()
                        btnLogin.isEnabled = true
                        btnLogin.text = "Đăng nhập"
                    }
                } catch (e: Exception) {
                    Toast.makeText(
                        this@LoginActivity,
                        "Không thể kết nối server. Kiểm tra lại mạng!",
                        Toast.LENGTH_SHORT
                    ).show()
                    btnLogin.isEnabled = true
                    btnLogin.text = "Đăng nhập"
                }
            }
        }

        // Nút đăng ký
        btnRegister.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }

        // Quên mật khẩu
        tvForgotPassword.setOnClickListener {
            // TODO: Mở màn hình quên mật khẩu
        }
    }

    private fun navigateAfterLogin() {
        val intent = Intent(this, OwnerMainActivity::class.java)
        startActivity(intent)
        finish()
    }
}