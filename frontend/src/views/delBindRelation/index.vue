<template>
  <div class="delbind-page">
    <div class="delbind-cols">
      <!-- 卡片1: 清除公众号/小程序绑定数据 -->
      <el-card class="delbind-card" shadow="never">
        <template #header>
          <div class="delbind-title">清除公众号/小程序绑定数据</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form1.companyId" placeholder="请输入企业ID" />
          </el-form-item>
          <el-form-item label="应用 ID" required>
            <el-select v-model="form1.appId" style="width:100%">
              <el-option v-for="a in appList" :key="a.id" :label="a.name" :value="a.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="Status" required>
            <el-select v-model="form1.status" style="width:100%">
              <el-option v-for="s in ['0', '1', '2']" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form1.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="delbind-actions">
            <el-button type="primary" :loading="loading1" @click="clearBind">提交</el-button>
            <el-button @click="reset1">重置</el-button>
          </div>
          <div class="result">{{ formatResult(result1) }}</div>
        </el-form>
      </el-card>

      <!-- 卡片2: 清除过期企业信息数据 -->
      <el-card class="delbind-card" shadow="never">
        <template #header>
          <div class="delbind-title">清除过期企业信息数据</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form2.companyIds" placeholder="支持逗号/换行/空格分隔多个企业ID" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form2.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="delbind-actions">
            <el-button type="primary" :loading="loading2" @click="clearExpired">提交</el-button>
            <el-button @click="reset2">重置</el-button>
          </div>
          <div class="delbind-notice">
            <ol>
              <b>清除过期企业，功能包含以下3点：</b>
              <li>企业设置为注销状态</li>
              <li>关闭员工雷达，清除员工和推荐官app登录token</li>
              <li>解除企业第三方绑定关系(公众号、小程序、企微)</li>
            </ol>
          </div>
          <div class="result">{{ formatResult(result2) }}</div>
        </el-form>
      </el-card>

      <!-- 卡片3: 清除app登录token -->
      <el-card class="delbind-card" shadow="never">
        <template #header>
          <div class="delbind-title">清除app登录token</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form3.companyId" placeholder="请输入企业ID" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form3.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="delbind-actions">
            <el-button type="primary" :loading="loading3" @click="clearToken">提交</el-button>
            <el-button @click="reset3">重置</el-button>
          </div>
          <div class="result">{{ formatResult(result3) }}</div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

// 应用ID下拉硬编码（复刻 AT_delBindRelation.html 第 80-86 行）
const appList = [
  { id: 'wx_oa', name: '公众号' },
  { id: 'card', name: '小程序' },
  { id: 'cpe_backlog', name: '自建应用' },
  { id: 'cpe_investment_applet', name: '招商/推广版小程序' },
  { id: 'cpe_partner_applet', name: '合伙人小程序' },
]

const form1 = reactive({ companyId: '', appId: 'wx_oa', status: '0', env: 'prod' })
const form2 = reactive({ companyIds: '', env: 'prod' })
const form3 = reactive({ companyId: '', env: 'prod' })
const result1 = ref('')
const result2 = ref('')
const result3 = ref('')
const loading1 = ref(false)
const loading2 = ref(false)
const loading3 = ref(false)

// 后端 delBindRelation 返回含 <br/>，转为换行，文本插值 + pre-wrap 展示（防 XSS）
function formatResult(str) {
  return (str || '').replace(/<br\s*\/?>/gi, '\n')
}

async function clearBind() {
  if (!form1.companyId) { ElMessage.warning('"企业ID"不能为空！'); return }
  loading1.value = true
  try {
    const resp = await http.post('/sv/forWeCom', {
      companyId: form1.companyId, appId: form1.appId, status: form1.status,
      env: form1.env, type: 3,
    })
    result1.value = resp.data?.data || ''
  } catch (e) {
    result1.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading1.value = false
  }
}

async function clearExpired() {
  if (!form2.companyIds) { ElMessage.warning('"企业ID"不能为空！'); return }
  loading2.value = true
  try {
    const resp = await http.post('/sv/delBindRelation', {
      companyIds: form2.companyIds, env: form2.env,
    })
    result2.value = resp.data?.data || ''
  } catch (e) {
    result2.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading2.value = false
  }
}

async function clearToken() {
  if (!form3.companyId) { ElMessage.warning('"企业ID"不能为空！'); return }
  loading3.value = true
  try {
    const resp = await http.post('/sv/cleanAppToken', {
      companyId: form3.companyId, env: form3.env,
    })
    result3.value = resp.data?.data || resp.data?.msg || '操作完成'
  } catch (e) {
    result3.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading3.value = false
  }
}

function reset1() {
  form1.companyId = ''; form1.appId = 'wx_oa'; form1.status = '0'; form1.env = 'prod'
  result1.value = ''
}
function reset2() {
  form2.companyIds = ''; form2.env = 'prod'
  result2.value = ''
}
function reset3() {
  form3.companyId = ''; form3.env = 'prod'
  result3.value = ''
}
</script>

<style scoped>
.delbind-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.delbind-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.delbind-card {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.delbind-card :deep(.el-card__body) { overflow-y: auto; }
.delbind-title { text-align: center; font-weight: 600; font-size: 18px; }
.delbind-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
.delbind-notice {
  font-size: 12px;
  color: #92400e;
  border-radius: 8px;
  margin: 8px 0;
  text-align: left;
  line-height: 1.625;
  background: #fffbeb;
  padding: 12px;
}
.delbind-notice ol { padding-left: 20px; margin: 0; }
.result {
  margin-top: 12px;
  font-size: 14px;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
