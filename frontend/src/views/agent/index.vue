<template>
  <div class="ag-page">
    <div class="ag-side">
      <div class="side-hd">
        <el-button class="btn-newchat" @click="newChat">＋ 新会话</el-button>
        <div class="side-label">历史会话</div>
      </div>
      <div class="side-list">
        <div
          v-for="h in historyList"
          :key="h.id"
          :class="['hht', { active: h.id === chatId }]"
        >
          <span class="tit" @click="switchChat(h.id)">{{ h.title }}</span>
          <span class="del-btn" @click.stop="delHistory(h.id)">✕</span>
        </div>
      </div>
    </div>

    <div class="ag-card">
      <div class="ag-hd">
        🤖 Agent
        <span class="tag">项目专属助手 · 企业/用户查询 · 联网搜索 · 日志分析</span>
      </div>

      <div class="chat-area" ref="containerRef">
        <div v-if="qaList.length === 0" class="welcome">
          你好，我是 Agent 🤖<br>
          可以帮你查企业/用户信息、联网搜索、分析报错日志
        </div>
        <div v-for="(qa, qi) in qaList" :key="qi" class="qa-block">
          <div class="msg-row user">
            <div class="msg-body">{{ qa.ask }}</div>
          </div>
          <div class="msg-row assistant">
            <div class="msg-body" v-html="renderMd(qa.answer)"></div>
          </div>
        </div>

        <!-- streaming / loading -->
        <div v-if="stream.ask" class="qa-block">
          <div class="msg-row user">
            <div class="msg-body">{{ stream.ask }}</div>
          </div>
          <div class="msg-row assistant">
            <div class="msg-body" :class="{ 'no-bubble': !stream.started }">
              <template v-if="!stream.started">
                <span style="display: flex; align-items: center; gap: 10px; color: #2c5cc5; font-size: 13px;">
                  <i class="fa-solid fa-hourglass"></i> AI 正在处理，请稍候
                </span>
              </template>
              <template v-else>
                <div v-if="stream.statusMsg" class="status-banner" :class="{ done: stream.done }">
                  <span v-html="stream.statusMsg"></span>
                </div>
                <div v-if="stream.logs.length > 0" class="stream-logs">
                  <details v-for="(log, li) in stream.logs" :key="li"
                    :class="['log-item', { 'log-result': log.step === 'tool_result' }]">
                    <summary v-if="log.step === 'tool_call'">🔧 调用工具 {{ log.tool }}</summary>
                    <summary v-else-if="log.step === 'tool_result'">✅ 工具 {{ log.tool }} 返回</summary>
                    <pre>{{ log.step === 'tool_call' ? formatJSON(log.args) : log.result }}</pre>
                  </details>
                </div>
                <span v-html="renderMd(stream.text)"></span>
                <span v-if="!stream.done" class="stream-cursor"> ▌</span>
              </template>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-foot">
        <div class="input-wrap">
          <div
            class="input-editor"
            contenteditable="true"
            ref="editorRef"
            @keydown.enter.exact.prevent="submitAsk"
            data-placeholder="输入问题… 支持查企业/用户信息、联网搜索、分析日志"
          ></div>
          <el-button v-if="streaming" class="btn-stop" circle size="small" @click="stopStream" title="停止生成">
            <el-icon><i class="fa-solid fa-stop"></i></el-icon>
          </el-button>
          <el-button class="btn-send" type="primary" circle @click="submitAsk" :disabled="streaming" title="发送 (Enter)">
            <el-icon><i class="fa-solid fa-arrow-up"></i></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 右侧链接抽屉 -->
    <Teleport to="body">
      <div v-if="drawerVisible" class="drawer-mask" @click="closeDrawer"></div>
      <div :class="['drawer', { show: drawerVisible }]">
        <div class="drawer-hd">
          <el-button text @click="closeDrawer" title="关闭">✕</el-button>
          <span class="drawer-title">{{ drawerUrl }}</span>
          <el-button text @click="openInNewTab" title="在新窗口打开">↗ 新窗口打开</el-button>
        </div>
        <div class="drawer-body">
          <iframe v-if="drawerUrl" class="drawer-iframe" :src="drawerUrl"></iframe>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue'
import http from '../../api/http.js'
import { marked } from 'marked'

marked.setOptions({ breaks: true, gfm: true })

const containerRef = ref(null)
const editorRef = ref(null)

const historyList = ref([])
const chatId = ref(0)
const qaList = ref([])
const streaming = ref(false)
const drawerVisible = ref(false)
const drawerUrl = ref('')

const stream = reactive({
  ask: '',
  started: false,
  statusMsg: '',
  text: '',
  logs: [],
  done: false,
})

let abortCtrl = null

function renderMd(text) {
  if (!text) return ''
  try { return marked.parse(text) }
  catch { return escapeHTML(text).replace(/\n/g, '<br>') }
}

function formatJSON(v) {
  if (!v) return ''
  try { return JSON.stringify(v, null, 2) } catch { return String(v) }
}

function escapeHTML(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function scrollToBottom() {
  nextTick(() => {
    if (containerRef.value) containerRef.value.scrollTop = containerRef.value.scrollHeight
  })
}

async function submitAsk() {
  if (streaming.value) return
  const text = (editorRef.value?.innerText || '').trim()
  if (!text) return

  streaming.value = true
  if (editorRef.value) editorRef.value.innerHTML = ''

  Object.assign(stream, { ask: text, started: false, statusMsg: '', text: '', logs: [], done: false })
  scrollToBottom()

  abortCtrl = new AbortController()
  let textBuf = ''

  try {
    const resp = await fetch('/pv/agent/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': http.getCSRF() },
      body: JSON.stringify({ input: text, id: chatId.value || 0 }),
      signal: abortCtrl.signal,
    })

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const parts = buf.split('\n\n')
      buf = parts.pop()
      for (const p of parts) {
        if (!p.startsWith('data: ')) continue
        const ds = p.slice(6)
        if (!ds || ds === '[DONE]') continue
        let ev
        try { ev = JSON.parse(ds) } catch { continue }

        if (ev.type === 'start') {
          stream.started = true
        } else if (ev.type === 'status') {
          if (ev.content === 'thinking') {
            stream.statusMsg = '💭 分析中<span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span>'
          } else if (ev.content.startsWith('调用工具')) {
            stream.statusMsg = '🔧 ' + escapeHTML(ev.content) + '…'
          } else {
            stream.statusMsg = escapeHTML(ev.content)
          }
        } else if (ev.type === 'log') {
          try {
            const d = JSON.parse(ev.content)
            if (d && (d.step === 'tool_call' || d.step === 'tool_result')) {
              stream.logs.push(d)
            }
          } catch { /* skip */ }
        } else if (ev.type === 'text') {
          textBuf += ev.content
          stream.text = textBuf
        } else if (ev.type === 'done') {
          if (ev.id) chatId.value = ev.id
          stream.done = true
          qaList.value.push({ ask: text, answer: textBuf })
          Object.assign(stream, { ask: '', started: false, statusMsg: '', text: '', logs: [], done: false })
          loadHistory()
        } else if (ev.type === 'error') {
          qaList.value.push({ ask: text, answer: '❌ ' + ev.content })
          Object.assign(stream, { ask: '', started: false, statusMsg: '', text: '', logs: [], done: false })
        }
      }
      scrollToBottom()
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      if (stream.started) {
        qaList.value.push({ ask: text, answer: textBuf || '⏹ 已停止' })
      }
      Object.assign(stream, { ask: '', started: false, statusMsg: '', text: '', logs: [], done: false })
    } else {
      console.error('agent stream err:', err)
      if (stream.started && textBuf) {
        qaList.value.push({ ask: text, answer: textBuf })
      }
      Object.assign(stream, { ask: '', started: false, statusMsg: '', text: '', logs: [], done: false })
    }
  } finally {
    streaming.value = false
    abortCtrl = null
  }
}

function stopStream() {
  if (abortCtrl) abortCtrl.abort()
}

function loadHistory() {
  http.post('/pv/agent/history', { type: 'gethishh' })
    .then(res => {
      const raw = res.data?.data
      historyList.value = Array.isArray(raw) ? raw : Object.values(raw || {})
    })
    .catch(err => console.log('loadHistory err:', err))
}

function switchChat(id) {
  if (id === chatId.value) return
  const item = historyList.value.find(h => h.id === id)
  if (!item) return
  chatId.value = id
  try {
    const arr = JSON.parse(item.content)
    qaList.value = Array.isArray(arr) ? arr.map(c => ({ ask: c.ask, answer: c.answer })) : []
  } catch {
    qaList.value = []
  }
  scrollToBottom()
  loadHistory()
}

function delHistory(id) {
  http.post('/pv/agent/history', { type: 'delhistory', id })
    .then(() => {
      if (id === chatId.value) { chatId.value = 0; qaList.value = [] }
      loadHistory()
    })
    .catch(err => console.log('delHistory err:', err))
}

function newChat() {
  chatId.value = 0
  qaList.value = []
  if (editorRef.value) editorRef.value.innerHTML = ''
  loadHistory()
}

function openDrawer(url) {
  if (!url) return
  drawerUrl.value = url
  drawerVisible.value = true
}
function closeDrawer() {
  drawerVisible.value = false
  drawerUrl.value = ''
}
function openInNewTab() {
  if (drawerUrl.value) window.open(drawerUrl.value, '_blank')
}

// 拦截回答里的链接点击（右侧抽屉打开）
function handleChatClick(e) {
  const a = e.target.closest('a')
  if (!a) return
  const href = a.getAttribute('href')
  if (!href || href.startsWith('#')) return
  e.preventDefault()
  openDrawer(href)
}

onMounted(() => {
  loadHistory()
  containerRef.value?.addEventListener('click', handleChatClick)
})
</script>

<style scoped>
.ag-page { width: 100%; height: 100%; display: flex; padding: 12px; background: #f0f2f5; gap: 12px; }

.ag-side {
  width: 220px; flex-shrink: 0; display: flex; flex-direction: column;
  background: #fff; border-radius: 14px; box-shadow: 0 2px 12px rgba(0,0,0,.08); overflow: hidden;
}
.side-hd { padding: 14px 14px 10px; border-bottom: 1px solid #f0f0f0; }
.btn-newchat { width: 100%; }
.side-label { margin-top: 10px; font-size: 12px; color: #999; }
.side-list { flex: 1; overflow-y: auto; padding: 8px; }
.side-list::-webkit-scrollbar { width: 5px; }
.side-list::-webkit-scrollbar-thumb { background: #d9d9d9; border-radius: 5px; }

.hht {
  display: flex; align-items: center; gap: 6px; padding: 8px 10px; border-radius: 8px;
  cursor: pointer; font-size: 13px; color: #333; margin-bottom: 2px;
}
.hht:hover { background: #f5f5f5; }
.hht.active { background: #eef1fe; color: #4f6ef7; }
.hht .tit { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hht .del-btn { color: #bbb; font-size: 12px; flex-shrink: 0; padding: 2px 4px; border-radius: 4px; }
.hht .del-btn:hover { color: #ff4d4f; background: #fff0f0; }

.ag-card {
  flex: 1; display: flex; flex-direction: column; border-radius: 14px;
  background: #fff; box-shadow: 0 2px 12px rgba(0,0,0,.08); overflow: hidden; min-width: 0;
}
.ag-hd {
  padding: 12px 20px; border-bottom: 1px solid #f0f0f0;
  font-size: 15px; font-weight: 600; color: #333; display: flex; align-items: center; gap: 8px;
}
.ag-hd .tag {
  font-size: 12px; font-weight: 400; color: #999;
  background: #f5f5f5; padding: 2px 8px; border-radius: 10px;
}

.chat-area {
  flex: 1; overflow-y: auto; padding: 20px 24px; display: flex;
  flex-direction: column; align-items: center; gap: 24px;
}
.chat-area::-webkit-scrollbar { width: 5px; }
.chat-area::-webkit-scrollbar-thumb { background: #d9d9d9; border-radius: 5px; }

.qa-block { width: 800px; max-width: 100%; background: #fff; border-radius: 12px; padding: 16px 20px; box-shadow: 0 1px 4px rgba(0,0,0,.05); }
.msg-row { display: flex; }
.msg-row + .msg-row { margin-top: 14px; }
.msg-row.user { justify-content: flex-end; }
.msg-body { flex: 1; min-width: 0; line-height: 1.72; overflow-wrap: break-word; word-break: break-word; }
.msg-body:not(.no-bubble) { padding: 10px 14px; border-radius: 10px; }
.msg-row.user .msg-body:not(.no-bubble) { flex: 0 1 auto; text-align: left; background: #1a1a1a; color: #fff; }
.msg-row.assistant .msg-body:not(.no-bubble) { background: #f7f7f8; }

.welcome { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #aaa; font-size: 20px; }

.status-banner { font-size: 13px; color: #2c5cc5; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
.status-banner.done { display: none; }

:deep(.stream-cursor) { color: #4f6ef7; animation: blink 1s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }

:deep(.loading-dot) {
  display: inline-block; width: 5px; height: 5px; margin-left: 3px;
  border-radius: 50%; background: #4f6ef7; vertical-align: middle;
  animation: dot-bounce 1.2s infinite ease-in-out;
}
:deep(.loading-dot:nth-child(2)) { animation-delay: .2s; }
:deep(.loading-dot:nth-child(3)) { animation-delay: .4s; }
@keyframes dot-bounce { 0%, 80%, 100% { transform: scale(0); opacity: .3; } 40% { transform: scale(1); opacity: 1; } }

/* 执行日志流 */
.stream-logs { margin: 4px 0 8px; display: flex; flex-direction: column; gap: 4px; }
:deep(.log-item) { border: 1px solid #eee; border-radius: 6px; font-size: 12px; background: #fafafa; overflow: hidden; }
:deep(.log-item summary) {
  cursor: pointer; padding: 5px 10px; color: #555; user-select: none;
  list-style: none; display: flex; align-items: center; gap: 6px;
}
:deep(.log-item summary::-webkit-details-marker) { display: none; }
:deep(.log-item summary:hover) { background: #f0f0f0; }
:deep(.log-item summary::before) { content: '▸'; color: #999; transition: transform .15s; flex-shrink: 0; }
:deep(.log-item[open] summary::before) { transform: rotate(90deg); }
:deep(.log-item pre) {
  margin: 0; padding: 8px 10px; border-top: 1px solid #eee; background: #fff;
  overflow: auto; white-space: pre-wrap; word-break: break-all; font-size: 12px;
  color: #666; max-height: 200px;
}
:deep(.log-item.log-result summary) { color: #2e7d32; }

/* Markdown 排版 */
:deep(.msg-body h1), :deep(.msg-body h2), :deep(.msg-body h3) { margin: .5em 0 .25em; }
:deep(.msg-body h2) { font-size: 1.15em; border-bottom: 1px solid #e8e8e8; padding-bottom: 3px; }
:deep(.msg-body h3) { font-size: 1.05em; }
:deep(.msg-body p) { margin: .35em 0; }
:deep(.msg-body ul), :deep(.msg-body ol) { padding-left: 1.4em; margin: .25em 0; }
:deep(.msg-body pre) {
  background: #2d2d2d; color: #e8e8e8; padding: 12px 14px; border-radius: 8px;
  overflow-x: auto; font-size: 13px; line-height: 1.45; margin: 6px 0;
  white-space: pre-wrap; word-break: break-all;
}
:deep(.msg-body code) { background: rgba(0,0,0,.05); padding: 2px 5px; border-radius: 3px; font-size: .88em; }
:deep(.msg-body pre code) { background: none; padding: 0; }
:deep(.msg-body blockquote) { border-left: 3px solid #ccc; padding-left: 10px; color: #666; margin: 6px 0; }
:deep(.msg-body table) { border-collapse: collapse; margin: 6px 0; width: 100%; }
:deep(.msg-body th), :deep(.msg-body td) { border: 1px solid #ddd; padding: 5px 8px; text-align: left; }
:deep(.msg-body a) { color: #4f6ef7; }
:deep(.msg-row.user .msg-body code) { background: rgba(255,255,255,.15); color: #fff; }
:deep(.msg-row.user .msg-body pre) { background: #444; color: #ddd; }
:deep(.msg-row.user .msg-body a) { color: #aac4ff; }

/* 输入区 */
.chat-foot { padding: 10px 20px 16px; display: flex; justify-content: center; border-top: 1px solid #f0f0f0; }
.input-wrap {
  width: 100%; max-width: 800px; display: flex; align-items: flex-end; gap: 8px;
  border: 1px solid #e0e0e0; border-radius: 12px; padding: 10px 12px;
  background: #fafafa; transition: border-color .2s;
}
.input-wrap:focus-within { border-color: #4f6ef7; box-shadow: 0 0 0 2px rgba(79,110,247,.1); }
.input-editor {
  flex: 1; border: 0; outline: none; font-size: 14px; line-height: 1.5; margin: 5px 0;
  max-height: 140px; overflow-y: auto; word-break: break-word;
}
.input-editor:empty::before { content: attr(data-placeholder); color: #aaa; }
.btn-send { background: #4f6ef7 !important; border-color: #4f6ef7 !important; }
.btn-stop { margin-right: 0; }

/* 右侧抽屉 */
.drawer-mask { position: fixed; inset: 0; background: rgba(0,0,0,.3); z-index: 999; }
.drawer {
  position: fixed; top: 0; right: 0; width: 62%; height: 100%; z-index: 1000;
  background: #fff; box-shadow: -4px 0 20px rgba(0,0,0,.15);
  display: flex; flex-direction: column; transform: translateX(100%);
  transition: transform .22s ease;
}
.drawer.show { transform: translateX(0); }
.drawer-hd { display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-bottom: 1px solid #f0f0f0; }
.drawer-title { flex: 1; font-size: 14px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.drawer-body { flex: 1; position: relative; }
.drawer-iframe { width: 100%; height: 100%; border: 0; }
</style>
