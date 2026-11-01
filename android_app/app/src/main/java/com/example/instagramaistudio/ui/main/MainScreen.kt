package com.example.instagramaistudio.ui.main

import android.content.Intent
import android.net.Uri
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation3.runtime.NavKey
import com.example.instagramaistudio.data.ScheduledItemData
import com.example.instagramaistudio.theme.*
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun MainScreen(
    onItemClick: (NavKey) -> Unit = {},
    modifier: Modifier = Modifier,
    viewModel: MainScreenViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current

    Scaffold(
        modifier = modifier
            .fillMaxSize()
            .navigationBarsPadding(),
        containerColor = DeepSpace,
        topBar = {
            TopAppBarGlass(
                status = state.status.status,
                isRefreshing = state.isRefreshing,
                onRefresh = { viewModel.refreshAll() },
                onOpenProfile = {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://instagram.com/stanger.man69"))
                    context.startActivity(intent)
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Mode Tabs (Native Studio vs Web Dashboard)
            TabRow(
                selectedTabIndex = state.selectedTab,
                containerColor = CardBg,
                contentColor = PurpleAccent,
                modifier = Modifier.fillMaxWidth()
            ) {
                Tab(
                    selected = state.selectedTab == 0,
                    onClick = { viewModel.selectTab(0) },
                    text = { Text("⚡ Native Studio", fontWeight = FontWeight.Bold, fontSize = 13.sp) }
                )
                Tab(
                    selected = state.selectedTab == 1,
                    onClick = { viewModel.selectTab(1) },
                    text = { Text("🌐 Web Dashboard", fontWeight = FontWeight.Bold, fontSize = 13.sp) }
                )
            }

            // Action Feedback Banner
            state.actionMessage?.let { msg ->
                val bg = if (state.isError) Color(0x33EF4444) else EmeraldBg
                val fg = if (state.isError) RedFailed else EmeraldGreen
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(bg)
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(msg, color = fg, fontSize = 12.sp, modifier = Modifier.weight(1f))
                    Text(
                        "✕",
                        color = fg,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier
                            .clickable { viewModel.clearMessage() }
                            .padding(4.dp)
                    )
                }
            }

            if (state.selectedTab == 1) {
                // Cloud Web Dashboard View
                WebDashboardView(url = "https://instagram-agent-x9pn.onrender.com/")
            } else {
                // Native Studio View
                NativeStudioView(
                    state = state,
                    viewModel = viewModel
                )
            }
        }
    }
}

@Composable
fun TopAppBarGlass(
    status: String,
    isRefreshing: Boolean,
    onRefresh: () -> Unit,
    onOpenProfile: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(CardBg)
            .statusBarsPadding()
            .padding(horizontal = 16.dp, vertical = 10.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.weight(1f)
        ) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(
                        Brush.linearGradient(
                            listOf(Color(0xFF833AB4), Color(0xFFFD1D1D), Color(0xFFFCB045))
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text("📷", fontSize = 17.sp)
            }

            Column {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("Instagram AI Studio", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(6.dp))
                            .background(EmeraldBg)
                            .padding(horizontal = 5.dp, vertical = 2.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(3.dp)) {
                            Box(modifier = Modifier.size(5.dp).clip(CircleShape).background(EmeraldGreen))
                            Text("24/7 Cloud", color = EmeraldGreen, fontSize = 9.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
                Text("@stanger.man69 • Autopilot", color = TextMuted, fontSize = 11.sp)
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onRefresh, modifier = Modifier.size(34.dp)) {
                if (isRefreshing) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp), color = PurpleAccent, strokeWidth = 2.dp)
                } else {
                    Text("🔄", fontSize = 15.sp)
                }
            }

            Button(
                onClick = onOpenProfile,
                colors = ButtonDefaults.buttonColors(containerColor = CardBgLight),
                shape = RoundedCornerShape(10.dp),
                contentPadding = PaddingValues(horizontal = 9.dp, vertical = 4.dp),
                modifier = Modifier.height(32.dp)
            ) {
                Text("IG ↗", color = TextPrimary, fontSize = 11.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun NativeStudioView(
    state: InstagramStudioUiState,
    viewModel: MainScreenViewModel
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 48.dp)
    ) {
        // 1. Stats Row
        item {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                StatCard(title = "Followers", value = "${state.stats.followers}", subtitle = "Live Sync", modifier = Modifier.weight(1f))
                StatCard(title = "Uploads", value = "${state.stats.totalUploads}", subtitle = "Posts & Reels", modifier = Modifier.weight(1f))
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                StatCard(
                    title = "Next Slot",
                    value = if (state.status.nextScheduledPost.isNotBlank()) state.status.nextScheduledPost else "Slot Window Active",
                    subtitle = state.status.istTime.ifBlank { "IST Autopilot" },
                    modifier = Modifier.weight(1f)
                )
                StatCard(title = "Uptime", value = "100% Online", subtitle = "Render Cloud", modifier = Modifier.weight(1f))
            }
        }

        // 2. Today's Autopilot Slot Tracker
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = CardBg),
                shape = RoundedCornerShape(18.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, CardBorder, RoundedCornerShape(18.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Today's Slot Catch-Up Tracker", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        SlotBadge(name = "Morning (11 AM)", isDone = state.status.morningDone)
                        SlotBadge(name = "Afternoon (3 PM)", isDone = state.status.afternoonDone)
                        SlotBadge(name = "Evening (7 PM)", isDone = state.status.eveningDone)
                    }
                }
            }
        }

        // 2b. Viral Growth & Comment-to-DM Bot
        item {
            GrowthBotCard(
                isLoading = state.isActionLoading,
                onScanNow = { viewModel.triggerGrowthScan() }
            )
        }

        // 3. Instant 1-Click Publishing Hub
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = CardBg),
                shape = RoundedCornerShape(18.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, CardBorder, RoundedCornerShape(18.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Instant 1-Click Publishing Hub", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text("Trigger immediate AI generation and publish directly to Instagram", color = TextMuted, fontSize = 11.sp)

                    Button(
                        onClick = { viewModel.triggerReelNow() },
                        enabled = !state.isActionLoading,
                        colors = ButtonDefaults.buttonColors(containerColor = PurpleAccent),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(46.dp)
                    ) {
                        Text("🎬 Create & Post 12s Reel NOW", fontWeight = FontWeight.Bold, fontSize = 13.sp)
                    }

                    Button(
                        onClick = { viewModel.triggerPostNow() },
                        enabled = !state.isActionLoading,
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3B82F6)),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(46.dp)
                    ) {
                        Text("🖼️ Create & Post Image NOW", fontWeight = FontWeight.Bold, fontSize = 13.sp)
                    }
                }
            }
        }

        // 4. Custom Shayari Studio
        item {
            CustomShayariCard(
                isLoading = state.isActionLoading,
                onGenerate = { topic, onResult -> viewModel.generateShayari(topic, onResult) },
                onPublish = { isReel, hook, quote -> viewModel.publishCustom(isReel, hook, quote) }
            )
        }

        // 5. Schedule Future Post Studio
        item {
            ScheduleContentCard(
                isLoading = state.isActionLoading,
                onSchedule = { type, time, hook, quote -> viewModel.scheduleItem(type, time, hook, quote) }
            )
        }

        // 6. Live Scheduled Queue
        item {
            ScheduledQueueCard(
                items = state.queue,
                onCancel = { id -> viewModel.cancelScheduled(id) }
            )
        }
    }
}

@Composable
fun StatCard(title: String, value: String, subtitle: String, modifier: Modifier = Modifier) {
    Card(
        colors = CardDefaults.cardColors(containerColor = CardBg),
        shape = RoundedCornerShape(16.dp),
        modifier = modifier.border(1.dp, CardBorder, RoundedCornerShape(16.dp))
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(title, color = TextMuted, fontSize = 11.sp)
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = value,
                color = Color.White,
                fontWeight = FontWeight.Bold,
                fontSize = if (value.length > 14) 12.sp else 16.sp,
                lineHeight = if (value.length > 14) 15.sp else 20.sp,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(subtitle, color = PurpleAccent, fontSize = 10.sp, maxLines = 1)
        }
    }
}

@Composable
fun SlotBadge(name: String, isDone: Boolean) {
    val bg = if (isDone) EmeraldBg else CardBgLight
    val fg = if (isDone) EmeraldGreen else TextMuted
    val icon = if (isDone) "✓ Done" else "⏳ Waiting"

    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(bg)
            .padding(horizontal = 8.dp, vertical = 6.dp)
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(name.split(" ")[0], color = Color.White, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
            Text(icon, color = fg, fontSize = 10.sp)
        }
    }
}

@Composable
fun GrowthBotCard(isLoading: Boolean, onScanNow: () -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = CardBg),
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, CardBorder, RoundedCornerShape(18.dp))
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("🚀 Viral Growth Bot", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Box(modifier = Modifier.clip(RoundedCornerShape(4.dp)).background(AmberBg).padding(horizontal = 6.dp, vertical = 2.dp)) {
                        Text("Active", color = AmberPending, fontSize = 9.sp, fontWeight = FontWeight.Bold)
                    }
                }
                Text("Comment-to-DM", color = TextMuted, fontSize = 11.sp)
            }
            Text(
                "Auto-likes comments & sends instant DMs for keywords: SUKOON, SHAYARI, LINK",
                color = TextMuted,
                fontSize = 11.sp
            )
            Button(
                onClick = onScanNow,
                enabled = !isLoading,
                colors = ButtonDefaults.buttonColors(containerColor = CardBgLight),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(36.dp)
            ) {
                Text("🔍 Scan Comments & DMs NOW", color = TextPrimary, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
            }
        }
    }
}

@Composable
fun CustomShayariCard(
    isLoading: Boolean,
    onGenerate: (topic: String, onResult: (hook: String, quote: String) -> Unit) -> Unit,
    onPublish: (isReel: Boolean, hook: String?, quote: String) -> Unit
) {
    var hook by remember { mutableStateOf("") }
    var quote by remember { mutableStateOf("") }

    Card(
        colors = CardDefaults.cardColors(containerColor = CardBg),
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, CardBorder, RoundedCornerShape(18.dp))
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("✍️ Custom Shayari Studio", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp)
            Text("Type lines below, or tap an AI Mood to auto-fill:", color = TextMuted, fontSize = 11.sp)

            // 1-Tap AI Mood Chips (Horizontal Scroll)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                PresetChip("⚡ Attitude") { onGenerate("attitude") { h, q -> hook = h; quote = q } }
                PresetChip("🌙 Sukoon") { onGenerate("sukoon") { h, q -> hook = h; quote = q } }
                PresetChip("❤️ Mohabbat") { onGenerate("mohabbat") { h, q -> hook = h; quote = q } }
                PresetChip("🥀 Tanhai") { onGenerate("tanhai") { h, q -> hook = h; quote = q } }
                PresetChip("⏳ Zindagi") { onGenerate("zindagi") { h, q -> hook = h; quote = q } }
                PresetChip("🔥 Success") { onGenerate("success") { h, q -> hook = h; quote = q } }
            }

            OutlinedTextField(
                value = hook,
                onValueChange = { hook = it },
                label = { Text("Hook Line (e.g. Ye baat yaad rakhna...)") },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White,
                    focusedBorderColor = PurpleAccent,
                    unfocusedBorderColor = CardBorder,
                    focusedContainerColor = InputBg,
                    unfocusedContainerColor = InputBg
                ),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            )

            OutlinedTextField(
                value = quote,
                onValueChange = { quote = it },
                label = { Text("Shayari / Quote Text (Gold Highlight)") },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White,
                    focusedBorderColor = PurpleAccent,
                    unfocusedBorderColor = CardBorder,
                    focusedContainerColor = InputBg,
                    unfocusedContainerColor = InputBg
                ),
                shape = RoundedCornerShape(12.dp),
                minLines = 2,
                maxLines = 4,
                modifier = Modifier.fillMaxWidth()
            )

            Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                Button(
                    onClick = { onPublish(true, hook.ifBlank { null }, quote) },
                    enabled = !isLoading && quote.isNotBlank(),
                    colors = ButtonDefaults.buttonColors(containerColor = PurpleAccent),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Publish Reel", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                }
                Button(
                    onClick = { onPublish(false, hook.ifBlank { null }, quote) },
                    enabled = !isLoading && quote.isNotBlank(),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF6366F1)),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Publish Image", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
fun ScheduleContentCard(
    isLoading: Boolean,
    onSchedule: (type: String, time: String, hook: String?, quote: String?) -> Unit
) {
    var mediaType by remember { mutableStateOf("reel") }
    var scheduledTime by remember { mutableStateOf(getFutureIST(2)) }
    var isCustom by remember { mutableStateOf(false) }
    var hook by remember { mutableStateOf("") }
    var quote by remember { mutableStateOf("") }

    Card(
        colors = CardDefaults.cardColors(containerColor = CardBg),
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, CardBorder, RoundedCornerShape(18.dp))
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("📅 Schedule Post / Reel (IST)", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp)
            Text("Pick a future time. Cloud agent will auto-publish.", color = TextMuted, fontSize = 11.sp)

            // Format Selection
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(
                    selected = mediaType == "reel",
                    onClick = { mediaType = "reel" },
                    label = { Text("🎬 12s Reel") },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = PurpleAccent,
                        selectedLabelColor = Color.White
                    ),
                    modifier = Modifier.weight(1f)
                )
                FilterChip(
                    selected = mediaType == "post",
                    onClick = { mediaType = "post" },
                    label = { Text("🖼️ Image Post") },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = PinkAccent,
                        selectedLabelColor = Color.White
                    ),
                    modifier = Modifier.weight(1f)
                )
            }

            // Quick Presets with Horizontal Scroll
            Text("Quick Presets (IST):", color = TextMuted, fontSize = 11.sp)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                PresetChip("+2 Hours") { scheduledTime = getFutureIST(2) }
                PresetChip("Tomorrow 11 AM") { scheduledTime = getTomorrowIST(11, 0) }
                PresetChip("Tomorrow 3 PM") { scheduledTime = getTomorrowIST(15, 0) }
                PresetChip("Tomorrow 7 PM") { scheduledTime = getTomorrowIST(19, 0) }
            }

            // Target DateTime Input
            OutlinedTextField(
                value = scheduledTime,
                onValueChange = { scheduledTime = it },
                label = { Text("Scheduled Time (YYYY-MM-DD HH:MM)") },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White,
                    focusedBorderColor = PurpleAccent,
                    unfocusedBorderColor = CardBorder,
                    focusedContainerColor = InputBg,
                    unfocusedContainerColor = InputBg
                ),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            )

            // Content Source Toggle
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    if (isCustom) "✍️ Custom Lines" else "🤖 Auto AI Vault Shayari",
                    color = GoldAccent,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold
                )
                TextButton(onClick = { isCustom = !isCustom }) {
                    Text(if (isCustom) "Switch to Auto AI" else "Switch to Custom", color = PurpleAccent, fontSize = 11.sp)
                }
            }

            if (isCustom) {
                OutlinedTextField(
                    value = hook,
                    onValueChange = { hook = it },
                    label = { Text("Custom Hook (Optional)") },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = Color.White,
                        unfocusedTextColor = Color.White,
                        focusedBorderColor = PurpleAccent,
                        unfocusedBorderColor = CardBorder,
                        focusedContainerColor = InputBg,
                        unfocusedContainerColor = InputBg
                    ),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.fillMaxWidth()
                )
                OutlinedTextField(
                    value = quote,
                    onValueChange = { quote = it },
                    label = { Text("Custom Shayari Text") },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = Color.White,
                        unfocusedTextColor = Color.White,
                        focusedBorderColor = PurpleAccent,
                        unfocusedBorderColor = CardBorder,
                        focusedContainerColor = InputBg,
                        unfocusedContainerColor = InputBg
                    ),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.fillMaxWidth()
                )
            }

            Button(
                onClick = {
                    onSchedule(mediaType, scheduledTime, hook.ifBlank { null }, quote.ifBlank { null })
                },
                enabled = !isLoading,
                colors = ButtonDefaults.buttonColors(containerColor = PurpleAccent),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(46.dp)
            ) {
                Text("Schedule Post (IST)", fontWeight = FontWeight.Bold, fontSize = 13.sp)
            }
        }
    }
}

@Composable
fun PresetChip(text: String, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(CardBgLight)
            .clickable(onClick = onClick)
            .padding(horizontal = 10.dp, vertical = 6.dp)
    ) {
        Text(text, color = TextPrimary, fontSize = 11.sp, fontWeight = FontWeight.Medium, maxLines = 1)
    }
}

@Composable
fun ScheduledQueueCard(
    items: List<ScheduledItemData>,
    onCancel: (id: Int) -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = CardBg),
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, CardBorder, RoundedCornerShape(18.dp))
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("📋 Live Scheduled Queue", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp)

            if (items.isEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text("No upcoming scheduled posts. Use form above to schedule!", color = TextMuted, fontSize = 11.sp)
                }
            } else {
                items.forEach { item ->
                    ScheduledRowItem(item = item, onCancel = { onCancel(item.id) })
                }
            }
        }
    }
}

@Composable
fun ScheduledRowItem(item: ScheduledItemData, onCancel: () -> Unit) {
    val isPending = item.status == "pending"
    val isPublished = item.status == "published"
    val badgeColor = if (isPending) AmberPending else if (isPublished) EmeraldGreen else RedFailed
    val badgeBg = if (isPending) AmberBg else if (isPublished) EmeraldBg else Color(0x25EF4444)

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(CardBgLight)
            .padding(10.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(if (item.mediaType == "reel") "🎬 Reel" else "🖼️ Post", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(4.dp))
                        .background(badgeBg)
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                ) {
                    Text(item.status.uppercase(), color = badgeColor, fontSize = 9.sp, fontWeight = FontWeight.Bold)
                }
            }
            Text("⏰ ${item.scheduledTime} IST", color = PurpleAccent, fontSize = 11.sp, fontWeight = FontWeight.Medium)
            Text(item.quote?.take(35)?.let { "$it..." } ?: "🤖 Auto AI Vault Shayari", color = TextMuted, fontSize = 10.sp)
        }

        if (isPending) {
            TextButton(onClick = onCancel) {
                Text("Cancel", color = RedFailed, fontSize = 11.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun WebDashboardView(url: String) {
    AndroidView(
        factory = { ctx ->
            WebView(ctx).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.loadWithOverviewMode = true
                settings.useWideViewPort = true
                webViewClient = WebViewClient()
                loadUrl(url)
            }
        },
        modifier = Modifier.fillMaxSize()
    )
}

fun getFutureIST(hoursAhead: Int): String {
    val cal = Calendar.getInstance(TimeZone.getTimeZone("GMT+5:30"))
    cal.add(Calendar.HOUR_OF_DAY, hoursAhead)
    val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US)
    sdf.timeZone = TimeZone.getTimeZone("GMT+5:30")
    return sdf.format(cal.time)
}

fun getTomorrowIST(hour: Int, min: Int): String {
    val cal = Calendar.getInstance(TimeZone.getTimeZone("GMT+5:30"))
    cal.add(Calendar.DAY_OF_YEAR, 1)
    cal.set(Calendar.HOUR_OF_DAY, hour)
    cal.set(Calendar.MINUTE, min)
    val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US)
    sdf.timeZone = TimeZone.getTimeZone("GMT+5:30")
    return sdf.format(cal.time)
}
