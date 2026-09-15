<template>
  <div class="error-page">
    <div class="error-card">
      <div class="error-code">404</div>
      <div class="error-title">页面未找到</div>
      <div class="error-desc">您访问的页面不存在或已被移除。</div>
      <div class="error-actions">
        <el-button @click="router.back()">返回上一页</el-button>
        <el-button type="primary" @click="router.push('/home')">回首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.error-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
}
.error-card {
  text-align: center;
  background: var(--bg-card);
  padding: 60px 80px;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}
.error-code {
  font-size: 72px;
  font-weight: 700;
  color: var(--color-primary-light);
  line-height: 1;
}
.error-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 16px;
}
.error-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 8px;
}
.error-actions {
  margin-top: 32px;
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
