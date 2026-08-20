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
            {{ isRunning ? 'Running...' : `▶ Process Unprocessed (${unprocessedCount})` }}
          </button>
          <button v-for="group in errorGroups" :key="group" @click="openConfigModal(group.toLowerCase())" :disabled="isRunning" class="secondary-btn">
            ↻ Process {{ group }} ({{ getGroupCount(group) }})
          </button>
          <button @click="showDraftModal = true" class="secondary-btn">
            📄 Export Drafts
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
    <!-- Drafts Modal -->
    <div v-if="showDraftModal" class="modal-overlay" @click.self="showDraftModal = false">
      <div class="modal-content" style="max-height: 90vh; overflow-y: auto;">
        <h3>Generate Email Drafts</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 20px;">File: {{ filename }}</p>

        <div class="config-section">
          <h4>Select Template</h4>
          <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 10px;">
            <label v-for="(t, idx) in draftTemplates" :key="idx" style="display: flex; gap: 10px; align-items: flex-start; cursor: pointer;">
              <input type="radio" v-model="selectedDraftTemplate" :value="idx" name="draft_template" style="margin-top: 4px;" />
              <div style="flex: 1; padding: 10px; background: var(--panel-bg); border: 1px solid var(--border-color); border-radius: 6px;">
                <div style="font-weight: 500; margin-bottom: 4px;">Template {{ idx === 6 ? 'Random' : idx + 1 }}</div>
                <div style="font-size: 12px; color: var(--text-muted); white-space: pre-wrap;" v-if="idx < 6">{{ t.substring(0, 100) }}...</div>
                <div style="font-size: 12px; color: var(--text-muted);" v-else>Randomly assigns one of the 6 templates to each recipient.</div>
              </div>
            </label>
          </div>
        </div>

        <div class="modal-actions" style="margin-top: 20px;">
          <button @click="showDraftModal = false" class="secondary-btn">Cancel</button>
          <button @click="generateDrafts" class="primary-btn">📥 Download Drafts</button>
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

// Drafts State
const showDraftModal = ref(false)
const selectedDraftTemplate = ref(0)
const draftTemplates = [
  `Hi {first_name},\n\nI’m Shailesh, an IIT BHU’24 grad and SDE with 2+ years of experience in scalable systems, full-stack, and AI/LLM tools (currently at Eduvanz Financing).\n\nI'm exploring SDE opportunities at your organization and would love to connect. I’ve attached my resume for your reference. \n\nBest,\nShailesh Yadav\n+917355603902`,
  `Hi {first_name},\n\nI am an SDE with 2+ years of experience building scalable, real-time, and AI/LLM-powered systems (Java, Python, React) at Eduvanz Financing. \n\nAs an IIT BHU’24 graduate, I admire the work happening at your organization and am currently looking for new SDE roles. I’ve attached my resume—would love to chat if there's a fit!\n\nBest regards,\nShailesh Yadav\n+917355603902`,
  `Hi {first_name},\n\nI’m reaching out to express my interest in SDE roles at your organization. I bring 2+ years of full-stack and AI development experience from Eduvanz Financing, backed by a degree from IIT BHU ('24).\n\nMy stack includes Java, Python, React, and VectorDBs. Please find my resume attached. Looking forward to connecting!\n\nThanks,\nShailesh Yadav\n+917355603902`,
  `Hi {first_name},\n\nI’m an SDE (IIT BHU’24) specializing in Java, Python, React, and LLM implementations. With 2+ years of hands-on experience at Eduvanz Financing, I'm now exploring open software engineering opportunities at your organization.\n\nI’ve attached my resume outlining my recent work with scalable applications. Let me know if you have any openings that align!\n\nBest,\nShailesh Yadav\n+917355603902`,
  `Hi {first_name},\n\nHope you're having a great week! \n\nI’m Shailesh, an IIT BHU'24 alum with 2+ years of SDE experience building scalable full-stack and AI-driven solutions. I’d love to bring my expertise to the engineering team at your organization. \n\nMy resume is attached for your review. Would be grateful for a quick chat if there are any suitable openings.\n\nBest,\nShailesh Yadav\n+917355603902`,
  `Hi {first_name},\n\nI’m Shailesh Yadav, an IIT BHU’24 graduate with 2+ years of experience as an SDE at Eduvanz Financing Pvt. Ltd.\n\nI'm exploring SDE opportunities at your organization and would love to connect. My experience has primarily been in scalable systems, full stack, real-time applications, and AI/LLM-powered systems and tools.\n\nExperience: 2+ years\nCurrent Company: Eduvanz Financing\nTech Stack: Java, Python, Nodejs, Flask, Springboot, Reactjs, Postgresql, Cursor, VectorDB, LLMs \n\nI’ve attached my resume for your reference and would be grateful if you could consider me for any suitable SDE openings.\n\nRegards,\nShailesh Yadav\nMobile: +917355603902`,
  'Random'
]

const downloadFile = (filename, content, mimeType) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const generateDrafts = () => {
  const baseName = props.filename.replace('.csv', '')
  const data = selectedFileContent.value
  
  if (data.length === 0) {
    showToast('No records available to generate drafts.', 'error')
    return
  }

  const jsonData = []
  let txtContent = `EMAIL DRAFTS FOR: ${baseName}\n`
  txtContent += `TEMPLATE SELECTED: ${selectedDraftTemplate.value === 6 ? 'random' : selectedDraftTemplate.value + 1}\n`
  txtContent += "==================================================\n\n"

  data.forEach((row, index) => {
    let firstName = String(row.first_name || '').trim()
    if (!firstName || firstName.toLowerCase() === 'nan' || firstName.toLowerCase() === 'none') {
      firstName = 'Team'
    }

    let companyName = String(row.company || '').trim()
    if (!companyName || companyName.toLowerCase() === 'nan' || companyName.toLowerCase() === 'none') {
      companyName = 'your company'
    }

    const emailAddress = String(row.email || 'No Email').trim()
    const position = String(row.position || 'Unknown Role').trim()

    let tIdx = selectedDraftTemplate.value
    if (tIdx === 6) {
      tIdx = index % 6
    }
    
    let template = draftTemplates[tIdx]
    let formattedBody = template.replace(/{first_name}/g, firstName).replace(/{company}/g, companyName)
    let subject = "SDE Opportunities | Shailesh Yadav (IIT BHU'24, 2+ YOE)"

    jsonData.push({
        recipient_id: index + 1,
        email: emailAddress,
        role: position,
        company: companyName,
        first_name: firstName,
        subject: subject,
        body: formattedBody
    })
    
    txtContent += `--- Recipient #${index + 1} ---\n`
    txtContent += `To:      ${emailAddress}\n`
    txtContent += `Role:    ${position}\n`
    txtContent += `Subject: ${subject}\n`
    txtContent += "------------------------------\n"
    txtContent += formattedBody + "\n\n"
    txtContent += "==================================================\n\n"
  })

  downloadFile(`${baseName}.txt`, txtContent, 'text/plain')
  downloadFile(`${baseName}.json`, JSON.stringify(jsonData, null, 4), 'application/json')
  
  showDraftModal.value = false
  showToast('Drafts generated and downloaded!')
}

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

const unprocessedCount = computed(() => {
  return selectedFileContent.value.filter(row => {
    const vg = String(row.verdict_group || '').toLowerCase()
    const v = String(row.verdict || '').toLowerCase()
    return (vg === '' || vg === 'pending' || vg === 'nan') && (v === '' || v === 'pending' || v === 'nan')
  }).length
})

const getGroupCount = (groupName) => {
  return selectedFileContent.value.filter(row => {
    const vg = row.verdict_group || ''
    return vg === groupName
  }).length
}

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

const loadFileContentQuietly = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/files/${props.filename}`)
    const json = await res.json()
    if (json.status !== "not_found" && json.status !== "error") {
      selectedFileContent.value = json.data || []
    }
  } catch (e) {
    // Ignore errors for background fetch
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
    
    if (isRunning.value) {
      loadFileContentQuietly()
    }
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
