<template>
  <div class="wecom-page">
    <div class="wecom-cols">
      <!-- 卡片1: 生成企微应用链接 -->
      <el-card class="wecom-card" shadow="never">
        <template #header>
          <div class="wecom-title">生成企微应用链接</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form1.companyId" placeholder="请输入企业ID" />
          </el-form-item>
          <el-form-item label="应用 ID" required>
            <el-select v-model="form1.appId" style="width:100%">
              <el-option v-for="a in appList" :key="a.id" :label="a.name" :value="a.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form1.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="wecom-actions">
            <el-button type="primary" :loading="loading1" @click="genLink">提交</el-button>
            <el-button @click="reset1">重置</el-button>
          </div>
          <el-input v-model="result1" type="textarea" :rows="4" readonly class="wecom-result" placeholder="结果" />
        </el-form>
      </el-card>

      <!-- 卡片2: 获取密文企微ID -->
      <el-card class="wecom-card" shadow="never">
        <template #header>
          <div class="wecom-title">获取密文企微ID</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="企微ID(明文)" required>
            <el-input v-model="form2.corpId" placeholder="请输入企微ID" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form2.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="wecom-actions">
            <el-button type="primary" :loading="loading2" @click="getCorpId">提交</el-button>
            <el-button @click="reset2">重置</el-button>
          </div>
          <el-input v-model="result2" type="textarea" :rows="4" readonly class="wecom-result" placeholder="结果" />
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

// 应用ID下拉硬编码（复刻 AT_wecom.html 第 82-90 行）
const appList = [
  { id: 'cpe_tong', name: '通讯录' },
  { id: 'cpe_radar', name: '雷达' },
  { id: 'cpe_file', name: '文件' },
  { id: 'cpe_article', name: '文章' },
  { id: 'cpe_video', name: '视频' },
  { id: 'cpe_poster', name: '海报' },
  { id: 'cpe_manual', name: '宣传册' },
  { id: 'cpe_case', name: '案例' },
]

const form1 = reactive({ companyId: '', appId: 'cpe_tong', env: 'prod' })
const form2 = reactive({ corpId: '', env: 'prod' })
const result1 = ref('')
const result2 = ref('')
const loading1 = ref(false)
const loading2 = ref(false)

async function genLink() {
  const cid = form1.companyId
  if (!cid || cid.length < 18 || cid.length > 19 || isNaN(cid)) {
    ElMessage.warning('企业ID只能是18或19位的纯数字！'); return
  }
  loading1.value = true
  try {
    const resp = await http.post('/sv/forWeCom', {
      companyId: cid, appId: form1.appId, env: form1.env, type: 1,
    })
    result1.value = resp.data?.data || ''
    if (result1.value.includes('http')) {
      window.open(result1.value)
    }
  } catch (e) {
    result1.value = ''
    ElMessage.error('生成失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading1.value = false
  }
}

async function getCorpId() {
  const corpid = form2.corpId
  if (!corpid) { ElMessage.warning('"企微ID(明文)"不能为空！'); return }
  loading2.value = true
  try {
    const resp = await http.post('/sv/forWeCom', {
      corpId: corpid, env: form2.env, type: 2,
    })
    result2.value = resp.data?.data || ''
  } catch (e) {
    result2.value = ''
    ElMessage.error('获取失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading2.value = false
  }
}

function reset1() {
  form1.companyId = ''; form1.appId = 'cpe_tong'; form1.env = 'prod'
  result1.value = ''
}
function reset2() {
  form2.corpId = ''; form2.env = 'prod'
  result2.value = ''
}
</script>

<style scoped>
.wecom-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.wecom-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.wecom-card {
  flex: 1;
  min-width: 0;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.wecom-card :deep(.el-card__body) { overflow-y: auto; }
.wecom-title { text-align: center; font-weight: 600; font-size: 20px; }
.wecom-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
.wecom-result { margin-top: 8px; }
</style>
