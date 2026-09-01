<template>
  <div class="batch-page">
    <el-card class="batch-card" shadow="never">
      <template #header>
        <div class="batch-title">批量删除线索</div>
      </template>
      <el-form label-position="top">
        <el-form-item label="选择企业ID" required>
          <el-select v-model="form.cid" placeholder="选择企业ID" style="width:100%">
            <el-option
              v-for="c in companies"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" required>
          <el-input
            v-model="form.phones"
            type="textarea"
            :rows="8"
            placeholder="输入手机号（支持逗号/换行/空格分隔多个）"
          />
        </el-form-item>
        <el-form-item label="环境">
          <el-radio-group v-model="form.env">
            <el-radio value="prod">生产环境</el-radio>
            <el-radio value="test">测试环境</el-radio>
          </el-radio-group>
        </el-form-item>
        <div class="batch-actions">
          <el-button type="primary" :loading="loading" @click="submit">提交</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
        <div class="batch-result">{{ result }}</div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

// 硬编码企业列表（复刻旧模板 AT_batchDeleteClue.html 第 77-81 行）
const companies = [
  { id: '693225071459762176', name: '石家庄七度文化传播有限公司(693225071459762176)【18630183501】' },
  { id: '844635664262787073', name: '石家庄七度文化传播有限公司转介绍(844635664262787073)【13303043501】' },
]

const form = reactive({ cid: '', phones: '', env: 'prod' })
const result = ref('')
const loading = ref(false)

async function submit() {
  if (!form.cid) { ElMessage.warning('企业ID不能为空！'); return }
  if (!form.phones.trim()) { ElMessage.warning('手机号码不能为空！'); return }
  loading.value = true
  try {
    const resp = await http.post('/sv/batchDeleteClue', {
      cid: form.cid, phones: form.phones, env: form.env,
    })
    result.value = resp.data?.data || ''
  } catch (e) {
    result.value = ''
    ElMessage.error('删除失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

function reset() {
  form.cid = ''
  form.phones = ''
  form.env = 'prod'
  result.value = ''
}
</script>

<style scoped>
.batch-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-sizing: border-box;
  background: #f0f2f5;
  overflow: hidden;
}
.batch-card {
  width: 680px;
  max-width: 100%;
  max-height: 100%;
  overflow-y: auto;
}
.batch-title { text-align: center; font-weight: 600; font-size: 20px; }
.batch-actions { display: flex; justify-content: center; gap: 12px; margin-top: 8px; }
.batch-result {
  margin-top: 16px;
  min-height: 40px;
  max-height: 360px;
  overflow-y: auto;
  padding: 10px;
  border-radius: 8px;
  font-size: 15px;
  text-align: center;
  word-break: break-all;
  white-space: pre-wrap;
  color: #409eff;
}
</style>
