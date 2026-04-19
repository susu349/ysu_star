<template>
  <div class="test-container">
    <h1>API 测试页面</h1>
    <button @click="testDirectFetch">直接 fetch 测试</button>
    <button @click="testApiClient">API Client 测试</button>
    <hr>
    <h3>结果:</h3>
    <pre>{{ result }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getContestList } from '@/api/contest'

const result = ref('')

const testDirectFetch = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/v1/contest/list?limit=5')
    const data = await res.json()
    result.value = JSON.stringify(data, null, 2)
    console.log('直接 fetch 结果:', data)
  } catch (e) {
    result.value = '错误: ' + e.message
  }
}

const testApiClient = async () => {
  try {
    const data = await getContestList({ limit: 5 })
    result.value = JSON.stringify(data, null, 2)
    console.log('API Client 结果:', data)
    console.log('data.items:', data?.items)
    console.log('typeof data:', typeof data)
  } catch (e) {
    result.value = '错误: ' + e.message
  }
}
</script>

<style scoped>
.test-container {
  padding: 20px;
}
pre {
  background: #f5f5f5;
  padding: 10px;
  overflow: auto;
}
</style>
