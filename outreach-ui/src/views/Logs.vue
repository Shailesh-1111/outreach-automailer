<template>
  <main>
    <section class="data-section">
      <div class="section-header">
        <h2>System Logs</h2>
        <div style="display: flex; gap: 10px; align-items: center;">
          <span class="badge" v-if="logsData.length > 0">{{ logsData.length }} requests logged</span>
          <button class="icon-btn" @click="loadLogs">↻ Refresh</button>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Filename</th>
              <th>Mode Triggered</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(log, index) in logsData" :key="index">
              <td>{{ log.Timestamp || '-' }}</td>
              <td style="font-weight: 500;">📄 {{ log.Filename || '-' }}</td>
              <td><span class="badge" style="background: var(--panel-bg); border: 1px solid var(--border-color);">{{ log.Mode || 'all' }}</span></td>
              <td><span class="status-badge status-sent">{{ log.Status || '-' }}</span></td>
            </tr>
            <tr v-if="isLoading">
              <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 30px;">
                <div class="spinner"></div> Loading logs...
              </td>
            </tr>
            <tr v-else-if="logsData.length === 0">
              <td colspan="4" style="text-align: center; color: var(--text-muted);">No pipeline jobs have been triggered yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '../composables/useToast'

const { showToast } = useToast()
const logsData = ref([])
const isLoading = ref(true)

const API_BASE = 'http://127.0.0.1:8000'

const loadLogs = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/logs`)
    const data = await res.json()
    if (data.error) throw new Error(data.error)
    logsData.value = Array.isArray(data) ? data.slice().reverse() : []
  } catch (e) {
    showToast('Failed to load system logs', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>
