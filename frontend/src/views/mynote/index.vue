<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-note-sticky"></i> 我的笔记</h2>
      </div>
      <el-button type="primary" size="small" @click="openAdd">新增记录</el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-bar__inner">
        <el-input v-model="searchKey" placeholder="搜索标题/内容" clearable style="width:220px" @keyup.enter="search"
          @clear="search" />
        <el-button type="primary" :loading="loading" @click="search">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>
    </div>

    <!-- 笔记列表 -->
    <div class="mo-body">
      <div class="m-card" style="height:100%;">
        <div class="note-list" ref="listRef" v-loading="loading">
          <template v-if="list.length">
            <div v-for="note in list" :key="note.id" class="note-item">
              <div class="note-badge">{{ note.tit }}</div>
              <div class="note-content" v-html="renderContent(note.nc)"></div>
              <div class="note-footer">
                <span class="note-meta">{{ metaText(note) }}</span>
                <span class="note-actions">
                  <el-button type="primary" link @click="openEdit(note)">编辑</el-button>
                  <el-dropdown trigger="hover" @command="(cmd) => onActionCommand(cmd, note)">
                    <span class="more-trigger"><el-icon><MoreFilled /></el-icon></span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="del" style="color: var(--el-color-danger)">
                          <el-icon><Delete /></el-icon>删除
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
              </div>
            </div>
            <div class="note-bottom">--已经到底部了--</div>
          </template>
          <el-empty v-else description="无数据" />
        </div>
      </div>
    </div>

    <!-- 回到顶部 -->
    <el-backtop target=".note-list" :right="40" :bottom="40" />

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑' : '新增'" width="60%">
      <el-input v-model="dialog.tit" placeholder="输入标题..." style="margin-bottom:12px" />
      <el-input v-model="dialog.nc" type="textarea" :rows="12" placeholder="输入内容..." />
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MoreFilled, Delete } from '@element-plus/icons-vue'
import http from '../../api/http'

const loading = ref(false)
const submitting = ref(false)
const list = ref([])
const searchKey = ref('')
const listRef = ref(null)
const dialog = reactive({ visible: false, isEdit: false, id: 0, tit: '', nc: '' })

function metaText(note) {
  return note.ut ? `于 ${note.ct} 创建, ${note.ut} 更新` : `于 ${note.ct} 创建`
}

function renderContent(text) {
  if (!text) return ''
  const urlRegex = /(https?:\/\/[^\s<>"'，。（）【】、；：]+)/g
  const links = []; let s = String(text).replace(urlRegex, (m) => { links.push(m); return ` ${links.length - 1} ` })
  s = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
  s = s.replace(/\n/g, '<br/>')
  s = s.replace(/ (\d+) /g, (_, i) => {
    const url = links[Number(i)]; const esc = url.replace(/&/g, '&amp;').replace(/"/g, '&quot;')
    return `<a href="${esc}" target="_blank" rel="noopener noreferrer">${esc}</a>`
  })
  return s
}

async function load() {
  loading.value = true
  try {
    const param = searchKey.value.trim() === '' ? 0 : searchKey.value.trim()
    const resp = await http.post('/pv/mynote/getnote', { param })
    const a = resp.data?.data; list.value = Array.isArray(a) ? a : []
  } catch (e) { list.value = []; ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading.value = false }
}

function search() { load() }
function reset() { searchKey.value = ''; load() }

function openAdd() { dialog.isEdit = false; dialog.id = 0; dialog.tit = ''; dialog.nc = ''; dialog.visible = true }
function openEdit(note) { dialog.isEdit = true; dialog.id = note.id; dialog.tit = note.tit; dialog.nc = note.nc; dialog.visible = true }

async function submit() {
  if (dialog.tit.trim() === '' || dialog.nc.trim() === '') { ElMessage.warning('标题和内容都不能为空！'); return }
  submitting.value = true
  try {
    let resp
    if (dialog.isEdit) { resp = await http.post('/pv/mynote/editnote', { id: dialog.id, newtit: dialog.tit, newnc: dialog.nc }) }
    else { resp = await http.post('/pv/mynote/istnote', { tit: dialog.tit, nc: dialog.nc }) }
    ElMessage.success(resp.data?.data || '操作成功！'); dialog.visible = false; await load()
  } catch (e) { ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message)) }
  finally { submitting.value = false }
}

function onActionCommand(cmd, note) {
  if (cmd === 'del') confirmDel(note)
}

function confirmDel(note) {
  ElMessageBox.confirm('确定删除吗？', '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    .then(async () => {
      try { const resp = await http.post('/pv/mynote/delnote', { id: note.id }); ElMessage.success(resp.data?.data || '删除成功！'); await load() }
      catch (e) { ElMessage.error('删除失败：' + (e?.response?.data?.msg || e.message)) }
    }).catch(() => { })
}

onMounted(() => { load() })
</script>

<style scoped>
.mo-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--bg-page);
  min-width: 0;
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

.search-bar {
  flex-shrink: 0;
  padding: 0 14px;
}

.search-bar__inner {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 10px 16px;
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  gap: 10px;
}

.mo-body {
  flex: 1;
  padding: 12px 14px 14px;
  overflow: hidden;
  min-height: 0;
  min-width: 0;
  box-sizing: border-box;
}

.m-card {
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  overflow: hidden;
  transition: box-shadow .2s;
  display: flex;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;
}

.m-card:hover {
  box-shadow: var(--shadow-card-hover);
}

.note-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
  width: 100%;
  box-sizing: border-box;
  background: var(--bg-card);
}

.note-list::-webkit-scrollbar {
  width: 4px;
}

.note-list::-webkit-scrollbar-track {
  background: var(--bg-subtle);
}

.note-list::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 4px;
}

.note-item {
  padding: 10px 0;
  overflow: hidden;
  max-width: 100%;
}

.note-badge {
  display: block;
  padding: 6px 25px;
  margin: -2px -12px 8px;
  background: var(--bg-subtle);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.note-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.625;
  margin-bottom: 8px;
  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
  padding: 0 30px;
}

.note-content :deep(a) {
  color: var(--color-primary-light);
}

.note-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
}

.note-meta {
  font-size: 12px;
  color: var(--text-placeholder);
}

.note-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.more-trigger {
  display: flex;
  align-items: center;
  font-size: 16px;
  color: var(--text-placeholder);
  cursor: pointer;
  outline: none;
}

.more-trigger:hover {
  color: var(--text-secondary);
}

.note-bottom {
  text-align: center;
  font-weight: 500;
  color: var(--text-placeholder);
  padding: 12px 0;
  font-size: 13px;
}
</style>
