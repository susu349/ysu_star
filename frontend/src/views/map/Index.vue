<template>
  <div class="map-page">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="goHome">校园AI助手</h1>
        <div class="header-actions">
          <div class="search-box">
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索地点..."
              @keyup.enter="searchPOIs"
            />
            <button class="search-btn" @click="searchPOIs">🔍</button>
          </div>
          <span class="welcome-text">欢迎，{{ userStore.username }}</span>
          <button @click="handleLogout" class="logout-btn">退出登录</button>
        </div>
      </div>
    </header>

    <main class="main">
      <div class="map-layout">
        <!-- 左侧面板 -->
        <aside class="side-panel" :class="{ collapsed: panelCollapsed }">
          <div class="panel-header">
            <h2>📍 智慧地图</h2>
            <button class="toggle-btn" @click="panelCollapsed = !panelCollapsed">
              {{ panelCollapsed ? '→' : '←' }}
            </button>
          </div>

          <div v-if="!panelCollapsed" class="panel-content">
            <div class="panel-tabs">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                :class="['tab', { active: activeTab === tab.key }]"
                @click="activeTab = tab.key"
              >
                {{ tab.label }}
              </button>
            </div>

            <!-- 热门地点 -->
            <div v-if="activeTab === 'pois'" class="panel-section">
              <h3>🔥 热门地点</h3>
              <div class="poi-list">
                <div
                  v-for="poi in hotPOIs"
                  :key="poi.id"
                  class="poi-item"
                  @click="focusPOI(poi)"
                >
                  <div class="poi-icon">{{ getPOIIcon(poi.poi_type) }}</div>
                  <div class="poi-info">
                    <div class="poi-name">{{ poi.name }}</div>
                    <div class="poi-stats">
                      <span>📷 {{ poi.check_in_count }} 打卡</span>
                      <span>❤️ {{ poi.like_count }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 最新打卡 -->
            <div v-if="activeTab === 'checkins'" class="panel-section">
              <h3>✨ 最新打卡</h3>
              <div class="checkin-list">
                <div
                  v-for="checkin in recentCheckIns"
                  :key="checkin.id"
                  class="checkin-item"
                  @click="viewCheckIn(checkin)"
                >
                  <div v-if="checkin.images && checkin.images.length > 0" class="checkin-image">
                    <img :src="checkin.images[0]" alt="" />
                  </div>
                  <div class="checkin-content">
                    <div class="checkin-text">{{ checkin.content || '分享了这个地点' }}</div>
                    <div class="checkin-meta">
                      <span class="checkin-time">{{ formatTime(checkin.created_at) }}</span>
                      <span class="checkin-likes">❤️ {{ checkin.like_count }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 热门话题 -->
            <div v-if="activeTab === 'topics'" class="panel-section">
              <h3>💬 热门话题</h3>
              <div class="topic-list">
                <div
                  v-for="topic in hotTopics"
                  :key="topic.id"
                  class="topic-item"
                  @click="filterByTopic(topic)"
                >
                  <span class="topic-tag">#{{ topic.name }}</span>
                  <span class="topic-count">{{ topic.check_in_count }} 打卡</span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        <!-- 地图区域 -->
        <div class="map-area">
          <div id="map" class="map-container"></div>

          <!-- 地图控制按钮 -->
          <div class="map-controls">
            <button class="control-btn" @click="zoomIn" title="放大">+</button>
            <button class="control-btn" @click="zoomOut" title="缩小">−</button>
            <button class="control-btn" @click="resetView" title="重置">📍</button>
            <button class="control-btn primary" @click="openCheckInModal" title="打卡">
              📷 打卡
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- 打卡弹窗 -->
    <div v-if="showCheckInModal" class="modal-overlay" @click.self="showCheckInModal = false">
      <div class="modal checkin-modal">
        <div class="modal-header">
          <h3>📷 分享打卡</h3>
          <button class="close-btn" @click="showCheckInModal = false">✕</button>
        </div>
        <div class="modal-body">
          <!-- 选择地点 -->
          <div class="form-group">
            <label>选择地点</label>
            <select v-model="checkInForm.poi_id" class="form-select">
              <option value="">请选择地点...</option>
              <option v-for="poi in hotPOIs" :key="poi.id" :value="poi.id">
                {{ poi.name }}
              </option>
            </select>
          </div>

          <!-- 输入内容 -->
          <div class="form-group">
            <label>分享内容</label>
            <textarea
              v-model="checkInForm.content"
              class="form-textarea"
              placeholder="分享你的所见所闻..."
              rows="4"
            ></textarea>
          </div>

          <!-- 上传图片 -->
          <div class="form-group">
            <label>上传图片</label>
            <div class="image-upload" @click="triggerImageUpload">
              <input
                ref="imageInput"
                type="file"
                accept="image/*"
                multiple
                @change="handleImageSelect"
                style="display: none"
              />
              <div class="upload-placeholder">
                <span class="upload-icon">🖼️</span>
                <span>点击或拖拽上传图片</span>
              </div>
            </div>
            <div class="image-preview">
              <div v-for="(img, idx) in checkInForm.images" :key="idx" class="preview-item">
                <img :src="img" alt="" />
                <button class="remove-btn" @click="removeImage(idx)">✕</button>
              </div>
            </div>
          </div>

          <!-- 添加话题 -->
          <div class="form-group">
            <label>添加话题</label>
            <div class="topic-selector">
              <button
                v-for="topic in hotTopics"
                :key="topic.id"
                :class="['topic-chip', { active: checkInForm.topics.includes(topic.name) }]"
                @click="toggleTopic(topic.name)"
              >
                #{{ topic.name }}
              </button>
            </div>
          </div>

          <!-- 可见性 -->
          <div class="form-group">
            <label>可见性</label>
            <div class="visibility-options">
              <label
                v-for="opt in visibilityOptions"
                :key="opt.value"
                :class="['visibility-option', { active: checkInForm.visibility === opt.value }]"
                @click="checkInForm.visibility = opt.value"
              >
                <span class="option-icon">{{ opt.icon }}</span>
                <span class="option-label">{{ opt.label }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showCheckInModal = false">取消</button>
          <button class="btn-primary" @click="submitCheckIn" :disabled="submitting">
            {{ submitting ? '发布中...' : '发布打卡' }}
          </button>
        </div>
      </div>
    </div>

    <!-- POI详情弹窗 -->
    <div v-if="showPOIDetail" class="modal-overlay" @click.self="showPOIDetail = false">
      <div class="modal poi-detail-modal">
        <div v-if="currentPOI" class="poi-detail">
          <div class="modal-header">
            <h3>{{ getPOIIcon(currentPOI.poi_type) }} {{ currentPOI.name }}</h3>
            <button class="close-btn" @click="showPOIDetail = false">✕</button>
          </div>
          <div class="modal-body">
            <p v-if="currentPOI.description" class="poi-desc">{{ currentPOI.description }}</p>

            <div class="poi-meta">
              <div v-if="currentPOI.address" class="meta-item">
                <span>📍</span>
                <span>{{ currentPOI.address }}</span>
              </div>
              <div v-if="currentPOI.opening_hours" class="meta-item">
                <span>🕐</span>
                <span>{{ currentPOI.opening_hours }}</span>
              </div>
            </div>

            <div class="poi-stats-bar">
              <div class="stat-item">
                <div class="stat-value">{{ currentPOI.check_in_count }}</div>
                <div class="stat-label">打卡</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ currentPOI.favorite_count }}</div>
                <div class="stat-label">收藏</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ currentPOI.view_count }}</div>
                <div class="stat-label">浏览</div>
              </div>
            </div>

            <div class="poi-actions">
              <button
                :class="['action-btn', { active: currentPOI.favorited }]"
                @click="toggleFavorite"
              >
                {{ currentPOI.favorited ? '❤️ 已收藏' : '🤍 收藏' }}
              </button>
              <button class="action-btn primary" @click="quickCheckIn">
                📷 在此打卡
              </button>
            </div>

            <div class="poi-checkins">
              <h4>最近打卡</h4>
              <div class="mini-checkin-list">
                <div
                  v-for="checkin in poiCheckIns"
                  :key="checkin.id"
                  class="mini-checkin"
                >
                  <div class="mini-checkin-content">
                    {{ checkin.content || '分享了这个地点' }}
                  </div>
                  <div class="mini-checkin-time">{{ formatTime(checkin.created_at) }}</div>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  getHotPOIs,
  getRecentCheckIns,
  getHotTopics,
  getPOIDetail,
  getCheckInList,
  createCheckIn,
  uploadMapImage,
  toggleFavorite as toggleFavoriteAPI,
  hasFavoritedPOI
} from '@/api/map'

const router = useRouter()
const userStore = useUserStore()

// 状态
const map = ref(null)
const markers = ref([])
const panelCollapsed = ref(false)
const activeTab = ref('pois')
const searchKeyword = ref('')
const hotPOIs = ref([])
const recentCheckIns = ref([])
const hotTopics = ref([])
const showCheckInModal = ref(false)
const showPOIDetail = ref(false)
const currentPOI = ref(null)
const poiCheckIns = ref([])
const submitting = ref(false)
const imageInput = ref(null)

const tabs = [
  { key: 'pois', label: '热门地点' },
  { key: 'checkins', label: '最新打卡' },
  { key: 'topics', label: '热门话题' }
]

const visibilityOptions = [
  { value: 'public', label: '公开', icon: '🌍' },
  { value: 'friends', label: '好友', icon: '👥' },
  { value: 'private', label: '私密', icon: '🔒' }
]

const checkInForm = ref({
  poi_id: '',
  content: '',
  images: [],
  topics: [],
  visibility: 'public'
})

// 燕山大学校园地图上的POI坐标（基于图片像素位置）
// 我们需要把经纬度映射到图片像素坐标，这里简化处理
const poiPixelMap = {
  // 这些是示例，需要根据实际地图调整
  // "poi-id": [x, y] 像素坐标
}

// 工具函数
const getPOIIcon = (type) => {
  const icons = {
    building: '🏢',
    landscape: '🌳',
    food: '🍽️',
    facility: '⚙️',
    other: '📍'
  }
  return icons[type] || '📍'
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = (now - date) / 1000

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  return date.toLocaleDateString('zh-CN')
}

// 地图操作 - 使用Simple CRS展示单张大图
const initMap = () => {
  // 使用Simple CRS，像素坐标系统
  const yx = L.CRS.Simple

  // 地图图片尺寸 - 需要根据实际图片调整
  const mapWidth = 4000
  const mapHeight = 3000

  // 创建地图
  map.value = L.map('map', {
    crs: yx,
    minZoom: -2,
    maxZoom: 2,
    zoomControl: false
  })

  // 添加单张图片作为图层
  const imageUrl = '/map-tiles/campus_map.png'
  const imageBounds = [[0, 0], [mapHeight, mapWidth]]

  L.imageOverlay(imageUrl, imageBounds).addTo(map.value)

  // 设置地图视图到中心
  map.value.setView([mapHeight / 2, mapWidth / 2], 0)

  // 添加POI标记
  updateMarkers()

  // 点击地图添加打卡
  map.value.on('click', (e) => {
    checkInForm.value.latitude = e.latlng.lat
    checkInForm.value.longitude = e.latlng.lng
  })
}

const updateMarkers = () => {
  if (!map.value) return

  markers.value.forEach(m => m.remove())
  markers.value = []

  // 为每个POI创建一个简单的标记（暂时使用随机位置，或者我们可以预定义位置）
  const mapHeight = 3000
  const mapWidth = 4000

  hotPOIs.value.forEach((poi, index) => {
    // 临时：在地图上分布POI
    const row = Math.floor(index / 4)
    const col = index % 4
    const y = (mapHeight / 5) * (row + 1)
    const x = (mapWidth / 5) * (col + 1)

    const icon = L.divIcon({
      html: `<div style="background: white; padding: 8px; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-size: 20px;">${getPOIIcon(poi.poi_type)}</div>`,
      className: 'custom-marker',
      iconSize: [40, 40],
      iconAnchor: [20, 20]
    })

    const marker = L.marker([y, x], { icon })
      .addTo(map.value)
      .on('click', () => openPOIDetail(poi))

    markers.value.push(marker)
  })
}

const zoomIn = () => map.value?.zoomIn()
const zoomOut = () => map.value?.zoomOut()
const resetView = () => {
  const mapHeight = 3000
  const mapWidth = 4000
  map.value?.setView([mapHeight / 2, mapWidth / 2], 0)
}

const focusPOI = (poi) => {
  openPOIDetail(poi)
}

// 数据加载
const loadData = async () => {
  try {
    const [poisRes, checkinsRes, topicsRes] = await Promise.all([
      getHotPOIs(20),
      getRecentCheckIns(20),
      getHotTopics(10)
    ])

    hotPOIs.value = poisRes.items || []
    recentCheckIns.value = checkinsRes.items || []
    hotTopics.value = topicsRes.items || []

    updateMarkers()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// POI详情
const openPOIDetail = async (poi) => {
  try {
    const detailRes = await getPOIDetail(poi.id)
    currentPOI.value = detailRes

    const favoritedRes = await hasFavoritedPOI(poi.id)
    currentPOI.value.favorited = favoritedRes.has_favorited

    const checkinsRes = await getCheckInList({ poi_id: poi.id, page_size: 10 })
    poiCheckIns.value = checkinsRes.items || []

    showPOIDetail.value = true
  } catch (error) {
    console.error('加载POI详情失败:', error)
  }
}

const toggleFavorite = async () => {
  if (!currentPOI.value) return
  try {
    const res = await toggleFavoriteAPI({ poi_id: currentPOI.value.id })
    currentPOI.value.favorited = res.favorited
    currentPOI.value.favorite_count = res.favorite_count
  } catch (error) {
    console.error('收藏操作失败:', error)
  }
}

const quickCheckIn = () => {
  if (!currentPOI.value) return
  checkInForm.value.poi_id = currentPOI.value.id
  showPOIDetail.value = false
  showCheckInModal.value = true
}

// 打卡相关
const openCheckInModal = () => {
  checkInForm.value = {
    poi_id: '',
    content: '',
    images: [],
    topics: [],
    visibility: 'public'
  }
  showCheckInModal.value = true
}

const triggerImageUpload = () => {
  imageInput.value?.click()
}

const handleImageSelect = async (e) => {
  const files = Array.from(e.target.files)
  for (const file of files) {
    try {
      const res = await uploadMapImage(file)
      checkInForm.value.images.push(res.url)
    } catch (error) {
      console.error('上传图片失败:', error)
      alert('图片上传失败')
    }
  }
}

const removeImage = (idx) => {
  checkInForm.value.images.splice(idx, 1)
}

const toggleTopic = (topic) => {
  const idx = checkInForm.value.topics.indexOf(topic)
  if (idx > -1) {
    checkInForm.value.topics.splice(idx, 1)
  } else {
    checkInForm.value.topics.push(topic)
  }
}

const submitCheckIn = async () => {
  if (!checkInForm.value.poi_id) {
    alert('请选择打卡地点')
    return
  }

  submitting.value = true
  try {
    await createCheckIn(checkInForm.value)
    showCheckInModal.value = false
    alert('打卡发布成功！')
    loadData()
  } catch (error) {
    console.error('发布打卡失败:', error)
    alert('发布失败，请重试')
  } finally {
    submitting.value = false
  }
}

const viewCheckIn = (checkin) => {
  console.log('查看打卡:', checkin)
}

const filterByTopic = (topic) => {
  activeTab.value = 'checkins'
  console.log('筛选话题:', topic)
}

const searchPOIs = () => {
  console.log('搜索:', searchKeyword.value)
}

// 导航
const goHome = () => router.push('/home')

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    await userStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  initMap()
  loadData()
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style scoped>
.map-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  z-index: 1000;
  flex-shrink: 0;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 4px 8px;
}

.search-box input {
  border: none;
  background: transparent;
  padding: 8px;
  width: 200px;
  outline: none;
}

.search-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  padding: 8px;
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
}

.main {
  flex: 1;
  overflow: hidden;
}

.map-layout {
  display: flex;
  height: 100%;
}

/* 侧边栏 */
.side-panel {
  width: 360px;
  background: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.side-panel.collapsed {
  width: 60px;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h2 {
  margin: 0;
  font-size: 18px;
}

.toggle-btn {
  border: none;
  background: #f5f7fa;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
}

.panel-tabs {
  display: flex;
  padding: 8px;
  gap: 4px;
}

.tab {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.tab.active {
  background: #2C68FF;
  color: white;
}

.panel-section {
  padding: 16px;
}

.panel-section h3 {
  margin: 0 0 12px;
  font-size: 15px;
  color: #333;
}

/* POI列表 */
.poi-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.poi-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.poi-item:hover {
  background: #f0f4ff;
  transform: translateX(4px);
}

.poi-icon {
  font-size: 28px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 10px;
}

.poi-info {
  flex: 1;
}

.poi-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.poi-stats {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 12px;
}

/* 打卡列表 */
.checkin-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkin-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 12px;
  cursor: pointer;
}

.checkin-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.checkin-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.checkin-content {
  flex: 1;
}

.checkin-text {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
}

.checkin-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

/* 话题列表 */
.topic-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.topic-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f9fafb;
  border-radius: 10px;
  cursor: pointer;
}

.topic-tag {
  font-weight: 600;
  color: #2C68FF;
}

.topic-count {
  font-size: 12px;
  color: #999;
}

/* 地图区域 */
.map-area {
  flex: 1;
  position: relative;
}

.map-container {
  width: 100%;
  height: 100%;
  background: #333;
}

.map-controls {
  position: absolute;
  right: 20px;
  top: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 1000;
}

.control-btn {
  width: 44px;
  height: 44px;
  border: none;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.12);
  cursor: pointer;
  font-size: 20px;
}

.control-btn.primary {
  width: auto;
  padding: 0 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 14px;
  font-weight: 600;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: white;
  border-radius: 16px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.checkin-modal {
  width: 500px;
}

.poi-detail-modal {
  width: 480px;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  border: none;
  background: #f5f7fa;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 表单 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  font-size: 14px;
}

.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  font-size: 14px;
  resize: none;
}

.image-upload {
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
}

.upload-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.image-preview {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.preview-item {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-item .remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border: none;
  background: rgba(0,0,0,0.6);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
}

.topic-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.topic-chip {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
}

.topic-chip.active {
  background: #2C68FF;
  color: white;
  border-color: #2C68FF;
}

.visibility-options {
  display: flex;
  gap: 12px;
}

.visibility-option {
  flex: 1;
  padding: 16px;
  border: 2px solid #f0f0f0;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
}

.visibility-option.active {
  border-color: #2C68FF;
  background: #f0f4ff;
}

.option-icon {
  font-size: 24px;
  display: block;
  margin-bottom: 4px;
}

.option-label {
  font-size: 13px;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:disabled {
  opacity: 0.6;
}

.btn-secondary {
  background: #f5f7fa;
  color: #666;
}

/* POI详情 */
.poi-desc {
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.poi-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.poi-stats-bar {
  display: flex;
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2C68FF;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.poi-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.action-btn {
  flex: 1;
  padding: 12px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
}

.action-btn.active {
  background: #fff0f0;
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.poi-checkins h4 {
  margin: 0 0 12px;
  font-size: 15px;
}

.mini-checkin-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mini-checkin {
  padding: 12px;
  background: #f9fafb;
  border-radius: 10px;
}

.mini-checkin-content {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.mini-checkin-time {
  font-size: 12px;
  color: #999;
}
</style>
