<template>
  <div class="container">
    <header>
      <div style="display: flex; gap: 30px; align-items: center;">
        <div class="header-title">
          <h1 style="cursor:pointer;" @click="$router.push('/')">Outreach Dashboard</h1>
          <p>Manage and track your job application emails</p>
        </div>
        
        <div class="profile-card" v-if="profile.name">
          <div class="profile-info">
            <div style="font-size: 15px; font-weight: 600; color: var(--text-main);">
              {{ profile.name }} <span style="font-size: 14px; font-weight: 400; color: var(--text-muted)">• {{ profile.experience }}</span>
            </div>
            <div style="font-size: 13px; color: var(--text-muted); margin-top: 2px;">✉️ {{ profile.email }}</div>
          </div>
          <button class="icon-btn edit-profile-btn" @click="showProfileModal = true">✏️</button>
        </div>
      </div>
      
      <div style="display: flex; align-items: center; gap: 15px;">
        <button class="icon-btn" @click="toggleTheme" style="padding: 6px 10px; font-size: 16px;">
          {{ isDark ? '☀️Light' : '🌙Dark' }}
        </button>
        <!-- Only show main navigation if we are NOT on a file detail page -->
        <nav class="header-nav" v-if="$route.path === '/' || $route.path === '/history' || $route.path === '/logs' || $route.path === '/drafts'">
          <router-link to="/" class="nav-btn" exact-active-class="active">Processing Queue</router-link>
          <router-link to="/history" class="nav-btn" exact-active-class="active">Processed History</router-link>
          <router-link to="/logs" class="nav-btn" exact-active-class="active">System Logs</router-link>
          <router-link to="/drafts" class="nav-btn" exact-active-class="active">Make Email Drafts</router-link>
        </nav>
      </div>
    </header>

    <!-- The current matched page component gets injected here -->
    <router-view></router-view>
  </div>

  <div v-if="showProfileModal" class="modal-overlay" @click.self="showProfileModal = false">
    <div class="modal-content" style="max-width: 400px; height: auto; min-height: auto;">
      <h3>Edit Profile Details</h3>
      <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
        <div>
          <label style="font-size: 12px; color: var(--text-muted);">Name</label>
          <input v-model="editProfile.name" type="text" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid var(--border-color); background: var(--row-hover-bg); color: var(--text-main); margin-top: 4px;" />
        </div>
        <div>
          <label style="font-size: 12px; color: var(--text-muted);">Experience</label>
          <input v-model="editProfile.experience" type="text" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid var(--border-color); background: var(--row-hover-bg); color: var(--text-main); margin-top: 4px;" />
        </div>
        <div>
          <label style="font-size: 12px; color: var(--text-muted);">Email (Template Reply-To)</label>
          <input v-model="editProfile.email" type="text" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid var(--border-color); background: var(--row-hover-bg); color: var(--text-main); margin-top: 4px;" />
        </div>
      </div>
      <div class="modal-actions" style="margin-top: 25px;">
        <button @click="showProfileModal = false" class="secondary-btn">Cancel</button>
        <button @click="saveProfile" class="primary-btn">Save Changes</button>
      </div>
    </div>
  </div>

  <div class="toast" :class="{ show: toast.show }" :style="{ borderLeftColor: toast.type === 'error' ? 'var(--danger)' : 'var(--primary)' }">
    {{ toast.message }}
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from './composables/useToast'
const { toast } = useToast()

const isDark = ref(false)
const profile = ref({ name: '', email: '', experience: '' })
const editProfile = ref({ name: '', email: '', experience: '' })
const showProfileModal = ref(false)

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const loadProfile = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/profile')
    profile.value = await res.json()
    editProfile.value = { ...profile.value }
  } catch (e) {
    console.error("Failed to load profile", e)
  }
}

const saveProfile = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editProfile.value)
    })
    const data = await res.json()
    toast.message = data.message
    toast.show = true
    setTimeout(() => { toast.show = false }, 3000)
    profile.value = { ...editProfile.value }
    showProfileModal.value = false
  } catch(e) {
    console.error("Failed to save profile")
  }
}

onMounted(() => {
  loadProfile()
  const savedTheme = localStorage.getItem('theme') || 'light'
  isDark.value = savedTheme === 'dark'
  document.documentElement.setAttribute('data-theme', savedTheme)
})
</script>

<style>
/* Profile Card Styles */
.profile-card {
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  padding: 10px 18px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
  min-width: 260px;
}
.profile-info {
  display: flex;
  flex-direction: column;
}
.edit-profile-btn {
  padding: 4px;
  font-size: 14px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
}
.edit-profile-btn:hover {
  background: var(--row-hover-bg);
  border-color: var(--border-color);
}

/* Filter Styles */
.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.filter-group label {
  font-size: 14px;
  color: var(--text-muted);
  font-weight: 500;
}
.filter-select {
  background: var(--panel-bg);
  color: var(--text-main);
  border: 1px solid var(--border-color);
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  cursor: pointer;
}
.filter-select:focus {
  border-color: var(--primary);
}

/* Tooltip Styles */
.tooltip-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  margin-left: 6px;
  cursor: help;
}

.tooltip-icon {
  background: var(--btn-secondary-bg);
  color: var(--text-main);
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
}

.tooltip-text {
  visibility: hidden;
  background-color: var(--text-main);
  color: var(--panel-bg);
  text-align: center;
  border-radius: 4px;
  padding: 6px 12px;
  position: absolute;
  z-index: 100;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.3s;
  white-space: normal;
  font-size: 13px;
  width: 250px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.tooltip-container:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

.header-nav {
  display: flex;
  border: 1px solid var(--btn-border);
  border-radius: 6px;
  overflow: hidden;
  box-shadow: var(--btn-shadow);
}

.nav-btn {
  background: var(--panel-bg);
  border: none;
  border-right: 1px solid var(--btn-border);
  color: var(--text-muted);
  padding: 6px 16px;
  font-weight: 500;
  border-radius: 0;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: inherit;
  text-decoration: none;
}

.nav-btn:last-child {
  border-right: none;
}

.nav-btn:hover {
  background: var(--row-hover-bg);
  color: var(--text-main);
}

.nav-btn.active {
  background: var(--btn-secondary-bg);
  color: var(--text-main);
  border: none;
  border-right: 1px solid var(--btn-border);
  box-shadow: inset 0 -2px 0 var(--primary); /* active bottom underline */
}

.nav-btn.active:last-child {
  border-right: none;
}
</style>
