<template>
  <div class="ic-page">
    <div class="ic-panel">
      <!-- 工具栏 -->
      <div class="ic-toolbar">
        <el-select v-model="method" class="ic-method" style="width: 100px">
          <el-option label="GET" value="get" />
          <el-option label="POST" value="post" />
        </el-select>
        <el-select v-model="env" placeholder="选择环境" class="ic-env" clearable>
          <el-option label="soonProd" value="https://soon-api.aijiatui.com" />
          <el-option label="soonTest" value="https://soon-api-dev.aijiatui.com" />
          <el-option label="meetProd" value="https://api.mmeett.com" />
          <el-option label="meetTest" value="https://vcard-api.aijiatui.com" />
          <el-option label="originProd" value="https://borigin.aijiatui.com" />
          <el-option label="originTest" value="https://borigin-test.aijiatui.com" />
          <el-option label="saasProd" value="http://msr.jtscprod.com" />
          <el-option label="saasTest" value="http://msr.jiatuitest.com" />
        </el-select>
        <el-input v-model="uri" placeholder="输入接口地址" class="ic-uri" />
        <el-button class="ic-icon-btn" @click="toggleHistory" title="请求历史">
          <el-icon>
            <Clock />
          </el-icon>
        </el-button>
        <el-button class="ic-icon-btn" @click="toggleCurl" title="粘贴curl命令">
          <el-icon>
            <Monitor />
          </el-icon>
        </el-button>
      </div>

      <!-- 主体：左输入 / 右结果 -->
      <div class="ic-body">
        <div class="ic-left">
          <div>
            <label class="ic-label">请求头 Headers</label>
            <el-input v-model="headers" type="textarea" :rows="7" placeholder="input request headers" />
          </div>
          <div>
            <label class="ic-label">请求参数 Params / Body</label>
            <el-input v-model="params" type="textarea" :rows="7" placeholder="input request params" />
          </div>
          <div>
            <label class="ic-label">上传文件（可选）</label>
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="false"
              multiple
              drag
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
            </el-upload>
            <div v-if="uploadFiles.length" class="upload-file-list">
              <div v-for="(item, idx) in uploadFiles" :key="idx" class="upload-file-item">
                <el-input v-model="item.fieldName" size="small" placeholder="字段名" class="upload-field-name" />
                <span class="upload-file-name" :title="item.file.name">{{ item.file.name }}</span>
                <el-button type="danger" link size="small" @click="handleFileRemove(idx)">删除</el-button>
              </div>
            </div>
          </div>
          <div class="ic-actions">
            <el-button style="flex:1" @click="resetParam">重&nbsp;&nbsp;置</el-button>
            <el-button type="primary" style="flex:1" :loading="loading" :disabled="loading"
              @click="sendRequest">调&nbsp;&nbsp;用</el-button>
          </div>
        </div>
        <div class="ic-result">
          <div class="ic-result-inner">
            <div v-if="loading" class="ic-note">加载中...</div>
            <div v-if="error" class="ic-error">{{ error }}</div>
            <div v-for="(card, idx) in resultCards" :key="idx" class="ic-card">
              <div class="ic-card__head">
                <span class="ic-card__method">{{ card.requestType }}</span>
                <span class="ic-card__uri">{{ card.hostUri }}</span>
                <el-button size="small" type="info" plain @click="copyCurl(card)" class="ic-card__curl">curl</el-button>
              </div>
              <div class="ic-card__fields">
                <div class="ic-field"><span class="ic-field__label">请求头部:</span><span class="ic-field__value">{{
                  card.reqHeader }}</span></div>
                <div class="ic-field"><span class="ic-field__label">请求内容:</span><span class="ic-field__value">{{
                  card.reqParam }}</span></div>
                <div class="ic-field"><span class="ic-field__label">响应头部:</span><span class="ic-field__value">{{
                  card.resHeader }}</span></div>
                <div class="ic-field ic-field--top">
                  <span class="ic-field__label">响应内容:</span>
                  <div class="ic-field__body">
                    <span class="ic-field__value ic-field__value--mono">{{ card.resBody }}</span>
                    <el-button size="small" type="primary" plain @click="copyBody(card.resBody)" style="margin-top:8px">复制</el-button>
                  </div>
                </div>
              </div>
              <div class="ic-card__footer">第{{ idx + 1 }}条</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 遮罩层：点击关闭弹窗 -->
      <div v-if="showHistory || showCurl" class="ic-overlay" @click="showHistory = false; showCurl = false"></div>

      <!-- 历史记录面板 -->
      <div v-if="showHistory" class="ic-dropdown">
        <div class="ic-dropdown__header">
          <span class="ic-dropdown__title">Request history</span>
          <el-icon class="ic-dropdown__close" @click="showHistory = false">
            <Close />
          </el-icon>
        </div>
        <div class="ic-dropdown__body">
          <div v-if="historyLoading" style="padding: 16px; text-align: center">加载中...</div>
          <div v-else-if="!history.length" style="padding: 16px; text-align: center; color: #999">暂无历史记录</div>
          <div v-for="h in history" :key="h.id" class="ic-his-row">
            <div class="ic-his-main">
              <div class="ic-his-name" v-if="editingNameId === h.id">
                <el-input v-model="historyNames[h.id]" size="small" @blur="saveHistoryName(h.id)"
                  @keyup.enter="saveHistoryName(h.id)" placeholder="输入自定义名称" />
              </div>
              <span class="ic-his-text" @click="fillFromHistory(h)" :title="`【${h.method}】${h.host}${h.uri}`">
                <span v-if="historyNames[h.id]" class="ic-his-label">{{ historyNames[h.id] }}</span>
                <span class="ic-his-url">【{{ h.method }}】{{ h.host }}{{ h.uri }}</span>
              </span>
            </div>
            <div class="ic-his-actions">
              <el-button class="ic-his-rename" text type="info" @click.stop="toggleEditName(h)" title="编辑名称">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button class="ic-his-replay" text type="primary" @click.stop="replayRequest(h)" title="一键重放">
                <el-icon>
                  <RefreshRight />
                </el-icon>
              </el-button>
              <el-button class="ic-his-delete" text type="danger" @click.stop="deleteHistory(h)" title="删除">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- curl 粘贴面板 -->
      <div v-if="showCurl" class="ic-dropdown ic-dropdown--center">
        <div style="font-weight: 600; color: #374151; margin-bottom: 8px">粘贴curl命令，自动解析填充</div>
        <el-input v-model="curlInput" type="textarea" :rows="5"
          placeholder="粘贴curl命令，例如：&#10;curl -X POST https://example.com/api -H 'Content-Type: application/json' -d '{&quot;key&quot;:&quot;value&quot;}'" />
        <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px">
          <el-button @click="closeCurl">取消</el-button>
          <el-button type="primary" @click="parseCurl">解析并填充</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, Monitor, Close, RefreshRight, Delete, UploadFilled, Edit } from '@element-plus/icons-vue'
import http from '../../api/http'

const method = ref('post')
const env = ref('')
const uri = ref('')
const headers = ref('')
const params = ref('')
const loading = ref(false)
const error = ref('')
const resultCards = ref([])
const uploadRef = ref(null)
const fileList = ref([])
const selectedFiles = ref([])
const uploadFiles = ref([])

const showHistory = ref(false)
const historyLoading = ref(false)
const history = ref([])

const showCurl = ref(false)
const curlInput = ref('')
const historyNames = reactive({})
const editingNameId = ref(null)

// 预设环境 host 列表
const KNOWN_HOSTS = [
  'https://soon-api.aijiatui.com',
  'https://wecard-dev.aijiatui.com',
  'https://api.mmeett.com',
  'https://vcard-api.aijiatui.com',
  'https://borigin.aijiatui.com',
  'https://borigin-test.aijiatui.com',
  'http://msr.jtscprod.com',
  'http://msr.jiatuitest.com',
]

function resetParam() {
  method.value = 'post'
  env.value = ''
  uri.value = ''
  headers.value = ''
  params.value = ''
  error.value = ''
  resultCards.value = []
  showHistory.value = false
  uploadFiles.value = []
}

function handleFileChange(file, uploadFileList) {
  uploadFiles.value.push({ file: file.raw, fieldName: 'image' })
}

function handleFileRemove(index) {
  uploadFiles.value.splice(index, 1)
}

// 将 Python 风格字面量转为合法 JSON
function pythonToJSON(text) {
  const kw = { None: 'null', True: 'true', False: 'false' }
  let out = ''
  let inSingle = false
  let inDouble = false
  let i = 0
  while (i < text.length) {
    const c = text[i]
    if (inSingle) {
      if (c === '\\') {
        const n = text[i + 1]
        if (n === "'") out += "'"
        else if (n === '"') out += '\\"'
        else out += c + (n || '')
        i += 2
        continue
      }
      if (c === "'") { out += '"'; inSingle = false }
      else if (c === '"') out += '\\"'
      else out += c
      i++
      continue
    }
    if (inDouble) {
      if (c === '\\') { out += c + (text[i + 1] || ''); i += 2; continue }
      if (c === '"') { out += c; inDouble = false }
      else out += c
      i++
      continue
    }
    if (c === "'") { out += '"'; inSingle = true; i++; continue }
    if (c === '"') { out += c; inDouble = true; i++; continue }
    let matched = false
    for (const k in kw) {
      if (text.startsWith(k, i) &&
        (i === 0 || !/[a-zA-Z0-9_]/.test(text[i - 1])) &&
        !/[a-zA-Z0-9_]/.test(text[i + k.length] || '')) {
        out += kw[k]
        i += k.length
        matched = true
        break
      }
    }
    if (matched) continue
    out += c
    i++
  }
  return out
}

// 将文本解析为 JSON 对象
function parseTextToJSON(text) {
  if (!text || !text.trim()) return {}
  try {
    const parsed = JSON.parse(text)
    if (typeof parsed === 'object' && parsed !== null) return parsed
  } catch (e) { }
  if (text.includes("'")) {
    try {
      const pyParsed = JSON.parse(pythonToJSON(text))
      if (typeof pyParsed === 'object' && pyParsed !== null) return pyParsed
    } catch (e) { }
  }
  const lines = text.split('\n')
  const result = {}
  let hasKV = false
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    if (/^[[{(]/.test(trimmed)) continue
    const colonIdx = trimmed.indexOf(':')
    if (colonIdx > 0) {
      result[trimmed.substring(0, colonIdx).trim()] = trimmed.substring(colonIdx + 1).trim()
      hasKV = true
    }
  }
  if (hasKV) return result
  if (text.includes('=') && !text.includes('\n')) {
    try {
      const params = new URLSearchParams(text)
      const urlResult = {}
      params.forEach((v, k) => { urlResult[k] = v })
      if (Object.keys(urlResult).length > 0) return urlResult
    } catch (e) { }
  }
  return text
}

function splitHostAndUri(host, uriPath) {
  const cleanHost = (host || '').replace(/\/+$/, '')
  if (KNOWN_HOSTS.includes(cleanHost)) return { env: cleanHost, uri: uriPath || '/' }
  if (cleanHost) return { env: '', uri: cleanHost + (uriPath || '') }
  return { env: '', uri: uriPath || '' }
}

async function sendRequest() {
  if (!env.value && !uri.value.includes('http://') && !uri.value.includes('https://')) {
    ElMessage.warning('输入正确的请求域名和接口地址！')
    return
  }
  loading.value = true
  error.value = ''
  resultCards.value = []
  try {
    let resp
    if (uploadFiles.value.length > 0) {
      // 有文件时，使用 FormData（multipart/form-data）
      const fd = new FormData()
      fd.append('setenv', env.value)
      fd.append('uri', uri.value)
      fd.append('headers', JSON.stringify(parseTextToJSON(headers.value)))
      fd.append('params', JSON.stringify(parseTextToJSON(params.value)))
      fd.append('type', 'requestinterface')
      uploadFiles.value.forEach((item) => {
        fd.append(item.fieldName, item.file)
      })
      resp = await http.post('/pv/easyIC', fd)
    } else {
      resp = await http.post('/pv/easyIC', {
        setreqtype: method.value,
        setenv: env.value,
        uri: uri.value,
        headers: parseTextToJSON(headers.value),
        params: parseTextToJSON(params.value),
        type: 'requestinterface',
      })
    }
    if (resp.data.error || !resp.data.data) {
      error.value = '请求异常: ' + (resp.data.error || '未获取到数据')
      return
    }
    const res = resp.data.data
    const cards = []
    let reqHeader = '/'
    let reqParam = '/'
    const keys = Object.keys(res)
    for (const k of keys) {
      const item = res[k]
      if (item.request_headers) reqHeader = item.request_headers
      if (item.request_params) reqParam = item.request_params
      cards.push({
        requestType: item.request_type,
        hostUri: item.host_uri,
        reqHeader,
        reqParam,
        resHeader: item.response_headers || '',
        resBody: JSON.stringify(item.response_body),
      })
    }
    resultCards.value = cards
    showHistory.value = false
  } catch (e) {
    const errMsg = e.response?.data ? JSON.stringify(e.response.data) : e.message
    error.value = '请求失败: ' + errMsg
  } finally {
    loading.value = false
  }
}

function copyBody(body) {
  navigator.clipboard.writeText(body).then(() => {
    ElMessage.success('复制成功！')
  })
}

function copyCurl(card) {
  let curl = `curl -X ${card.requestType.toUpperCase()} '${card.hostUri}'`
  // headers
  try {
    const h = typeof card.reqHeader === 'string' ? JSON.parse(card.reqHeader) : card.reqHeader
    if (typeof h === 'object' && h !== null) {
      Object.entries(h).forEach(([k, v]) => {
        curl += ` -H '${k}: ${v}'`
      })
    }
  } catch (e) { }
  // body
  if (card.requestType !== 'get' && card.reqParam && card.reqParam !== '/') {
    let bodyStr = ''
    if (typeof card.reqParam === 'object') {
      bodyStr = JSON.stringify(card.reqParam)
    } else {
      try {
        bodyStr = JSON.stringify(JSON.parse(card.reqParam))
      } catch (e) {
        bodyStr = String(card.reqParam)
      }
    }
    curl += ` -d '${bodyStr}'`
  }
  navigator.clipboard.writeText(curl).then(() => {
    ElMessage.success('curl 已复制！')
  })
}

function toggleHistory() {
  showCurl.value = false
  showHistory.value = !showHistory.value
  if (showHistory.value) loadHistory()
}

function toggleCurl() {
  showHistory.value = false
  showCurl.value = !showCurl.value
}

function closeCurl() {
  showCurl.value = false
  curlInput.value = ''
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const resp = await http.post('/pv/easyIC', { type: 'gethistory' })
    const raw = resp.data?.data
    history.value = Array.isArray(raw) ? raw : Object.values(raw || {})
    loadHistoryNames()
  } catch (e) {
    history.value = []
  } finally {
    historyLoading.value = false
  }
}

function fillFromHistory(h) {
  const parts = splitHostAndUri(h.host, h.uri)
  env.value = parts.env
  uri.value = parts.uri
  method.value = h.method
  headers.value = h.header || ''
  params.value = h.param || ''
  showHistory.value = false
}

async function replayRequest(h) {
  fillFromHistory(h)
  await sendRequest()
}

async function deleteHistory(h) {
  if (!confirm('确定要删除这条历史记录吗？')) return
  try {
    const resp = await http.post('/pv/easyIC', { type: 'deletehistory', id: h.id })
    if (resp.data.success || resp.data.data) {
      history.value = history.value.filter(item => item.id !== h.id)
      ElMessage.success('删除成功！')
    } else {
      ElMessage.error('删除失败！')
    }
  } catch (e) {
    ElMessage.error('删除失败，请重试')
  }
}

function toggleEditName(h) {
  if (editingNameId.value === h.id) {
    editingNameId.value = null
    saveHistoryName(h.id)
  } else {
    editingNameId.value = h.id
    if (!historyNames[h.id]) historyNames[h.id] = ''
  }
}

function saveHistoryName(id) {
  const name = (historyNames[id] || '').trim()
  const allNames = JSON.parse(localStorage.getItem('easyIC_historyNames') || '{}')
  if (name) {
    allNames[id] = name
  } else {
    delete allNames[id]
    delete historyNames[id]
  }
  localStorage.setItem('easyIC_historyNames', JSON.stringify(allNames))
  editingNameId.value = null
}

function loadHistoryNames() {
  const allNames = JSON.parse(localStorage.getItem('easyIC_historyNames') || '{}')
  Object.keys(allNames).forEach(id => {
    historyNames[id] = allNames[id]
  })
}

function parseCurl() {
  const curlStr = curlInput.value.trim()
  if (!curlStr) {
    ElMessage.warning('请粘贴curl命令！')
    return
  }
  let cmd = curlStr.replace(/\\\n/g, ' ').replace(/\s+/g, ' ').trim()

  // 提取 URL
  let url = ''
  const urlMatch = cmd.match(/(?:curl\s+)(?:-[a-zA-Z]+\s+[^\s]+\s+)*?(['"]?)(https?:\/\/[^\s'"]+)\1/)
  if (urlMatch) url = urlMatch[2]
  else {
    const simpleMatch = cmd.match(/(https?:\/\/[^\s'"]+)/)
    if (simpleMatch) url = simpleMatch[1]
  }
  if (!url) {
    ElMessage.warning('未能识别URL，请检查curl命令格式！')
    return
  }

  // 提取方法
  let m = 'GET'
  const methodMatch = cmd.match(/(?:-X|--request)\s+['"]?(\w+)['"]?/i)
  if (methodMatch) m = methodMatch[1].toUpperCase()
  else if (/(?:-d|--data|--data-raw|--data-binary)\s+/.test(cmd)) m = 'POST'

  // 提取 headers
  const hdrs = []
  const headerRegex = /(?:-H|--header)\s+(?:'([^'\\]*(?:\\.[^'\\]*)*)'|"([^"\\]*(?:\\.[^"\\]*)*)")/g
  let hMatch
  while ((hMatch = headerRegex.exec(cmd)) !== null) {
    let val = hMatch[1] ?? hMatch[2]
    val = val.replace(/\\"/g, '"').replace(/\\'/g, "'")
    hdrs.push(val)
  }

  // 提取 body
  let body = ''
  const bodyMatch = cmd.match(/(?:-d|--data|--data-raw|--data-binary)\s+(?:'([^'\\]*(?:\\.[^'\\]*)*)'|"([^"\\]*(?:\\.[^"\\]*)*)")/)
  if (bodyMatch) {
    body = ((bodyMatch[1] ?? bodyMatch[2]) || '').replace(/\\"/g, '"').replace(/\\'/g, "'")
  }

  // 分割 URL 为 host + uri
  let host = ''
  let uriPath = '/'
  try {
    const urlObj = new URL(url)
    host = urlObj.origin
    uriPath = urlObj.pathname + urlObj.search
  } catch (e) {
    host = url
  }

  method.value = m.toLowerCase()
  if (KNOWN_HOSTS.includes(host)) {
    env.value = host
    uri.value = uriPath
  } else {
    env.value = ''
    uri.value = host + uriPath
  }
  headers.value = hdrs.join('\n')
  params.value = body

  closeCurl()
  ElMessage.success('curl解析成功，已填充表单！')
}
</script>

<style scoped>
.ic-page {
  height: 100%;
  overflow: hidden;
  background: var(--bg-page);
  padding: 12px;
  box-sizing: border-box;
  display: flex;
}

.ic-panel {
  position: relative;
  flex: 1;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ic-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
  flex-shrink: 0;
}

.ic-method :deep(.el-input__inner) {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-primary-light);
}

.ic-env {
  width: 200px;
}

.ic-uri {
  flex: 1;
  min-width: 200px;
}

.ic-icon-btn {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border-radius: 8px;
}

.ic-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

.ic-left {
  flex: 0 1 520px;
  min-width: 320px;
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  padding: 16px;
  gap: 16px;
  overflow-y: auto;
}

.ic-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.ic-actions {
  display: flex;
  gap: 12px;
  margin-top: auto;
}

.ic-result {
  flex: 1;
  min-width: 0;
  background: var(--bg-subtle);
  overflow-y: auto;
}

.ic-result-inner {
  padding: 16px;
}

.ic-note {
  text-align: center;
  color: var(--text-placeholder);
  padding: 20px;
}

.ic-error {
  color: #ef4444;
  margin-bottom: 12px;
  padding: 10px;
  background: #fef2f2;
  border-radius: 8px;
}

.ic-card {
  border-radius: 12px;
  border: 1px solid var(--border-light);
  background: var(--bg-card);
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06);
}

.ic-card__head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.ic-card__method {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-primary-light);
  line-height: 1;
}

.ic-card__uri {
  font-size: 16px;
  color: var(--text-primary);
  word-break: break-all;
  padding-top: 2px;
  flex: 1;
}

.ic-card__curl {
  flex-shrink: 0;
  font-size: 12px;
  font-family: monospace;
}

.ic-card__fields {
  margin-top: 12px;
  font-size: 14px;
}

.ic-field {
  display: flex;
  gap: 12px;
  margin: 6px 0;
}

.ic-field--top {
  align-items: flex-start;
}

.ic-field__label {
  width: 80px;
  flex-shrink: 0;
  font-weight: 600;
  color: var(--text-muted);
}

.ic-field__value {
  word-break: break-all;
  color: var(--text-primary);
}

.ic-field__value--mono {
  font-family: monospace;
  font-size: 12px;
}

.ic-field__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ic-card__footer {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--border-light);
  text-align: center;
  font-size: 12px;
  color: var(--text-placeholder);
}

/* 下拉面板（历史 / curl） */
.ic-dropdown {
  position: absolute;
  right: 16px;
  top: 56px;
  z-index: 50;
  width: 500px;
  max-height: 320px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, .1);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.ic-dropdown--center {
  left: 50%;
  transform: translateX(-50%);
  right: auto;
  width: 520px;
  padding: 16px;
}

.ic-dropdown__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  height: 36px;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border-light);
}

.ic-dropdown__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.ic-dropdown__close {
  cursor: pointer;
  color: var(--text-placeholder);
}

.ic-dropdown__close:hover {
  color: var(--text-secondary);
}

.ic-dropdown__body {
  overflow-y: auto;
  max-height: 280px;
}

/* 历史记录行 */
.ic-his-row:hover {
  background: var(--bg-subtle);
}

.upload-file-list {
  margin-top: 8px;
}

.upload-file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: var(--bg-subtle, #f5f7fa);
  border-radius: 6px;
  margin-bottom: 4px;
}

.upload-field-name {
  width: 100px;
  flex-shrink: 0;
}

.upload-file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  color: var(--text-secondary);
}

.ic-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
}

.ic-dropdown {
  z-index: 100;
}

.ic-his-row {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-bottom: 1px solid var(--border-light, #f0f0f0);
}

.ic-his-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ic-his-name {
  width: 100%;
}

.ic-his-text {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  min-width: 0;
}

.ic-his-label {
  font-weight: 600;
  font-size: 13px;
  color: var(--color-primary-light, #409eff);
}

.ic-his-url {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.ic-his-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  gap: 0;
}

.ic-his-rename {
  flex-shrink: 0;
}
</style>
