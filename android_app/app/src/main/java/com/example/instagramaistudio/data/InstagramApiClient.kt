package com.example.instagramaistudio.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

data class ServerStatusData(
    val status: String = "online",
    val account: String = "@stanger.man69",
    val sessionAuthenticated: Boolean = true,
    val vaultQuotesReady: Int = 0,
    val istTime: String = "",
    val nextScheduledPost: String = "",
    val lastPostInfo: String = "None yet",
    val morningDone: Boolean = false,
    val afternoonDone: Boolean = false,
    val eveningDone: Boolean = false
)

data class ProfileStatsData(
    val followers: Int = 34,
    val totalUploads: Int = 10,
    val username: String = "stanger.man69"
)

data class ScheduledItemData(
    val id: Int,
    val mediaType: String,
    val scheduledTime: String,
    val status: String,
    val hook: String? = null,
    val quote: String? = null
)

data class GeneratedShayariData(
    val hook: String,
    val quote: String,
    val category: String
)

class InstagramApiClient(private val baseUrl: String = "https://instagram-agent-x9pn.onrender.com") {

    suspend fun generateShayari(topic: String = "sukoon"): Result<GeneratedShayariData> = withContext(Dispatchers.IO) {
        try {
            val json = getRequest("$baseUrl/api/generate/shayari?topic=${URLEncoder.encode(topic, "UTF-8")}")
            val obj = JSONObject(json)
            Result.success(
                GeneratedShayariData(
                    hook = obj.optString("hook", ""),
                    quote = obj.optString("quote", ""),
                    category = obj.optString("category", topic.uppercase())
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getStatus(): Result<ServerStatusData> = withContext(Dispatchers.IO) {
        try {
            val json = getRequest("$baseUrl/api/status")
            val obj = JSONObject(json)
            val slots = obj.optJSONObject("today_slots_published")
            Result.success(
                ServerStatusData(
                    status = obj.optString("status", "online"),
                    account = obj.optString("account", "@stanger.man69"),
                    sessionAuthenticated = obj.optBoolean("session_authenticated", true),
                    vaultQuotesReady = obj.optInt("vault_quotes_ready", 0),
                    istTime = obj.optString("ist_time", ""),
                    nextScheduledPost = obj.optString("next_scheduled_post", ""),
                    lastPostInfo = obj.optString("last_post_info", "None yet"),
                    morningDone = slots?.optBoolean("morning_reel") ?: false,
                    afternoonDone = slots?.optBoolean("afternoon_post") ?: false,
                    eveningDone = slots?.optBoolean("evening_reel") ?: false
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getProfileStats(): Result<ProfileStatsData> = withContext(Dispatchers.IO) {
        try {
            val json = getRequest("$baseUrl/stats")
            val obj = JSONObject(json)
            val profile = obj.optJSONObject("profile")
            Result.success(
                ProfileStatsData(
                    followers = profile?.optInt("follower_count") ?: 34,
                    totalUploads = profile?.optInt("media_count") ?: 10,
                    username = profile?.optString("username", "stanger.man69") ?: "stanger.man69"
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun triggerReel(hook: String? = null, quote: String? = null): Result<String> = withContext(Dispatchers.IO) {
        try {
            val params = mutableListOf<String>()
            if (!hook.isNullOrBlank()) params.add("hook=${URLEncoder.encode(hook, "UTF-8")}")
            if (!quote.isNullOrBlank()) params.add("quote=${URLEncoder.encode(quote, "UTF-8")}")
            val query = if (params.isNotEmpty()) "?" + params.joinToString("&") else ""
            val json = postRequest("$baseUrl/trigger/reel$query", "")
            val obj = JSONObject(json)
            Result.success(obj.optString("message", "Reel triggered successfully!"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun triggerPost(quote: String? = null, category: String? = null): Result<String> = withContext(Dispatchers.IO) {
        try {
            val params = mutableListOf<String>()
            if (!quote.isNullOrBlank()) params.add("quote=${URLEncoder.encode(quote, "UTF-8")}")
            if (!category.isNullOrBlank()) params.add("category=${URLEncoder.encode(category, "UTF-8")}")
            val query = if (params.isNotEmpty()) "?" + params.joinToString("&") else ""
            val json = postRequest("$baseUrl/trigger/post$query", "")
            val obj = JSONObject(json)
            Result.success(obj.optString("message", "Post triggered successfully!"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getScheduledList(): Result<List<ScheduledItemData>> = withContext(Dispatchers.IO) {
        try {
            val json = getRequest("$baseUrl/api/schedule/list")
            val obj = JSONObject(json)
            val arr = obj.optJSONArray("items") ?: JSONArray()
            val list = mutableListOf<ScheduledItemData>()
            for (i in 0 until arr.length()) {
                val item = arr.getJSONObject(i)
                list.add(
                    ScheduledItemData(
                        id = item.getInt("id"),
                        mediaType = item.optString("media_type", "reel"),
                        scheduledTime = item.optString("scheduled_time", ""),
                        status = item.optString("status", "pending"),
                        hook = if (item.isNull("hook")) null else item.optString("hook"),
                        quote = if (item.isNull("quote")) null else item.optString("quote")
                    )
                )
            }
            Result.success(list)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun schedulePost(
        mediaType: String,
        scheduledTime: String,
        hook: String? = null,
        quote: String? = null
    ): Result<String> = withContext(Dispatchers.IO) {
        try {
            val body = JSONObject().apply {
                put("media_type", mediaType)
                put("scheduled_time", scheduledTime)
                if (!hook.isNullOrBlank()) put("hook", hook)
                if (!quote.isNullOrBlank()) put("quote", quote)
            }
            val json = postJsonRequest("$baseUrl/api/schedule", body.toString())
            val obj = JSONObject(json)
            if (obj.optString("status") == "success") {
                Result.success(obj.optString("message", "Scheduled successfully!"))
            } else {
                Result.failure(Exception(obj.optString("message", "Scheduling failed")))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteScheduledItem(id: Int): Result<String> = withContext(Dispatchers.IO) {
        try {
            val json = postRequest("$baseUrl/api/schedule/delete/$id", "")
            val obj = JSONObject(json)
            Result.success(obj.optString("message", "Deleted item #$id"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun getRequest(urlStr: String): String {
        val url = URL(urlStr)
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 15000
            readTimeout = 15000
            setRequestProperty("User-Agent", "InstagramAgentAndroid/1.0")
        }
        return conn.inputStream.bufferedReader().use(BufferedReader::readText)
    }

    private fun postRequest(urlStr: String, body: String): String {
        val url = URL(urlStr)
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 15000
            readTimeout = 15000
            doOutput = true
            setRequestProperty("User-Agent", "InstagramAgentAndroid/1.0")
        }
        if (body.isNotEmpty()) {
            OutputStreamWriter(conn.outputStream).use { it.write(body) }
        }
        return conn.inputStream.bufferedReader().use(BufferedReader::readText)
    }

    private fun postJsonRequest(urlStr: String, jsonBody: String): String {
        val url = URL(urlStr)
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 15000
            readTimeout = 15000
            doOutput = true
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("User-Agent", "InstagramAgentAndroid/1.0")
        }
        OutputStreamWriter(conn.outputStream).use { it.write(jsonBody) }
        return conn.inputStream.bufferedReader().use(BufferedReader::readText)
    }
}
