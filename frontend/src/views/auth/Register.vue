<template>
  <div class="register-container">
    <div class="register-box">
      <h1>校园AI助手</h1>
      <h2>用户注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>学号/工号</label>
          <input v-model="registerData.id" type="text" placeholder="请输入学号/工号" required />
        </div>
        <div class="form-group">
          <label>用户名</label>
          <input v-model="registerData.username" type="text" placeholder="请输入用户名" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="registerData.password" type="password" placeholder="请输入密码（至少6位）" required />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input v-model="confirmPassword" type="password" placeholder="请再次输入密码" required />
        </div>
        <div class="form-group">
          <label>真实姓名（可选）</label>
          <input v-model="registerData.real_name" type="text" placeholder="请输入真实姓名" />
        </div>
        <div class="form-group">
          <label>角色</label>
          <select v-model="registerData.role">
            <option value="student">学生</option>
            <option value="teacher">教师</option>
          </select>
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="login-link">
        已有账号？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/auth'

const router = useRouter()

const loading = ref(false)
const confirmPassword = ref('')
const registerData = reactive({
  id: '',
  username: '',
  password: '',
  real_name: '',
  role: 'student'
})

const handleRegister = async () => {
  if (!registerData.id || !registerData.username || !registerData.password) {
    alert('请填写必填项')
    return
  }

  if (registerData.password.length < 6) {
    alert('密码至少需要6位')
    return
  }

  if (registerData.password !== confirmPassword.value) {
    alert('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    await register(registerData)
    alert('注册成功！请登录')
    router.push('/login')
  } catch (error) {
    console.error('Register failed:', error)
    alert(error.response?.data?.detail || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 0;
}

.register-box {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

.register-box h1 {
  text-align: center;
  color: #333;
  margin-bottom: 8px;
  font-size: 28px;
}

.register-box h2 {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 18px;
  font-weight: normal;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.register-box button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
}

.register-box button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.register-box button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 24px;
  color: #666;
  font-size: 14px;
}

.login-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
