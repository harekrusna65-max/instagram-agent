package com.example.instagramaistudio.util

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat

object NotificationHelper {
    private const val CHANNEL_ID = "instagram_ai_studio_channel"
    private const val CHANNEL_NAME = "Instagram Agent Uploads"
    private const val CHANNEL_DESC = "Notifications for automatic and manual Instagram uploads"

    fun init(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(CHANNEL_ID, CHANNEL_NAME, importance).apply {
                description = CHANNEL_DESC
                enableVibration(true)
                setShowBadge(true)
            }
            val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager
            notificationManager?.createNotificationChannel(channel)
        }
    }

    fun showNotification(
        context: Context,
        title: String,
        message: String,
        targetUrl: String? = null,
        notificationId: Int = System.currentTimeMillis().toInt()
    ) {
        init(context)

        val intent = if (!targetUrl.isNullOrBlank() && targetUrl.startsWith("http")) {
            Intent(Intent.ACTION_VIEW, Uri.parse(targetUrl))
        } else {
            val launchIntent = context.packageManager.getLaunchIntentForPackage(context.packageName)
            launchIntent ?: Intent(Intent.ACTION_VIEW, Uri.parse("https://instagram.com/stanger.man69"))
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
        )

        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)

        try {
            NotificationManagerCompat.from(context).notify(notificationId, builder.build())
        } catch (e: SecurityException) {
            // Android 13+ permission not granted
        } catch (e: Exception) {
            // Other notification errors
        }
    }
}
