<template>
  <div class="busk-page">
    <div class="busk-card">
      <el-card shadow="never">
        <template #header>
          <div class="busk-title">工具版升级 SK</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企业数据" required>
            <div class="busk-seats">
              <el-input v-model="form.companyIds" type="textarea" :rows="4" placeholder="企业 ID" />
              <el-input v-model="form.sseats" type="textarea" :rows="4" placeholder="销售席位" />
              <el-input v-model="form.pseats" type="textarea" :rows="4" placeholder="推荐官席位" />
            </div>
          </el-form-item>

          <el-form-item label="企业模块">
            <el-checkbox-group v-model="form.mk">
              <el-checkbox value="M107">M107（推广表单）</el-checkbox>
              <el-checkbox value="M138">M138（任务中心）</el-checkbox>
              <el-checkbox value="M139">M139（产品库）</el-checkbox>
              <el-checkbox value="M141">M141（折扣卡）</el-checkbox>
              <el-checkbox value="M142">M142（小程序装修）</el-checkbox>
              <el-checkbox value="M143">M143（AI名片）</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="环境">
            <el-radio-group v-model="form.env">
              <el-radio value="prod">生产</el-radio>
              <el-radio value="test">测试</el-radio>
            </el-radio-group>
          </el-form-item>

          <div class="busk-actions">
            <el-button type="primary" :loading="loading" @click="submit">提交</el-button>
            <el-button @click="reset">重置</el-button>
          </div>

          <div class="result">{{ formatResult(result1) }}</div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const form = reactive({ companyIds: '', sseats: '', pseats: '', mk: [], env: 'prod' })
const result1 = ref('')
const loading = ref(false)

// 后端返回含 <br/>，转成换行，文本插值 + pre-wrap 展示（防 XSS）
function formatResult(str) {
  return (str || '').replace(/<br\s*\/?>/gi, '\n')
}

async function submit() {
  const { companyIds, sseats, pseats, mk, env } = form
  if (!companyIds || !sseats || !pseats) {
    ElMessage.warning('必填项不能为空！')
    return
  }
  loading.value = true
  try {
    const resp = await http.post('/sv/baseUpgradeSK', {
      companyIds, sseats, pseats,
      mk: mk.join(','),
      env,
    })
    result1.value = resp.data?.data || ''
  } catch (e) {
    result1.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

function reset() {
  form.companyIds = ''
  form.sseats = ''
  form.pseats = ''
  form.mk = []
  form.env = 'prod'
  result1.value = ''
}
</script>

<style scoped>
.busk-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 12px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
}
.busk-card {
  width: 720px;
  max-width: 100%;
  display: flex;
  flex-direction: column;
}
.busk-card :deep(.el-card) {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.busk-card :deep(.el-card__body) { overflow-y: auto; padding: 24px; }
.busk-title { text-align: center; font-weight: 600; font-size: 16px; }
.busk-seats {
  display: flex;
  gap: 10px;
  width: 100%;
}
.busk-seats :deep(.el-textarea) {
  flex: 1;
  min-width: 0;
}
.busk-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
.result {
  margin-top: 12px;
  min-height: 40px;
  font-size: 14px;
  color: #444;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-all;
  border-top: 1px solid #e4e7ed;
  padding-top: 8px;
}
</style>
