<template>
  <div class="detail-container">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="goHome">校园AI助手</h1>
        <div class="user-info">
          <span class="welcome-text">欢迎，{{ userStore.username }}</span>
          <button @click="handleLogout" class="logout-btn">退出登录</button>
        </div>
      </div>
    </header>

    <div class="container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="!contest" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">赛事不存在</div>
        <button class="btn-primary" @click="goBack">返回列表</button>
      </div>

      <div v-else class="detail-content">
        <div class="back-nav" @click="goBack">← 返回赛事列表</div>

        <div class="detail-header">
          <div>
            <span class="tag" :class="getLevelTagClass(contest.level)">{{ getLevelText(contest.level) }}</span>
            <h1 class="title">{{ contest.title }}</h1>
            <div class="meta-row">
              <span v-if="contest.organizer" class="meta-item">🏠 {{ contest.organizer }}</span>
              <span class="meta-item">👁️ {{ contest.view_count || 0 }} 次浏览</span>
              <span class="meta-item">👥 {{ contest.team_count || 0 }} 支队伍</span>
            </div>
          </div>
          <button class="btn-primary large">立即报名</button>
        </div>

        <div class="detail-body">
          <div class="main-section">
            <div class="section">
              <h3 class="section-title">赛事简介</h3>
              <p class="section-content">{{ contest.summary || contest.brief_description || '暂无简介' }}</p>
            </div>

            <div class="section" v-if="contest.description">
              <h3 class="section-title">详细说明</h3>
              <div class="section-content" v-html="contest.description"></div>
            </div>

            <div class="section" v-if="contest.eligibility_requirements">
              <h3 class="section-title">参赛资格</h3>
              <p class="section-content">{{ contest.eligibility_requirements }}</p>
            </div>

            <div class="section" v-if="contest.participation_process">
              <h3 class="section-title">参赛流程</h3>
              <p class="section-content">{{ contest.participation_process }}</p>
            </div>

            <div class="section" v-if="contest.awards_info">
              <h3 class="section-title">奖项信息</h3>
              <p class="section-content">{{ contest.awards_info }}</p>
            </div>

            <div class="section" v-if="contest.recommendations">
              <h3 class="section-title">推荐建议</h3>
              <p class="section-content">{{ contest.recommendations }}</p>
            </div>

            <div class="section" v-if="contest.tags && contest.tags.length > 0">
              <h3 class="section-title">赛事标签</h3>
              <div class="tags">
                <span class="tag" v-for="tag in contest.tags" :key="tag">{{ tag }}</span>
              </div>
            </div>
          </div>

          <div class="side-section">
            <div class="info-card">
              <h3 class="card-title">时间信息</h3>
              <div class="info-item">
                <span class="label">报名开始</span>
                <span class="value">{{ formatDate(contest.registration_start) }}</span>
              </div>
              <div class="info-item">
                <span class="label">报名截止</span>
                <span class="value" :class="{ urgent: getDaysLeft(contest.registration_end) <= 30 && getDaysLeft(contest.registration_end) > 0 }">
                  {{ formatDate(contest.registration_end) }}
                  <span v-if="getDaysLeft(contest.registration_end) <= 30 && getDaysLeft(contest.registration_end) > 0" class="urgent-badge">还剩 {{ getDaysLeft(contest.registration_end) }} 天</span>
                </span>
              </div>
              <div class="info-item">
                <span class="label">比赛开始</span>
                <span class="value">{{ formatDate(contest.contest_start) }}</span>
              </div>
              <div class="info-item" v-if="contest.contest_end">
                <span class="label">比赛结束</span>
                <span class="value">{{ formatDate(contest.contest_end) }}</span>
              </div>
            </div>

            <div class="info-card" v-if="contest.contact_info || contest.contact">
              <h3 class="card-title">联系方式</h3>
              <p class="contact-text">{{ contest.contact_info || contest.contact }}</p>
            </div>

            <div class="info-card">
              <h3 class="card-title">快捷操作</h3>
              <button class="btn-primary block">立即报名</button>
              <button class="btn-outline block mt-3">寻找队友</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { getContestDetail } from '@/api/contest'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const contest = ref(null)

const fetchContestDetail = async () => {
  loading.value = true
  try {
    const data = await getContestDetail(route.params.id)
    contest.value = data
  } catch (error) {
    console.error('获取赛事详情失败:', error)
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

const goBack = () => {
  router.push('/contest')
}

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    await userStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  fetchContestDetail()
})
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.back-nav {
  color: #2C68FF;
  cursor: pointer;
  margin-bottom: 24px;
  font-size: 14px;
}

.back-nav:hover {
  text-decoration: underline;
}

.detail-header {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: #1D2129;
  margin: 12px 0;
}

.meta-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 14px;
  color: #86909C;
}

.detail-body {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
}

.main-section {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.section {
  margin-bottom: 32px;
}

.section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1D2129;
  margin-bottom: 16px;
}

.section-content {
  font-size: 15px;
  color: #4E5969;
  line-height: 1.8;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 4px 12px;
  background: #F7F8FA;
  border-radius: 12px;
  font-size: 13px;
  color: #4E5969;
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

.side-section {
  position: sticky;
  top: 84px;
  height: fit-content;
}

.info-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1D2129;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  font-size: 14px;
  color: #86909C;
}

.info-item .value {
  font-size: 14px;
  color: #1D2129;
  text-align: right;
}

.info-item .value.urgent {
  color: #F53F3F;
}

.urgent-badge {
  display: block;
  font-size: 12px;
  margin-top: 4px;
}

.contact-text {
  font-size: 14px;
  color: #4E5969;
  line-height: 1.6;
}

.btn-primary {
  padding: 12px 32px;
  background: #2C68FF;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-primary:hover {
  background: #1a53e6;
}

.btn-primary.large {
  padding: 14px 40px;
}

.btn-primary.block {
  width: 100%;
}

.btn-outline {
  padding: 12px 32px;
  background: white;
  color: #2C68FF;
  border: 1px solid #2C68FF;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-outline:hover {
  background: rgba(44, 104, 255, 0.05);
}

.btn-outline.block {
  width: 100%;
}

.mt-3 {
  margin-top: 12px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: #86909C;
  margin-bottom: 24px;
}

.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
