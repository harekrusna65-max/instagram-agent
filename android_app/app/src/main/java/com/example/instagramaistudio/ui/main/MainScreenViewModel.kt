package com.example.instagramaistudio.ui.main

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.instagramaistudio.data.InstagramApiClient
import com.example.instagramaistudio.data.ProfileStatsData
import com.example.instagramaistudio.data.ScheduledItemData
import com.example.instagramaistudio.data.ServerStatusData
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class InstagramStudioUiState(
    val status: ServerStatusData = ServerStatusData(),
    val stats: ProfileStatsData = ProfileStatsData(),
    val queue: List<ScheduledItemData> = emptyList(),
    val isRefreshing: Boolean = false,
    val isActionLoading: Boolean = false,
    val actionMessage: String? = null,
    val isError: Boolean = false,
    val selectedTab: Int = 0 // 0 = Native Studio, 1 = Web Cloud Dashboard
)

class MainScreenViewModel(
    private val client: InstagramApiClient = InstagramApiClient()
) : ViewModel() {

    private val _uiState = MutableStateFlow(InstagramStudioUiState())
    val uiState: StateFlow<InstagramStudioUiState> = _uiState.asStateFlow()

    init {
        refreshAll()
    }

    fun selectTab(index: Int) {
        _uiState.update { it.copy(selectedTab = index) }
    }

    fun refreshAll() {
        viewModelScope.launch {
            _uiState.update { it.copy(isRefreshing = true) }
            val statusRes = client.getStatus()
            val statsRes = client.getProfileStats()
            val queueRes = client.getScheduledList()

            _uiState.update { current ->
                current.copy(
                    status = statusRes.getOrDefault(current.status),
                    stats = statsRes.getOrDefault(current.stats),
                    queue = queueRes.getOrDefault(current.queue),
                    isRefreshing = false
                )
            }
        }
    }

    fun triggerReelNow() {
        viewModelScope.launch {
            _uiState.update { it.copy(isActionLoading = true, actionMessage = "Rendering & uploading 12s Reel to Instagram...") }
            val res = client.triggerReel()
            res.onSuccess { msg ->
                _uiState.update { it.copy(isActionLoading = false, actionMessage = "🎉 Reel triggered! Live in ~25s.", isError = false) }
                refreshAll()
            }.onFailure { err ->
                _uiState.update { it.copy(isActionLoading = false, actionMessage = "Error: ${err.message}", isError = true) }
            }
        }
    }

    fun triggerPostNow() {
        viewModelScope.launch {
            _uiState.update { it.copy(isActionLoading = true, actionMessage = "Designing & uploading image post...") }
            val res = client.triggerPost()
            res.onSuccess { msg ->
                _uiState.update { it.copy(isActionLoading = false, actionMessage = "🎉 Post triggered! Live in ~15s.", isError = false) }
                refreshAll()
            }.onFailure { err ->
                _uiState.update { it.copy(isActionLoading = false, actionMessage = "Error: ${err.message}", isError = true) }
            }
        }
    }

    fun generateShayari(topic: String, onResult: (hook: String, quote: String) -> Unit) {
        viewModelScope.launch {
            _uiState.update { it.copy(actionMessage = "✨ AI Generating $topic shayari...", isError = false) }
            val res = client.generateShayari(topic)
            res.onSuccess { data ->
                _uiState.update { it.copy(actionMessage = "✨ Generated ${data.category} shayari!", isError = false) }
                onResult(data.hook, data.quote)
            }.onFailure { err ->
                _uiState.update { it.copy(actionMessage = "Error: ${err.message}", isError = true) }
            }
        }
    }

    fun publishCustom(isReel: Boolean, hook: String?, quote: String) {
        if (quote.isBlank()) {
            _uiState.update { it.copy(actionMessage = "Please enter a shayari/quote first!", isError = true) }
            return
        }
        viewModelScope.launch {
            _uiState.update { it.copy(isActionLoading = true, actionMessage = "Publishing custom ${if (isReel) "Reel" else "Post"}...") }
            val res = if (isReel) client.triggerReel(hook, quote) else client.triggerPost(quote)
            res.onSuccess {
                _uiState.update { it.copy(isActionLoading = false, actionMessage = "🎉 Custom content sent to Instagram!", isError = false) }
                refreshAll()
            }.onFailure { err ->
                _uiState.update { it.copy(isActionLoading = false, actionMessage = "Error: ${err.message}", isError = true) }
            }
        }
    }

    fun scheduleItem(mediaType: String, scheduledTime: String, hook: String?, quote: String?) {
        if (scheduledTime.isBlank()) {
            _uiState.update { it.copy(actionMessage = "Please select target date and time (IST)!", isError = true) }
            return
        }
        viewModelScope.launch {
            _uiState.update { it.copy(isActionLoading = true, actionMessage = "Scheduling $mediaType...") }
            val res = client.schedulePost(mediaType, scheduledTime, hook, quote)
            res.onSuccess { msg ->
                _uiState.update { it.copy(isActionLoading = false, actionMessage = "🎉 $msg", isError = false) }
                refreshAll()
            }.onFailure { err ->
                _uiState.update { it.copy(isActionLoading = false, actionMessage = "Schedule Error: ${err.message}", isError = true) }
            }
        }
    }

    fun cancelScheduled(id: Int) {
        viewModelScope.launch {
            val res = client.deleteScheduledItem(id)
            res.onSuccess { msg ->
                _uiState.update { it.copy(actionMessage = "Cancelled post #$id", isError = false) }
                refreshAll()
            }.onFailure { err ->
                _uiState.update { it.copy(actionMessage = "Error: ${err.message}", isError = true) }
            }
        }
    }

    fun triggerGrowthScan() {
        viewModelScope.launch {
            _uiState.update { it.copy(actionMessage = "🚀 Scanning recent comments & DMs...", isError = false) }
            val res = client.triggerGrowthScan()
            res.onSuccess { msg ->
                _uiState.update { it.copy(actionMessage = "🎉 $msg", isError = false) }
            }.onFailure { err ->
                _uiState.update { it.copy(actionMessage = "Scan Error: ${err.message}", isError = true) }
            }
        }
    }

    fun clearMessage() {
        _uiState.update { it.copy(actionMessage = null) }
    }
}
