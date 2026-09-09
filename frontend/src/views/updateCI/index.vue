<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-pen-to-square"></i> 企业信息修改</h2>
      </div>
    </div>

    <div class="mo-body">
      <!-- 左栏：表单 -->
      <div class="m-card">
        <div class="m-card-hd accent-blue">
          <div class="m-card-hd-left"><i class="fa-solid fa-sliders card-icon"></i>
            <h3>企业信息修改</h3>
          </div>
        </div>
        <div class="m-card-bd">
          <div class="fg fg-wide">
            <div class="fgr"><label><span class="rq">*</span>企业ID</label>
              <el-input v-model="form.cid" type="textarea" :rows="2" placeholder="请输入企业ID，多个换行分隔" />
            </div>
            <div class="fgr"><label>企业名称</label><el-input v-model="form.cname" placeholder="请输入企业名称" /></div>
            <div class="fgr"><label>管理员姓名</label><el-input v-model="form.admname" placeholder="请输入管理员名称" /></div>
            <div class="fgr"><label>企业类型</label>
              <el-select v-model="form.ctype" clearable placeholder="请选择" style="width:100%">
                <el-option label="7" value="7" /><el-option label="0" value="0" />
              </el-select>
            </div>
            <div class="fgr"><label>付款方式</label>
              <el-select v-model="form.payment" clearable placeholder="请选择" style="width:100%">
                <el-option label="预充值" value="3" /><el-option label="线下" value="0" />
              </el-select>
            </div>
            <div class="fgr"><label>有效期限</label>
              <el-date-picker v-model="form.etime" type="date" value-format="YYYY-MM-DD" placeholder="请选择日期"
                style="width:100%" />
            </div>
            <div class="fgr"><label>雷达总数</label><el-input v-model="form.rnum" placeholder="请输入雷达数" /></div>
            <div class="fgr"><label>人资ID</label>
              <el-select v-model="form.tpid" clearable placeholder="请选择" style="width:100%">
                <el-option label="1" value="1" />
              </el-select>
            </div>
            <div class="fgr"><label>企业状态</label><el-input v-model="form.cstatus" placeholder="状态:0禁用,1正常,2注销" /></div>
            <div class="fgr"><label>企业/销售席位</label><el-input v-model="form.tseat" placeholder="企业/销售席位" /></div>
            <div class="fgr"><label>推荐官席位</label><el-input v-model="form.ptseat" placeholder="推荐官席位" /></div>
            <div class="fgr"><label>员工雷达</label>
              <div class="uci-dual">
                <el-input v-model="form.cardids" type="textarea" :rows="2" placeholder="员工IDs" style="flex:1;" />
                <el-select v-model="form.rs" clearable placeholder="请选择雷达状态" style="flex:1; width:80px; flex-shrink:0;">
                  <el-option label="关闭" value="0" />
                  <el-option label="AI雷达" value="1" />
                  <el-option label="AI和BOSS雷达" value="3" />
                </el-select>
              </div>
            </div>
          </div>
          <EnvRadio v-model="form.env" name="env1" />
          <BtnGroup @reset="reset" @submit="submit" :loading="loading" />
          <div v-if="result1" class="result" v-html="sanitize(result1)"></div>
        </div>
      </div>

      <!-- 右栏：执行结果 -->
      <div class="log-panel">
        <OperationLog ref="log" :ds="[4]" :init-num="100" title="最近更新记录" />
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

const form = reactive({
  cid: '', cname: '', admname: '', ctype: '', payment: '', etime: '',
  tpid: '', cstatus: '', rnum: '', tseat: '', ptseat: '', cardids: '', rs: '', env: 'prod',
})
const result1 = ref('')
const loading = ref(false)
const log = ref(null)

function sanitize(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/&lt;b&gt;/gi, '<b>').replace(/&lt;\/b&gt;/gi, '</b>').replace(/&lt;br\s*\/?&gt;/gi, '<br/>')
}

function isEmpty() {
  const { cname, admname, ctype, payment, etime, tpid, cstatus, rnum, tseat, ptseat, cardids } = form
  return [cname, admname, ctype, payment, etime, tpid, cstatus, rnum, tseat, ptseat, cardids].every(v => v === '')
}

async function submit() {
  if (!form.cid) { ElMessage.warning('企业id不能为空！'); return }
  if (isEmpty()) { ElMessage.warning('修改类型不能全部为空！'); return }
  loading.value = true
  try {
    const resp = await http.post('/sv/updateCInfo', { ...form })
    result1.value = resp.data?.data || ''
    form.cname = ''; form.admname = ''; form.rnum = ''; form.cstatus = ''
    form.tseat = ''; form.ptseat = ''; form.cardids = ''; form.ctype = ''
    form.payment = ''; form.etime = ''; form.tpid = ''; form.rs = ''
    log.value?.refresh(10)
  } catch (e) { result1.value = ''; ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading.value = false }
}

function reset() {
  Object.assign(form, {
    cid: '', cname: '', admname: '', ctype: '', payment: '', etime: '',
    tpid: '', cstatus: '', rnum: '', tseat: '', ptseat: '', cardids: '', rs: '', env: 'prod',
  })
  result1.value = ''
}
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
  align-items: center;
  width: fit-content;
  margin: 0 auto;
}

.fg-wide {
  grid-template-columns: auto minmax(250px, 420px);
}

.fgr {
  display: contents;
}

.fgr label {
  text-align: left;
  white-space: nowrap;
  font-size: 13px;
  color: #475569;
}

.fgr :deep(.el-input),
.fgr :deep(.el-select) {
  width: 100% !important;
}

.rq {
  color: #ef4444;
  margin-right: 2px;
}

.uci-dual {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  width: 100%;
}

:deep(.env-group) {
  display: inline-flex;
  justify-content: center;
  margin: 14px auto 10px;
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

.result :deep(b) {
  font-weight: 700;
  color: #1e293b;
}
</style>
