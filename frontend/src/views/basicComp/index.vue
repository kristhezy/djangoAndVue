<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-cubes"></i> 销售工具版配置</h2>
      </div>
    </div>

    <div class="mo-body">
      <!-- 左栏：配置表单 -->
      <div class="m-card">
        <div class="m-card-hd accent-blue">
          <div class="m-card-hd-left"><i class="fa-solid fa-sliders card-icon"></i>
            <h3>销售工具版配置</h3>
          </div>
        </div>
        <div class="m-card-bd">
          <div class="fg fg-wide">
            <div class="fgr"><label><span class="rq">*</span>企业 IDs</label>
              <el-input v-model="form.companyId" type="textarea" :rows="3"
                placeholder="示例: 727972691243679744,593467466257072128" />
            </div>
            <div class="fgr"><label><span class="rq">*</span>企业模块</label>
              <el-checkbox-group v-model="form.mk">
                <el-checkbox value="M100">M100（官网）</el-checkbox>
                <el-checkbox value="M103">M103（推力系统）</el-checkbox>
                <el-checkbox value="M104">M104（小程序）</el-checkbox>
                <el-checkbox value="M114">M114（普通版商城）</el-checkbox>
                <el-checkbox value="M115" disabled>M115（直播）</el-checkbox>
                <el-checkbox value="M119">M119（活动分发）</el-checkbox>
                <el-checkbox value="M120">M120（优惠券）</el-checkbox>
                <el-checkbox value="M124">M124（企微助手）</el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
          <EnvRadio v-model="form.env" name="env1" />
          <BtnGroup @reset="reset" @submit="submit" :loading="loading" />
          <div class="result">{{ result1 }}</div>
        </div>
      </div>

      <!-- 右栏：执行结果 -->
      <div class="log-panel">
        <OperationLog ref="log" :ds="[2]" :init-num="100" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'
import OperationLog from '../../components/OperationLog.vue'

// --- Inline sub-components ---
const EnvRadio = {
  props: ['modelValue', 'name'], emits: ['update:modelValue'],
  template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = {
  props: ['loading'],
  emits: ['reset', 'submit'],
  template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" :loading="loading" @click="$emit('submit')">提交</el-button></div>`,
}

const form = reactive({ companyId: '', mk: ['M100', 'M103', 'M104', 'M114', 'M119', 'M120'], env: 'prod' })
const result1 = ref('')
const loading = ref(false)
const log = ref(null)

async function submit() {
  const { companyId, mk, env } = form
  if (!companyId) {
    ElMessage.warning('企业id不能为空！')
    return
  }
  if (!mk.length) {
    ElMessage.warning('模块最少选择一个！')
    return
  }
  loading.value = true
  try {
    const resp = await http.post('/sv/basicComp', {
      companyId,
      mk: mk.join(','),
      env,
    })
    result1.value = resp.data?.data?.basicCompanyConfig || ''
    log.value?.refresh(6)
  } catch (e) {
    result1.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

function reset() {
  form.companyId = ''
  form.mk = ['M100', 'M103', 'M104', 'M114', 'M119', 'M120']
  form.env = 'prod'
  result1.value = ''
}
</script>

<style scoped>
/* ===================== 页面骨架 ===================== */
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

/* ===================== 卡片 ===================== */
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

/* ===================== 右栏日志 ===================== */
.log-panel {
  flex: 1;
  min-width: 0;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ===================== 表单 Grid ===================== */
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

/* ===================== 环境切换 ===================== */
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

/* ===================== 按钮 ===================== */
:deep(.btn-group) {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 10px 0 12px;
}

/* ===================== 结果区 ===================== */
.result {
  width: 100%;
  min-height: 60px;
  max-height: 200px;
  overflow-y: auto;
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
</style>
