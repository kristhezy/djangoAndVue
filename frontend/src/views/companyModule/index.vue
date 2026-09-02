<template>
  <div class="cm-page">
    <el-card class="cm-panel" shadow="never">
      <!-- 企业 IDs -->
      <div class="cm-block">
        <div class="cm-label">企 业 IDs:</div>
        <el-input
          v-model="form.companyId"
          placeholder="示例:'727972691243679744,593467466257072128,583716956373278720'"
        />
      </div>

      <!-- 企业模块：单列，6 组从上到下依次排布（保持原模板语义分组顺序） -->
      <div class="cm-label">企业模块:</div>
      <div v-for="g in groups" :key="g.title" class="cm-group">
        <div class="cm-group__title" :class="{ 'cm-group__title--muted': g.muted }">{{ g.title }}</div>
        <div class="cm-grid">
          <el-checkbox
            v-for="it in g.items"
            :key="it.k"
            v-model="it.checked"
            :class="{ 'cm-check--bold': it.bold }"
            @change="onCheckChange(it)"
          >{{ it.label }}</el-checkbox>
        </div>
      </div>

      <!-- 环境 + 操作 -->
      <div class="cm-opt">
        <el-radio-group v-model="form.env">
          <el-radio value="prod">生产环境</el-radio>
          <el-radio value="test">测试环境</el-radio>
        </el-radio-group>
        <span class="cm-sep">||</span>
        <el-radio-group v-model="form.cm">
          <el-radio value="addm">增加模块</el-radio>
          <el-radio value="delm">删除模块</el-radio>
        </el-radio-group>
      </div>

      <!-- 提交 + 重置 -->
      <div class="cm-actions">
        <el-button type="primary" :loading="loading" @click="submit">提交</el-button>
        <el-button @click="reset">重置</el-button>
      </div>

      <!-- 结果：内联展示，有内容才出现 -->
      <div v-if="result1" class="cm-result">{{ result1 }}</div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const form = reactive({ companyId: '', env: 'prod', cm: 'addm' })
const result1 = ref('')
const loading = ref(false)

// 6 组模块，M107 两个条目 value 相同、标 mutex 互斥（复刻模板 mutex-checkbox）
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

// M107 互斥：勾选其一，取消另一个
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
  if (!companyId) {
    ElMessage.warning('企业id不能为空！')
    return
  }
  const mk = getCheckedMk()
  if (!mk) {
    ElMessage.warning('至少选择一个模块！')
    return
  }
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
.cm-page {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
  background: #f0f2f5;
  box-sizing: border-box;
}
.cm-panel {
  max-width: 1200px;
  margin: 0 auto;
}
.cm-block {
  margin-bottom: 12px;
}
.cm-label {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 6px;
}
.cm-group {
  margin-bottom: 8px;
}
.cm-group__title {
  display: inline-block;
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid #6366f1;
  padding-bottom: 3px;
  margin-bottom: 5px;
}
.cm-group__title--muted {
  color: #909399;
  border-bottom: none;
}
.cm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  row-gap: 2px;
  column-gap: 8px;
}
.cm-grid :deep(.el-checkbox) {
  margin-right: 0;
  height: 24px;
  white-space: nowrap;
}
.cm-check--bold :deep(.el-checkbox__label) {
  font-weight: 700;
}
.cm-opt {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}
.cm-sep {
  color: #c0c4cc;
  margin: 0 4px;
}
.cm-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
}
.cm-result {
  margin-top: 12px;
  padding: 10px 16px;
  background: #f5f6f8;
  border-radius: 6px;
  font-size: 15px;
  color: #6366f1;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
