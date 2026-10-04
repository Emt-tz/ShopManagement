plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}
android {
    namespace = "app.emtshop.mobile"
    compileSdk = 34
    defaultConfig {
        applicationId = "app.emtshop.mobile"; minSdk = 26; targetSdk = 34; versionCode = 1; versionName = "0.1.0"
        // 10.0.2.2 is the host machine from the Android emulator. Override for a real server: -PemtshopUrl=https://...
        buildConfigField("String", "BASE_URL", "\"${(project.findProperty("emtshopUrl") as String?) ?: "http://10.0.2.2:8080"}\"")
    }
    buildFeatures { compose = true; buildConfig = true }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.09.03"))
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.activity:activity-compose:1.9.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.6")
    implementation("androidx.navigation:navigation-compose:2.8.2")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
    testImplementation("junit:junit:4.13.2")
}
