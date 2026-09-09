<template>
  <div class="error-page">
    <div class="error-card">
      <div class="error-code">403</div>
      <div class="error-title">无权限访问</div>
      <div class="error-desc">您没有权限访问该页面，请联系管理员。</div>
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
  background: #f0f2f5;
}
.error-card {
  text-align: center;
  background: #fff;
  padding: 60px 80px;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}
.error-code {
  font-size: 72px;
  font-weight: 700;
  color: #e6a23c;
  line-height: 1;
}
.error-title {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin-top: 16px;
}
.error-desc {
  font-size: 14px;
  color: #64748b;
  margin-top: 8px;
}
.error-actions {
  margin-top: 32px;
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
