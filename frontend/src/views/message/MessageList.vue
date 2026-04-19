<template>
  <div class="message-container">
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
      <div class="message-layout">
        <!-- 会话列表 -->
        <aside class="conversation-list">
          <div class="list-header">
            <h3>私信</h3>
          </div>

          <div v-if="loading" class="loading-state small">
            <div class="loading-spinner small"></div>
          </div>

          <div v-else-if="conversations.length === 0" class="empty-state small">
            <p>暂无会话</p>
          </div>

          <div
            v-else
            class="conversation-item"
            v-for="conv in conversations"
            :key="conv.user_id"
            :class="{ active: selectedUserId === conv.user_id }"
            @click="selectConversation(conv)"
          >
            <div class="conversation-avatar">
              {{ conv.user_id?.charAt(0)?.toUpperCase() || '?' }}
            </div>
            <div class="conversation-info">
              <div class="conversation-top">
                <span class="conversation-name">用户 {{ conv.user_id?.slice(0, 8) }}</span>
                <span v-if="conv.unread_count > 0" class="unread-badge">{{ conv.unread_count }}</span>
              </div>
              <p class="conversation-preview">{{ conv.last_message?.content || '暂无消息' }}</p>
            </div>
          </div>
        </aside>

        <!-- 聊天区域 -->
        <main class="chat-area">
          <div v-if="!selectedUserId" class="empty-chat">
            <div class="empty-icon">💬</div>
            <p>选择一个会话开始聊天</p>
          </div>

          <div v-else>
            <!-- 聊天头部 -->
            <div class="chat-header">
              <div class="chat-user-info">
                <div class="conversation-avatar">
                  {{ selectedUserId?.charAt(0)?.toUpperCase() || '?' }}
                </div>
                <span class="chat-user-name">用户 {{ selectedUserId?.slice(0, 8) }}</span>
              </div>
            </div>

            <!-- 消息列表 -->
            <div class="messages-list" ref="messagesListRef">
              <div v-if="messagesLoading" class="loading-state small">
                <div class="loading-spinner small"></div>
              </div>

              <div v-else-if="messages.length === 0" class="empty-state small">
                <p>暂无消息，开始聊天吧</p>
              </div>

              <div
                v-else
                class="message-item"
                v-for="msg in messages"
                :key="msg.id"
                :class="{ 'message-sent': msg.sender_id === userStore.userId }"
              >
                <div class="message-avatar" v-if="msg.sender_id !== userStore.userId">
                  {{ msg.sender_id?.charAt(0)?.toUpperCase() || '?' }}
                </div>
                <div class="message-bubble">
                  <p class="message-text">{{ msg.content }}</p>
                  <span class="message-time">{{ formatDate(msg.created_at) }}</span>
                </div>
                <div class="message-avatar sent" v-if="msg.sender_id === userStore.userId">
                  {{ msg.sender_id?.charAt(0)?.toUpperCase() || '?' }}
                </div>
              </div>
            </div>

            <!-- 输入区域 -->
            <div class="chat-input-wrapper">
              <textarea
                v-model="newMessage"
                class="chat-input"
                placeholder="输入消息..."
                rows="2"
                @keydown.enter.prevent="sendMessage"
              ></textarea>
              <button class="btn-primary send-btn" @click="sendMessage" :disabled="!newMessage.trim()">
                发送
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { getConversations, getMessagesWithUser, sendMessage as sendMessageApi } from '@/api/contest'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const messagesLoading = ref(false)
const conversations = ref([])
const messages = ref([])
const selectedUserId = ref(null)
const newMessage = ref('')
const messagesListRef = ref(null)

const fetchConversations = async () => {
  loading.value = true
  try {
    const data = await getConversations()
    conversations.value = data || []
  } catch (error) {
    console.error('获取会话列表失败:', error)
  } finally {
    loading.value = false
  }
}

const selectConversation = async (conv) => {
  selectedUserId.value = conv.user_id
  await fetchMessages(conv.user_id)
}

const fetchMessages = async (userId) => {
  messagesLoading.value = true
  try {
    const data = await getMessagesWithUser(userId, { limit: 100 })
    messages.value = data.items || data || []
    await scrollToBottom()
  } catch (error) {
    console.error('获取消息失败:', error)
  } finally {
    messagesLoading.value = false
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedUserId.value) return

  try {
    await sendMessageApi({
      receiver_id: selectedUserId.value,
      content: newMessage.value
    })
    newMessage.value = ''
    await fetchMessages(selectedUserId.value)
    await fetchConversations()
  } catch (error) {
    console.error('发送消息失败:', error)
    alert('发送消息失败')
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesListRef.value) {
    messagesListRef.value.scrollTop = messagesListRef.value.scrollHeight
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goHome = () => {
  router.push('/home')
}

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    await userStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  fetchConversations()
})
</script>

<style scoped>
.message-container {
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

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.message-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
  height: calc(100vh - 120px);
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
}

.conversation-list {
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
}

.list-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.list-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1D2129;
}

.conversation-item {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.25s ease;
  border-bottom: 1px solid #f5f5f5;
}

.conversation-item:hover {
  background: #F7F8FA;
}

.conversation-item.active {
  background: rgba(44, 104, 255, 0.05);
}

.conversation-avatar {
  width: 44px;
  height: 44px;
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

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.conversation-name {
  font-size: 15px;
  font-weight: 600;
  color: #1D2129;
}

.unread-badge {
  background: #F53F3F;
  color: white;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

.conversation-preview {
  font-size: 13px;
  color: #86909C;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-area {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #86909C;
}

.empty-chat .empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.chat-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-user-name {
  font-size: 16px;
  font-weight: 600;
  color: #1D2129;
}

.messages-list {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-item.message-sent {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.message-avatar.sent {
  background: linear-gradient(135deg, #34E4AA 0%, #00A870 100%);
}

.message-bubble {
  max-width: 60%;
  padding: 12px 16px;
  background: #F7F8FA;
  border-radius: 12px;
  position: relative;
}

.message-sent .message-bubble {
  background: #2C68FF;
  color: white;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 4px 0;
  word-break: break-word;
}

.message-time {
  font-size: 11px;
  color: #86909C;
  opacity: 0.7;
}

.message-sent .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.chat-input-wrapper {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #E5E6EB;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
  outline: none;
  transition: border-color 0.3s;
}

.chat-input:focus {
  border-color: #2C68FF;
}

.send-btn {
  padding: 10px 24px;
  white-space: nowrap;
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

.empty-state.small {
  padding: 40px 20px;
  text-align: center;
}

.empty-state.small p {
  margin: 0;
  color: #86909C;
  font-size: 14px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
</style>
