<template>
  <main>
    <section class="data-section">
      <div class="section-header">
        <h2>Processing Queue Files</h2>
        <div style="display: flex; gap: 10px; align-items: center;">
          <input type="file" ref="fileInput" @change="handleFileUpload" accept=".csv" style="display: none" />
          <button class="primary-btn" @click="triggerFileInput">+ Upload new list</button>
          <button class="icon-btn" @click="loadFiles">↻ Refresh</button>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Sr No.</th>
              <th>File Name</th>
              <th>Total Rows</th>
              <th>Processed</th>
              <th>Success</th>
              <th>Fail</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(file, index) in files" :key="file.filename">
              <td style="color: var(--text-muted);">{{ index + 1 }}</td>
              <td @click="$router.push(`/file/${file.filename}`)" style="cursor: pointer; color: var(--primary); font-weight: 600;">
                📄 {{ file.filename }}
              </td>
              <td>{{ file.total_rows }}</td>
              <td>{{ file.processed }}</td>
              <td><span class="status-sent">{{ file.success }}</span></td>
              <td><span class="status-failed">{{ file.fail }}</span></td>
              <td>
                <button @click="$router.push(`/file/${file.filename}`)" class="secondary-btn run-sm-btn">
                  View Details
                </button>
              </td>
            </tr>
            <tr v-if="isLoading">
              <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">
                <div class="spinner"></div> Loading files...
              </td>
            </tr>
            <tr v-else-if="hasError">
              <td colspan="7" style="text-align: center; color: var(--danger); padding: 30px;">
                ⚠️ Failed to load files from server. Is the backend running?
              </td>
            </tr>
            <tr v-else-if="files.length === 0">
              <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">No CSV files found in processing queue.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../composables/useToast'

const router = useRouter()
const { showToast } = useToast()
const files = ref([])
const isRunning = ref(false)
const isLoading = ref(true)
const hasError = ref(false)
const fileInput = ref(null)

const API_BASE = 'http://127.0.0.1:8000'

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!file.name.toLowerCase().endsWith('.csv')) {
    showToast('Only CSV files are allowed!', 'error')
    event.target.value = ''
    return
  }

  try {
    isLoading.value = true
    const textBody = await file.text()
    const res = await fetch(`${API_BASE}/api/upload?filename=${encodeURIComponent(file.name)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: textBody
    })
    const data = await res.json()
    if (res.ok) {
      showToast(data.message)
      loadFiles()
    } else {
      showToast(data.detail || 'Upload failed on server', 'error')
    }
  } catch (e) {
    showToast(`Upload failed: ${e.message}`, 'error')
    console.error("Upload Error: ", e)
  } finally {
    event.target.value = ''
    isLoading.value = false
  }
}

const loadFiles = async () => {
  isLoading.value = true
  hasError.value = false
  try {
    const res = await fetch(`${API_BASE}/api/files`)
    if (!res.ok) throw new Error("API failed")
    const data = await res.json()
    files.value = data.sort((a, b) => b.created_at - a.created_at)
  } catch (e) {
    hasError.value = true
    showToast('Failed to load files', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadFiles()
})
</script>
