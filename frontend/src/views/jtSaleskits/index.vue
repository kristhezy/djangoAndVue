<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-cube"></i> Saleskits配置</h2>
      </div>
    </div>

    <div class="mo-body">
      <!-- 左栏：配置表单 -->
      <div class="m-card">
        <div class="m-card-hd accent-blue">
          <div class="m-card-hd-left"><i class="fa-solid fa-sliders card-icon"></i>
            <h3>加推 Saleskits 配置</h3>
          </div>
        </div>
        <div class="m-card-bd">
          <div class="fg fg-wide">
            <div class="fgr"><label><span class="rq">*</span>企业ID/席位</label>
              <div class="jtsk-seats">
                <el-input v-model="form.companyIds" type="textarea" :rows="4" placeholder="企业 ID/IDs" />
                <el-input v-model="form.sseats" type="textarea" :rows="4" placeholder="销售席位" />
                <el-input v-model="form.pseats" type="textarea" :rows="4" placeholder="推荐官席位" />
              </div>
            </div>
            <div v-show="form.type === 'zs'" class="fgr"><label>企业模块</label>
              <el-checkbox-group v-model="form.mk">
                <el-checkbox value="M107">M107（推广表单）</el-checkbox>
                <el-checkbox value="M138">M138（任务中心）</el-checkbox>
                <el-checkbox value="M139">M139（产品库）</el-checkbox>
                <el-checkbox value="M142">M142（toB版）</el-checkbox>
                <el-checkbox value="M143">M143（AI名片）</el-checkbox>
              </el-checkbox-group>
            </div>
            <div v-show="form.type === 'jz'" class="fgr"><label>家装类型</label>
              <el-radio-group v-model="form.jzc" size="small">
                <el-radio value="hmy_company">红蚂蚁</el-radio>
                <el-radio value="ds_company">点石</el-radio>
              </el-radio-group>
            </div>
          </div>
          <div class="tab-row">
            <div class="tab-group">
              <label :class="{ active: form.type === 'zs' }"><input type="radio" name="type" value="zs"
                  :checked="form.type === 'zs'" @change="form.type = 'zs'" /><span>招商版</span></label>
              <label :class="{ active: form.type === 'jz' }"><input type="radio" name="type" value="jz"
                  :checked="form.type === 'jz'" @change="form.type = 'jz'" /><span>家装版</span></label>
            </div>
          </div>
          <EnvRadio v-model="form.env" name="env1" />
          <BtnGroup @reset="reset" @submit="submit" :loading="loading" />
          <div class="result">{{ formatResult(result1) }}</div>
        </div>
      </div>

      <!-- 右栏：执行结果 -->
      <div class="log-panel">
        <OperationLog ref="log" :ds="[3]" :init-num="100" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
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

const form = reactive({ companyIds: '', sseats: '', pseats: '', mk: [], type: 'zs', jzc: '', env: 'prod' })
const result1 = ref('')
const loading = ref(false)
const log = ref(null)

function formatResult(str) { return (str || '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/?b>/gi, '') }

watch(() => form.type, (v) => { if (v === 'jz') form.mk = [] })

async function submit() {
  const { companyIds, sseats, pseats, mk, env, type, jzc } = form
  if (!companyIds || !sseats || !pseats) { ElMessage.warning('必填项不能为空！'); return }
  if (type === 'jz' && !jzc) { ElMessage.warning('家装类型不能为空! '); return }
  loading.value = true
  try {
    const resp = await http.post('/sv/jtSaleskits', { companyIds, sseats, pseats, mk: mk.join(','), env, type: type === 'zs' ? 0 : 1, jzc })
    result1.value = resp.data?.data?.skCompanyConfig || ''
    log.value?.refresh(6)
  } catch (e) { result1.value = ''; ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading.value = false }
}

function reset() { form.companyIds = ''; form.sseats = ''; form.pseats = ''; form.mk = []; form.type = 'zs'; form.jzc = ''; form.env = 'prod'; result1.value = '' }
</script>

<style scoped>
.mo-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #f5f6fa;
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
  color: #1e293b;
  letter-spacing: .3px;
}

.page-title i {
  color: #6366f1;
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
  background: #fff;
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
  color: #1e293b;
  letter-spacing: .2px;
}

.m-card-bd {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  overflow-y: auto;
  border-top: 1px solid #f1f5f9;
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
  grid-template-columns: auto minmax(280px, 440px);
}

.fgr {
  display: contents;
}

.fgr label {
  text-align: left;
  white-space: nowrap;
  font-size: 13px;
  color: #475569;
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

.jtsk-seats {
  display: flex;
  gap: 10px;
  width: 100%;
}

.jtsk-seats :deep(.el-textarea) {
  flex: 1;
  min-width: 0;
}

.tab-row {
  display: flex;
  justify-content: center;
  margin: 10px 0 4px;
}

:deep(.tab-group) {
  display: inline-flex;
  gap: 0;
  background: #f1f5f9;
  border-radius: 6px;
  padding: 2px;
  flex-wrap: nowrap;
}

:deep(.tab-group label) {
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
  color: #64748b;
  transition: all .2s;
  user-select: none;
  white-space: nowrap;
}

:deep(.tab-group label.active) {
  background: #fff;
  color: #6366f1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .1);
  font-weight: 600;
}

:deep(.tab-group input[type="radio"]) {
  display: none;
}

:deep(.env-group) {
  display: inline-flex;
  justify-content: center;
  margin: 10px auto 8px;
}

:deep(.env-track) {
  display: inline-flex;
  gap: 0;
  background: #f1f5f9;
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
  color: #64748b;
  transition: all .2s;
  user-select: none;
  white-space: nowrap;
}

:deep(.env-track label.active) {
  background: #fff;
  color: #6366f1;
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
  min-height: 60px;
  max-height: 200px;
  overflow-y: auto;
  padding: 10px 14px;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 13px;
  text-align: left;
  line-height: 1.7;
  color: #475569;
  white-space: pre-wrap;
  word-break: break-all;
}

.result:empty {
  display: none;
}
</style>
