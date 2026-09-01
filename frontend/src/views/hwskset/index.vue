<template>
  <div class="hwsk-page">
    <div class="hwsk-cols">
      <!-- 左栏：配置 -->
      <el-card class="hwsk-panel hwsk-panel--main" shadow="never">
        <template #header>
          <div class="hwsk-title">华为云 SK 配置</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="手机号码">
            <el-input
              v-model="form.loginName"
              placeholder="输入登录手机号查询企业ID"
              @blur="onLoginNameBlur"
              @keyup.enter="onLoginNameEnter"
            />
          </el-form-item>

          <el-form-item>
            <div class="hwsk-duo">
              <div class="hwsk-duo__col">
                <div class="hwsk-duo__label">企业名称</div>
                <el-input v-model="form.cname" placeholder="输入企业名称" />
              </div>
              <div class="hwsk-duo__col">
                <div class="hwsk-duo__label">企业 ID</div>
                <el-input v-model="form.cid" placeholder="请输入企业ID" />
                <div class="hwsk-qcierr">{{ qcierr }}</div>
              </div>
            </div>
          </el-form-item>

          <el-form-item>
            <div class="hwsk-duo">
              <div class="hwsk-duo__col">
                <div class="hwsk-duo__label">付款方式</div>
                <el-select v-model="form.payment" style="width: 100%">
                  <el-option value="3" label="预充值" />
                  <el-option value="1" label="线下" />
                </el-select>
              </div>
              <div class="hwsk-duo__col">
                <div class="hwsk-duo__label">销售席位</div>
                <el-input v-model="form.tseat" placeholder="输入销售席位" />
              </div>
            </div>
          </el-form-item>

          <el-form-item label="企业模块">
            <el-checkbox-group v-model="form.mk">
              <el-checkbox value="M107">M107（推广表单）</el-checkbox>
              <el-checkbox value="M138">M138（任务中心）</el-checkbox>
              <el-checkbox value="M139">M139（产品库）</el-checkbox>
              <el-checkbox value="M142">M142（toB版）</el-checkbox>
              <el-checkbox value="M143">M143（AI名片）</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="环境">
            <el-radio-group v-model="form.env">
              <el-radio value="prod">生产</el-radio>
              <el-radio value="test">测试</el-radio>
            </el-radio-group>
          </el-form-item>

          <div class="hwsk-actions">
            <el-button type="primary" :loading="loading" @click="submit">提交</el-button>
            <el-button @click="reset">重置</el-button>
          </div>

          <div class="result">{{ formatResult(result1) }}</div>
        </el-form>
      </el-card>

      <!-- 右栏：执行结果 -->
      <OperationLog ref="log" :ds="[15]" :init-num="10" />
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'
import OperationLog from '../../components/OperationLog.vue'

const form = reactive({ loginName: '', cname: '', cid: '', payment: '3', tseat: '', mk: [], env: 'prod' })
const result1 = ref('')
const qcierr = ref('')
const loading = ref(false)
const log = ref(null)

// 后端返回含 <br/> 与 <b>，转成换行并去掉 b 标签，文本插值 + pre-wrap 展示（防 XSS）
function formatResult(str) {
  return (str || '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/?b>/gi, '')
}

// 根据登录手机号查询企业ID（blur / Enter 触发）
async function getCidByLname() {
  const ln = form.loginName
  if (!ln) return
  try {
    const resp = await http.post('/sv/querycompid/saas', { ln, env: form.env })
    if (resp.data?.code === '10002') {
      qcierr.value = resp.data?.data || ''
    } else {
      qcierr.value = ''
      form.cid = resp.data?.data?.cid || ''
      form.cname = resp.data?.data?.cn || ''
    }
  } catch (e) {
    console.log('getCidByLname err:', e.message)
  }
}
function onLoginNameBlur() {
  if (form.loginName === '') return
  getCidByLname()
}
function onLoginNameEnter() {
  if (form.loginName === '') {
    ElMessage.warning('输入手机号码查询!')
    return
  }
  getCidByLname()
}

async function submit() {
  const { cid, cname, payment, tseat, mk, env } = form
  if (!cid) {
    ElMessage.warning('输入企业id！')
    return
  }
  if (!cname && !payment && !tseat && !mk.length) {
    ElMessage.warning('修改类型不能全部为空！')
    return
  }
  loading.value = true
  try {
    const resp = await http.post('/sv/hwskset', {
      cid, cname, payment, tseat,
      ptseat: '',
      mk: mk.join(','),
      env,
    })
    result1.value = resp.data?.data?.hwskCompanyConfig || ''
    log.value?.refresh(7)
  } catch (e) {
    result1.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

function reset() {
  form.loginName = ''
  form.cname = ''
  form.cid = ''
  form.payment = '3'
  form.tseat = ''
  form.mk = []
  form.env = 'prod'
  result1.value = ''
  qcierr.value = ''
}
</script>

<style scoped>
.hwsk-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.hwsk-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.hwsk-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.hwsk-panel--main {
  flex: 1.2;
}
.hwsk-panel :deep(.el-card__body) { overflow-y: auto; }
.hwsk-title { text-align: center; font-weight: 600; font-size: 16px; }
.hwsk-duo {
  display: flex;
  gap: 10px;
  width: 100%;
}
.hwsk-duo__col {
  flex: 1;
  min-width: 0;
}
.hwsk-duo__label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}
.hwsk-qcierr {
  color: #f56c6c;
  font-size: 12px;
  min-height: 20px;
  margin-top: 2px;
}
.hwsk-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
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
