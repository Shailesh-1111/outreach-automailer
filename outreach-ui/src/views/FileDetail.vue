<template>
  <main>
    <nav class="header-nav" style="margin-bottom: 20px;">
      <button class="nav-btn active" @click="$router.push('/')">← Back to Queue</button>
    </nav>
    <section class="data-section">
      <div class="section-header">
        <h2>Viewing: {{ filename }}</h2>
        <div style="display: flex; gap: 10px; align-items: center;">
          <span class="badge">{{ selectedFileContent.length }} records</span>
          <button class="icon-btn" @click="loadFileContent">↻ Refresh</button>
        </div>
      </div>
      
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button @click="openConfigModal('unprocessed')" :disabled="isRunning" class="primary-btn">
            {{ isRunning ? 'Running...' : '▶ Process Unprocessed' }}
          </button>
          <button v-for="group in errorGroups" :key="group" @click="openConfigModal(group.toLowerCase())" :disabled="isRunning" class="secondary-btn">
            ↻ Process {{ group }}
          </button>
        </div>
        
        <div class="filter-group">
          <label>Filter Status:</label>
          <select v-model="statusFilter" class="filter-select">
            <option value="All">All Records</option>
            <option value="Success">Success</option>
            <option value="Error">Errors / Failed</option>
            <option value="Skipped">Skipped</option>
            <option value="Pending">Pending</option>
          </select>
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
            <tr v-for="(row, index) in filteredContent" :key="index" :class="getRowClass(row.verdict_group || row.verdict)">
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
              <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">
                <div class="spinner"></div> Loading records...
              </td>
            </tr>
            <tr v-else-if="hasError === 'not_found'">
              <td colspan="7" style="text-align: center; color: var(--danger); padding: 30px;">
                ⚠️ {{ serverMessage }}
              </td>
            </tr>
            <tr v-else-if="hasError">
              <td colspan="7" style="text-align: center; color: var(--danger); padding: 30px;">
                ⚠️ {{ serverMessage }}
              </td>
            </tr>
            <tr v-else-if="filteredContent.length === 0">
              <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">{{ serverMessage || 'No records match the filter.' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Configuration Modal -->
    <div v-if="showConfigModal" class="modal-overlay" @click.self="showConfigModal = false">
      <div class="modal-content">
        <h3>Configure Pipeline Run</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 20px;">Target: {{ pendingMode }}</p>

        <div class="config-section">
          <h4>1. Select Role</h4>
          <div class="tag-group">
            <button v-for="r in availableRoles" :key="r" @click="selectRole(r)" :class="['tag-btn', selectedRole === r ? 'active' : '']">{{ r }}</button>
          </div>
        </div>
        
        <div class="config-section">
          <h4>2. Select Template</h4>
          <div class="tag-group">
            <button v-for="t in availableTemplates" :key="t.id" @click="selectTemplate(t.id)" :class="['tag-btn', selectedTemplate === t.id ? 'active' : '']">{{ t.name }}</button>
          </div>
        </div>

        <div class="config-section preview-section">
          <h4>Live Preview</h4>
          <div class="preview-box" v-html="previewHtml"></div>
        </div>

        <div class="modal-actions">
          <button @click="showConfigModal = false" class="secondary-btn">Cancel</button>
          <button @click="confirmAndRun" class="primary-btn">▶ Start Processing</button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from '../composables/useToast'

const props = defineProps({
  filename: {
    type: String,
    required: true
  }
})

const { showToast } = useToast()
const selectedFileContent = ref([])
const isRunning = ref(false)
const isLoading = ref(true)
const hasError = ref(false)
const serverMessage = ref('')
const statusFilter = ref('All')

// Modal State
const showConfigModal = ref(false)
const pendingMode = ref('unprocessed')
const selectedRole = ref('')
const selectedTemplate = ref('')
const previewHtml = ref('Loading preview...')

const availableRoles = ref([])
const availableTemplates = ref([])

const errorGroups = computed(() => {
  const groups = new Set()
  selectedFileContent.value.forEach(row => {
    const vg = row.verdict_group || ''
    if (vg.toLowerCase().includes('error') || vg.toLowerCase().includes('failed')) {
      groups.add(vg)
    }
  })
  return Array.from(groups)
})

const filteredContent = computed(() => {
  if (statusFilter.value === 'All') return selectedFileContent.value
  
  return selectedFileContent.value.filter(row => {
    const v = String(row.verdict_group || row.verdict || '').toLowerCase()
    
    if (statusFilter.value === 'Success') return v.includes('success') || v === 'sent'
    if (statusFilter.value === 'Error') return v.includes('error') || v.includes('failed')
    if (statusFilter.value === 'Skipped') return v.includes('skipped')
    if (statusFilter.value === 'Pending') return !v || v === 'pending'
    return true
  })
})

const API_BASE = 'http://127.0.0.1:8000'

const loadConfig = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/config`)
    const data = await res.json()
    availableRoles.value = data.roles || []
    availableTemplates.value = data.templates || []
    if (availableRoles.value.length > 0) selectedRole.value = availableRoles.value[0]
    if (availableTemplates.value.length > 0) selectedTemplate.value = availableTemplates.value[0].id
  } catch (e) {
    console.error("Failed to load config", e)
  }
}

const loadFileContent = async () => {
  isLoading.value = true
  hasError.value = false
  serverMessage.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/files/${props.filename}`)
    const json = await res.json()
    
    serverMessage.value = json.message || ''
    
    if (json.status === "not_found" || json.status === "error") {
      hasError.value = json.status
      showToast(json.message, 'error')
      selectedFileContent.value = []
    } else {
      // success or empty
      selectedFileContent.value = json.data || []
    }
  } catch (e) {
    hasError.value = true
    serverMessage.value = "Failed to connect to backend server."
    showToast('Connection failed', 'error')
  } finally {
    isLoading.value = false
  }
}

const checkStatus = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/status/${props.filename}`)
    const data = await res.json()
    if (isRunning.value && !data.is_running) {
      // Job just finished, reload table data
      loadFileContent()
    }
    isRunning.value = data.is_running
  } catch (e) {
    console.error("Status check failed", e)
  }
}

const fetchPreview = async () => {
  try {
    previewHtml.value = 'Loading preview...'
    const res = await fetch(`${API_BASE}/api/preview?role=${encodeURIComponent(selectedRole.value)}&template=${encodeURIComponent(selectedTemplate.value)}`)
    const data = await res.json()
    previewHtml.value = data.html
  } catch (e) {
    previewHtml.value = 'Failed to load preview.'
  }
}

const selectRole = (r) => {
  selectedRole.value = r
  fetchPreview()
}

const selectTemplate = (t) => {
  selectedTemplate.value = t
  fetchPreview()
}

const openConfigModal = (mode) => {
  pendingMode.value = mode
  showConfigModal.value = true
  fetchPreview()
}

const confirmAndRun = async () => {
  showConfigModal.value = false
  isRunning.value = true
  try {
    const res = await fetch(`${API_BASE}/api/run/${props.filename}?mode=${pendingMode.value}&role=${encodeURIComponent(selectedRole.value)}&template=${encodeURIComponent(selectedTemplate.value)}`, { method: 'POST' })
    const data = await res.json()
    if (res.status === 409) {
      showToast(data.detail, 'error')
      checkStatus() // verify status
      return
    }
    showToast(data.message)
  } catch (e) {
    showToast('Error starting pipeline!', 'error')
    isRunning.value = false
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

let statusInterval = null

onMounted(() => {
  loadConfig()
  loadFileContent()
  checkStatus()
  statusInterval = setInterval(checkStatus, 3000)
})

onUnmounted(() => {
  if (statusInterval) clearInterval(statusInterval)
})
</script>
