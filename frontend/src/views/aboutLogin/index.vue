<template>
  <div class="alogin-page">
    <div class="alogin-cols">
      <!-- 卡片1: 查询验证码 -->
      <el-card class="alogin-card" shadow="never">
        <template #header>
          <div class="alogin-title">查询验证码</div>
        </template>
        <el-form label-width="auto">
          <el-form-item label="手机号码" required>
            <el-input v-model="form1.tel" maxlength="11" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form1.env">
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="alogin-actions">
            <el-button type="primary" :loading="loading1" @click="queryCode">查询</el-button>
            <el-button @click="reset1">重置</el-button>
          </div>
          <div class="alogin-note">注：查询10分钟以内的短信验证码。</div>
          <div class="result">{{ result1 }}</div>
        </el-form>
      </el-card>

      <!-- 卡片2: 设置销售/推荐官固定验证码 -->
      <el-card class="alogin-card" shadow="never">
        <template #header>
          <div class="alogin-title">设置销售/推荐官固定验证码</div>
        </template>
        <el-form label-width="auto">
          <el-form-item v-show="form2.role === 'sale'" label="企业 ID" required>
            <el-input v-model="form2.cid" placeholder="请输入企业ID" />
          </el-form-item>
          <el-form-item label="手机号" required>
            <el-input v-model="form2.tel" maxlength="11" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="验证码" required>
            <el-input v-model="form2.code" maxlength="4" placeholder="请输入4位验证码" />
          </el-form-item>
          <el-form-item label="角色">
            <el-radio-group v-model="form2.role">
              <el-radio value="sale">销售</el-radio>
              <el-radio value="partner">推荐官</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form2.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="alogin-actions">
            <el-button type="primary" :loading="loading2" @click="setCode">提交</el-button>
            <el-button @click="reset2">重置</el-button>
          </div>
          <div class="result">{{ result2 }}</div>
        </el-form>
      </el-card>

      <!-- 卡片3: 小程序码 -->
      <el-card class="alogin-card" shadow="never">
        <template #header>
          <div class="alogin-title">小程序码</div>
        </template>
        <div class="alogin-thumb-grid">
          <el-image
            v-for="name in thumbNames"
            :key="name"
            :src="`/static/img/${name}.png`"
            :preview-src-list="[`/static/img/${name}.png`]"
            :preview-teleported="true"
            fit="contain"
            class="alogin-thumb"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

// 小程序码图片名（复刻 AT_aboutLogin.html 第 161-169 行）
const thumbNames = ['jdkf', 'jdcs', 'mdcszy', 'hxbd', 'dzhx', 'wfw666', 'jtmp', 'jtty', 'cjzsbys']

const form1 = reactive({ tel: '', env: 'test' })
const form2 = reactive({ cid: '', tel: '', code: '', role: 'sale', env: 'prod' })
const result1 = ref('')
const result2 = ref('')
const loading1 = ref(false)
const loading2 = ref(false)

const isDigits = (s) => /^\d+$/.test(s)

async function queryCode() {
  if (!form1.tel) { result1.value = "'手机号码'不能为空! "; return }
  loading1.value = true
  try {
    const resp = await http.post('/sv/queryLoginCode', { tel: form1.tel, env: form1.env })
    result1.value = resp.data?.data || ''
  } catch (e) {
    result1.value = ''
    ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading1.value = false
  }
}

async function setCode() {
  const { cid, tel, code, role, env } = form2
  let data
  if (role === 'sale') {
    if (!cid) { result2.value = '企业ID不能为空！'; return }
    if (cid.length < 18 || !isDigits(cid)) { result2.value = '企业ID为18位以上的纯数字！'; return }
    data = { cid, tel, code, role, env }
  } else {
    data = { tel, code, role, env }
  }
  if (!tel) { result2.value = '手机号不能为空！'; return }
  if (tel.length !== 11 || !isDigits(tel)) { result2.value = '手机号只能为11位纯数字！'; return }
  if (!code) { result2.value = '验证码不能为空！'; return }
  if (code.length !== 4 || !isDigits(code)) { result2.value = '验证码只能是4位纯数字！'; return }

  loading2.value = true
  try {
    const resp = await http.post('/sv/splc', data)
    result2.value = resp.data?.data || ''
  } catch (e) {
    result2.value = ''
    ElMessage.error('设置失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading2.value = false
  }
}

function reset1() {
  form1.tel = ''; form1.env = 'test'
  result1.value = ''
}
function reset2() {
  form2.cid = ''; form2.tel = ''; form2.code = ''; form2.role = 'sale'; form2.env = 'prod'
  result2.value = ''
}
</script>

<style scoped>
.alogin-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.alogin-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.alogin-card {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.alogin-card :deep(.el-card__body) { overflow-y: auto; }
.alogin-title { text-align: center; font-weight: 600; font-size: 18px; }
.alogin-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
.alogin-note { font-size: 12px; color: #f56c6c; text-align: center; margin: 6px 0; }
.alogin-thumb-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.alogin-thumb {
  width: 140px;
  height: 140px;
  border-radius: 8px;
  cursor: pointer;
}
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
