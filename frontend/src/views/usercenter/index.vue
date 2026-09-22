<template>
    <div class="mo-page">
        <div class="toolbar">
            <div class="toolbar-left">
                <h2 class="page-title"><i class="fa-solid fa-user-circle"></i> 个人中心</h2>
            </div>
        </div>

        <div class="mo-body">
            <!-- 左栏：用户信息 + 加密 -->
            <div class="left-col">
                <!-- 个人信息 -->
                <div class="m-card profile-card">
                    <div class="profile-bg"></div>
                    <div class="m-card-bd profile-body">
                        <div class="uc-avatar">
                            <img v-if="lid == 8" :src="avatarSrc" alt="GZHZY" class="uc-avatar__img" />
                            <div v-else class="uc-avatar__placeholder"><i class="fa-solid fa-user"></i></div>
                        </div>
                        <span class="uc-name">{{ rn }}</span>
                        <span class="uc-role">{{ job }} · 加推</span>
                        <div class="uc-motto" v-if="lid == 8">
                            己所不欲, 勿施于人!<br />
                            工欲善其事, 必先利其器!
                        </div>
                    </div>
                </div>

                <!-- 加密工具 -->
                <div class="m-card">
                    <div class="m-card-hd accent-green">
                        <div class="m-card-hd-left"><i class="fa-solid fa-lock card-icon"></i>
                            <h3>加密工具</h3>
                        </div>
                    </div>
                    <div class="m-card-bd">
                        <div class="enc-grid">
                            <el-input v-model="enc.txt" placeholder="输入密码..." />
                            <el-input v-model="enc.jxuid" placeholder="userId..." />
                        </div>
                        <el-button type="primary" :loading="enc.loading" @click="encrypt"
                            style="margin-top:10px;">加密</el-button>
                        <div class="enc-hint">注：userId=0时不做截取，否则截取中间16位</div>
                        <div v-if="enc.result" class="enc-result">{{ enc.result }}</div>
                        <el-input v-model="enc.compare" placeholder="输入对比数据..." style="margin-top:10px;" />
                    </div>
                </div>
            </div>

            <!-- 中栏：企业开户 -->
            <div class="right-col">
                <!-- 企业开户 -->
                <div :class="['m-card', { collapsed: !coaOpen }]">
                    <div class="m-card-hd accent-blue" @click="coaOpen = !coaOpen" style="cursor:pointer;">
                        <div class="m-card-hd-left"><i class="fa-solid fa-building card-icon"></i>
                            <h3>企业(手工)开户</h3>
                        </div>
                        <i :class="['fa-solid fa-chevron-right chevron', { open: coaOpen }]"></i>
                    </div>
                    <div v-show="coaOpen" class="m-card-bd">
                        <div class="form-grid">
                            <div class="fgr"><label>企业名称</label><el-input v-model="coa.cname" placeholder="请输入企业名称" />
                            </div>
                            <div class="fgr"><label>登录手机号</label><el-input v-model="coa.loginname"
                                    placeholder="请输入登录手机号" /></div>
                            <div class="fgr"><label>登录密码</label><el-input v-model="coa.passwd" type="password"
                                    placeholder="请输入登录密码" show-password /></div>
                            <div class="fgr"><label>企业类型</label>
                                <el-select v-model="coa.ctype" style="width:100%"><el-option label="7"
                                        value="7" /><el-option label="0" value="0" /></el-select>
                            </div>
                            <div class="fgr"><label>有效期限</label>
                                <el-date-picker v-model="coa.etime" type="date" value-format="YYYY-MM-DD"
                                    placeholder="请选择日期" style="width:100%" />
                            </div>
                        </div>
                        <EnvRadio v-model="coa.env" name="envCoa" />
                        <BtnGroup @submit="submitCoa" :loading="coa.loading" submitText="提交开户" />
                        <div v-if="coa.utip" class="result-box" v-html="coa.utip"></div>
                        <div v-if="coa.cinfo" class="result-box" v-html="coa.cinfo"></div>
                    </div>
                </div>
            </div>

            <!-- 右栏：TP用户 + FiveMillion -->
            <div class="right-col">

                <!-- TP用户增删改 -->
                <div :class="['m-card', { collapsed: !urpOpen }]">
                    <div class="m-card-hd accent-orange" @click="urpOpen = !urpOpen" style="cursor:pointer;">
                        <div class="m-card-hd-left"><i class="fa-solid fa-users-gear card-icon"></i>
                            <h3>TP用户增删改</h3>
                        </div>
                        <div class="m-card-hd-right">
                            <i :class="['fa-solid fa-chevron-right chevron', { open: urpOpen }]"></i>
                        </div>
                    </div>
                    <div v-show="urpOpen" class="m-card-bd">
                        <div class="urp-op-bar">
                            <label :class="{ active: urp.oprate === 'registUser' }"
                                @click="urp.oprate = 'registUser'">注册用户</label>
                            <label :class="{ active: urp.oprate === 'modifyRole' }"
                                @click="urp.oprate = 'modifyRole'">修改角色</label>
                            <label :class="{ active: urp.oprate === 'deleteUser' }"
                                @click="urp.oprate = 'deleteUser'">删除用户</label>
                        </div>
                        <div class="form-grid">
                            <div v-show="showUn" class="fgr"><label>用户姓名</label><el-input v-model="urp.userName"
                                    placeholder="未填写则用账号覆盖" /></div>
                            <div class="fgr"><label>登录账号</label><el-input v-model="urp.account" placeholder="请输入登录账号" />
                            </div>
                            <div v-show="showEmail" class="fgr"><label>用户邮箱</label><el-input v-model="urp.userEmail"
                                    placeholder="请输入用户邮箱" /></div>
                            <div v-show="showPwd" class="fgr"><label>用户密码</label><el-input v-model="urp.pwd"
                                    type="password" placeholder="请输入用户密码" show-password /></div>
                            <div v-show="showUvs" class="fgr"><label>活跃状态</label>
                                <el-radio-group v-model="urp.plant"><el-radio value="tp">活跃</el-radio><el-radio
                                        value="asp">不活跃</el-radio></el-radio-group>
                            </div>
                            <div v-show="showUrole" class="fgr"><label>用户角色</label>
                                <el-radio-group v-model="urp.urole"><el-radio value="normal">普通用户</el-radio><el-radio
                                        value="admin">管理员</el-radio></el-radio-group>
                            </div>
                        </div>
                        <BtnGroup @reset="resetUrp" @submit="submitUrp" :loading="urp.loading" />
                        <div v-if="urp.rlt" class="result-box result-box--error" v-html="urp.rlt"></div>
                    </div>
                </div>

                <!-- FiveMillion -->
                <div :class="['m-card', { collapsed: !fmOpen }]">
                    <div class="m-card-hd accent-purple" @click="fmOpen = !fmOpen" style="cursor:pointer;">
                        <div class="m-card-hd-left"><i class="fa-solid fa-dice card-icon"></i>
                            <h3>FiveMillion</h3>
                        </div>
                        <i :class="['fa-solid fa-chevron-right chevron', { open: fmOpen }]"></i>
                    </div>
                    <div v-show="fmOpen" class="m-card-bd">
                        <div class="fm-type-bar">
                            <label :class="{ active: fm.cp === 'ssq' }"
                                @click="fm.cp = 'ssq'; onFmCpChange()">SSQ</label>
                            <label :class="{ active: fm.cp === 'dlt' }"
                                @click="fm.cp = 'dlt'; onFmCpChange()">DLT</label>
                            <label :class="{ active: fm.cp === 'kl8' }"
                                @click="fm.cp = 'kl8'; onFmCpChange()">KL8</label>
                        </div>
                        <div v-show="fm.isLocalVisible" class="fm-row">
                            <span class="fm-label">本地数据（{{ fm.localTotal }}）</span>
                            <el-radio-group v-model="fm.isl" size="small"><el-radio value="yes">是</el-radio><el-radio
                                    value="no">否</el-radio></el-radio-group>
                            <el-button type="danger" plain size="small" @click="showCleanDialog">清空本地</el-button>
                        </div>
                        <div class="fm-gen-row">
                            <span class="fm-label">次数</span>
                            <el-input v-model="fm.nt" type="number" style="width:90px;" />
                            <div class="fm-btn-group">
                                <el-button type="primary" :loading="fm.loading" @click="submitFm">生成</el-button>
                                <el-button @click="resetFm">重置</el-button>
                            </div>
                        </div>
                        <div v-if="fm.result" class="uc-fm-result">{{ fm.result }}</div>
                    </div>
                </div>
            </div>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'
import { useMenuStore } from '../../store/menu'

const EnvRadio = {
    props: ['modelValue', 'name'], emits: ['update:modelValue'],
    template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = {
    props: ['loading', 'submitText'],
    emits: ['reset', 'submit'],
    template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" :loading="loading" @click="$emit('submit')">{{ submitText || '提交' }}</el-button></div>`,
}

const avatarSrc = '../static/img/gzhzy.png'
const rn = ref('')
const lid = ref(0)
const job = ref('')
const urpOpen = ref(true)
const coaOpen = ref(true)
const fmOpen = ref(false)

// 查询职位
async function queryUserInfo() {
    try {
        const resp = await http.post('/pv/usercenter/queryuinfo', { uctype: 'queryuinfo' })
        job.value = resp.data?.data?.job || ''
    } catch (e) { ElMessage.error('查询职位失败') }
}

// 加密
const enc = reactive({ txt: '', jxuid: '', compare: '', result: '', loading: false })
async function encrypt() {
    if (!enc.txt) { ElMessage.warning('输入加密内容！'); return }
    enc.loading = true
    try {
        const resp = await http.post('/pv/usercenter/enc', { txt: enc.txt, jxuid: enc.jxuid, uctype: 'enc' })
        enc.result = resp.data?.data?.encryption || ''
    } catch (e) { ElMessage.error('加密失败') }
    finally { enc.loading = false }
}

// 企业开户
const coa = reactive({ cname: '', loginname: '', passwd: 'a123456', ctype: '7', etime: '2030-12-31', env: 'test', utip: '', cinfo: '', loading: false })
async function submitCoa() {
    if (!coa.cname || !coa.ctype || !coa.etime || !coa.loginname || !coa.passwd) { ElMessage.warning('必填项不能为空！'); return }
    if (isNaN(coa.loginname) || coa.loginname.length !== 11) { ElMessage.warning('登录手机号必须是11位数字！'); return }
    coa.loading = true
    try {
        const resp = await http.post('/pv/usercenter/coa', {
            companyName: coa.cname, companyType: coa.ctype, expireTime: coa.etime, loginName: coa.loginname, password: coa.passwd, env: coa.env, uctype: 'coa',
        })
        const d = resp.data?.data || {}; coa.utip = d.coaTitle || ''; coa.cinfo = d.coaInfo || ''
    } catch (e) { ElMessage.error('操作失败') }
    finally { coa.loading = false }
}

// TP用户增删改
const urp = reactive({ userName: '', account: '', userEmail: '', pwd: '', plant: 'tp', urole: 'normal', oprate: 'registUser', rlt: '', loading: false })
const showUn = computed(() => urp.oprate !== 'modifyRole' && urp.oprate !== 'deleteUser')
const showEmail = computed(() => urp.oprate !== 'deleteUser')
const showPwd = computed(() => urp.oprate !== 'deleteUser')
const showUvs = computed(() => urp.oprate !== 'deleteUser' && urp.oprate !== 'modifyRole')
const showUrole = computed(() => urp.oprate !== 'deleteUser')
function resetUrp() { urp.userName = ''; urp.account = ''; urp.userEmail = ''; urp.pwd = ''; urp.plant = 'tp'; urp.urole = 'normal'; urp.oprate = 'registUser'; urp.rlt = '' }
async function submitUrp() {
    if (!urp.account) { urp.rlt = '账号不能为空！'; return }
    if (urp.oprate === 'registUser') {
        if (urp.pwd.length < 3) { urp.rlt = '密码不能少于3位！'; return }
        if (!urp.userEmail) { urp.rlt = '邮箱不能为空！'; return }
    }
    const ur = urp.plant === 'tp' ? (urp.urole === 'normal' ? '2' : '99') : '2'
    urp.loading = true
    try {
        const resp = await http.post('/pv/registTP', { name: urp.userName, lname: urp.account, email: urp.userEmail, pwd: urp.pwd, plant: urp.plant, ur, oprate: urp.oprate })
        const res = resp.data?.data?.registTestPlant || ''; urp.rlt = res
        if (urp.oprate === 'modifyRole' && res.includes('【isPwdChanged】') && urp.pwd) {
            urp.rlt = res.replace('【isPwdChanged】', '') + '<br/><span style="color:red;">密码已修改，请重新登录。</span>'
            setTimeout(() => { window.location.href = '/logout' }, 1500)
        }
    } catch (e) { urp.rlt = '操作失败' }
    finally { urp.loading = false }
}

// FiveMillion
const fm = reactive({ cp: 'ssq', isl: 'no', nt: '10', result: '', loading: false, localTotal: '', isLocalVisible: true, showCleanDialog: false, cleaning: false, cleanResult: '' })
function onFmCpChange() { fm.isLocalVisible = fm.cp === 'ssq' }
async function getLocalTotal() {
    try { const resp = await http.post('/pv/usercenter/gettotal', { uctype: 'gettotal' }); fm.localTotal = resp.data?.data?.getTotal || '' }
    catch (e) { fm.localTotal = '' }
}
async function submitFm() {
    const nt = parseInt(fm.nt)
    if (!nt || isNaN(nt) || nt <= 0) { ElMessage.warning('输入正整数！'); return }
    if (fm.isl === 'yes' && nt > 100) { fm.result = '输入100及以内的正整数！'; return }
    if (fm.isl === 'no' && nt > 1000000) { fm.result = '输入1000000及以内的正整数！'; return }
    fm.loading = true
    try {
        const resp = await http.post('/pv/usercenter/fm', { nt: fm.nt, cp: fm.cp, isl: fm.isl, uctype: 'fm' })
        fm.result = resp.data?.data?.fiveMillion || ''; getLocalTotal()
    } catch (e) { fm.result = '生成失败' }
    finally { fm.loading = false }
}
function resetFm() { fm.cp = 'ssq'; fm.isl = 'no'; fm.nt = '10'; fm.result = ''; fm.isLocalVisible = true }
function showCleanDialog() {
    if (!fm.localTotal || fm.localTotal === '0') { ElMessage.warning('无数据！'); return }
    fm.cleanResult = ''; fm.cleaning = false; fm.showCleanDialog = true
}
async function cleanLocalData() {
    fm.cleaning = true
    try {
        const resp = await http.post('/pv/usercenter/cld', { uctype: 'cld' })
        fm.cleanResult = resp.data?.data?.cleanLocalData || '清理完成'; fm.result = ''; getLocalTotal()
    } catch (e) { fm.cleanResult = '清理失败' }
    finally { fm.cleaning = false }
}

onMounted(() => { getLocalTotal() })

// menuStore.fetchMenu 是异步的，AppLayout 挂载后发起请求，
// usercenter 的 onMounted 可能先于数据返回，需 watch 等待
const menuStore = useMenuStore()
watch(() => menuStore.loaded, (loaded) => {
    if (loaded) {
        rn.value = menuStore.user?.rn || ''
        lid.value = menuStore.user?.lid || 0
        queryUserInfo()
    }
}, { immediate: true })
</script>

<style scoped>
.mo-page {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    background: var(--bg-page);
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
    color: var(--text-primary);
    letter-spacing: .3px;
}

.page-title i {
    color: var(--color-primary-light);
    margin-right: 4px;
}

.mo-body {
    flex: 1;
    padding: 0 14px 14px;
    overflow: hidden;
    min-height: 0;
    display: flex;
    gap: 12px;
}

.left-col {
    flex: 1;
    min-width: 0;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.left-col::-webkit-scrollbar {
    width: 4px;
}

.left-col::-webkit-scrollbar-track {
    background: transparent;
}

.left-col::-webkit-scrollbar-thumb {
    background: var(--scrollbar-thumb);
    border-radius: 4px;
}

.right-col {
    flex: 1;
    min-width: 0;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
}

.right-col::-webkit-scrollbar {
    width: 4px;
}

.right-col::-webkit-scrollbar-track {
    background: transparent;
}

.right-col::-webkit-scrollbar-thumb {
    background: var(--scrollbar-thumb);
    border-radius: 4px;
}

/* ─── 通用卡片 ─── */
.m-card {
    background: var(--bg-card);
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
    overflow: visible;
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

.m-card-hd-right {
    display: flex;
    align-items: center;
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
    color: var(--text-primary);
    letter-spacing: .2px;
}

.m-card-bd {
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    overflow-y: auto;
    border-top: 1px solid var(--border-card);
}

.m-card-bd::-webkit-scrollbar {
    width: 4px;
}

.m-card-bd::-webkit-scrollbar-track {
    background: transparent;
}

.m-card-bd::-webkit-scrollbar-thumb {
    background: var(--border-light);
    border-radius: 4px;
}

.accent-blue {
    border-left-color: #3b82f6;
}

.accent-blue .card-icon {
    color: #3b82f6;
}

.accent-green {
    border-left-color: #22c55e;
}

.accent-green .card-icon {
    color: #22c55e;
}

.accent-orange {
    border-left-color: #f59e0b;
}

.accent-orange .card-icon {
    color: #f59e0b;
}

.accent-purple {
    border-left-color: #8b5cf6;
}

.accent-purple .card-icon {
    color: #8b5cf6;
}

.m-card.collapsed .m-card-bd {
    display: none;
}

.chevron {
    font-size: 11px;
    color: var(--text-placeholder);
    transition: transform .25s ease;
}

.chevron.open {
    transform: rotate(90deg);
}

/* ─── 个人信息卡 ─── */
.profile-card {
    position: relative;
}

.profile-bg {
    height: 72px;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
    border-radius: 12px 12px 0 0;
}

.profile-body {
    align-items: center;
    padding: 0 18px 20px;
    margin-top: -40px;
    position: relative;
    z-index: 1;
    border-top: none;
}

.uc-avatar {
    margin-bottom: 10px;
}

.uc-avatar__img {
    width: 80px;
    height: 80px;
    border-radius: 9999px;
    border: 4px solid #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .12);
    object-fit: cover;
    background: var(--bg-card);
}

.uc-avatar__placeholder {
    width: 80px;
    height: 80px;
    border-radius: 9999px;
    border: 4px solid #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .12);
    background: var(--border-light);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: var(--text-placeholder);
}

.uc-name {
    display: block;
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    text-align: center;
}

.uc-role {
    display: block;
    font-size: 12px;
    color: var(--text-placeholder);
    margin-top: 2px;
    text-align: center;
    letter-spacing: .3px;
}

.uc-motto {
    text-align: center;
    font-size: 13px;
    color: var(--text-muted);
    line-height: 1.7;
    margin-top: 14px;
    padding: 10px 14px;
    background: var(--bg-subtle);
    border-radius: 8px;
    border: 1px solid var(--border-light);
}

/* ─── 加密工具 ─── */
.enc-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    width: 100%;
}

.enc-hint {
    font-size: 11px;
    color: var(--text-placeholder);
    margin-top: 6px;
    text-align: center;
}

.enc-result {
    margin-top: 10px;
    padding: 8px 12px;
    width: 100%;
    font-size: 13px;
    color: var(--color-primary-light);
    word-break: break-all;
    text-align: center;
    background: var(--bg-active);
    border-radius: 8px;
    border: 1px solid #c7d2fe;
}

/* ─── 表单网格 ─── */
.form-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    column-gap: 14px;
    row-gap: 12px;
    align-items: center;
    width: fit-content;
    margin: 0 auto 12px;
}

.form-grid .fgr {
    display: contents;
}

.form-grid .fgr label {
    text-align: right;
    white-space: nowrap;
    font-size: 13px;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 4px;
}

.form-grid .fgr label::before {
    content: '';
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--color-primary-light);
    flex-shrink: 0;
}

.form-grid .fgr :deep(.el-input),
.form-grid .fgr :deep(.el-select),
.form-grid .fgr :deep(.el-date-editor) {
    width: 100% !important;
    min-width: 140px;
}

/* ─── TP 操作栏（tab-group 样式） ─── */
.urp-op-bar {
    display: inline-flex;
    gap: 0;
    background: var(--bg-hover);
    border-radius: 6px;
    padding: 2px;
    margin-bottom: 14px;
    flex-wrap: nowrap;
}

.urp-op-bar label {
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 16px;
    border-radius: 5px;
    border: none;
    background: transparent;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
    transition: all .2s;
    user-select: none;
    white-space: nowrap;
}

.urp-op-bar label.active {
    background: var(--bg-card);
    color: #f59e0b;
    box-shadow: 0 1px 3px rgba(0, 0, 0, .1);
    font-weight: 600;
}

/* ─── FM 类型栏 ─── */
.fm-type-bar {
    display: inline-flex;
    gap: 0;
    background: var(--bg-hover);
    border-radius: 6px;
    padding: 2px;
    margin-bottom: 12px;
    flex-wrap: nowrap;
}

.fm-type-bar label {
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    padding: 6px 20px;
    border-radius: 5px;
    border: none;
    background: transparent;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-muted);
    transition: all .2s;
    user-select: none;
    white-space: nowrap;
}

.fm-type-bar label.active {
    background: var(--bg-card);
    color: #8b5cf6;
    box-shadow: 0 1px 3px rgba(0, 0, 0, .1);
    font-weight: 600;
}

.fm-row,
.fm-gen-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 6px 0;
    flex-wrap: wrap;
}

.fm-btn-group {
    display: flex;
    gap: 8px;
    flex-shrink: 0;
}

.fm-label {
    font-size: 13px;
    color: var(--text-secondary);
    white-space: nowrap;
}

/* ─── BtnGroup / EnvRadio ─── */
:deep(.btn-group) {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin: 10px 0 12px;
}

:deep(.env-group) {
    display: inline-flex;
    justify-content: center;
    margin: 8px 0;
}

:deep(.env-track) {
    display: inline-flex;
    gap: 0;
    background: var(--bg-hover);
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
    color: var(--text-muted);
    transition: all .2s;
    user-select: none;
    white-space: nowrap;
}

:deep(.env-track label.active) {
    background: var(--bg-card);
    color: var(--color-primary-light);
    box-shadow: 0 1px 3px rgba(0, 0, 0, .1);
    font-weight: 600;
}

:deep(.env-track label i) {
    font-size: 11px;
}

:deep(.env-track input[type="radio"]) {
    display: none;
}

/* ─── 结果区 ─── */
.result-box {
    width: 100%;
    margin-top: 10px;
    padding: 10px 14px;
    border-radius: 8px;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    font-size: 13px;
    text-align: left;
    line-height: 1.7;
    color: #15803d;
    white-space: pre-wrap;
    word-break: break-all;
}

.result-box--error {
    background: #fef2f2;
    border-color: #fecaca;
    color: #dc2626;
}

.result-box:empty {
    display: none;
}

.uc-fm-result {
    width: 100%;
    max-height: 360px;
    overflow-y: auto;
    text-align: left;
    font-size: 13px;
    line-height: 1.7;
    color: var(--text-secondary);
    padding: 10px 14px;
    background: var(--bg-subtle);
    border-radius: 8px;
    border: 1px solid var(--border-light);
    margin-top: 10px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
</style>
