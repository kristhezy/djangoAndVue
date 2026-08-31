<template>
  <div class="merge-page">
    <el-card class="panel">
      <h2 class="title">手工合并用户</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="企业ID" prop="companyId">
          <el-input v-model="form.companyId" placeholder="请输入企业 ID" />
        </el-form-item>
        <el-form-item label="openID" prop="opids">
          <el-input v-model="form.opids" type="textarea" :rows="6"
            placeholder="多个 openID 换行分隔" />
        </el-form-item>
        <el-form-item label="环境">
          <el-radio-group v-model="form.env">
            <el-radio value="prod">生产环境</el-radio>
            <el-radio value="test">测试环境</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="submit">
            合并用户
          </el-button>
          <el-button size="large" @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-alert v-if="result" :title="result" :type="alertType" :closable="false" />
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import http from '../../api/http'

const formRef = ref()
const loading = ref(false)
const result = ref('')
const alertType = ref('success')

const form = reactive({ companyId: '', opids: '', env: 'prod' })

const rules = {
  companyId: [{ required: true, message: '企业ID不能为空', trigger: 'blur' }],
  opids: [{ required: true, message: 'openID不能为空', trigger: 'blur' }],
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  result.value = ''
  try {
    const resp = await http.post('/sv/mergeUser', {
      companyId: form.companyId,
      opids: form.opids,
      env: form.env,
    })
    // 后端返回 {code,msg,data:{a: 合并结果字符串}}；旧版 res.data 实为对象，
    // 此处取真实结果字符串展示，修正旧版 [object Object] 问题。
    const a = resp.data?.data?.a ?? JSON.stringify(resp.data?.data ?? '')
    result.value = a
    alertType.value = String(resp.data?.code) === '0' ? 'success' : 'error'
  } catch (e) {
    alertType.value = 'error'
    result.value = '请求失败：' + (e?.response?.data?.msg || e.message)
  } finally {
    loading.value = false
  }
}

function reset() {
  form.companyId = ''
  form.opids = ''
  form.env = 'prod'
  result.value = ''
}
</script>

<style scoped>
.merge-page { height: 100%; display: flex; justify-content: center; padding: 24px; }
.panel { width: 640px; max-width: 100%; align-self: flex-start; }
.title { text-align: center; margin-bottom: 16px; }
</style>
