<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-cubes"></i> 企业模块配置</h2>
      </div>
    </div>

    <div class="mo-body">
      <div class="m-card">
        <div class="m-card-hd accent-blue">
          <div class="m-card-hd-left"><i class="fa-solid fa-puzzle-piece card-icon"></i><h3>企业模块配置</h3></div>
        </div>
        <div class="m-card-bd">
          <!-- 企业 IDs -->
          <div class="fg fg-wide">
            <div class="fgr"><label><span class="rq">*</span>企业 IDs</label>
              <el-input v-model="form.companyId" placeholder="示例:'727972691243679744,593467466257072128'" />
            </div>
          </div>

          <!-- 企业模块分组 -->
          <div class="cm-modules">
            <div v-for="g in groups" :key="g.title" class="cm-group">
              <div class="cm-group__title" :class="{ 'cm-group__title--muted': g.muted }">
                {{ g.title }}<span v-if="g.isNew" class="cm-new">NEW</span>
              </div>
              <div class="cm-grid">
                <el-checkbox v-for="it in g.items" :key="it.k" v-model="it.checked"
                  :class="{ 'cm-check--bold': it.bold, 'cm-check--muted': g.muted }"
                  @change="onCheckChange(it)">{{ it.label }}</el-checkbox>
              </div>
            </div>
          </div>

          <!-- 操作选项 -->
          <div class="cm-opt">
            <div class="cm-count" :class="{ 'cm-count--active': checkedCount > 0 }">已选 {{ checkedCount }} 个模块</div>
          </div>
          <div class="cm-radio-row">
            <EnvRadio v-model="form.env" name="env1" />
            <span class="cm-sep">|</span>
            <div class="tab-group">
              <label :class="{active:form.cm==='addm'}"><input type="radio" name="cm" value="addm" :checked="form.cm==='addm'" @change="form.cm='addm'"/><span>增加模块</span></label>
              <label :class="{active:form.cm==='delm'}"><input type="radio" name="cm" value="delm" :checked="form.cm==='delm'" @change="form.cm='delm'"/><span>删除模块</span></label>
            </div>
          </div>
          <BtnGroup @reset="reset" @submit="submit" :loading="loading" />
          <div v-if="result1" class="result">{{ result1 }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

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

const form = reactive({ companyId: '', env: 'prod', cm: 'addm' })
const result1 = ref('')
const loading = ref(false)

const groups = reactive([
  {
    title: '• 共用模块',
    items: [
      { k: 'mk100', v: 'M100', label: 'M100(官网)', checked: false },
      { k: 'mk105', v: 'M105', label: 'M105(动态)', checked: false },
      { k: 'mk107', v: 'M107', label: 'M107(表单)', checked: false, mutex: true },
      { k: 'mk108', v: 'M108', label: 'M108(视频)', checked: false },
      { k: 'mk109', v: 'M109', label: 'M109(宣传册)', checked: false },
      { k: 'mk110', v: 'M110', label: 'M110(案例库)', checked: false },
      { k: 'mk111', v: 'M111', label: 'M111(海报)', checked: false },
      { k: 'mk112', v: 'M112', label: 'M112(文章)', checked: false },
      { k: 'mk113', v: 'M113', label: 'M113(文件)', checked: false },
    ],
  },
  {
    title: '• 转介绍/工具版专属',
    items: [
      { k: 'mk103', v: 'M103', label: 'M103(推力系统)', checked: false },
      { k: 'mk104', v: 'M104', label: 'M104(小程序)', checked: false },
      { k: 'mk114', v: 'M114', label: 'M114(普通版商城)', checked: false },
      { k: 'mk119', v: 'M119', label: 'M119(活动分发)', checked: false },
      { k: 'mk120', v: 'M120', label: 'M120(优惠券)', checked: false },
    ],
  },
  {
    title: '• Saleskits专属',
    isNew: true,
    items: [
      { k: 'mk140', v: 'M140', label: 'M140(PLG「企管」)', checked: false },
      { k: 'sk107', v: 'M107', label: 'M107(推广表单)', checked: false, mutex: true },
      { k: 'mk138', v: 'M138', label: 'M138(任务中心)', checked: false },
      { k: 'mk139', v: 'M139', label: 'M139(产品库)', checked: false },
      { k: 'mk142', v: 'M142', label: 'M142(toB版)', checked: false },
      { k: 'mk143', v: 'M143', label: 'M143(AI名片)', checked: false },
    ],
  },
  {
    title: '• 版本',
    items: [
      { k: 'mk127', v: 'M127', label: 'M127(加推云盘版)', checked: false },
      { k: 'mk128', v: 'M128', label: 'M128(转介绍3.0)', checked: false },
      { k: 'mk136', v: 'M136', label: 'M136(招商版)', checked: false },
      { k: 'mk137', v: 'M137', label: 'M137(Saleskits版)', checked: false },
      { k: 'mk146', v: 'M146', label: 'M146(家装版)', checked: false },
      { k: 'mk144', v: 'M144', label: 'M144(三一重工[定制])', checked: false },
    ],
  },
  {
    title: '• 不常用',
    items: [
      { k: 'mk115', v: 'M115', label: 'M115(直播)', checked: false },
      { k: 'mk116', v: 'M116', label: 'M116(图谱)', checked: false },
      { k: 'mk124', v: 'M124', label: 'M124(企微助手)', checked: false },
      { k: 'mk121', v: 'M121', label: 'M121(活码)', checked: false },
      { k: 'mk122', v: 'M122', label: 'M122(奥田定制)', checked: false },
      { k: 'mk123', v: 'M123', label: 'M123(课程培训)', checked: false },
      { k: 'mk129', v: 'M129', label: 'M129(自动化营销)', checked: false },
      { k: 'mk131', v: 'M131', label: 'M131(智能渠道码)', checked: false },
      { k: 'mk132', v: 'M132', label: 'M132(客户群运营)', checked: false },
      { k: 'mk025', v: 'M025', label: 'M025(商城分销)', checked: false, bold: true },
    ],
  },
  {
    title: '• 已停用模块:',
    muted: true,
    items: [
      { k: 'mk102', v: 'M102', label: 'M102(销售管理组件)', checked: false },
      { k: 'mk117', v: 'M117', label: 'M117(转介绍2.0)', checked: false },
      { k: 'mk106', v: 'M106', label: 'M106(推任务)', checked: false },
      { k: 'mk126', v: 'M126', label: 'M126(聊天侧边栏)', checked: false },
    ],
  },
])

const allItems = groups.flatMap(g => g.items)
const checkedCount = computed(() => allItems.filter(i => i.checked).length)

function onCheckChange(item) {
  if (!item.mutex || !item.checked) return
  allItems.forEach(other => {
    if (other !== item && other.mutex) other.checked = false
  })
}

function getCheckedMk() {
  return [...new Set(allItems.filter(i => i.checked).map(i => i.v))].join(',')
}

async function submit() {
  const { companyId, env, cm } = form
  if (!companyId) { ElMessage.warning('企业id不能为空！'); return }
  const mk = getCheckedMk()
  if (!mk) { ElMessage.warning('至少选择一个模块！'); return }
  loading.value = true
  try {
    const resp = await http.post('/sv/companyModule', { companyId, mk, env, cm })
    result1.value = resp.data?.data || ''
    allItems.forEach(i => { i.checked = false })
  } catch (e) {
    result1.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

function reset() {
  form.companyId = ''
  form.env = 'prod'
  form.cm = 'addm'
  allItems.forEach(i => { i.checked = false })
  result1.value = ''
}
</script>

<style scoped>
/* ===================== 页面骨架 ===================== */
.mo-page { display:flex; flex-direction:column; height:100%; overflow:hidden; background:var(--bg-page); }
.toolbar { display:flex; justify-content:space-between; align-items:center; padding:12px 20px 8px; flex-shrink:0; }
.toolbar-left { display:flex; align-items:center; gap:8px; }
.page-title { margin:0; font-size:16px; font-weight:700; color:var(--text-primary); letter-spacing:.3px; }
.page-title i { color:var(--color-primary-light); margin-right:4px; }

.mo-body { flex:1; padding:0 14px 14px; overflow-y:auto; display:flex; justify-content:center; align-items:flex-start; }
.mo-body::-webkit-scrollbar { width:4px; }
.mo-body::-webkit-scrollbar-track { background:transparent; }
.mo-body::-webkit-scrollbar-thumb { background:var(--scrollbar-thumb); border-radius:4px; }

/* ===================== 卡片 ===================== */
.m-card {
  background:var(--bg-card); border-radius:12px; width:900px; max-width:100%;
  box-shadow:var(--shadow-card);
  overflow:hidden; transition:box-shadow .2s;
}
.m-card:hover { box-shadow:var(--shadow-card-hover); }

.m-card-hd {
  display:flex; justify-content:space-between; align-items:center;
  padding:14px 18px; user-select:none;
  border-left:4px solid transparent;
}
.m-card-hd-left { display:flex; align-items:center; gap:10px; }
.card-icon { font-size:15px; width:18px; text-align:center; }
.m-card-hd h3 { margin:0; font-size:14px; font-weight:600; color:var(--text-primary); letter-spacing:.2px; }

.m-card-bd {
  padding:16px 18px; display:flex; flex-direction:column; align-items:center;
  border-top:1px solid var(--border-card);
}

.accent-blue  { border-left-color:#3b82f6; }  .accent-blue  .card-icon { color:#3b82f6; }

/* ===================== 表单 Grid ===================== */
.fg { display:grid; grid-template-columns:auto 1fr; column-gap:12px; row-gap:12px; align-items:start; width:100%; margin:0 auto 14px; }
.fg-wide { grid-template-columns:auto 1fr; max-width:600px; }
.fgr { display:contents; }
.fgr label { text-align:left; white-space:nowrap; font-size:13px; color:var(--text-secondary); padding-top:6px; }
.fgr :deep(.el-input), .fgr :deep(.el-select) { width:100% !important; }
.rq { color:#ef4444; margin-right:2px; }

/* ===================== 模块分组 ===================== */
.cm-modules { width:100%; margin-bottom:12px; }
.cm-group { margin-bottom:10px; }
.cm-group__title {
  display:inline-block; font-size:13px; font-weight:600; color:var(--text-primary);
  border-bottom:2px solid var(--color-primary-light); padding-bottom:3px; margin-bottom:5px;
}
.cm-group__title--muted { color:var(--text-placeholder); border-bottom:none; font-weight:400; }
.cm-new {
  display:inline-block; margin-left:6px; padding:0 5px;
  font-size:11px; font-weight:700; line-height:16px;
  color:#fff; background:#ef4444; border-radius:3px; vertical-align:1px;
}
.cm-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(160px, 1fr)); row-gap:2px; column-gap:8px; }
.cm-grid :deep(.el-checkbox) { margin-right:0; height:24px; white-space:nowrap; }
.cm-check--bold :deep(.el-checkbox__label) { font-weight:700; }
.cm-check--muted :deep(.el-checkbox__label) { color:var(--text-placeholder); }

/* ===================== 操作选项 ===================== */
.cm-opt { display:flex; justify-content:center; margin:8px 0 4px; }
.cm-count { font-size:13px; color:var(--text-placeholder); min-width:96px; text-align:center; }
.cm-count--active { color:var(--color-primary-light); font-weight:600; }

.cm-radio-row { display:flex; align-items:center; justify-content:center; gap:12px; margin:8px 0 4px; }
.cm-sep { color:var(--text-placeholder); font-size:14px; }

:deep(.tab-group) { display:inline-flex; gap:0; background:var(--bg-hover); border-radius:6px; padding:2px; flex-wrap:nowrap; }
:deep(.tab-group label) {
  cursor:pointer; display:inline-flex; align-items:center; gap:4px;
  padding:5px 14px; border-radius:5px; border:none; background:transparent;
  font-size:12px; font-weight:500; color:var(--text-muted); transition:all .2s;
  user-select:none; white-space:nowrap;
}
:deep(.tab-group label.active) { background:var(--bg-card); color:var(--color-primary-light); box-shadow:0 1px 3px rgba(0,0,0,.1); font-weight:600; }
:deep(.tab-group input[type="radio"]) { display:none; }

/* ===================== 环境切换 ===================== */
:deep(.env-group) { display:inline-flex; }
:deep(.env-track) { display:inline-flex; gap:0; background:var(--bg-hover); border-radius:6px; padding:2px; flex-wrap:nowrap; }
:deep(.env-track label) {
  cursor:pointer; display:inline-flex; align-items:center; gap:4px;
  padding:5px 14px; border-radius:5px; border:none; background:transparent;
  font-size:12px; font-weight:500; color:var(--text-muted); transition:all .2s;
  user-select:none; white-space:nowrap;
}
:deep(.env-track label.active) { background:var(--bg-card); color:var(--color-primary-light); box-shadow:0 1px 3px rgba(0,0,0,.1); font-weight:600; }
:deep(.env-track label i) { font-size:11px; }
:deep(.env-track input[type="radio"]) { display:none; }

/* ===================== 按钮 ===================== */
:deep(.btn-group) { display:flex; justify-content:center; gap:12px; margin:10px 0 12px; }

/* ===================== 结果区 ===================== */
.result {
  width:100%; min-height:32px; max-height:200px; overflow-y:auto;
  padding:10px 14px; border-radius:8px; background:var(--bg-subtle);
  font-size:13px; text-align:center; line-height:1.7; color:var(--color-primary-light);
  white-space:pre-wrap; word-break:break-all;
}
</style>
