<template>
  <div class="team-container">
    <!-- 导航 -->
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="goHome">校园AI助手</h1>
        <div class="user-info">
          <span class="welcome-text">欢迎，{{ userStore.username }}</span>
          <button @click="handleLogout" class="logout-btn">退出登录</button>
        </div>
      </div>
    </header>

    <!-- 页面标题区 -->
    <section class="page-header">
      <div class="container">
        <h1 class="page-title">赛事智能组队</h1>
        <p class="page-subtitle">共 {{ competitions.length }} 个赛事</p>
        <div class="tab-group">
          <div class="tab" :class="{ active: activeTab === 'recommend' }" @click="setActiveTab('recommend')">赛事推荐</div>
          <div class="tab" :class="{ active: activeTab === 'team' }" @click="setActiveTab('team')">组队大厅</div>
          <div class="tab" :class="{ active: activeTab === 'my' }" @click="setActiveTab('my')">我的队伍</div>
        </div>
      </div>
    </section>

    <div class="container">
      <div class="main-content">
        <!-- 侧边栏 -->
        <aside class="sidebar">
          <div class="filter-section">
            <h3 class="sidebar-title">赛事级别</h3>
            <ul class="category-list">
              <li :class="{ active: selectedLevel === null }" @click="setLevel(null)">全部 <span>{{ totalCount }}</span></li>
              <li :class="{ active: selectedLevel === 'NATIONAL' }" @click="setLevel('NATIONAL')">国家级 <span>{{ nationalCount }}</span></li>
              <li :class="{ active: selectedLevel === 'PROVINCIAL' }" @click="setLevel('PROVINCIAL')">省级 <span>{{ provincialCount }}</span></li>
              <li :class="{ active: selectedLevel === 'SCHOOL' }" @click="setLevel('SCHOOL')">校级 <span>{{ schoolCount }}</span></li>
            </ul>
          </div>
        </aside>

        <main>
          <!-- 赛事推荐 -->
          <div v-if="activeTab === 'recommend'">
            <div class="section-header" style="margin-bottom: 20px;">
              <h3 class="section-title">为你推荐的赛事</h3>
              <button class="btn btn-primary" @click="fetchCompetitions">刷新数据</button>
            </div>

            <div v-if="loading" class="loading-state">
              <div class="loading-spinner"></div>
              <p>加载中...</p>
            </div>

            <div v-else-if="displayCompetitions.length === 0" class="empty-state">
              <div class="empty-icon">📭</div>
              <div class="empty-text">暂无赛事数据</div>
            </div>

            <div v-else class="competition-card" v-for="competition in displayCompetitions" :key="competition.id" @click="goToDetail(competition.id)">
              <div class="competition-header">
                <div>
                  <h3 class="competition-title">{{ competition.title }}</h3>
                  <div class="competition-meta">
                    <span class="tag" :class="getLevelTagClass(competition.level)">{{ getLevelText(competition.level) }}</span>
                    <span class="meta-item" v-if="competition.organizer">🏠 {{ competition.organizer }}</span>
                    <span class="meta-item" v-if="competition.category">📂 {{ competition.category }}</span>
                    <span class="meta-item">👥 {{ competition.team_count || 0 }} 支队伍</span>
                  </div>
                </div>
                <button class="btn btn-primary" @click.stop>立即报名</button>
              </div>
              <p class="competition-summary">{{ competition.summary || competition.brief_description || '暂无简介' }}</p>
              <div class="competition-footer">
                <div class="competition-meta">
                  <span class="meta-item" v-if="competition.registration_end">📅 报名截止：{{ formatDate(competition.registration_end) }}</span>
                  <span class="meta-item" v-if="competition.contest_start">🎯 比赛时间：{{ formatDate(competition.contest_start) }}</span>
                </div>
                <span class="deadline" v-if="getDaysLeft(competition.registration_end) <= 30 && getDaysLeft(competition.registration_end) > 0">⚠️ 还剩 {{ getDaysLeft(competition.registration_end) }} 天截止</span>
                <span class="meta-item" v-else-if="getDaysLeft(competition.registration_end) > 30">还剩 {{ getDaysLeft(competition.registration_end) }} 天</span>
                <span class="deadline" v-else>已截止</span>
              </div>
            </div>
          </div>

          <!-- 组队大厅 -->
          <div v-if="activeTab === 'team'">
            <div class="section-header" style="margin-bottom: 20px;">
              <h3 class="section-title">组队大厅</h3>
              <button class="btn btn-primary">+ 创建队伍</button>
            </div>
            <div class="empty-state">
              <div class="empty-icon">👥</div>
              <div class="empty-text">组队大厅功能开发中...</div>
            </div>
          </div>

          <!-- 我的队伍 -->
          <div v-if="activeTab === 'my'">
            <div class="my-teams-section">
              <div class="section-header">
                <h3 class="section-title">我的队伍</h3>
                <button class="btn btn-primary">+ 创建队伍</button>
              </div>
              <div class="empty-state">
                <div class="empty-icon">👥</div>
                <div class="empty-text">你还没有创建或加入任何队伍</div>
                <button class="btn btn-primary">创建第一个队伍</button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('recommend')
const loading = ref(false)
const competitions = ref([])
const selectedLevel = ref(null)

// 计算属性
const totalCount = computed(() => competitions.value.length)
const nationalCount = computed(() => competitions.value.filter(c => c.level?.toUpperCase() === 'NATIONAL').length)
const provincialCount = computed(() => competitions.value.filter(c => c.level?.toUpperCase() === 'PROVINCIAL').length)
const schoolCount = computed(() => competitions.value.filter(c => c.level?.toUpperCase() === 'SCHOOL').length)

const displayCompetitions = computed(() => {
  let result = [...competitions.value]
  if (selectedLevel.value) {
    result = result.filter(c => c.level?.toUpperCase() === selectedLevel.value)
  }
  return result
})

// 方法
const setActiveTab = (tab) => {
  activeTab.value = tab
}

const setLevel = (level) => {
  selectedLevel.value = level
}

const fetchCompetitions = async () => {
  loading.value = true
  try {
    console.log('开始调用 API...')
    const response = await axios.get('http://localhost:8000/api/v1/contest/list?limit=500')
    console.log('API 返回:', response)
    competitions.value = response.data.items || response.data || []
    console.log('competitions.value:', competitions.value)
  } catch (error) {
    console.error('获取赛事列表失败:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '待定'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const getDaysLeft = (dateStr) => {
  if (!dateStr) return 999
  const date = new Date(dateStr)
  const now = new Date()
  const diff = Math.ceil((date - now) / (1000 * 60 * 60 * 24))
  return diff
}

const getLevelText = (level) => {
  const levelUpper = level?.toUpperCase()
  const map = {
    'NATIONAL': '国家级',
    'PROVINCIAL': '省级',
    'SCHOOL': '校级'
  }
  return map[levelUpper] || level || '未知'
}

const getLevelTagClass = (level) => {
  const levelUpper = level?.toUpperCase()
  const map = {
    'NATIONAL': 'tag-warning',
    'PROVINCIAL': 'tag-primary',
    'SCHOOL': 'tag-success'
  }
  return map[levelUpper] || ''
}

const goHome = () => {
  router.push('/home')
}

const goToDetail = (id) => {
  router.push(`/contest/${id}`)
}

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    await userStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  fetchCompetitions()
})
</script>

<style scoped>
.team-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  position: sticky;
  top: 0;
  z-index: 99;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.logo {
  font-size: 18px;
  font-weight: 600;
  color: #2C68FF;
  cursor: pointer;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.welcome-text {
  font-size: 14px;
  color: #4E5969;
}

.logout-btn {
  padding: 8px 20px;
  background: rgba(44, 104, 255, 0.1);
  color: #2C68FF;
  border: 1px solid rgba(44, 104, 255, 0.2);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: rgba(44, 104, 255, 0.2);
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 0;
  color: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  opacity: 0.9;
}

.tab-group {
  display: flex;
  gap: 8px;
  margin-top: 24px;
}

.tab {
  padding: 10px 24px;
  background: rgba(255,255,255,0.15);
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.25s ease;
}

.tab:hover {
  background: rgba(255,255,255,0.25);
}

.tab.active {
  background: white;
  color: #667eea;
}

.main-content {
  padding: 40px 0;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 24px;
}

.sidebar {
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 24px;
  height: fit-content;
  position: sticky;
  top: 84px;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #1D2129;
  margin-bottom: 16px;
}

.filter-section {
  margin-bottom: 24px;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-list li {
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #4E5969;
  transition: all 0.25s ease;
}

.category-list li:hover,
.category-list li.active {
  background: #F7F8FA;
  color: #2C68FF;
}

.category-list li span {
  float: right;
  color: #86909C;
  font-size: 13px;
}

.tag {
  display: inline-block;
  padding: 4px 12px;
  background: #F7F8FA;
  border-radius: 12px;
  font-size: 12px;
  color: #4E5969;
  cursor: pointer;
  transition: all 0.25s ease;
}

.tag:hover {
  background: #E5E6EB;
}

.tag-primary {
  background: rgba(44, 104, 255, 0.1);
  color: #2C68FF;
}

.tag-success {
  background: rgba(52, 228, 170, 0.1);
  color: #00A870;
}

.tag-warning {
  background: rgba(255, 125, 0, 0.1);
  color: #FF7D00;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.25s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: #2C68FF;
  color: white;
}

.btn-primary:hover {
  background: #1a53e6;
}

.btn-success {
  background: #34E4AA;
  color: white;
}

.btn-outline {
  background: white;
  border: 1px solid #E5E6EB;
  color: #4E5969;
}

.btn-outline:hover {
  border-color: #2C68FF;
  color: #2C68FF;
}

.btn-sm {
  padding: 6px 14px;
  font-size: 13px;
}

.competition-card {
  background: white;
  border-radius: 4px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 16px;
  transition: all 0.25s ease;
  cursor: pointer;
}

.competition-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.competition-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.competition-title {
  font-size: 18px;
  font-weight: 600;
  color: #1D2129;
  margin-bottom: 8px;
}

.competition-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #86909C;
}

.competition-summary {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.7;
  margin-bottom: 16px;
}

.competition-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.deadline {
  font-size: 13px;
  color: #F53F3F;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1D2129;
}

.team-card {
  background: white;
  border-radius: 4px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 16px;
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.team-name {
  font-size: 16px;
  font-weight: 600;
  color: #1D2129;
  margin-bottom: 8px;
}

.team-members {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.member-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #E5E6EB;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #4E5969;
}

.member-avatar.leader {
  background: #2C68FF;
  color: white;
}

.team-desc {
  font-size: 14px;
  color: #4E5969;
  margin-bottom: 12px;
}

.team-needs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.need-tag {
  padding: 4px 12px;
  background: rgba(255, 125, 0, 0.1);
  color: #FF7D00;
  border-radius: 12px;
  font-size: 12px;
}

.my-teams-section {
  background: white;
  border-radius: 4px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 24px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
  color: #86909C;
  margin-bottom: 16px;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
