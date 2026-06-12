import java.net.NetworkInterface
import java.net.Inet4Address
import java.util.Collections

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
}

fun getLocalIpAddress(): String {
    try {
        val interfaces = Collections.list(NetworkInterface.getNetworkInterfaces())
        for (netInt in interfaces) {
            if (!netInt.isUp || netInt.isLoopback || netInt.isVirtual) continue
            
            val name = netInt.name.lowercase()
            val displayName = netInt.displayName.lowercase()
            
            // Loại bỏ hoàn toàn card mạng ảo (VMware, VirtualBox, WSL, Hyper-V)
            if (name.contains("vbox") || name.contains("vmnet") || name.contains("wsl") || name.contains("virtual") ||
                displayName.contains("virtual") || displayName.contains("vmware") || displayName.contains("virtualbox") || displayName.contains("host-only") || displayName.contains("hyper-v")) {
                continue
            }
            
            val addresses = Collections.list(netInt.inetAddresses)
            for (addr in addresses) {
                if (addr is java.net.Inet4Address && !addr.isLoopbackAddress) {
                    val ip = addr.hostAddress
                    if (ip.startsWith("192.168.") || ip.startsWith("10.") || ip.startsWith("172.")) {
                        return ip
                    }
                }
            }
        }
    } catch (e: Exception) {
        // Fallback
    }
    return "192.168.1.4" // IP mặc định cũ
}

android {
    namespace = "com.example.quanlyphongtro"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.quanlyphongtro"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        
        // Tự động dò và nhúng IP máy tính khi build
        val localIp = getLocalIpAddress()
        buildConfigField("String", "BACKEND_IP", "\"$localIp\"")
    }

    buildFeatures {
        buildConfig = true
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
}

dependencies {
    implementation(libs.androidx.activity.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.androidx.constraintlayout)
    implementation(libs.androidx.core.ktx)
    implementation(libs.material)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)
    implementation("androidx.cardview:cardview:1.0.0")
    implementation("androidx.appcompat:appcompat:1.6.1")

    // Retrofit - gọi API
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")

    // Coroutines - xử lý bất đồng bộ
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}