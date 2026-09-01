<template>
  <div class="dzfn-page">
    <div class="dzfn-cols">
      <!-- 卡片1: 红蚂蚁企业修改客户阶段 -->
      <el-card class="dzfn-card" shadow="never">
        <template #header>
          <div class="dzfn-title">红蚂蚁企业修改客户阶段</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="客户 ID" required>
            <el-input v-model="form1.cfid" placeholder="输入CustomerFormID" />
          </el-form-item>
          <el-form-item label="跟进状态" required>
            <el-input v-model="form1.fs" placeholder="输入生命周期顺序，从0起" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form1.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="dzfn-actions">
            <el-button type="primary" :loading="loading1" @click="updateStage">提交</el-button>
            <el-button @click="reset1">重置</el-button>
          </div>
          <div class="result">{{ result1 }}</div>
        </el-form>
      </el-card>

      <!-- 卡片2: 华为云license激活 -->
      <el-card class="dzfn-card" shadow="never">
        <template #header>
          <div class="dzfn-title">华为云license激活</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form2.compid" placeholder="输入加推的企业ID" />
          </el-form-item>
          <el-form-item label="授权码" required>
            <el-input v-model="form2.lisence" placeholder="输入华为云lisence授权码" />
          </el-form-item>
          <el-form-item label="备注" required>
            <el-input v-model="form2.remark" placeholder="输入lisence的备注信息" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form2.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="dzfn-actions">
            <el-button type="primary" :loading="loading2" @click="activateLicense">提交</el-button>
            <el-button @click="reset2">重置</el-button>
          </div>
          <div class="result">{{ result2 }}</div>
        </el-form>
      </el-card>

      <!-- 卡片3: 预留 -->
      <el-card class="dzfn-card" shadow="never">
        <template #header>
          <div class="dzfn-title">预留功能区域</div>
        </template>
        <div class="dzfn-placeholder">
          <p>此区域预留用于未来功能扩展</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const form1 = reactive({ cfid: '', fs: '', env: 'prod' })
const form2 = reactive({ compid: '', lisence: '', remark: '', env: 'prod' })
const result1 = ref('')
const result2 = ref('')
const loading1 = ref(false)
const loading2 = ref(false)

async function updateStage() {
  if (!form1.cfid || !form1.fs) { ElMessage.warning('必填项不能为空！'); return }
  loading1.value = true
  try {
    const resp = await http.post('/sv/dzFunction', {
      cfid: form1.cfid, fs: form1.fs, env: form1.env, type: 'hmyupdcs',
    })
    result1.value = resp.data?.data || ''
  } catch (e) {
    result1.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading1.value = false
  }
}

async function activateLicense() {
  if (!form2.lisence) { ElMessage.warning('"lisence"不能为空！'); return }
  loading2.value = true
  try {
    const resp = await http.post('/sv/dzFunction', {
      compid: form2.compid, lisence: form2.lisence, remark: form2.remark,
      env: form2.env, type: 'hwylicensejh',
    })
    result2.value = resp.data?.data || ''
  } catch (e) {
    result2.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading2.value = false
  }
}

function reset1() {
  form1.cfid = ''; form1.fs = ''; form1.env = 'prod'
  result1.value = ''
}
function reset2() {
  form2.compid = ''; form2.lisence = ''; form2.remark = ''; form2.env = 'prod'
  result2.value = ''
}
</script>

<style scoped>
.dzfn-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.dzfn-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.dzfn-card {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.dzfn-card :deep(.el-card__body) { overflow-y: auto; }
.dzfn-title { text-align: center; font-weight: 600; font-size: 18px; }
.dzfn-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
.dzfn-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}
.dzfn-placeholder p {
  color: #c0c4cc;
  text-align: center;
  padding: 48px 20px;
}
.result {
  margin-top: 12px;
  min-height: 60px;
  font-size: 14px;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
  border-top: 1px solid #e4e7ed;
  padding-top: 8px;
}
</style>
