<template>
  <div class="at-page">
    <!-- 左侧：聊天区 -->
    <div class="at-chat">
      <div class="at-chat__hd">AI 对话</div>
      <div class="at-chat__area" ref="chatArea">
        <div v-if="welcome" class="at-welcome">欢迎来到AI的世界</div>
        <div v-for="(qa, idx) in messages" :key="idx" class="at-qa">
          <div class="at-msg at-msg--user">
            <div class="at-msg-body at-msg-body--user">
              {{ qa.ask }}
              <img v-if="qa.image" :src="qa.image" class="at-msg-img" @click="openLightbox(qa.image)" />
            </div>
          </div>
          <div class="at-actions at-actions--user">
            <button class="at-act-btn" @click="reAsk(qa)" title="重新提问">
              <el-icon><RefreshRight /></el-icon>
            </button>
            <button class="at-act-btn" @click="copyText(qa.ask)" title="复制">
              <el-icon><DocumentCopy /></el-icon>
            </button>
          </div>
          <div class="at-msg at-msg--assistant">
            <div class="at-msg-body">
              <details v-if="qa.thinking" class="at-thinking">
                <summary>💭 思考过程</summary>
                <div class="at-thinking-content" v-html="renderMd(qa.thinking)"></div>
              </details>
              <div v-html="renderMd(qa.answer)"></div>
            </div>
          </div>
          <div class="at-actions">
            <button class="at-act-btn" @click="copyText(qa.answer)" title="复制">
              <el-icon><DocumentCopy /></el-icon>
            </button>
          </div>
        </div>
        <div v-if="streaming" class="at-qa">
          <div class="at-msg at-msg--user">
            <div class="at-msg-body at-msg-body--user">{{ currentAsk }}</div>
          </div>
          <div class="at-msg at-msg--assistant">
            <div class="at-msg-body at-msg-body--streaming">
              <details v-if="streamThinking" class="at-thinking">
                <summary>💭 思考过程</summary>
                <div class="at-thinking-content" v-html="renderMd(streamThinking)"></div>
              </details>
              <div v-if="streamStatus" class="at-stream-status">{{ streamStatus }}</div>
              <div v-html="renderMd(streamText)"></div>
              <span class="at-stream-cursor">▌</span>
            </div>
          </div>
        </div>
        <div v-if="loading && !streaming" class="at-qa">
          <div class="at-msg at-msg--user">
            <div class="at-msg-body at-msg-body--user">{{ currentAsk }}</div>
          </div>
          <div class="at-msg at-msg--assistant">
            <div class="at-msg-body">
              <span class="at-loading-dots">
                <span class="at-dot"></span>
                <span class="at-dot"></span>
                <span class="at-dot"></span>
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="at-chat__foot">
        <div class="at-input-wrap">
          <input type="file" ref="fileInput" accept="image/*" style="display:none" @change="handleFileSelect" />
          <el-input v-model="askText" type="textarea" :rows="2" :autosize="{ minRows: 2, maxRows: 6 }"
            placeholder="输入问题… 支持粘贴图片" @keydown.enter.exact.prevent="submitAsk" />
          <div class="at-input-toolbar">
            <div class="at-left-btns">
              <el-button text @click="$refs.fileInput.click()" title="上传图片">
                <el-icon><Picture /></el-icon>
              </el-button>
              <img v-if="pendingImage" :src="pendingImage" class="at-pending-img" @click="pendingImage = ''" />
            </div>
            <div class="at-right-btns">
              <el-button v-if="streaming" circle @click="stopStream" title="停止">■</el-button>
              <el-button v-else type="primary" circle @click="submitAsk" :disabled="!askText.trim() && !pendingImage" title="发送">↑</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：历史记录 -->
    <div class="at-side">
      <div class="at-side__hd">
        <div class="at-side__logo">七进七出</div>
        <el-button class="at-newchat" @click="newChat">＋ 新对话</el-button>
        <div class="at-side__label">历史对话</div>
      </div>
      <div class="at-side__list">
        <div v-for="h in historyList" :key="h.id" class="at-hht" :class="{ active: h.id === chatId }"
          @click="switchChat(h)">
          <span class="at-hht__tit">{{ h.title }}</span>
          <el-button class="at-hht__del" text type="danger" @click.stop="delHistory(h)" title="删除">✕</el-button>
        </div>
      </div>
    </div>

    <!-- 图片光箱 -->
    <div v-if="lightboxSrc" class="at-lightbox" @click="lightboxSrc = ''">
      <el-icon class="at-lightbox__close" @click="lightboxSrc = ''"><Close /></el-icon>
      <img :src="lightboxSrc" @click.stop />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { RefreshRight, DocumentCopy, Picture, Close } from '@element-plus/icons-vue'
import http from '../../api/http'
import { marked } from 'marked'

marked.setOptions({ breaks: true, gfm: true })

const chatArea = ref(null)
const fileInput = ref(null)

const chatId = ref(0)
const messages = ref([])
const welcome = ref(false)
const loading = ref(false)
const streaming = ref(false)
const currentAsk = ref('')
const streamText = ref('')
const streamThinking = ref('')
const streamStatus = ref('')
const pendingImage = ref('')
const askText = ref('')
const lightboxSrc = ref('')
const historyList = ref([])

let abortCtrl = null

function renderMd(text) {
  if (!text) return ''
  try {
    return marked.parse(text)
  } catch (e) {
    return text.replace(/\n/g, '<br>')
  }
}

function openLightbox(src) {
  lightboxSrc.value = src
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('复制成功')
  })
}

function reAsk(qa) {
  askText.value = qa.ask
  if (qa.image) pendingImage.value = qa.image
  submitAsk()
}

function scrollToBottom() {
  nextTick(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight
    }
  })
}

async function compressImage(file, maxW = 1024, maxKB = 500) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      let w = img.width, h = img.height
      if (w > maxW) { h = Math.round(h * maxW / w); w = maxW }
      const canvas = document.createElement('canvas')
      canvas.width = w; canvas.height = h
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, w, h)
      let lo = 0.3, hi = 0.9, best = canvas.toDataURL('image/jpeg', 0.5)
      for (let k = 0; k < 4; k++) {
        const mid = (lo + hi) / 2
        const dataUrl = canvas.toDataURL('image/jpeg', mid)
        if (dataUrl.length > maxKB * 1024) hi = mid; else { best = dataUrl; lo = mid }
      }
      resolve(best)
    }
    img.onerror = () => reject(new Error('图片加载失败'))
    img.src = URL.createObjectURL(file)
  })
}

async function handleFileSelect(e) {
  const f = e.target.files[0]
  if (f) {
    try {
      pendingImage.value = await compressImage(f)
    } catch (err) {
      ElMessage.error('图片处理失败')
    }
  }
  e.target.value = ''
}

async function submitAsk() {
  if (loading.value || streaming.value) return
  const aw = askText.value.trim()
  const imgData = pendingImage.value

  if (!aw && !imgData) return

  loading.value = true
  streaming.value = false
  currentAsk.value = aw
  streamText.value = ''
  streamThinking.value = ''
  streamStatus.value = '正在准备…'
  askText.value = ''
  pendingImage.value = ''
  welcome.value = false
  scrollToBottom()

  const reqBody = { prompt: aw, id: chatId.value || 0 }
  if (imgData) {
    reqBody.image = imgData.startsWith('data:') ? imgData.split(',')[1] : imgData
  }

  abortCtrl = new AbortController()
  let textBuf = ''
  let thinkingBuf = ''

  try {
    const csrf = document.cookie.match(/djv_csrftoken=([^;]*)/)?.[1] || ''
    const resp = await fetch('/pv/aitools/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
      body: JSON.stringify(reqBody),
      signal: abortCtrl.signal,
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

    streaming.value = true
    loading.value = false

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
        if (p.startsWith(': ')) continue
        if (!p.startsWith('data: ')) continue
        const ds = p.slice(6)
        if (!ds || ds === '[DONE]') continue
        let ev
        try { ev = JSON.parse(ds) } catch (e) { continue }

        if (ev.type === 'start') {
          // stream started
        } else if (ev.type === 'status') {
          const msgMap = {
            preparing: '正在准备…',
            searching: '搜索中…',
            thinking: '分析中…',
            extracting: '正在识别图片文字…',
            analyzing: '正在理解并组织回答…',
            generating: '正在生成回答…',
            uploading: '正在上传图片…',
            cloud_ok: '图片已上传云端',
          }
          streamStatus.value = msgMap[ev.content] || ev.content
        } else if (ev.type === 'thinking') {
          thinkingBuf += ev.content
          streamThinking.value = thinkingBuf
        } else if (ev.type === 'text') {
          textBuf += ev.content
          streamText.value = textBuf
          streamStatus.value = ''
        } else if (ev.type === 'done') {
          if (ev.id) chatId.value = ev.id
          messages.value.push({
            ask: currentAsk.value,
            answer: textBuf,
            thinking: thinkingBuf,
            image: imgData,
          })
          streaming.value = false
          streamText.value = ''
          streamThinking.value = ''
          streamStatus.value = ''
          loadHistory()
        } else if (ev.type === 'error') {
          ElMessage.error(ev.content)
        }
      }
      scrollToBottom()
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      if (textBuf) {
        messages.value.push({
          ask: currentAsk.value,
          answer: textBuf,
          thinking: thinkingBuf,
          image: imgData,
        })
      }
    } else {
      ElMessage.error('请求失败: ' + err.message)
    }
  } finally {
    loading.value = false
    streaming.value = false
    abortCtrl = null
  }
}

function stopStream() {
  if (abortCtrl) {
    abortCtrl.abort()
    streaming.value = false
  }
}

async function loadHistory() {
  try {
    const resp = await http.post('/pv/aitools/gethishh', { type: 'gethishh' })
    const raw = resp.data?.data
    historyList.value = Array.isArray(raw) ? raw : Object.values(raw || {})
  } catch (e) {
    historyList.value = []
  }
}

function switchChat(h) {
  if (h.id === chatId.value) return
  chatId.value = h.id
  try {
    const arr = typeof h.content === 'string' ? JSON.parse(h.content) : h.content
    messages.value = Array.isArray(arr) ? arr : []
  } catch (e) {
    messages.value = []
  }
  welcome.value = false
  scrollToBottom()
}

function delHistory(h) {
  if (!confirm('确定删除这条对话记录吗？')) return
  http.post('/pv/aitools/delhistory', { type: 'delhistory', id: h.id })
    .then(() => {
      if (h.id === chatId.value) {
        chatId.value = 0
        messages.value = []
        welcome.value = true
      }
      loadHistory()
    })
    .catch(() => ElMessage.error('删除失败'))
}

function newChat() {
  chatId.value = 0
  messages.value = []
  askText.value = ''
  pendingImage.value = ''
  welcome.value = true
  loadHistory()
}

async function loadLatestChat() {
  try {
    const resp = await http.post('/pv/aitools/gethishh', { type: 'gethishh' })
    const data = resp.data?.data
    if (data && Object.keys(data).length > 0) {
      const keys = Object.keys(data)
      const last = data[keys[0]]
      chatId.value = last.id
      const arr = typeof last.content === 'string' ? JSON.parse(last.content) : last.content
      messages.value = Array.isArray(arr) ? arr : []
    } else {
      welcome.value = true
    }
  } catch (e) {
    welcome.value = true
  }
}

onMounted(() => {
  loadHistory()
  loadLatestChat()
})
</script>

<style scoped>
.at-page {
  height: 100%;
  overflow: hidden;
  background: var(--bg-page);
  padding: 12px;
  box-sizing: border-box;
  display: flex;
  gap: 16px;
}
.at-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.at-chat__hd {
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-card);
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
.at-chat__area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}
.at-chat__area::-webkit-scrollbar { width: 5px; }
.at-chat__area::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 5px; }
.at-welcome {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  font-size: 22px;
  font-family: "KaiTi", serif;
}
.at-qa {
  width: 800px;
  max-width: 100%;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.at-msg {
  display: flex;
}
.at-msg--user {
  justify-content: flex-end;
}
.at-msg-body {
  flex: 1;
  min-width: 0;
  line-height: 1.72;
  overflow-wrap: break-word;
  word-break: break-word;
}
.at-msg-body:not(.at-msg-body--user):not(.at-msg-body--streaming) {
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--bg-subtle);
}
.at-msg-body--user {
  flex: 0 1 auto;
  padding: 10px 14px;
  border-radius: 10px;
  background: #1e293b;
  color: #fff;
}
.at-msg-body--streaming {
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--bg-subtle);
}
.at-msg-img {
  display: block;
  max-width: 130px;
  max-height: 90px;
  border-radius: 8px;
  margin-top: 6px;
  cursor: pointer;
}
.at-thinking {
  margin-bottom: 6px;
  border: 1px solid var(--border-light);
  border-radius: 7px;
  overflow: hidden;
}
.at-thinking summary {
  padding: 6px 10px;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-placeholder);
  background: var(--bg-subtle);
  user-select: none;
}
.at-thinking-content {
  padding: 8px 12px;
  font-size: 12px;
  color: var(--text-muted);
  background: var(--bg-subtle);
  border-top: 1px solid var(--border-light);
  white-space: pre-wrap;
  word-break: break-word;
}
.at-stream-status {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 8px;
  background: var(--bg-active);
  color: var(--color-primary-light);
}
.at-stream-cursor {
  animation: pulse 1s infinite;
  color: var(--color-primary-light);
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.at-loading-dots {
  display: inline-flex;
  gap: 4px;
}
.at-dot {
  width: 7px;
  height: 7px;
  background: var(--scrollbar-thumb-hover);
  border-radius: 50%;
  animation: blink 1.4s infinite both;
}
.at-dot:nth-child(2) { animation-delay: .2s; }
.at-dot:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%,80%,100%{opacity:0} 40%{opacity:1} }
.at-actions {
  display: flex;
  gap: 6px;
  margin: 8px 0;
  opacity: 0;
  transition: opacity .15s;
}
.at-qa:hover .at-actions { opacity: 1; }
.at-actions--user { justify-content: flex-end; }
.at-act-btn {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 2px 8px;
  border-radius: 4px;
  border: 0;
  background: transparent;
  color: var(--text-placeholder);
  cursor: pointer;
  font-size: 12px;
}
.at-act-btn:hover { color: var(--text-secondary); background: rgba(0,0,0,0.05); }
.at-chat__foot {
  padding: 10px 20px 16px;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-card);
}
.at-input-wrap {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 10px 12px 8px;
  background: var(--bg-subtle);
}
.at-input-wrap:focus-within { border-color: var(--color-primary-light); }
.at-input-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
}
.at-left-btns {
  display: flex;
  align-items: center;
  gap: 8px;
}
.at-pending-img {
  max-width: 60px;
  max-height: 60px;
  border-radius: 6px;
  cursor: pointer;
}
.at-right-btns {
  display: flex;
  align-items: center;
  gap: 4px;
}
.at-side {
  flex: 0 1 280px;
  min-width: 200px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.at-side__hd {
  padding: 16px 16px 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-bottom: 1px solid var(--border-card);
}
.at-side__logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}
.at-newchat {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 0;
  border: 1px solid var(--border-light);
  border-radius: 10px;
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
}
.at-newchat:hover { background: var(--bg-hover); }
.at-side__label {
  color: var(--text-placeholder);
  font-size: 13px;
  margin-top: 4px;
}
.at-side__list {
  flex: 1;
  overflow-y: auto;
  padding: 6px 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.at-side__list::-webkit-scrollbar { width: 4px; }
.at-side__list::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 4px; }
.at-hht {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
}
.at-hht:hover { background: var(--bg-hover); }
.at-hht.active { background: var(--bg-active); font-weight: 500; color: var(--color-primary-light); }
.at-hht__tit {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}
.at-hht__del {
  display: none;
  margin-left: 6px;
  font-size: 13px;
}
.at-hht:hover .at-hht__del { display: block; }

/* 光箱 */
.at-lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: zoom-out;
}
.at-lightbox img {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 4px 32px rgba(0,0,0,0.5);
}
.at-lightbox__close {
  position: absolute;
  top: 16px;
  right: 20px;
  color: #fff;
  font-size: 28px;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
}
.at-lightbox__close:hover { background: rgba(255,255,255,0.2); }
</style>
