<template>
  <div class="as-page">
    <!-- 第一列 -->
    <div class="as-column">
      <!-- 卡片1: 综合查询 -->
      <el-card class="as-card" shadow="never">
        <template #header>
          <div class="as-card-header" @click="c1.collapsed = !c1.collapsed">
            <span class="as-card-header__title">综合查询</span>
            <el-icon class="as-card-header__arrow" :class="{ 'is-collapsed': c1.collapsed }">
              <ArrowDown />
            </el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="!c1.collapsed">
            <div class="as-form-grid">
              <label>{{ c1.queryLabel }}</label>
              <el-input v-model="c1.value" placeholder="请输入查询参数" />
              <label>查询类型:</label>
              <el-select v-model="c1.sel" placeholder="请选择" @change="onSelChange">
                <el-option label="SAAS手机号查询企业ID" value="qcompid" />
                <el-option label="基线版手机号查询企业ID" value="oqcompid" />
                <el-option label="查询企业微信ID" value="qwwid" />
                <el-option label="查询公众号小程序绑定" value="qocbind" />
                <el-option label="查询小程序/企微绑定" value="qwappbind" />
                <el-option label="根据明文查询密文企微ID" value="qopencorpid" />
              </el-select>
            </div>
            <div class="as-btns">
              <el-button type="primary" :loading="c1.loading" @click="submit1">查询 &gt;&gt;</el-button>
              <el-button @click="reset1">重置</el-button>
            </div>
            <div class="as-result" v-html="c1.result"></div>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 卡片3: 定制化小程序配置 -->
      <el-card class="as-card" shadow="never">
        <template #header>
          <div class="as-card-header" @click="c3.collapsed = !c3.collapsed">
            <span class="as-card-header__title">定制化小程序配置</span>
            <el-icon class="as-card-header__arrow" :class="{ 'is-collapsed': c3.collapsed }">
              <ArrowDown />
            </el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="!c3.collapsed">
            <div class="as-form-grid">
              <label>企业ID:</label>
              <el-input v-model="c3.cid" placeholder="请输入企业ID" />
              <label>小程序ID:</label>
              <el-input v-model="c3.appletCorpId" placeholder="请输入小程序ID" />
              <label>SECRET:</label>
              <el-input v-model="c3.secretKey" placeholder="请输入Secret" />
            </div>
            <div class="as-radio-group">
              <el-radio-group v-model="c3.applet">
                <el-radio value="dz">转介绍3.0</el-radio>
                <el-radio value="zs">Saleskits</el-radio>
                <el-radio value="org">基线版</el-radio>
              </el-radio-group>
            </div>
            <div class="as-row-actions">
              <el-checkbox v-model="c3.istest">测试环境</el-checkbox>
              <div class="as-btns">
                <el-button type="primary" :loading="c3.loading" @click="submit3">提交 &gt;&gt;</el-button>
                <el-button @click="reset3">重置</el-button>
              </div>
            </div>
            <div class="as-result" v-html="c3.result"></div>
          </div>
        </el-collapse-transition>
      </el-card>
    </div>

    <!-- 第二列 -->
    <div class="as-column">
      <!-- 卡片2: 配置隐私保护 -->
      <el-card class="as-card" shadow="never">
        <template #header>
          <div class="as-card-header" @click="c2.collapsed = !c2.collapsed">
            <span class="as-card-header__title">配置隐私保护</span>
            <el-icon class="as-card-header__arrow" :class="{ 'is-collapsed': c2.collapsed }">
              <ArrowDown />
            </el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="!c2.collapsed">
            <div class="as-form-grid">
              <label>企业ID:</label>
              <el-input v-model="c2.cid" placeholder="请输入企业ID" />
            </div>
            <div class="as-btns">
              <el-button type="primary" :loading="c2.loading" @click="submit2">提交 &gt;&gt;</el-button>
              <el-button @click="reset2">重置</el-button>
            </div>
            <div class="as-result" v-html="c2.result"></div>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 卡片4: 绑定企业和企微加密corpid -->
      <el-card class="as-card" shadow="never">
        <template #header>
          <div class="as-card-header" @click="c4.collapsed = !c4.collapsed">
            <span class="as-card-header__title">绑定企业和企微加密corpid</span>
            <el-icon class="as-card-header__arrow" :class="{ 'is-collapsed': c4.collapsed }">
              <ArrowDown />
            </el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="!c4.collapsed">
            <div class="as-form-grid">
              <label>企业ID:</label>
              <el-input v-model="c4.cid" placeholder="请输入企业ID" />
              <label>企微ID:</label>
              <el-input v-model="c4.corpId" placeholder="请输入企微ID" />
            </div>
            <div class="as-btns">
              <el-button type="primary" :loading="c4.loading" @click="submit4">提交 &gt;&gt;</el-button>
              <el-button @click="reset4">重置</el-button>
            </div>
            <div class="as-result" v-html="c4.result"></div>
          </div>
        </el-collapse-transition>
      </el-card>
    </div>

    <!-- 第三列 -->
    <div class="as-column">
      <!-- 卡片5: 激活注销手机号 -->
      <el-card class="as-card" shadow="never">
        <template #header>
          <div class="as-card-header" @click="c5.collapsed = !c5.collapsed">
            <span class="as-card-header__title">激活注销手机号</span>
            <el-icon class="as-card-header__arrow" :class="{ 'is-collapsed': c5.collapsed }">
              <ArrowDown />
            </el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="!c5.collapsed">
            <div class="as-form-grid">
              <label>手机号码:</label>
              <el-input v-model="c5.tel" placeholder="请输入手机号" maxlength="11" />
            </div>
            <div class="as-btns">
              <el-button type="primary" :loading="c5.loading" @click="submit5">激活 &gt;&gt;</el-button>
              <el-button @click="reset5">重置</el-button>
            </div>
            <div class="as-result" v-html="c5.result"></div>
          </div>
        </el-collapse-transition>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import http from '../../api/http'

// 卡片1: 综合查询
const c1 = reactive({
  value: '',
  sel: 'qcompid',
  queryLabel: '登录账号:',
  result: '',
  loading: false,
  collapsed: false,
})

function onSelChange() {
  const v = c1.sel
  if (v === 'qopencorpid') c1.queryLabel = '明文ID:'
  else if (v === 'qcompid') c1.queryLabel = '登录账号:'
  else c1.queryLabel = '企业ID:'
}

async function submit1() {
  if (!c1.value.trim()) {
    ElMessage.warning('查询参数不能为空！')
    return
  }
  if (!c1.sel) {
    ElMessage.warning('查询类型不能为空！')
    return
  }
  if (c1.sel === 'qcompid' || c1.sel === 'oqcompid') {
    if (c1.value.length !== 11) {
      ElMessage.warning('请输入正确的手机号！')
      return
    }
    const sysvs = c1.sel === 'qcompid' ? 'saas' : 'origin'
    c1.loading = true
    try {
      const resp = await http.post(`/sv/querycompid/${sysvs}`, {
        companyId: c1.value,
        env: 'prod',
      })
      const d = resp.data?.data || {}
      c1.result = `${d.cn || ''} (${d.cid || ''})`
    } catch (e) {
      ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
    } finally {
      c1.loading = false
    }
    return
  }
  const apiMap = {
    qwwid: '/sv/queryci',
    qocbind: '/sv/queryca',
    qwappbind: '/sv/queryaal',
    qopencorpid: '/sv/querySCID',
  }
  const api = apiMap[c1.sel]
  if (!api) return
  c1.loading = true
  try {
    const resp = await http.post(api, { companyId: c1.value, env: 'prod' })
    c1.result = resp.data?.data || ''
  } catch (e) {
    ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    c1.loading = false
  }
}

function reset1() {
  c1.value = ''
  c1.sel = 'qcompid'
  c1.queryLabel = '登录账号:'
  c1.result = ''
}

// 卡片2: 配置隐私保护
const c2 = reactive({
  cid: '',
  result: '',
  loading: false,
  collapsed: false,
})

async function submit2() {
  if (!c2.cid.trim()) {
    ElMessage.warning('企业id不能为空！')
    return
  }
  if (c2.cid.length < 18) {
    ElMessage.warning('企业id不能少于18位！')
    return
  }
  if (!/^\d+$/.test(c2.cid)) {
    ElMessage.warning('企业id只能是纯数字！')
    return
  }
  c2.loading = true
  try {
    const resp = await http.post('/sv/privset', { companyId: c2.cid })
    c2.result = resp.data?.data || ''
  } catch (e) {
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    c2.loading = false
  }
}

function reset2() {
  c2.cid = ''
  c2.result = ''
}

// 卡片3: 定制化小程序配置
const c3 = reactive({
  cid: '',
  appletCorpId: '',
  secretKey: '',
  applet: 'zs',
  istest: false,
  result: '',
  loading: false,
  collapsed: false,
})

async function submit3() {
  if (!c3.cid || !c3.appletCorpId || !c3.secretKey) {
    if (!c3.cid) { ElMessage.warning('企业id不能为空！'); return }
    if (!c3.appletCorpId) { ElMessage.warning('小程序id不能为空！'); return }
    if (!c3.secretKey) { ElMessage.warning('secretKey不能为空！'); return }
  }
  if (c3.applet === 'zs' || c3.applet === 'dz') {
    if (c3.cid.length < 18) {
      ElMessage.warning('企业id不能少于18位！')
      return
    }
  }
  if (!/^\d+$/.test(c3.cid)) {
    ElMessage.warning('企业id只能是纯数字！')
    return
  }
  c3.loading = true
  try {
    const resp = await http.post('/sv/dzapplet', {
      companyId: c3.cid,
      corpId: c3.appletCorpId,
      secretKey: c3.secretKey,
      applet: c3.applet,
      istest: c3.istest,
    })
    c3.result = resp.data?.data || ''
  } catch (e) {
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    c3.loading = false
  }
}

function reset3() {
  c3.cid = ''
  c3.appletCorpId = ''
  c3.secretKey = ''
  c3.applet = 'zs'
  c3.istest = false
  c3.result = ''
}

// 卡片4: 绑定企业和企微加密corpid
const c4 = reactive({
  cid: '',
  corpId: '',
  result: '',
  loading: false,
  collapsed: false,
})

async function submit4() {
  if (!c4.cid) { ElMessage.warning('企业id不能为空！'); return }
  if (!c4.corpId) { ElMessage.warning('corpId不能为空！'); return }
  c4.loading = true
  try {
    const resp = await http.post('/sv/selfcreatedCS', {
      companyId: c4.cid,
      corpId: c4.corpId,
    })
    c4.result = resp.data?.data || ''
  } catch (e) {
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    c4.loading = false
  }
}

function reset4() {
  c4.cid = ''
  c4.corpId = ''
  c4.result = ''
}

// 卡片5: 激活注销手机号
const c5 = reactive({
  tel: '',
  result: '',
  loading: false,
  collapsed: false,
})

async function submit5() {
  if (c5.tel.length !== 11) {
    ElMessage.warning('手机号只能是11位！')
    return
  }
  if (!/^\d+$/.test(c5.tel)) {
    ElMessage.warning('手机号只能是纯数字！')
    return
  }
  c5.loading = true
  try {
    const resp = await http.post('/sv/removeTagTel', {
      phoneNumber: c5.tel,
      env: 'prod',
    })
    c5.result = resp.data?.data || ''
  } catch (e) {
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    c5.loading = false
  }
}

function reset5() {
  c5.tel = ''
  c5.result = ''
}
</script>

<style scoped>
.as-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  gap: 12px;
}

.as-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  padding-top: 4px;
}

.as-column::-webkit-scrollbar {
  width: 5px;
}

.as-column::-webkit-scrollbar-track {
  background: transparent;
}

.as-column::-webkit-scrollbar-thumb {
  background: #ededed;
  border-radius: 10px;
}

.as-column::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.as-card {
  flex-shrink: 0;
  border: 1px solid #e9e9e9;
  border-radius: 14px;
}

.as-card :deep(.el-card__header) {
  padding: 0;
  border-bottom: none;
}

.as-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  background: #f0f2f5;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.3s;
  user-select: none;
  border-radius: 14px 14px 0 0;
}

.as-card-header:hover {
  background: #fafafa;
}

.as-card-header__title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.as-card-header__arrow {
  font-size: 12px;
  color: #666;
  transition: transform 0.3s;
}

.as-card-header__arrow.is-collapsed {
  transform: rotate(-90deg);
}

.as-card :deep(.el-card__body) {
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

/* 表单网格：label 宽度自适应 + 200px 输入框 */
.as-form-grid {
  display: grid;
  grid-template-columns: max-content 200px;
  column-gap: 8px;
  row-gap: 8px;
  align-items: center;
  width: 100%;
  max-width: 420px;
  justify-content: center;
}

.as-form-grid label {
  text-align: right;
  font-size: 14px;
  white-space: nowrap;
  color: #606266;
}

.as-radio-group {
  display: flex;
  justify-content: center;
  margin: 10px 0;
}

.as-row-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
}

.as-btns {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.as-result {
  margin-top: 10px;
  padding: 10px;
  border-radius: 8px;
  overflow-y: auto;
  overflow-x: hidden;
  font-size: 15px;
  text-align: center;
  width: 100%;
  min-height: 50px;
  max-height: 400px;
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
  background: #ffffff;
  /* border: 1px solid #f0f0f0; */
}
</style>
