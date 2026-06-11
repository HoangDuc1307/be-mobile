package com.example.quanlyphongtro.network

// ── Request bodies ──────────────────────────────────────────────
data class LoginRequest(
    val username: String,
    val password: String
)

data class RegisterRequest(
    val username: String,
    val password: String,
    val email: String = "",
    val phone: String = ""
)

// ── Response bodies ─────────────────────────────────────────────
data class UserResponse(
    val id: Int,
    val username: String,
    val email: String,
    val phone: String?,
    val is_owner: Boolean
)

data class AuthResponse(
    val user: UserResponse,
    val access: String,
    val refresh: String
)

data class RoomResponse(
    val id: Int,
    val name: String,
    val price: String,
    val area: Double,
    val status: String,          // "available" | "occupied"
    val description: String,
    val created_at: String,
    val tenant_name: String?,
    val tenant_phone: String?,
    val move_in: String?,
    val deposit: String?
)

data class ErrorResponse(
    val error: String
)

data class RoomRequest(
    val name: String,
    val price: String,
    val area: Double,
    val status: String,
    val description: String
)
