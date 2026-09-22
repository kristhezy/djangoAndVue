<template>
    <div class="mo-page">
        <!-- 顶部工具栏 -->
        <div class="toolbar">
            <div class="toolbar-left">
                <h2 class="page-title"><i class="fa-solid fa-headset"></i> 售后服务</h2>
            </div>
        </div>

        <div class="mo-body">
            <!-- 第一列 -->
            <div class="column">
                <!-- 卡片1: 综合查询 -->
                <div :class="['m-card', { collapsed: !cards.c1 }]">
                    <div class="m-card-hd accent-blue" @click="cards.c1 = !cards.c1">
                        <div class="m-card-hd-left"><i class="fa-solid fa-magnifying-glass card-icon"></i>
                            <h3>综合查询</h3>
                        </div>
                        <i :class="['fa-solid fa-chevron-right chevron', { open: cards.c1 }]"></i>
                    </div>
                    <div class="m-card-bd">
                        <div class="fg">
                            <div class="fgr"><label>{{ c1.queryLabel }}</label><el-input v-model="c1.value"
                                    placeholder="请输入查询参数" />
                            </div>
                            <div class="fgr"><label>查询类型</label>
                                <el-select v-model="c1.sel" placeholder="请选择" @change="onSelChange">
                                    <el-option label="SAAS手机号查询企业ID" value="qcompid" />
                                    <el-option label="基线版手机号查询企业ID" value="oqcompid" />
                                    <el-option label="查询企业微信ID" value="qwwid" />
                                    <el-option label="查询公众号小程序绑定" value="qocbind" />
                                    <el-option label="查询小程序/企微绑定" value="qwappbind" />
                                    <el-option label="根据明文查询密文企微ID" value="qopencorpid" />
                                </el-select>
                            </div>
                        </div>
                        <BtnGroup @reset="reset1" @submit="submit1" submit-text="查询" :loading="c1.loading" />
                        <ResultBox :text="c1.result" :loading="c1.loading" />
                    </div>
                </div>

                <!-- 卡片3: 定制化小程序配置 -->
                <div :class="['m-card', { collapsed: !cards.c3 }]">
                    <div class="m-card-hd accent-green" @click="cards.c3 = !cards.c3">
                        <div class="m-card-hd-left"><i class="fa-solid fa-puzzle-piece card-icon"></i>
                            <h3>定制化小程序配置</h3>
                        </div>
                        <i :class="['fa-solid fa-chevron-right chevron', { open: cards.c3 }]"></i>
                    </div>
                    <div class="m-card-bd">
                        <div class="fg">
                            <div class="fgr"><label>企业ID</label><el-input v-model="c3.cid" placeholder="请输入企业ID" />
                            </div>
                            <div class="fgr"><label>小程序ID</label><el-input v-model="c3.appletCorpId"
                                    placeholder="请输入小程序ID" /></div>
                            <div class="fgr"><label>SECRET</label><el-input v-model="c3.secretKey"
                                    placeholder="请输入Secret" /></div>
                        </div>
                        <div class="radio-group">
                            <el-radio-group v-model="c3.applet" size="small">
                                <el-radio value="dz">转介绍3.0</el-radio>
                                <el-radio value="zs">Saleskits</el-radio>
                                <el-radio value="org">基线版</el-radio>
                            </el-radio-group>
                        </div>
                        <div class="check-row">
                            <el-checkbox v-model="c3.istest">测试环境</el-checkbox>
                        </div>
                        <BtnGroup @reset="reset3" @submit="submit3" :loading="c3.loading" />
                        <ResultBox :text="c3.result" :loading="c3.loading" />
                    </div>
                </div>
            </div>

            <!-- 第二列 -->
            <div class="column">
                <!-- 卡片2: 配置隐私保护 -->
                <div :class="['m-card', { collapsed: !cards.c2 }]">
                    <div class="m-card-hd accent-orange" @click="cards.c2 = !cards.c2">
                        <div class="m-card-hd-left"><i class="fa-solid fa-shield-halved card-icon"></i>
                            <h3>配置隐私保护</h3>
                        </div>
                        <i :class="['fa-solid fa-chevron-right chevron', { open: cards.c2 }]"></i>
                    </div>
                    <div class="m-card-bd">
                        <div class="fg">
                            <div class="fgr"><label>企业ID</label><el-input v-model="c2.cid" placeholder="请输入企业ID" />
                            </div>
                        </div>
                        <BtnGroup @reset="reset2" @submit="submit2" :loading="c2.loading" />
                        <ResultBox :text="c2.result" :loading="c2.loading" />
                    </div>
                </div>

                <!-- 卡片4: 绑定企业和企微加密corpid -->
                <div :class="['m-card', { collapsed: !cards.c4 }]">
                    <div class="m-card-hd accent-purple" @click="cards.c4 = !cards.c4">
                        <div class="m-card-hd-left"><i class="fa-solid fa-link card-icon"></i>
                            <h3>绑定企业和企微加密corpid</h3>
                        </div>
                        <i :class="['fa-solid fa-chevron-right chevron', { open: cards.c4 }]"></i>
                    </div>
                    <div class="m-card-bd">
                        <div class="fg">
                            <div class="fgr"><label>企业ID</label><el-input v-model="c4.cid" placeholder="请输入企业ID" />
                            </div>
                            <div class="fgr"><label>企微ID</label><el-input v-model="c4.corpId" placeholder="请输入企微ID" />
                            </div>
                        </div>
                        <BtnGroup @reset="reset4" @submit="submit4" :loading="c4.loading" />
                        <ResultBox :text="c4.result" :loading="c4.loading" />
                    </div>
                </div>
            </div>

            <!-- 第三列 -->
            <div class="column">
                <!-- 卡片5: 激活注销手机号 -->
                <div :class="['m-card', { collapsed: !cards.c5 }]">
                    <div class="m-card-hd accent-red" @click="cards.c5 = !cards.c5">
                        <div class="m-card-hd-left"><i class="fa-solid fa-phone card-icon"></i>
                            <h3>激活注销手机号</h3>
                        </div>
                        <i :class="['fa-solid fa-chevron-right chevron', { open: cards.c5 }]"></i>
                    </div>
                    <div class="m-card-bd">
                        <div class="fg">
                            <div class="fgr"><label>手机号码</label><el-input v-model="c5.tel" placeholder="请输入手机号"
                                    maxlength="11" />
                            </div>
                        </div>
                        <BtnGroup @reset="reset5" @submit="submit5" submit-text="激活" :loading="c5.loading" />
                        <ResultBox :text="c5.result" :loading="c5.loading" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const warn = (msg) => ElMessage({ message: msg, type: 'warning', duration: 2500 })

// --- Inline sub-components ---
const BtnGroup = {
    props: ['loading', 'submitText'],
    emits: ['reset', 'submit'],
    template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" :loading="loading" @click="$emit('submit')">{{ submitText || '提交' }}</el-button></div>`,
}
const ResultBox = {
    props: ['text', 'loading'],
    template: `<div class="result"><span v-if="loading" class="result-loading"><i class="fa-solid fa-spinner fa-spin"></i> 加载中...</span><span v-else v-html="text||''"></span></div>`,
}

// --- Card collapse state ---
const cards = reactive({ c1: true, c2: true, c3: true, c4: true, c5: true })

// --- 卡片1: 综合查询 ---
const c1 = reactive({ value: '', sel: 'qcompid', queryLabel: '登录账号', result: '', loading: false })
function onSelChange() {
    const v = c1.sel
    if (v === 'qopencorpid') c1.queryLabel = '明文ID'
    else if (v === 'qcompid') c1.queryLabel = '登录账号'
    else c1.queryLabel = '企业ID'
}
async function submit1() {
    if (!c1.value.trim()) { warn('查询参数不能为空！'); return }
    if (!c1.sel) { warn('查询类型不能为空！'); return }
    if (c1.sel === 'qcompid' || c1.sel === 'oqcompid') {
        if (c1.value.length !== 11) { warn('请输入正确的手机号！'); return }
        const sysvs = c1.sel === 'qcompid' ? 'saas' : 'origin'
        c1.loading = true
        try {
            const resp = await http.post(`/sv/querycompid/${sysvs}`, { ln: c1.value, env: 'prod' })
            const d = resp.data?.data || {}
            if (!d.cn && !d.cid) {
                c1.result = '无企业信息'
            } else {
                c1.result = `${d.cn || ''} (${d.cid || ''})`
            }
        } catch (e) {
            ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
        } finally { c1.loading = false }
        return
    }
    const apiMap = { qwwid: '/sv/queryci', qocbind: '/sv/queryca', qwappbind: '/sv/queryaal', qopencorpid: '/sv/querySCID' }
    const api = apiMap[c1.sel]
    if (!api) return
    c1.loading = true
    try {
        const resp = await http.post(api, { companyId: c1.value, env: 'prod' })
        c1.result = resp.data?.data || ''
    } catch (e) {
        ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
    } finally { c1.loading = false }
}
function reset1() { c1.value = ''; c1.sel = 'qcompid'; c1.queryLabel = '登录账号'; c1.result = '' }

// --- 卡片2: 配置隐私保护 ---
const c2 = reactive({ cid: '', result: '', loading: false })
async function submit2() {
    if (!c2.cid.trim()) { warn('企业id不能为空！'); return }
    if (c2.cid.length < 18) { warn('企业id不能少于18位！'); return }
    if (!/^\d+$/.test(c2.cid)) { warn('企业id只能是纯数字！'); return }
    c2.loading = true
    try {
        const resp = await http.post('/sv/privset', { companyId: c2.cid })
        c2.result = resp.data?.data || ''
    } catch (e) {
        ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
    } finally { c2.loading = false }
}
function reset2() { c2.cid = ''; c2.result = '' }

// --- 卡片3: 定制化小程序配置 ---
const c3 = reactive({ cid: '', appletCorpId: '', secretKey: '', applet: 'zs', istest: false, result: '', loading: false })
async function submit3() {
    if (!c3.cid) { warn('企业id不能为空！'); return }
    if (!c3.appletCorpId) { warn('小程序id不能为空！'); return }
    if (!c3.secretKey) { warn('secretKey不能为空！'); return }
    if (c3.applet === 'zs' || c3.applet === 'dz') {
        if (c3.cid.length < 18) { warn('企业id不能少于18位！'); return }
    }
    if (!/^\d+$/.test(c3.cid)) { warn('企业id只能是纯数字！'); return }
    c3.loading = true
    try {
        const resp = await http.post('/sv/dzapplet', { companyId: c3.cid, corpId: c3.appletCorpId, secretKey: c3.secretKey, applet: c3.applet, istest: c3.istest })
        c3.result = resp.data?.data || ''
    } catch (e) {
        ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
    } finally { c3.loading = false }
}
function reset3() { c3.cid = ''; c3.appletCorpId = ''; c3.secretKey = ''; c3.applet = 'zs'; c3.istest = false; c3.result = '' }

// --- 卡片4: 绑定企业和企微加密corpid ---
const c4 = reactive({ cid: '', corpId: '', result: '', loading: false })
async function submit4() {
    if (!c4.cid) { warn('企业id不能为空！'); return }
    if (!c4.corpId) { warn('corpId不能为空！'); return }
    c4.loading = true
    try {
        const resp = await http.post('/sv/selfcreatedCS', { companyId: c4.cid, corpId: c4.corpId })
        c4.result = resp.data?.data || ''
    } catch (e) {
        ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
    } finally { c4.loading = false }
}
function reset4() { c4.cid = ''; c4.corpId = ''; c4.result = '' }

// --- 卡片5: 激活注销手机号 ---
const c5 = reactive({ tel: '', result: '', loading: false })
async function submit5() {
    if (c5.tel.length !== 11) { warn('手机号只能是11位！'); return }
    if (!/^\d+$/.test(c5.tel)) { warn('手机号只能是纯数字！'); return }
    c5.loading = true
    try {
        const resp = await http.post('/sv/removeTagTel', { phoneNumber: c5.tel, env: 'prod' })
        c5.result = resp.data?.data || ''
    } catch (e) {
        ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
    } finally { c5.loading = false }
}
function reset5() { c5.tel = ''; c5.result = '' }

onMounted(() => { })
</script>

<style scoped>
/* ===================== 页面骨架 ===================== */
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
    display: flex;
    gap: 12px;
    padding: 0 12px 12px;
    flex: 1;
    overflow: hidden;
    min-height: 0;
    ;
}

.column {
    display: flex;
    flex-direction: column;
    gap: 12px;
    flex: 1;
    min-width: 240px;
    overflow-y: auto;
    height: 100%;
    padding: 2px;
}

.column::-webkit-scrollbar {
    width: 4px;
}

.column::-webkit-scrollbar-track {
    background: transparent;
}

.column::-webkit-scrollbar-thumb {
    background: var(--scrollbar-thumb);
    border-radius: 4px;
}

.column::-webkit-scrollbar-thumb:hover {
    background: var(--scrollbar-thumb-hover);
}

/* ===================== 卡片 ===================== */
.m-card {
    background: var(--bg-card);
    border-radius: 12px;
    flex-shrink: 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
    overflow: hidden;
    transition: box-shadow .2s;
}

.m-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, .08), 0 2px 4px rgba(0, 0, 0, .04);
}

.m-card-hd {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 18px;
    cursor: pointer;
    user-select: none;
    border-left: 4px solid transparent;
    transition: background .15s;
}

.m-card-hd:hover {
    background: var(--bg-hover);
}

.m-card-hd-left {
    display: flex;
    align-items: center;
    gap: 10px;
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

.chevron {
    font-size: 11px;
    color: var(--text-placeholder);
    transition: transform .25s ease;
}

.chevron.open {
    transform: rotate(90deg);
}

.m-card.collapsed .m-card-bd {
    display: none;
}

.m-card-bd {
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    align-items: center;
    border-top: 1px solid var(--border-card);
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

.accent-red {
    border-left-color: #ef4444;
}

.accent-red .card-icon {
    color: #ef4444;
}

/* ===================== 表单 Grid ===================== */
.fg {
    display: grid;
    grid-template-columns: auto minmax(120px, 300px);
    column-gap: 12px;
    row-gap: 12px;
    align-items: center;
    width: fit-content;
    margin: 0 auto;
}

.fgr {
    display: contents;
}

.fgr label {
    text-align: left;
    white-space: nowrap;
    font-size: 13px;
    color: var(--text-secondary);
}

.fgr :deep(.el-input),
.fgr :deep(.el-select) {
    width: 100% !important;
}

/* ===================== 按钮 ===================== */
:deep(.btn-group) {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin: 10px 0 12px;
}

/* ===================== 结果区 ===================== */
.result {
    width: 100%;
    min-height: 32px;
    max-height: 160px;
    overflow-y: auto;
    padding: 10px 14px;
    border-radius: 8px;
    background: var(--bg-subtle);
    font-size: 13px;
    text-align: center;
    line-height: 1.7;
    color: var(--text-secondary);
    word-wrap: break-word;
    word-break: break-all;
    white-space: pre-wrap;
}

.result:empty {
    display: none;
}

.result-loading {
    color: var(--color-primary-light);
    font-weight: 500;
}

.result-loading i {
    margin-right: 4px;
}

/* ===================== 杂项 ===================== */
.radio-group {
    display: flex;
    justify-content: center;
    margin: 10px auto 8px;
}

.check-row {
    display: flex;
    justify-content: center;
    margin-bottom: 8px;
}
</style>
