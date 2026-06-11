package com.example.quanlyphongtro.network

import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // ── Auth ────────────────────────────────────────────────────
    @POST("auth/login/")
    suspend fun login(@Body body: LoginRequest): Response<AuthResponse>

    @POST("auth/register/")
    suspend fun register(@Body body: RegisterRequest): Response<AuthResponse>

    // ── Rooms ───────────────────────────────────────────────────
    @GET("api/rooms/")
    suspend fun getRooms(@Header("Authorization") token: String): Response<List<RoomResponse>>

    @POST("api/rooms/")
    suspend fun createRoom(
        @Header("Authorization") token: String,
        @Body body: RoomRequest
    ): Response<RoomResponse>

    @GET("api/rooms/{room_id}/")
    suspend fun getRoomDetail(
        @Header("Authorization") token: String,
        @Path("room_id") roomId: Int
    ): Response<RoomResponse>

    @PUT("api/rooms/{room_id}/")
    suspend fun updateRoom(
        @Header("Authorization") token: String,
        @Path("room_id") roomId: Int,
        @Body body: RoomRequest
    ): Response<RoomResponse>

    @DELETE("api/rooms/{room_id}/")
    suspend fun deleteRoom(
        @Header("Authorization") token: String,
        @Path("room_id") roomId: Int
    ): Response<Void>

    @POST("api/rooms/{room_id}/remove/")
    suspend fun removeTenant(
        @Header("Authorization") token: String,
        @Path("room_id") roomId: Int
    ): Response<Void>
}
