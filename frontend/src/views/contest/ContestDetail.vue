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
            <!-- 赛事简介 - 使用 AI 生成的简洁说明 -->
            <div class="section">
              <h3 class="section-title">赛事简介</h3>
              <p class="section-content">{{ contest.brief_description || contest.summary || '暂无简介' }}</p>
            </div>

            <!-- 折叠区域：详细信息 -->
            <div class="collapsible-section">
              <div class="collapsible-header" @click="toggleSection('details')">
                <span class="collapsible-title">📋 详细信息</span>
                <span class="collapsible-icon">{{ expandedSections.details ? '−' : '+' }}</span>
              </div>
              <div v-if="expandedSections.details" class="collapsible-content">
                <div class="info-grid">
                  <div class="info-block" v-if="contest.eligibility_requirements">
                    <h4>参赛资格</h4>
                    <p>{{ contest.eligibility_requirements }}</p>
                  </div>
                  <div class="info-block" v-if="contest.participation_process">
                    <h4>参赛流程</h4>
                    <p>{{ contest.participation_process }}</p>
                  </div>
                  <div class="info-block" v-if="contest.awards_info">
                    <h4>奖项信息</h4>
                    <p>{{ contest.awards_info }}</p>
                  </div>
                  <div class="info-block" v-if="contest.recommendations">
                    <h4>推荐建议</h4>
                    <p>{{ contest.recommendations }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 附件列表 -->
            <div class="section" v-if="attachments && attachments.length > 0">
              <h3 class="section-title">📎 赛事附件</h3>
              <div class="attachments-list">
                <a
                  v-for="attachment in attachments"
                  :key="attachment.id"
                  :href="attachment.url"
                  target="_blank"
                  class="attachment-item"
                >
                  <span class="attachment-icon">{{ getFileIcon(attachment.file_type) }}</span>
                  <span class="attachment-name">{{ attachment.name }}</span>
                  <span class="attachment-size" v-if="attachment.file_size">{{ formatFileSize(attachment.file_size) }}</span>
                  <span class="attachment-download">📥 下载</span>
                </a>
              </div>
            </div>

            <!-- 标签 -->
            <div class="section" v-if="contest.tags && contest.tags.length > 0">
              <h3 class="section-title">🏷️ 赛事标签</h3>
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
              <h3 class="card-title">结队方式</h3>
              <div class="team-method-detail">
                <p class="method-item">✅ 加入已有队伍</p>
                <p class="method-item">✅ 创建新队伍</p>
                <p class="method-hint">建议：先浏览赛事详情，再选择合适的队伍加入或创建新队伍</p>
              </div>
            </div>

            <div class="info-card">
              <h3 class="card-title">快捷操作</h3>
              <button class="btn-primary block">立即报名</button>
              <button class="btn-outline block mt-3">寻找队友</button>
            </div>
          </div>
        </div>

        <!-- 评论区 -->
        <div class="comments-section">
          <h3 class="section-title">💬 赛事评论</h3>

          <!-- 发表评论 -->
          <div class="comment-input-wrapper">
            <textarea
              v-model="newComment"
              class="comment-input"
              placeholder="说说你的看法..."
              rows="3"
            ></textarea>
            <div class="comment-actions">
              <button class="btn-primary" @click="submitComment" :disabled="!newComment.trim()">发表评论</button>
            </div>
          </div>

          <!-- 评论列表 -->
          <div class="comments-list">
            <div v-if="commentsLoading" class="loading-state small">
              <div class="loading-spinner small"></div>
            </div>

            <div v-else-if="comments.length === 0" class="empty-state small">
              <p>暂无评论，来抢沙发吧！</p>
            </div>

            <div v-else class="comment-item" v-for="comment in comments" :key="comment.id">
              <div class="comment-avatar">
                {{ comment.user_id?.charAt(0)?.toUpperCase() || '?' }}
              </div>
              <div class="comment-content-wrapper">
                <div class="comment-header">
                  <span class="comment-user">用户 {{ comment.user_id?.slice(0, 8) }}</span>
                  <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                </div>
                <p class="comment-text">{{ comment.content }}</p>
                <div class="comment-footer">
                  <button class="like-btn" @click="likeComment(comment.id)">
                    👍 {{ comment.like_count || 0 }}
                  </button>
                  <button class="reply-btn" @click="replyToComment(comment)">回复</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { getContestDetail, getContestAttachments, getContestComments, createComment, likeComment as likeCommentApi } from '@/api/contest'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const contest = ref(null)
const comments = ref([])
const commentsLoading = ref(false)
const newComment = ref('')
const attachments = ref([])

const expandedSections = reactive({
  details: false
})

const toggleSection = (section) => {
  expandedSections[section] = !expandedSections[section]
}

const getFileIcon = (fileType) => {
  const typeMap = {
    'pdf': '📄',
    'doc': '📝',
    'docx': '📝',
    'xls': '📊',
    'xlsx': '📊',
    'ppt': '📽️',
    'pptx': '📽️',
    'zip': '📦',
    'rar': '📦',
  }
  return typeMap[fileType?.toLowerCase()] || '📎'
}

const formatFileSize = (bytes) => {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const fetchContestDetail = async () => {
  loading.value = true
  try {
    const data = await getContestDetail(route.params.id)
    contest.value = data
    // 获取附件
    const attachData = await getContestAttachments(route.params.id)
    attachments.value = attachData || []
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
    'INTERNATIONAL': '国际级',
    'PROVINCIAL': '省级',
    'PROVINCE': '省级',
    'SCHOOL': '校级'
  }
  return map[levelUpper] || level || '未知'
}

const getLevelTagClass = (level) => {
  const levelUpper = level?.toUpperCase()
  const map = {
    'NATIONAL': 'tag-warning',
    'INTERNATIONAL': 'tag-warning',
    'PROVINCIAL': 'tag-primary',
    'PROVINCE': 'tag-primary',
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

const fetchComments = async () => {
  commentsLoading.value = true
  try {
    const data = await getContestComments(route.params.id, { limit: 100 })
    comments.value = data.items || data || []
  } catch (error) {
    console.error('获取评论失败:', error)
  } finally {
    commentsLoading.value = false
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  try {
    await createComment({
      contest_id: route.params.id,
      content: newComment.value
    })
    newComment.value = ''
    await fetchComments()
  } catch (error) {
    console.error('发表评论失败:', error)
    alert('发表评论失败')
  }
}

const likeComment = async (commentId) => {
  try {
    await likeCommentApi(commentId)
    await fetchComments()
  } catch (error) {
    console.error('点赞失败:', error)
  }
}

const replyToComment = (comment) => {
  alert('回复功能开发中...')
}

onMounted(() => {
  fetchContestDetail()
  fetchComments()
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

.collapsible-section {
  margin-bottom: 24px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.collapsible-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #F7F8FA;
  cursor: pointer;
  transition: background 0.25s ease;
}

.collapsible-header:hover {
  background: #f0f2f5;
}

.collapsible-title {
  font-size: 16px;
  font-weight: 600;
  color: #1D2129;
}

.collapsible-icon {
  font-size: 24px;
  color: #86909C;
  font-weight: 300;
}

.collapsible-content {
  padding: 20px;
}

.info-grid {
  display: grid;
  gap: 20px;
}

.info-block {
  padding: 16px;
  background: #F7F8FA;
  border-radius: 8px;
}

.info-block h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1D2129;
}

.info-block p {
  margin: 0;
  font-size: 14px;
  color: #4E5969;
  line-height: 1.7;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #F7F8FA;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.25s ease;
}

.attachment-item:hover {
  background: #f0f2f5;
}

.attachment-icon {
  font-size: 24px;
}

.attachment-name {
  flex: 1;
  font-size: 14px;
  color: #1D2129;
}

.attachment-size {
  font-size: 13px;
  color: #86909C;
}

.attachment-download {
  padding: 6px 12px;
  background: rgba(44, 104, 255, 0.1);
  color: #2C68FF;
  border-radius: 4px;
  font-size: 13px;
  transition: background 0.25s ease;
}

.attachment-item:hover .attachment-download {
  background: rgba(44, 104, 255, 0.15);
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

.team-method-detail {
  padding: 8px 0;
}

.method-item {
  font-size: 14px;
  color: #1D2129;
  margin: 8px 0;
  padding-left: 8px;
}

.method-hint {
  font-size: 13px;
  color: #86909C;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
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

.comments-section {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid #f0f0f0;
}

.comment-input-wrapper {
  margin-bottom: 24px;
}

.comment-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #E5E6EB;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  outline: none;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.comment-input:focus {
  border-color: #2C68FF;
}

.comment-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.comments-list {
  margin-top: 24px;
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  flex-shrink: 0;
}

.comment-content-wrapper {
  flex: 1;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.comment-user {
  font-size: 14px;
  font-weight: 600;
  color: #1D2129;
}

.comment-time {
  font-size: 13px;
  color: #86909C;
}

.comment-text {
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 12px 0;
  word-break: break-word;
}

.comment-footer {
  display: flex;
  gap: 16px;
}

.like-btn,
.reply-btn {
  padding: 4px 12px;
  background: none;
  border: none;
  color: #86909C;
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.25s ease;
}

.like-btn:hover,
.reply-btn:hover {
  color: #2C68FF;
  background: rgba(44, 104, 255, 0.05);
}

.empty-state.small {
  padding: 40px 20px;
}

.empty-state.small p {
  margin: 0;
  color: #86909C;
  font-size: 14px;
}

.loading-state.small {
  padding: 40px 20px;
}

.loading-spinner.small {
  width: 24px;
  height: 24px;
  border-width: 3px;
  margin: 0 auto;
}
</style>
