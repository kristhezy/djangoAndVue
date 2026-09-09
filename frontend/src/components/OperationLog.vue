<template>
  <div class="oplog-card">
    <div class="oplog-hd">
      <div class="oplog-hd-left"><i class="fa-solid fa-clock-rotate-left oplog-icon"></i>
        <h3>{{ title }}</h3>
      </div>
    </div>
    <div v-loading="loading" class="oplog-bd">
      <div v-if="!records.length" class="oplog-empty">暂无数据</div>
      <div v-for="(r, i) in records" :key="i" class="oplog-item">
        <div class="oplog-item__head">
          <span class="oplog-item__title">{{ r.env }} ┆ {{ r.companyName }}（{{ r.companyId }}）</span>
          <span class="oplog-item__time">{{ r.t }}</span>
        </div>
        <div class="oplog-item__msg" v-html="sanitize(r.message)"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../api/http'

// ds: 操作记录来源 ds 数组（如 [1]/[2]/[3]/[15]）；initNum: 进入页面时查询条数
const props = defineProps({
  ds: { type: Array, required: true },
  initNum: { type: Number, default: 100 },
  title: { type: String, default: '执行结果' },
})

const loading = ref(false)
const records = ref([])

// 先转义全部 HTML，再只还原 <b> 与 <br/>，既保留加粗/换行又防 XSS
function sanitize(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/&lt;b&gt;/gi, '<b>')
    .replace(/&lt;\/b&gt;/gi, '</b>')
    .replace(/&lt;br\s*\/?&gt;/gi, '<br/>')
}

async function qbdan(num) {
  const resp = await http.post('/sv/qmbydsan', { dss: props.ds, num })
  const res = resp.data?.data?.qmbydsan
  if (!Array.isArray(res)) {
    records.value = []
    return
  }
  records.value = res
}

async function querymsgbyds(num) {
  loading.value = true
  try {
    await qbdan(num)
    const resp = await http.post('/sv/aftergetqmbydsan', { dss: props.ds, num })
    if (resp.data?.data === '更新数据成功！') {
      await qbdan(num)
    }
  } catch (e) {
    console.log('查询操作信息err:', e.message)
  } finally {
    loading.value = false
  }
}

function refresh(num) {
  return querymsgbyds(num)
}

onMounted(() => querymsgbyds(props.initNum))

defineExpose({ refresh })
</script>

<style scoped>
.oplog-card {
  background: #fff;
  border-radius: 12px;
  flex: 1;
  min-width: 0;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow .2s;
}

.oplog-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, .08), 0 2px 4px rgba(0, 0, 0, .04);
}

.oplog-hd {
  display: flex;
  align-items: center;
  padding: 14px 18px;
  user-select: none;
  border-left: 4px solid #22c55e;
}

.oplog-hd-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.oplog-icon {
  font-size: 15px;
  width: 18px;
  text-align: center;
  color: #22c55e;
}

.oplog-hd h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  letter-spacing: .2px;
}

.oplog-bd {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
  border-top: 1px solid #f1f5f9;
  padding: 0;
}

.oplog-empty {
  color: #c0c4cc;
  text-align: center;
  padding: 48px 20px;
}

.oplog-item {
  padding: 10px 18px;
  border-bottom: 1px solid #f1f5f9;
}

.oplog-item:last-child {
  border-bottom: none;
}

.oplog-item__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.oplog-item__title {
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
}

.oplog-item__time {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
}

.oplog-item__msg {
  margin-top: 4px;
  font-size: 13px;
  color: #475569;
  word-break: break-all;
  line-height: 1.5;
}

.oplog-item__msg :deep(b) {
  font-weight: 700;
  color: #1e293b;
}
</style>
