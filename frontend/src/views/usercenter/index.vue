<template>
  <div class="uc-page">
    <!-- 左栏：用户信息 -->
    <div class="uc-left">
      <el-card class="uc-card" shadow="never">
        <div class="uc-profile">
          <div class="uc-avatar">
            <img v-if="lid === 8" :src="avatarSrc" alt="GZHZY" class="uc-avatar__img" />
          </div>
          <div>
            <span class="uc-name">{{ rn }}</span>
            <span class="uc-role">测试工程师 | 加推</span>
          </div>
        </div>
        <div class="uc-motto" v-if="lid === 8">
          己所不欲, 勿施于人!<br/>
          工欲善其事, 必先利其器!
        </div>

        <!-- 加密区 -->
        <div class="uc-enc">
          <div class="uc-enc__form">
            <el-input v-model="enc.txt" placeholder="输入密码..." class="uc-enc__main" />
            <el-input v-model="enc.jxuid" placeholder="userId..." class="uc-enc__id" />
            <el-button type="primary" :loading="enc.loading" @click="encrypt">加密</el-button>
          </div>
          <div class="uc-enc__hint">注：userId=0时，不做截取处理。否则截取中间16位。</div>
          <div v-if="enc.result" class="uc-enc__result">{{ enc.result }}</div>
          <el-input v-model="enc.compare" placeholder="请输入对比数据..." class="uc-enc__compare" />
        </div>
      </el-card>
    </div>

    <!-- 右栏：功能 -->
    <div class="uc-right">
      <el-card class="uc-card" shadow="never">
        <el-tabs v-model="activeTab" type="card" class="uc-tabs">
          <!-- Tab 1: 企业开户 -->
          <el-tab-pane label="企业(手工)开户" name="coa">
            <div class="uc-tab-heading">
              <span class="uc-section-title">企业(手工)开户</span>
            </div>
            <div class="uc-form-row">
              <span class="uc-form-label">◈ 企业名称:</span>
              <el-input v-model="coa.cname" placeholder="请输入企业名称" />
            </div>
            <div class="uc-form-row">
              <span class="uc-form-label">◈ 登录手机号:</span>
              <el-input v-model="coa.loginname" placeholder="请输入登录手机号" />
            </div>
            <div class="uc-form-row">
              <span class="uc-form-label">◈ 登录密码:</span>
              <el-input v-model="coa.passwd" type="password" placeholder="请输入登录密码" show-password />
            </div>
            <div class="uc-form-row">
              <span class="uc-form-label">◈ 企业类型:</span>
              <el-select v-model="coa.ctype" placeholder="请选择">
                <el-option label="7" value="7" />
                <el-option label="0" value="0" />
              </el-select>
            </div>
            <div class="uc-form-row">
              <span class="uc-form-label">◈ 有效期限:</span>
              <el-date-picker v-model="coa.etime" type="date" value-format="YYYY-MM-DD" placeholder="请选择日期" />
            </div>
            <div class="uc-form-actions">
              <el-radio-group v-model="coa.env">
                <el-radio value="prod">生产环境</el-radio>
                <el-radio value="test">测试环境</el-radio>
              </el-radio-group>
            </div>
            <div class="uc-form-actions">
              <el-button type="primary" :loading="coa.loading" @click="submitCoa">提交</el-button>
            </div>
            <div v-if="coa.utip" class="uc-result" v-html="coa.utip"></div>
            <div v-if="coa.cinfo" class="uc-result" v-html="coa.cinfo"></div>
          </el-tab-pane>

          <!-- Tab 2: TP用户增删改 -->
          <el-tab-pane label="TP用户增删改" name="urp">
            <div class="uc-tab-heading">
              <span class="uc-section-title">TP用户增删改</span>
            </div>
            <div v-show="showUn" class="uc-form-row">
              <span class="uc-form-label">用户姓名:</span>
              <el-input v-model="urp.userName" placeholder="未填写，则用账号覆盖" />
            </div>
            <div class="uc-form-row">
              <span class="uc-form-label">登录账号:</span>
              <el-input v-model="urp.account" placeholder="请输入登录账号" />
            </div>
            <div v-show="showEmail" class="uc-form-row">
              <span class="uc-form-label">用户邮箱:</span>
              <el-input v-model="urp.userEmail" placeholder="请输入用户邮箱" />
            </div>
            <div v-show="showPwd" class="uc-form-row">
              <span class="uc-form-label">用户密码:</span>
              <el-input v-model="urp.pwd" type="password" placeholder="请输入用户密码" show-password />
            </div>
            <div v-show="showUvs" class="uc-form-row">
              <span class="uc-form-label">活跃状态:</span>
              <el-radio-group v-model="urp.plant">
                <el-radio value="tp">活跃</el-radio>
                <el-radio value="asp">不活跃(不可登录)</el-radio>
              </el-radio-group>
            </div>
            <div v-show="showUrole" class="uc-form-row">
              <span class="uc-form-label">用户角色:</span>
              <el-radio-group v-model="urp.urole">
                <el-radio value="normal">普通用户</el-radio>
                <el-radio value="admin">管理员</el-radio>
              </el-radio-group>
            </div>
            <el-divider />
            <div class="uc-form-actions">
              <el-radio-group v-model="urp.oprate">
                <el-radio value="registUser">注册用户</el-radio>
                <el-radio value="modifyRole">修改角色</el-radio>
                <el-radio value="deleteUser">删除用户</el-radio>
              </el-radio-group>
            </div>
            <div class="uc-form-actions">
              <el-button @click="resetUrp">重置</el-button>
              <el-button type="primary" :loading="urp.loading" @click="submitUrp">提交</el-button>
            </div>
            <div v-if="urp.rlt" class="uc-result-note" v-html="urp.rlt"></div>
          </el-tab-pane>

          <!-- Tab 3: FiveMillion -->
          <el-tab-pane label="FiveMillion" name="fm">
            <div class="uc-tab-heading">
              <span class="uc-section-title">FiveMillion</span>
            </div>
            <div class="uc-form-actions">
              <span>类型:</span>
              <el-radio-group v-model="fm.cp" @change="onFmCpChange">
                <el-radio value="ssq">SSQ</el-radio>
                <el-radio value="dlt">DLT</el-radio>
                <el-radio value="kl8">KL8</el-radio>
              </el-radio-group>
            </div>
            <div v-show="fm.isLocalVisible" class="uc-form-row">
              <span>是否取本地数据（{{ fm.localTotal }}）:</span>
              <el-radio-group v-model="fm.isl">
                <el-radio value="yes">是</el-radio>
                <el-radio value="no">否</el-radio>
              </el-radio-group>
              <el-button type="danger" plain @click="showCleanDialog">清空本地数据</el-button>
            </div>
            <div class="uc-form-row">
              <span>次数:</span>
              <el-input v-model="fm.nt" type="number" class="uc-input--xs" />
              <el-button type="primary" :loading="fm.loading" @click="submitFm">生成</el-button>
              <el-button @click="resetFm">重置</el-button>
            </div>
            <div v-if="fm.result" class="uc-fm-result">{{ fm.result }}</div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <!-- 清空本地数据确认弹窗 -->
    <el-dialog v-model="fm.showCleanDialog" title="确认" width="360px">
      <div v-if="!fm.cleaning">{{ fm.cleanResult || '确认要清除本地数据吗？' }}</div>
      <div v-else>清理中...</div>
      <template #footer>
        <el-button v-if="!fm.cleaning && !fm.cleanResult" @click="fm.showCleanDialog = false">取消</el-button>
        <el-button v-if="!fm.cleaning && !fm.cleanResult" type="danger" @click="cleanLocalData">确定</el-button>
        <el-button v-if="fm.cleanResult" @click="fm.showCleanDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

// 静态资源路径（Vite 不处理动态绑定的 src）
const avatarSrc = '/static/img/gzhzy.png'

// 用户信息（从 session 获取）
const rn = ref('')
const lid = ref(0)

const activeTab = ref('coa')

// 加密
const enc = reactive({
  txt: '',
  jxuid: '',
  compare: '',
  result: '',
  loading: false,
})

async function encrypt() {
  if (!enc.txt) {
    ElMessage.warning('输入加密内容！')
    return
  }
  enc.loading = true
  try {
    const resp = await http.post('/pv/usercenter/enc', {
      txt: enc.txt,
      jxuid: enc.jxuid,
      uctype: 'enc',
    })
    enc.result = resp.data?.data?.encryption || ''
  } catch (e) {
    ElMessage.error('加密失败')
  } finally {
    enc.loading = false
  }
}

// 企业开户
const coa = reactive({
  cname: '',
  loginname: '',
  passwd: 'a123456',
  ctype: '7',
  etime: '2030-12-31',
  env: 'test',
  utip: '',
  cinfo: '',
  loading: false,
})

async function submitCoa() {
  if (!coa.cname || !coa.ctype || !coa.etime || !coa.loginname || !coa.passwd) {
    ElMessage.warning('必填项不能为空！')
    return
  }
  if (isNaN(coa.loginname) || coa.loginname.length !== 11) {
    ElMessage.warning('登录手机号必须是11位数字！')
    return
  }
  coa.loading = true
  try {
    const resp = await http.post('/pv/usercenter/coa', {
      companyName: coa.cname,
      companyType: coa.ctype,
      expireTime: coa.etime,
      loginName: coa.loginname,
      password: coa.passwd,
      env: coa.env,
      uctype: 'coa',
    })
    const d = resp.data?.data || {}
    coa.utip = d.coaTitle || ''
    coa.cinfo = d.coaInfo || ''
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    coa.loading = false
  }
}

// TP用户增删改
const urp = reactive({
  userName: '',
  account: '',
  userEmail: '',
  pwd: '',
  plant: 'tp',
  urole: 'normal',
  oprate: 'registUser',
  rlt: '',
  loading: false,
})

const showUn = computed(() => urp.oprate !== 'modifyRole' && urp.oprate !== 'deleteUser')
const showEmail = computed(() => urp.oprate !== 'deleteUser')
const showPwd = computed(() => urp.oprate !== 'deleteUser')
const showUvs = computed(() => urp.oprate !== 'deleteUser' && urp.oprate !== 'modifyRole')
const showUrole = computed(() => urp.oprate !== 'deleteUser')

function resetUrp() {
  urp.userName = ''
  urp.account = ''
  urp.userEmail = ''
  urp.pwd = ''
  urp.plant = 'tp'
  urp.urole = 'normal'
  urp.oprate = 'registUser'
  urp.rlt = ''
}

async function submitUrp() {
  if (!urp.account) {
    urp.rlt = '账号不能为空！'
    return
  }
  if (urp.oprate === 'registUser') {
    if (urp.pwd.length < 3) {
      urp.rlt = '密码不能少于3位！'
      return
    }
    if (!urp.userEmail) {
      urp.rlt = '邮箱不能为空！'
      return
    }
  }
  const ur = urp.plant === 'tp' ? (urp.urole === 'normal' ? '2' : '99') : '2'
  urp.loading = true
  try {
    const resp = await http.post('/pv/registTP', {
      name: urp.userName,
      lname: urp.account,
      email: urp.userEmail,
      pwd: urp.pwd,
      plant: urp.plant,
      ur,
      oprate: urp.oprate,
    })
    const res = resp.data?.data?.registTestPlant || ''
    urp.rlt = res
    // 修改当前用户密码 → 跳转登录
    if (urp.oprate === 'modifyRole' && res.includes('【isPwdChanged】') && urp.pwd) {
      urp.rlt = res.replace('【isPwdChanged】', '') + '<br/><span style="color:red;">密码已修改，请重新登录。</span>'
      setTimeout(() => { window.location.href = '/logout' }, 1500)
    }
  } catch (e) {
    urp.rlt = '操作失败'
  } finally {
    urp.loading = false
  }
}

// FiveMillion
const fm = reactive({
  cp: 'ssq',
  isl: 'no',
  nt: '10',
  result: '',
  loading: false,
  localTotal: '',
  isLocalVisible: true,
  showCleanDialog: false,
  cleaning: false,
  cleanResult: '',
})

function onFmCpChange() {
  fm.isLocalVisible = fm.cp === 'ssq'
}

async function getLocalTotal() {
  try {
    const resp = await http.post('/pv/usercenter/gettotal', { uctype: 'gettotal' })
    fm.localTotal = resp.data?.data?.getTotal || ''
  } catch (e) {
    fm.localTotal = ''
  }
}

async function submitFm() {
  const nt = parseInt(fm.nt)
  if (!nt || isNaN(nt) || nt <= 0) {
    ElMessage.warning('输入正整数！')
    return
  }
  if (fm.isl === 'yes' && nt > 100) {
    fm.result = '输入100及以内的正整数！'
    return
  }
  if (fm.isl === 'no' && nt > 1000000) {
    fm.result = '输入1000000及以内的正整数！'
    return
  }
  fm.loading = true
  try {
    const resp = await http.post('/pv/usercenter/fm', {
      nt: fm.nt,
      cp: fm.cp,
      isl: fm.isl,
      uctype: 'fm',
    })
    fm.result = resp.data?.data?.fiveMillion || ''
    getLocalTotal()
  } catch (e) {
    fm.result = '生成失败'
  } finally {
    fm.loading = false
  }
}

function resetFm() {
  fm.cp = 'ssq'
  fm.isl = 'no'
  fm.nt = '10'
  fm.result = ''
  fm.isLocalVisible = true
}

function showCleanDialog() {
  if (!fm.localTotal || fm.localTotal === '0') {
    ElMessage.warning('无数据！')
    return
  }
  fm.cleanResult = ''
  fm.cleaning = false
  fm.showCleanDialog = true
}

async function cleanLocalData() {
  fm.cleaning = true
  try {
    const resp = await http.post('/pv/usercenter/cld', { uctype: 'cld' })
    fm.cleanResult = resp.data?.data?.cleanLocalData || '清理完成'
    fm.result = ''
    getLocalTotal()
  } catch (e) {
    fm.cleanResult = '清理失败'
  } finally {
    fm.cleaning = false
  }
}

onMounted(() => {
  // 获取用户信息（从 session 或 API）
  const session = JSON.parse(sessionStorage.getItem('user') || '{}')
  rn.value = session.rn || ''
  lid.value = session.lid || 0
  getLocalTotal()
})
</script>

<style scoped>
.uc-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  gap: 16px;
}
.uc-left {
  width: 600px;
  min-width: 300px;
  flex-shrink: 0;
  overflow-y: auto;
}
.uc-right {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
}
.uc-card {
  height: 100%;
  border-radius: 16px;
}
.uc-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}
.uc-avatar {
  margin-bottom: 12px;
}
.uc-avatar__img {
  width: 110px;
  height: 110px;
  border-radius: 9999px;
  border: 3px solid #f3f4f6;
  object-fit: cover;
}
.uc-name {
  display: block;
  font-size: 30px;
  font-weight: 600;
  color: #111827;
  text-align: center;
}
.uc-role {
  display: block;
  font-size: 18px;
  color: #9ca3af;
  margin-top: 4px;
  text-align: center;
}
.uc-motto {
  margin: 16px 0;
  text-align: center;
  font-size: 18px;
  color: #4b5563;
  line-height: 1.625;
}
.uc-enc {
  width: 100%;
  padding: 0 20px;
}
.uc-enc__form {
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
}
.uc-enc__main {
  flex: 1;
  min-width: 100px;
}
.uc-enc__id {
  width: 150px;
  flex: none;
}
.uc-enc__hint {
  font-size: 12px;
  color: #d1d5db;
  margin-top: 6px;
  text-align: center;
}
.uc-enc__result {
  margin-top: 8px;
  font-size: 13px;
  color: #6366f1;
  word-break: break-all;
  min-height: 20px;
  text-align: center;
}
.uc-enc__compare {
  margin-top: 10px;
  width: 100%;
}
.uc-tabs {
  height: 100%;
}
.uc-tab-heading {
  text-align: center;
  margin-bottom: 24px;
}
.uc-section-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  padding-bottom: 6px;
  border-bottom: 3px solid #6366f1;
}
.uc-form-row {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 6px 0;
  gap: 8px;
}
.uc-form-label {
  text-align: right;
  min-width: 100px;
  font-size: 14px;
  color: #6b7280;
}
.uc-form-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin: 12px 0;
}
.uc-input--xs {
  width: 60px;
}
.uc-result {
  text-align: center;
  font-size: 14px;
  margin-top: 12px;
  color: #374151;
}
.uc-result-note {
  font-size: 12px;
  color: #ef4444;
  text-align: center;
  margin: 6px 0;
}
.uc-fm-result {
  width: 100%;
  max-height: 550px;
  overflow-y: auto;
  text-align: center;
  font-size: 14px;
  line-height: 1.625;
  color: #374151;
  padding: 10px;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #f9fafb;
  margin-top: 12px;
}
</style>
