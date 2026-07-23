<template>
  <main>
    <section class="data-section">
      <div class="section-header">
        <h2>Global Processed History</h2>
        <div style="display: flex; gap: 10px; align-items: center;">
          <div class="filter-group" style="margin-right: 15px;">
            <label>Filter Status:</label>
            <select v-model="statusFilter" class="filter-select">
              <option value="All">All Records</option>
              <option value="Success">Success</option>
              <option value="Error">Errors / Failed</option>
              <option value="Skipped">Skipped</option>
            </select>
          </div>
          <span class="badge" v-if="historyData.length > 0">{{ historyData.length }} total records</span>
          <button class="icon-btn" @click="loadHistory">↻ Refresh</button>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Sr No.</th>
              <th>Name</th>
              <th>Company</th>
              <th>Email</th>
              <th>Sent</th>
              <th>Verdict Group</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in filteredHistory" :key="index" :class="getRowClass(row.verdict_group || row.verdict)">
              <td style="color: var(--text-muted);">{{ index + 1 }}</td>
              <td>{{ row.first_name || '-' }}</td>
              <td>{{ row.company || '-' }}</td>
              <td>{{ row.email || '-' }}</td>
              <td>{{ formatBoolean(row.is_sent) }}</td>
              <td>
                <div style="display: flex; align-items: center;">
                  <span v-html="formatVerdict(row.verdict_group || row.verdict)"></span>
                  <div class="tooltip-container" v-if="row.verdict">
                    <div class="tooltip-icon">i</div>
                    <span class="tooltip-text">{{ row.verdict }}</span>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="isLoading">
              <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">
                <div class="spinner"></div> Loading history...
              </td>
            </tr>
            <tr v-else-if="hasError">
              <td colspan="6" style="text-align: center; color: var(--danger); padding: 30px;">
                ⚠️ Failed to load global history. Check backend connection.
              </td>
            </tr>
            <tr v-else-if="filteredHistory.length === 0">
              <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">No global history found or no matches. Run a job first!</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '../composables/useToast'

const { showToast } = useToast()
const historyData = ref([])
const statusFilter = ref('All')
const isLoading = ref(true)
const hasError = ref(false)

const filteredHistory = computed(() => {
  if (statusFilter.value === 'All') return historyData.value
  
  return historyData.value.filter(row => {
    const v = String(row.verdict_group || row.verdict || '').toLowerCase()
    
    if (statusFilter.value === 'Success') return v.includes('success') || v === 'sent'
    if (statusFilter.value === 'Error') return v.includes('error') || v.includes('failed')
    if (statusFilter.value === 'Skipped') return v.includes('skipped')
    return true
  })
})

const API_BASE = 'http://127.0.0.1:8000'

const loadHistory = async () => {
  isLoading.value = true
  hasError.value = false
  try {
    const res = await fetch(`${API_BASE}/api/history`)
    if (!res.ok) throw new Error("API failed")
    const data = await res.json()
    if (data.error) throw new Error(data.error)
    historyData.value = Array.isArray(data) ? data.slice().reverse() : []
  } catch (e) {
    hasError.value = true
    showToast('Failed to load global history', 'error')
  } finally {
    isLoading.value = false
  }
}

const formatBoolean = (val) => {
  if (val === true || val === 'true' || val === 'True') return '✅ Yes'
  if (val === false || val === 'false' || val === 'False') return '❌ No'
  return '-'
}

const formatVerdict = (verdict) => {
  if (!verdict) return 'Pending'
  return String(verdict)
}

const getRowClass = (verdict) => {
  if (!verdict) return 'row-unprocessed'
  const v = String(verdict).toLowerCase()
  if (v.includes('success') || v === 'sent') return 'row-success'
  if (v.includes('error') || v.includes('failed')) return 'row-failed'
  if (v.includes('skipped')) return 'row-skipped'
  return 'row-unprocessed'
}

onMounted(() => {
  loadHistory()
})
</script>
