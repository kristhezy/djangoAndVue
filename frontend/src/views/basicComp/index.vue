<template>
  <div class="bccfg-page">
    <div class="bccfg-cols">
      <!-- 左栏：配置 -->
      <el-card class="bccfg-panel bccfg-panel--main" shadow="never">
        <template #header>
          <div class="bccfg-title">销售工具版配置</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企业 IDs" required>
            <el-input
              v-model="form.companyId"
              type="textarea"
              :rows="3"
              placeholder="示例: 727972691243679744,593467466257072128"
            />
          </el-form-item>

          <el-form-item label="企业模块" required>
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
          </el-form-item>

          <el-form-item label="环境">
            <el-radio-group v-model="form.env">
              <el-radio value="prod">生产</el-radio>
              <el-radio value="test">测试</el-radio>
            </el-radio-group>
          </el-form-item>

          <div class="bccfg-actions">
            <el-button type="primary" :loading="loading" @click="submit">提交</el-button>
            <el-button @click="reset">重置</el-button>
          </div>

          <div class="result">{{ result1 }}</div>
        </el-form>
      </el-card>

      <!-- 右栏：执行结果 -->
      <OperationLog ref="log" :ds="[2]" :init-num="10" />
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'
import OperationLog from '../../components/OperationLog.vue'

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
.bccfg-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.bccfg-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.bccfg-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.bccfg-panel--main {
  flex: 1.2;
}
.bccfg-panel :deep(.el-card__body) { overflow-y: auto; }
.bccfg-title { text-align: center; font-weight: 600; font-size: 16px; }
.bccfg-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
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
