<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 左侧装饰面板 -->
      <div class="left-panel">
        <div class="poetry">
          <div>两岸猿声啼不住</div>
          <div class="line2">轻舟已过万重山</div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="right-panel">
        <h1>测试平台登录</h1>
        <el-form :model="form" class="login-form" @submit.prevent="handleLogin">
          <el-form-item>
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              size="large"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="form.remember">记住账号</el-checkbox>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { doLogin } from '../../api/login'

const router = useRouter()
const route = useRoute()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember: true,
})

onMounted(() => {
  // 恢复记住的用户名
  form.username = localStorage.getItem('username') || ''
  // 清理旧版明文密码缓存
  localStorage.removeItem('password')
  if (form.username) {
    form.remember = true
  }
})

async function handleLogin() {
  if (!form.username) {
    ElMessage.warning('请输入账号')
    return
  }
  if (!form.password) {
    ElMessage.warning('请输入密码')
    return
  }

  loading.value = true
  try {
    const next = route.query.next || ''
    const { data: res } = await doLogin(form.username, form.password, next)
    if (res.success) {
      // 保存/清除记住的用户名
      if (form.remember) {
        localStorage.setItem('username', form.username)
      } else {
        localStorage.removeItem('username')
      }
      ElMessage.success('登录成功')
      let target = res.redirect_url || '/home'
      try {
        const u = new URL(target)
        target = u.pathname + u.search
      } catch { /* already a relative path */ }
      router.push(target)
    } else {
      ElMessage.error(res.error || '登录失败')
    }
  } catch (err) {
    console.error('登录失败:', err)
    ElMessage.error('登录失败，请检查网络')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('../../assets/bg.webp') no-repeat center center fixed;
  background-size: cover;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.login-container {
  display: flex;
  width: 780px;
  height: 440px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* 左侧装饰面板 */
.left-panel {
  flex: 1;
  background: linear-gradient(135deg, #2D7EE8 0%, #1a5bbf 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  font-family: "KaiTi", "STKaiti", "楷体", "Noto Serif SC", serif;
}

.left-panel .poetry {
  color: rgba(255, 255, 255, 0.9);
  font-size: 22px;
  line-height: 2;
  letter-spacing: 4px;
  text-align: center;
}

.left-panel .poetry .line2 {
  margin-top: 16px;
}

/* 右侧表单面板 */
.right-panel {
  flex: 1;
  background: var(--bg-card);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 48px;
}

.right-panel h1 {
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 32px;
}

.login-form {
  width: 100%;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 6px;
}

.login-btn {
  width: 100%;
  font-size: 16px;
  background-color: #2D7EE8;
  border-color: #2D7EE8;
}

.login-btn:hover {
  background-color: #1a5bbf;
  border-color: #1a5bbf;
}
</style>
