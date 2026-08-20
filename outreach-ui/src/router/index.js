import { createRouter, createWebHistory } from 'vue-router'
import Queue from '../views/Queue.vue'
import History from '../views/History.vue'
import FileDetail from '../views/FileDetail.vue'
import Logs from '../views/Logs.vue'
import Drafts from '../views/Drafts.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Queue },
    { path: '/history', component: History },
    { path: '/logs', component: Logs },
    { path: '/drafts', component: Drafts },
    { path: '/file/:filename', component: FileDetail, props: true }
  ]
})

export default router
