<template>
  <div class="jtsk-page">
    <div class="jtsk-cols">
      <!-- 左栏：配置 -->
      <el-card class="jtsk-panel jtsk-panel--main" shadow="never">
        <template #header>
          <div class="jtsk-title">加推 Saleskits 配置</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企业 ID / 席位" required>
            <div class="jtsk-seats">
              <el-input
                v-model="form.companyIds"
                type="textarea"
                :rows="4"
                placeholder="企业 ID/IDs"
              />
              <el-input
                v-model="form.sseats"
                type="textarea"
                :rows="4"
                placeholder="销售席位"
              />
              <el-input
                v-model="form.pseats"
                type="textarea"
                :rows="4"
                placeholder="推荐官席位"
              />
            </div>
          </el-form-item>

          <el-form-item v-show="form.type === 'zs'" label="企业模块">
            <el-checkbox-group v-model="form.mk">
              <el-checkbox value="M107">M107（推广表单）</el-checkbox>
              <el-checkbox value="M138">M138（任务中心）</el-checkbox>
              <el-checkbox value="M139">M139（产品库）</el-checkbox>
              <el-checkbox value="M142">M142（toB版）</el-checkbox>
              <el-checkbox value="M143">M143（AI名片）</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item v-show="form.type === 'jz'" label="家装类型">
            <el-radio-group v-model="form.jzc">
              <el-radio value="hmy_company">红蚂蚁</el-radio>
              <el-radio value="ds_company">点石</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="版本">
            <el-radio-group v-model="form.type">
              <el-radio value="zs">招商版</el-radio>
              <el-radio value="jz">家装版</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="环境">
            <el-radio-group v-model="form.env">
              <el-radio value="prod">生产</el-radio>
              <el-radio value="test" :disabled="form.type === 'jz'">测试</el-radio>
            </el-radio-group>
          </el-form-item>

          <div class="jtsk-actions">
            <el-button type="primary" :loading="loading" @click="submit">提交</el-button>
            <el-button @click="reset">重置</el-button>
          </div>

          <div class="result">{{ formatResult(result1) }}</div>
        </el-form>
      </el-card>

      <!-- 右栏：执行结果 -->
      <el-card class="jtsk-panel" shadow="never">
        <template #header>
          <div class="jtsk-title">执行结果</div>
        </template>
        <div v-loading="logLoading" class="jtsk-log">
          <div v-if="!records.length" class="jtsk-empty">暂无数据</div>
          <div v-for="(r, i) in records" :key="i" class="jtsk-item">
            <div class="jtsk-item__head">
              <span class="jtsk-item__title">{{ r.env }} ┆ {{ r.companyName }}（{{ r.companyId }}）</span>
              <span class="jtsk-item__time">{{ r.t }}</span>
            </div>
            <div class="jtsk-item__msg">{{ r.message }}</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const form = reactive({ companyIds: '', sseats: '', pseats: '', mk: [], type: 'zs', jzc: '', env: 'prod' })
const result1 = ref('')
const loading = ref(false)
const records = ref([])
const logLoading = ref(false)

// 后端返回含 <br/> 与 <b>，转成换行并去掉 b 标签，文本插值 + pre-wrap 展示（防 XSS）
function formatResult(str) {
  return (str || '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/?b>/gi, '')
}

// 版本切换：家装版时清空模块勾选
watch(() => form.type, (v) => {
  if (v === 'jz') form.mk = []
})

// 查询操作信息列表
async function qbdan(num) {
  const resp = await http.post('/sv/qmbydsan', { dss: [3], num })
  const res = resp.data?.data?.qmbydsan
  if (!Array.isArray(res)) {
    records.value = []
    return
  }
  records.value = res
}

// 查询并异步刷新缓存
async function querymsgbyds(num) {
  logLoading.value = true
  try {
    await qbdan(num)
    const resp = await http.post('/sv/aftergetqmbydsan', { dss: [3], num })
    if (resp.data?.data === '更新数据成功！') {
      await qbdan(num)
    }
  } catch (e) {
    console.log(`查询操作信息err: ${e.message}`)
  } finally {
    logLoading.value = false
  }
}

async function submit() {
  const { companyIds, sseats, pseats, mk, env, type, jzc } = form
  if (!companyIds || !sseats || !pseats) {
    ElMessage.warning('必填项不能为空！')
    return
  }
  if (type === 'jz' && !jzc) {
    ElMessage.warning('家装类型不能为空! ')
    return
  }
  loading.value = true
  try {
    const resp = await http.post('/sv/jtSaleskits', {
      companyIds, sseats, pseats,
      mk: mk.join(','),
      env,
      type: type === 'zs' ? 0 : 1,
      jzc,
    })
    result1.value = resp.data?.data?.skCompanyConfig || ''
    querymsgbyds(6)
  } catch (e) {
    result1.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

function reset() {
  form.companyIds = ''
  form.sseats = ''
  form.pseats = ''
  form.mk = []
  form.type = 'zs'
  form.jzc = ''
  form.env = 'prod'
  result1.value = ''
}

onMounted(() => {
  querymsgbyds(10)
})
</script>

<style scoped>
.jtsk-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.jtsk-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.jtsk-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.jtsk-panel--main {
  flex: 1.2;
}
.jtsk-panel :deep(.el-card__body) { overflow-y: auto; }
.jtsk-title { text-align: center; font-weight: 600; font-size: 16px; }
.jtsk-seats {
  display: flex;
  gap: 10px;
  width: 100%;
}
.jtsk-seats :deep(.el-textarea) {
  flex: 1;
  min-width: 0;
}
.jtsk-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
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
.jtsk-log { min-height: 200px; }
.jtsk-empty {
  color: #c0c4cc;
  text-align: center;
  padding: 48px 20px;
}
.jtsk-item {
  padding: 10px 12px;
  border-bottom: 1px solid #ebeef5;
}
.jtsk-item__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.jtsk-item__title { font-weight: 600; font-size: 14px; color: #303133; }
.jtsk-item__time { font-size: 12px; color: #909399; white-space: nowrap; }
.jtsk-item__msg {
  margin-top: 4px;
  font-size: 13px;
  color: #606266;
  word-break: break-all;
}
</style>
