package com.example.instagramaistudio.ui.main

import junit.framework.TestCase.assertNotNull
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import org.junit.Test

class MainScreenViewModelTest {
  @Test
  fun uiState_initiallyLoaded() = runTest {
    val viewModel = MainScreenViewModel()
    assertNotNull(viewModel.uiState.first())
  }
}
