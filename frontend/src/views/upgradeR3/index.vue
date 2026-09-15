<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-arrows-rotate"></i> 转介绍 3.0 配置</h2>
      </div>
    </div>

    <div class="mo-body">
      <!-- 左栏：配置表单 -->
      <div class="m-card">
        <div class="m-card-hd accent-blue">
          <div class="m-card-hd-left"><i class="fa-solid fa-sliders card-icon"></i>
            <h3>转介绍 3.0 配置</h3>
          </div>
        </div>
        <div class="m-card-bd">
          <div class="fg fg-wide">
            <div class="fgr"><label><span class="rq">*</span>企业ID/席位</label>
              <div class="ur3-seats">
                <el-input v-model="form.companyIds" type="textarea" :rows="4" placeholder="企业 IDs" />
                <el-input v-model="form.seats" type="textarea" :rows="4" placeholder="席位数" />
              </div>
            </div>
          </div>
          <EnvRadio v-model="form.env" name="env1" />
          <BtnGroup @reset="reset" @submit="submit" :loading="loading" />
          <div class="result">{{ result1 }}</div>

          <template v-if="submitted">
            <div class="ur3-tips">菜单sql，若企业菜单异常，需执行此处sql</div>
            <div class="ur3-sql">{{ formatResult(sql) }}</div>
            <div class="ur3-copy">
              <el-button type="primary" plain size="small" @click="copyAndJump">复制并跳转提交sql</el-button>
            </div>
          </template>
        </div>
      </div>

      <!-- 右栏：执行结果 -->
      <div class="log-panel">
        <OperationLog ref="log" :ds="[1]" :init-num="100" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'
import OperationLog from '../../components/OperationLog.vue'

const EnvRadio = {
  props: ['modelValue', 'name'], emits: ['update:modelValue'],
  template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = {
  props: ['loading'],
  emits: ['reset', 'submit'],
  template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" :loading="loading" @click="$emit('submit')">提交</el-button></div>`,
}

const form = reactive({ companyIds: '', seats: '', env: 'prod' })
const result1 = ref('')
const sql = ref('')
const submitted = ref(false)
const loading = ref(false)
const log = ref(null)

function formatResult(str) { return (str || '').replace(/<br\s*\/?>/gi, '\n') }

async function submit() {
  const { companyIds, seats } = form
  if (!companyIds) { ElMessage.warning('企业id不能为空！'); return }
  if (!seats) { ElMessage.warning('席位数不能为空！'); return }
  loading.value = true
  try {
    const resp = await http.post('/sv/upgradeR3', { companyIds, seats, env: form.env })
    result1.value = resp.data?.data?.upgradeR3 || ''
    sql.value = resp.data?.data?.ur3sql || ''
    submitted.value = true
    log.value?.refresh(4)
  } catch (e) { result1.value = ''; ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading.value = false }
}

async function copyAndJump() {
  const text = formatResult(sql.value)
  try {
    if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text) }
    else { const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta) }
    ElMessage.success('复制成功！')
  } catch (e) { ElMessage.error('复制失败：' + e.message) }
  window.open('https://sqlprod.jiatuiyun.net/submitsql/', '_blank')
}

function reset() { form.companyIds = ''; form.seats = ''; form.env = 'prod'; result1.value = ''; sql.value = ''; submitted.value = false }
</script>

<style scoped>
.mo-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--bg-page);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 8px;
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: .3px;
}

.page-title i {
  color: var(--color-primary-light);
  margin-right: 4px;
}

.mo-body {
  flex: 1;
  padding: 0 14px 14px;
  overflow: hidden;
  display: flex;
  gap: 12px;
}

.m-card {
  background: var(--bg-card);
  border-radius: 12px;
  flex: 1.2;
  min-width: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  overflow: hidden;
  transition: box-shadow .2s;
  display: flex;
  flex-direction: column;
}

.m-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, .08), 0 2px 4px rgba(0, 0, 0, .04);
}

.m-card-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  user-select: none;
  border-left: 4px solid transparent;
}

.m-card-hd-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-icon {
  font-size: 15px;
  width: 18px;
  text-align: center;
}

.m-card-hd h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: .2px;
}

.m-card-bd {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  overflow-y: auto;
  border-top: 1px solid var(--border-card);
}

.accent-blue {
  border-left-color: #3b82f6;
}

.accent-blue .card-icon {
  color: #3b82f6;
}

.log-panel {
  flex: 1;
  min-width: 0;
}

.fg {
  display: grid;
  grid-template-columns: auto 1fr;
  column-gap: 12px;
  row-gap: 12px;
  align-items: start;
  width: fit-content;
  margin: 0 auto;
}

.fg-wide {
  grid-template-columns: auto minmax(300px, 500px);
}

.fgr {
  display: contents;
}

.fgr label {
  text-align: left;
  white-space: nowrap;
  font-size: 13px;
  color: var(--text-secondary);
  padding-top: 6px;
}

.fgr :deep(.el-input),
.fgr :deep(.el-select) {
  width: 100% !important;
}

.rq {
  color: #ef4444;
  margin-right: 2px;
}

.ur3-seats {
  display: flex;
  gap: 10px;
  width: 100%;
}

.ur3-seats :deep(.el-textarea) {
  flex: 1;
  min-width: 0;
}

:deep(.env-group) {
  display: inline-flex;
  justify-content: center;
  margin: 14px auto 10px;
}

:deep(.env-track) {
  display: inline-flex;
  gap: 0;
  background: var(--bg-hover);
  border-radius: 6px;
  padding: 2px;
  flex-wrap: nowrap;
}

:deep(.env-track label) {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 14px;
  border-radius: 5px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  transition: all .2s;
  user-select: none;
  white-space: nowrap;
}

:deep(.env-track label.active) {
  background: var(--bg-card);
  color: var(--color-primary-light);
  box-shadow: 0 1px 3px rgba(0, 0, 0, .1);
  font-weight: 600;
}

:deep(.env-track label i) {
  font-size: 11px;
}

:deep(.env-track input[type="radio"]) {
  display: none;
}

:deep(.btn-group) {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 10px 0 12px;
}

.result {
  width: 100%;
  min-height: 40px;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--bg-subtle);
  font-size: 13px;
  text-align: left;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
}

.result:empty {
  display: none;
}

.ur3-tips {
  margin-top: 12px;
  font-size: 12px;
  color: var(--text-placeholder);
}

.ur3-sql {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-placeholder);
  white-space: pre-wrap;
  word-break: break-all;
  padding: 8px 12px;
  background: var(--bg-subtle);
  border-radius: 6px;
}

.ur3-copy {
  margin-top: 8px;
}
</style>
