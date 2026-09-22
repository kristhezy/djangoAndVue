<template>
  <div v-if="visible" class="ap-float" :class="{ collapsed: !expanded }">
    <!-- 收起态：小圆按钮 -->
    <div v-if="!expanded" class="ap-dot" :class="'ap-dot--' + poll.status" @click="expanded = true" :title="poll.message || '审核轮询'">
      <i :class="dotIcon"></i>
    </div>

    <!-- 展开态：面板 -->
    <div v-else class="ap-panel">
      <div class="ap-panel-hd">
        <span class="ap-panel-title">
          <i :class="dotIcon" style="margin-right:4px"></i>审核轮询
        </span>
        <div class="ap-panel-actions">
          <el-button v-if="poll.status === 'polling'" text size="small" type="danger" @click="poll.stop">停止</el-button>
          <el-button text size="small" @click="expanded = false"><i class="fa-solid fa-minus"></i></el-button>
          <el-button v-if="isTerminal" text size="small" @click="poll.dismiss"><i class="fa-solid fa-xmark"></i></el-button>
        </div>
      </div>
      <div class="ap-panel-bd">
        <div class="ap-info-row">
          <span class="ap-label">企业</span>
          <span class="ap-val">{{ poll.company.cn || poll.company.cid }}</span>
        </div>
        <div class="ap-info-row">
          <span class="ap-label">状态</span>
          <span class="ap-val" :class="'ap-status--' + poll.status">{{ statusLabel }}</span>
        </div>
        <div class="ap-info-row">
          <span class="ap-label">信息</span>
          <span class="ap-val ap-msg">{{ poll.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuditPolling } from '../store/auditPolling'

const poll = useAuditPolling()
const expanded = ref(false)

const visible = computed(() => poll.status !== 'idle')

const isTerminal = computed(() =>
  ['passed', 'published', 'rejected', 'error', 'withdrawn'].includes(poll.status)
)

const dotIcon = computed(() => {
  const s = poll.status
  if (s === 'polling') return 'fa-solid fa-spinner fa-spin'
  if (s === 'passed' || s === 'published') return 'fa-solid fa-check'
  if (s === 'publishing') return 'fa-solid fa-spinner fa-spin'
  if (s === 'rejected' || s === 'error') return 'fa-solid fa-xmark'
  if (s === 'withdrawn') return 'fa-solid fa-rotate-left'
  return 'fa-solid fa-satellite-dish'
})

const statusLabel = computed(() => {
  const map = {
    polling: '轮询中',
    passed: '审核通过',
    publishing: '发布中…',
    published: '已发布',
    rejected: '审核被拒',
    error: '异常',
    withdrawn: '已撤回',
  }
  return map[poll.status] || poll.status
})
</script>

<style scoped>
.ap-float {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 2000;
}

/* 收起态圆点 */
.ap-dot {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  color: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,.15);
  transition: transform .2s, box-shadow .2s;
  background: var(--text-muted);
}

.ap-dot:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 16px rgba(0,0,0,.2);
}

.ap-dot--polling,
.ap-dot--publishing {
  background: #3b82f6;
  animation: ap-pulse 1.5s ease-in-out infinite;
}

.ap-dot--passed,
.ap-dot--published {
  background: #22c55e;
}

.ap-dot--rejected,
.ap-dot--error {
  background: #ef4444;
}

.ap-dot--withdrawn {
  background: #f59e0b;
}

@keyframes ap-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,.4); }
  50% { box-shadow: 0 0 0 10px rgba(59,130,246,0); }
}

/* 展开态面板 */
.ap-panel {
  width: 300px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,.12);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.ap-panel-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-card);
}

.ap-panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.ap-panel-actions {
  display: flex;
  gap: 2px;
}

.ap-panel-actions :deep(.el-button) {
  padding: 2px 6px;
  font-size: 12px;
}

.ap-panel-bd {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ap-info-row {
  display: flex;
  align-items: flex-start;
  font-size: 13px;
  line-height: 1.5;
}

.ap-label {
  color: var(--text-muted);
  width: 36px;
  flex-shrink: 0;
}

.ap-val {
  color: var(--text-primary);
  flex: 1;
  word-break: break-all;
}

.ap-msg {
  white-space: pre-wrap;
}

.ap-status--polling {
  color: #3b82f6;
  font-weight: 600;
}

.ap-status--passed,
.ap-status--published {
  color: #22c55e;
  font-weight: 600;
}

.ap-status--rejected,
.ap-status--error {
  color: #ef4444;
  font-weight: 600;
}

.ap-status--withdrawn {
  color: #f59e0b;
  font-weight: 600;
}
</style>
