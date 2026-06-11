package com.example.quanlyphongtro.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {

    // Android Emulator: 10.0.2.2 trỏ về localhost của máy host
    // Điện thoại thật: thay bằng IP máy tính trong cùng WiFi
    private const val BASE_URL = "http://192.168.1.4:8000/"

    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
