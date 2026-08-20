<template>
  <main class="drafts-container">
    <div class="section-header">
      <div style="display: flex; justify-content: space-between; align-items: flex-end; width: 100%;">
        <div>
          <h2 style="margin: 0; margin-bottom: 10px;">Email Draft Generator</h2>
          <div style="display: flex; gap: 10px; align-items: center;">
            <label style="font-weight: 500;">Select File:</label>
            <select v-model="selectedFile" @change="fetchContacts" style="padding: 0.5rem; border-radius: 6px;">
              <option value="" disabled>-- Choose a CSV --</option>
              <option v-for="f in files" :key="f.filename" :value="f.filename">{{ f.filename }}</option>
            </select>
            <span v-if="isLoadingContacts" class="spinner-small"></span>
          </div>
        </div>
        
        <div v-if="selectedFile && !isLoadingContacts" class="file-stats">
          <div class="stat-box">
            <span class="stat-label">Total</span>
            <span class="stat-val">{{ fileStats.total }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">Drafted</span>
            <span class="stat-val drafted">{{ fileStats.drafted }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">Left</span>
            <span class="stat-val left">{{ fileStats.left }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="draft-workspace">
      <!-- Column 1: Companies -->
      <div class="column companies-col">
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid #e5e7eb; background: #f9fafb;">
          <h3 style="padding: 0; border: none; margin: 0;">Companies</h3>
          <select v-model="companySortBy" style="padding: 0.3rem 0.5rem; border-radius: 4px; border: 1px solid #d1d5db; font-size: 0.85rem; outline: none; background: white; cursor: pointer;">
            <option value="left">Sort by: Left</option>
            <option value="total">Sort by: Total</option>
            <option value="drafted">Sort by: Drafted</option>
          </select>
        </div>
        <div style="padding: 0.5rem 1rem; border-bottom: 1px solid #e5e7eb; background: #fff;">
          <input v-model="companySearch" type="text" placeholder="Search company..." style="width: 100%; box-sizing: border-box; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 4px; font-size: 0.85rem; outline: none;" />
        </div>
        <div v-if="!selectedFile" class="empty-state">Select a file first.</div>
        <ul v-else class="list-group">
          <li v-for="comp in companies" :key="comp.name" 
              :class="{ active: selectedCompany === comp.name }"
              @click="selectCompany(comp.name)">
            <div class="comp-info">
              <div class="comp-name">{{ comp.name }}</div>
              <div class="comp-stats">
                <span class="tag tag-total">Total: {{ comp.total }}</span>
                <span class="tag tag-drafted">Drafted: {{ comp.drafted }}</span>
                <span class="tag tag-left">Left: {{ comp.left }}</span>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- Column 2: Emails -->
      <div class="column emails-col" v-if="selectedCompany">
        <h3>Emails at {{ selectedCompany }}</h3>
        <ul class="list-group">
          <li v-for="c in companyContacts" :key="c.email" 
              :class="{ drafted: c.is_drafted }">
            <div class="contact-info">
              <div class="c-name">{{ c.first_name }} {{ c.last_name }}</div>
              <div class="c-role">{{ c.position || 'Unknown Role' }}</div>
              <div class="c-email">{{ c.email }}</div>
            </div>
            <div class="contact-actions">
              <span v-if="c.is_drafted" class="badge success">Drafted</span>
              <button class="primary-btn sm" @click="startDraft(c)">Make Draft</button>
            </div>
          </li>
        </ul>
      </div>
      <div class="column emails-col empty-col" v-else>
        <div class="empty-state">Select a company to view emails.</div>
      </div>
    </div>

    <!-- Popup Modal for Draft Preview -->
    <div v-if="draftingContact" class="modal-overlay" @click.self="closeDraft">
      <div class="modal-content">
        <div class="modal-header">
          <div style="display: flex; align-items: center; gap: 10px;">
            <h3>Draft for {{ draftingContact.first_name || draftingContact.email }}</h3>
            <span v-if="draftingContact.is_drafted" class="header-warning">
              ⚠️ Already Drafted
            </span>
          </div>
          <button class="close-btn" @click="closeDraft">&times;</button>
        </div>

        <div class="modal-body">
          <div class="draft-controls">
            <div class="control-group">
              <label>Template:</label>
              <select v-model="selectedTemplate" @change="fetchPreview">
                <option v-for="t in config.templates" :key="t.id" :value="t.id">{{ t.name }}</option>
              </select>
            </div>
            <div class="control-group">
              <label>Role to Apply For:</label>
              <select v-model="selectedRole" @change="fetchPreview">
                <option v-for="r in config.roles" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
          </div>

          <div class="preview-box">
            <div v-if="isLoadingPreview" class="loading-state">Generating...</div>
            <div v-else style="display: flex; flex-direction: column; flex: 1;">
              <div style="margin-bottom: 10px; padding: 12px 15px; background: white; border-radius: 8px; box-shadow: 0 1px 5px rgba(0,0,0,0.05); display: flex; align-items: center; border: 1px solid #e5e7eb;">
                <strong style="margin-right: 10px; color: #4b5563;">Subject:</strong> 
                <input v-model="previewSubject" style="border: none; outline: none; flex: 1; font-family: inherit; font-size: 0.95rem; font-weight: 500;" />
              </div>
              <div class="preview-content editable-preview" v-html="previewHtml" contenteditable="true" ref="editablePreview"></div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="primary-btn lg w-full" @click="sendViaGmail">Send via Gmail ✉️</button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useToast } from '../composables/useToast'

const { showToast } = useToast()
const API_BASE = 'http://127.0.0.1:8000'

const files = ref([])
const selectedFile = ref('')
const contacts = ref([])
const isLoadingContacts = ref(false)

const config = ref({ roles: [], templates: [] })
const selectedCompany = ref('')
const draftingContact = ref(null)

const selectedRole = ref('')
const selectedTemplate = ref('')
const previewHtml = ref('')
const previewSubject = ref('')
const isLoadingPreview = ref(false)
const editablePreview = ref(null)

const companySortBy = ref('left')
const companySearch = ref('')

const fileStats = computed(() => {
  const total = contacts.value.length
  const drafted = contacts.value.filter(c => c.is_drafted).length
  return {
    total,
    drafted,
    left: total - drafted
  }
})

const companies = computed(() => {
  const compMap = {}
  contacts.value.forEach(c => {
    const compName = c.company || 'Unknown Company'
    if (!compMap[compName]) compMap[compName] = { total: 0, drafted: 0 }
    
    compMap[compName].total++
    if (c.is_drafted) {
      compMap[compName].drafted++
    }
  })
  
  let arr = Object.keys(compMap)
  if (companySearch.value) {
    const search = companySearch.value.toLowerCase()
    arr = arr.filter(name => name.toLowerCase().includes(search))
  }
  
  return arr.map(name => {
    const total = compMap[name].total
    const drafted = compMap[name].drafted
    const left = total - drafted
    return { name, total, drafted, left }
  }).sort((a,b) => b[companySortBy.value] - a[companySortBy.value])
})

const companyContacts = computed(() => {
  if (!selectedCompany.value) return []
  return contacts.value.filter(c => (c.company || 'Unknown Company') === selectedCompany.value)
})

const fetchFiles = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/files`)
    if (res.ok) {
      files.value = await res.json()
      if (files.value.some(f => f.filename === 'all_mails.csv')) {
        selectedFile.value = 'all_mails.csv'
        fetchContacts()
      }
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchConfig = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/config`)
    if (res.ok) {
      config.value = await res.json()
      if (config.value.roles?.length) selectedRole.value = config.value.roles[0]
      if (config.value.templates?.length) selectedTemplate.value = config.value.templates[0].id
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchContacts = async () => {
  if (!selectedFile.value) return
  isLoadingContacts.value = true
  contacts.value = []
  selectedCompany.value = ''
  draftingContact.value = null
  
  try {
    const res = await fetch(`${API_BASE}/api/files/${encodeURIComponent(selectedFile.value)}`)
    if (res.ok) {
      const data = await res.json()
      contacts.value = data.data || []
      // Convert string is_drafted to boolean if needed
      contacts.value.forEach(c => {
        if (typeof c.is_drafted === 'string') c.is_drafted = c.is_drafted.toLowerCase() === 'true'
      })
    }
  } catch (e) {
    console.error(e)
    showToast("Failed to fetch contacts", "error")
  } finally {
    isLoadingContacts.value = false
  }
}

const selectCompany = (companyName) => {
  selectedCompany.value = companyName
}

const startDraft = (contact) => {
  draftingContact.value = contact
  fetchPreview()
}

const closeDraft = () => {
  draftingContact.value = null
}

const fetchPreview = async () => {
  if (!draftingContact.value || !selectedRole.value || !selectedTemplate.value) return
  
  isLoadingPreview.value = true
  try {
    const c = draftingContact.value
    let firstName = 'Hiring Manager'
    if (c.first_name) {
      firstName = c.first_name.trim()
    } else if (c.last_name) {
      firstName = c.last_name.trim()
    }
    const name = encodeURIComponent(firstName)
    const company = encodeURIComponent(c.company || 'Your Company')
    const role = encodeURIComponent(selectedRole.value)
    const template = encodeURIComponent(selectedTemplate.value)
    
    const res = await fetch(`${API_BASE}/api/preview?name=${name}&company=${company}&role=${role}&template=${template}`)
    if (res.ok) {
      const data = await res.json()
      previewHtml.value = data.html
      previewSubject.value = data.subject || "SDE Opportunities"
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoadingPreview.value = false
  }
}

const sendViaGmail = async () => {
  if (!draftingContact.value) return
  const c = draftingContact.value
  const email = c.email
  
  if (!editablePreview.value) return
  
  let textBody = editablePreview.value.innerText
  let htmlBody = editablePreview.value.innerHTML
  
  try {
    const blobHtml = new Blob([htmlBody], { type: 'text/html' });
    const blobText = new Blob([textBody], { type: 'text/plain' });
    const item = new ClipboardItem({
      'text/html': blobHtml,
      'text/plain': blobText
    });
    await navigator.clipboard.write([item]);
    showToast("Copied styling! Press Ctrl+A then Ctrl+V in Gmail.", "success");
  } catch(e) {
    console.error("Clipboard copy failed", e);
  }

  const subject = previewSubject.value || "SDE Opportunities"

  // We provide the plain text in the body parameter as a fallback. 
  // If the user wants the rich formatting, they just press Ctrl+A and Ctrl+V to overwrite it!
  const mailtoLink = `https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(email)}&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(textBody)}`
  
  // Using a specific target name ('gmailOutreachTab') instead of '_blank' forces the browser to reuse the SAME tab!
  window.open(mailtoLink, 'gmailOutreachTab')
  
  // Mark as drafted in backend
  try {
    await fetch(`${API_BASE}/api/files/${encodeURIComponent(selectedFile.value)}/mark_drafted`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
    c.is_drafted = true
    showToast("Marked as drafted!", "success")
    closeDraft() // Close popup automatically after sending
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchFiles()
  fetchConfig()
})
</script>

<style scoped>
.drafts-container { padding: 0.5rem 0; height: calc(100vh - 220px); display: flex; flex-direction: column; overflow: hidden; box-sizing: border-box; }
.section-header { flex-shrink: 0; margin-bottom: 1rem; }
.file-stats { display: flex; gap: 15px; background: white; padding: 10px 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; }
.stat-box { display: flex; flex-direction: column; align-items: center; min-width: 60px; }
.stat-label { font-size: 0.75rem; color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.stat-val { font-size: 1.25rem; font-weight: 700; color: #1f2937; margin-top: 2px; }
.stat-val.drafted { color: #16a34a; }
.stat-val.left { color: #2563eb; }

.draft-workspace {
  display: flex;
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

.column {
  background: white;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Updated 2-column layout */
.companies-col { flex: 1; min-width: 350px; max-width: 450px; }
.emails-col { flex: 2; min-width: 400px; }
.empty-col { background: transparent; box-shadow: none; border: 2px dashed #d1d5db; align-items: center; justify-content: center; }

h3 { padding: 1rem; margin: 0; border-bottom: 1px solid #e5e7eb; background: #f9fafb; font-size: 1rem; }

.list-group {
  list-style: none; padding: 0; margin: 0; overflow-y: auto; flex: 1;
}

.list-group li {
  padding: 1rem; border-bottom: 1px solid #f3f4f6; cursor: pointer; transition: 0.2s;
  display: flex; justify-content: space-between; align-items: center;
}
.list-group li:hover { background: #f9fafb; }
.list-group li.active { background: #eff6ff; border-left: 4px solid var(--primary); }
.list-group li.drafted { background: #f8fafc; opacity: 0.8; } /* dim already drafted rows slightly */

.comp-info { display: flex; flex-direction: column; gap: 0.4rem; width: 100%; }
.comp-name { font-weight: 600; color: #1f2937; }
.comp-stats { display: flex; gap: 0.5rem; }

.tag { font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 12px; font-weight: 600; }
.tag-total { background: #e5e7eb; color: #374151; }
.tag-drafted { background: #dcfce7; color: #166534; }
.tag-left { background: #dbeafe; color: #1e40af; }

.contact-info { flex: 1; min-width: 0; padding-right: 1rem; }
.c-name { font-weight: 600; color: #1f2937; font-size: 0.95rem; }
.c-role { font-size: 0.8rem; color: #6b7280; margin: 0.2rem 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.c-email { font-size: 0.85rem; color: var(--primary); }

.contact-actions { display: flex; flex-direction: column; gap: 0.5rem; align-items: flex-end; }
.badge { font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; }
.badge.success { background: #dcfce7; color: #166534; }
.primary-btn.sm { padding: 0.4rem 0.8rem; font-size: 0.85rem; }

.empty-state { padding: 2rem; text-align: center; color: #9ca3af; font-style: italic; }
.spinner-small { width: 20px; height: 20px; border: 2px solid #e5e7eb; border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 90vw;
  max-width: 1000px;
  height: 90vh;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s ease;
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f9fafb;
}

.modal-header h3 { padding: 0; border: none; background: transparent; }

.close-btn {
  background: none; border: none; font-size: 1.5rem; color: #6b7280;
  cursor: pointer; transition: 0.2s;
}
.close-btn:hover { color: #111827; }

.header-warning {
  background: #fef2f2;
  color: #ef4444;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.75rem;
  border: 1px solid #fca5a5;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1;
}

.draft-controls { display: flex; gap: 1rem; flex-shrink: 0; }
.control-group { flex: 1; display: flex; flex-direction: column; gap: 0.4rem; }
.control-group label { font-size: 0.85rem; color: #4b5563; font-weight: 600; }
.control-group select { padding: 0.6rem; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.9rem; }

.preview-box { background: #f3f4f6; border-radius: 8px; padding: 1rem; flex: 1; display: flex; flex-direction: column; min-height: 200px; }
.editable-preview { 
  background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  outline: none; transition: border 0.2s; border: 1px solid transparent;
  flex: 1;
  overflow-y: auto;
}
.editable-preview:focus {
  border: 1px solid var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.w-full { width: 100%; }
.lg { padding: 0.8rem; font-size: 1rem; font-weight: 600; }
</style>
