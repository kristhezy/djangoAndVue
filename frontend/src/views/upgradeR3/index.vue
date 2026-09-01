<template>
  <div class="ur3-page">
    <div class="ur3-cols">
      <!-- 左栏：配置 -->
      <el-card class="ur3-panel ur3-panel--main" shadow="never">
        <template #header>
          <div class="ur3-title">转介绍 3.0 配置</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企业 ID / 席位" required>
            <div class="ur3-seats">
              <el-input
                v-model="form.companyIds"
                type="textarea"
                :rows="4"
                placeholder="企业 IDs"
              />
              <el-input
                v-model="form.seats"
                type="textarea"
                :rows="4"
                placeholder="席位数"
              />
            </div>
          </el-form-item>

          <el-form-item label="环境">
            <el-radio-group v-model="form.env">
              <el-radio value="prod">生产</el-radio>
              <el-radio value="test">测试</el-radio>
            </el-radio-group>
          </el-form-item>

          <div class="ur3-actions">
            <el-button type="primary" :loading="loading" @click="submit">提交</el-button>
            <el-button @click="reset">重置</el-button>
          </div>

          <div class="result">{{ result1 }}</div>

          <template v-if="submitted">
            <div class="ur3-tips">菜单sql,若企业菜单异常,需执行此处sql</div>
            <div class="ur3-sql">{{ formatResult(sql) }}</div>
            <div class="ur3-copy">
              <el-button type="primary" plain @click="copyAndJump">复制并跳转提交sql</el-button>
            </div>
          </template>
        </el-form>
      </el-card>

      <!-- 右栏：执行结果 -->
      <el-card class="ur3-panel" shadow="never">
        <template #header>
          <div class="ur3-title">执行结果</div>
        </template>
        <div v-loading="logLoading" class="ur3-log">
          <div v-if="!records.length" class="ur3-empty">暂无数据</div>
          <div v-for="(r, i) in records" :key="i" class="ur3-item">
            <div class="ur3-item__head">
              <span class="ur3-item__title">{{ r.env }} ┆ {{ r.companyName }}（{{ r.companyId }}）</span>
              <span class="ur3-item__time">{{ r.t }}</span>
            </div>
            <div class="ur3-item__msg">{{ r.message }}</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const form = reactive({ companyIds: '', seats: '', env: 'prod' })
const result1 = ref('')
const sql = ref('')
const submitted = ref(false)
const loading = ref(false)
const records = ref([])
const logLoading = ref(false)

// 后端 ur3sql 含 <br/> 与 \n，转成纯换行（防 XSS，不用 v-html）
function formatResult(str) {
  return (str || '').replace(/<br\s*\/?>/gi, '\n')
}

// 查询操作信息列表
async function qbdan(num) {
  const resp = await http.post('/sv/qmbydsan', { dss: [1], num })
  const res = resp.data?.data?.qmbydsan
  if (!Array.isArray(res)) {
    records.value = []
    return
  }
  records.value = res
}

// 查询并异步刷新缓存
async function querymsgbyds(num) {
  logLoading.value = true
  try {
    await qbdan(num)
    const resp = await http.post('/sv/aftergetqmbydsan', { dss: [1], num })
    if (resp.data?.data === '更新数据成功！') {
      await qbdan(num)
    }
  } catch (e) {
    console.log(`查询操作信息err: ${e.message}`)
  } finally {
    logLoading.value = false
  }
}

async function submit() {
  const { companyIds, seats, env } = form
  if (!companyIds) {
    ElMessage.warning('企业id不能为空！')
    return
  }
  if (!seats) {
    ElMessage.warning('席位数不能为空！')
    return
  }
  loading.value = true
  try {
    const resp = await http.post('/sv/upgradeR3', { companyIds, seats, env })
    result1.value = resp.data?.data?.upgradeR3 || ''
    sql.value = resp.data?.data?.ur3sql || ''
    submitted.value = true
    querymsgbyds(4)
  } catch (e) {
    result1.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

async function copyAndJump() {
  const text = formatResult(sql.value)
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
    } else {
      const ta = document.createElement('textarea')
      ta.value = text
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    ElMessage.success('复制成功！')
  } catch (e) {
    ElMessage.error('复制失败：' + e.message)
  }
  window.open('https://sqlprod.jiatuiyun.net/submitsql/', '_blank')
}

function reset() {
  form.companyIds = ''
  form.seats = ''
  form.env = 'prod'
  result1.value = ''
  sql.value = ''
  submitted.value = false
}

onMounted(() => {
  querymsgbyds(10)
})
</script>

<style scoped>
.ur3-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.ur3-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.ur3-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.ur3-panel--main {
  flex: 1.2;
}
.ur3-panel :deep(.el-card__body) { overflow-y: auto; }
.ur3-title { text-align: center; font-weight: 600; font-size: 16px; }
.ur3-seats {
  display: flex;
  gap: 10px;
  width: 100%;
}
.ur3-seats :deep(.el-textarea) {
  flex: 1;
  min-width: 0;
}
.ur3-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
.result {
  margin-top: 12px;
  min-height: 40px;
  font-size: 14px;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
  border-top: 1px solid #e4e7ed;
  padding-top: 8px;
}
.ur3-tips {
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
}
.ur3-sql {
  margin-top: 6px;
  font-size: 12px;
  color: #c0c4cc;
  white-space: pre-wrap;
  word-break: break-all;
  user-select: none;
}
.ur3-copy { margin-top: 10px; }
.ur3-log { min-height: 200px; }
.ur3-empty {
  color: #c0c4cc;
  text-align: center;
  padding: 48px 20px;
}
.ur3-item {
  padding: 10px 12px;
  border-bottom: 1px solid #ebeef5;
}
.ur3-item__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.ur3-item__title { font-weight: 600; font-size: 14px; color: #303133; }
.ur3-item__time { font-size: 12px; color: #909399; white-space: nowrap; }
.ur3-item__msg {
  margin-top: 4px;
  font-size: 13px;
  color: #606266;
  word-break: break-all;
}
</style>
