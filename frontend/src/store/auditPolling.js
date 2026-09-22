import { defineStore } from 'pinia'
import { ref, readonly } from 'vue'
import http from '../api/http'

const POLL_INTERVAL = 150000 // 15秒

export const useAuditPolling = defineStore('auditPolling', () => {
  const status = ref('idle')    // idle | polling | passed | publishing | published | rejected | error | withdrawn
  const count = ref(0)
  const message = ref('')
  const company = ref({ phone: '', cid: '', cn: '', appid: '', env: 'prod' })
  let timer = null

  function _clearTimer() {
    if (timer) { clearInterval(timer); timer = null }
  }

  function start(info) {
    if (status.value === 'polling') return // 已在轮询中，不重复启动
    company.value = { ...info }
    status.value = 'polling'
    count.value = 0
    message.value = '轮询中…'
    _check() // 立即查一次
    timer = setInterval(_check, POLL_INTERVAL)
  }

  function stop() {
    _clearTimer()
    if (status.value === 'polling') {
      status.value = 'idle'
      message.value = '已手动停止'
    }
  }

  function dismiss() {
    _clearTimer()
    status.value = 'idle'
    message.value = ''
    count.value = 0
  }

  async function _check() {
    count.value++
    message.value = `第 ${count.value} 次查询…`
    try {
      const resp = await http.post('/sv/miniprogramRelease/auditAndRelease', {
        ts: 'ads',
        phone: company.value.phone,
        cid: company.value.cid,
        cn: company.value.cn,
        appid: company.value.appid,
        env: company.value.env,
        type: 'auditAndRelease',
      })
      const data = resp.data?.data
      if (resp.data?.code != 0) {
        _clearTimer()
        status.value = 'error'
        message.value = data?.rlt || '查询异常'
        return
      }
      const rlt = data?.rlt || ''
      if (rlt.includes('审核成功') || rlt.includes('「审核成功」')) {
        // 审核通过 → 自动发布
        _clearTimer()
        status.value = 'passed'
        message.value = '审核通过，正在自动发布…'
        await _publish()
      } else if (rlt.includes('审核中')) {
        message.value = `审核中…（第 ${count.value} 次）`
        // status stays 'polling'
      } else if (rlt.includes('已撤回')) {
        _clearTimer()
        status.value = 'withdrawn'
        message.value = rlt
      } else if (rlt.includes('审核延后')) {
        message.value = `审核延后…（第 ${count.value} 次）`
      } else {
        // 审核被拒或其他
        _clearTimer()
        status.value = 'rejected'
        message.value = rlt || '审核未通过'
      }
    } catch (e) {
      _clearTimer()
      status.value = 'error'
      message.value = '网络异常：' + (e?.message || '请求失败')
    }
  }

  async function _publish() {
    status.value = 'publishing'
    try {
      const resp = await http.post('/sv/miniprogramRelease/auditAndRelease', {
        ts: 'rls',
        phone: company.value.phone,
        cid: company.value.cid,
        cn: company.value.cn,
        appid: company.value.appid,
        env: company.value.env,
        type: 'auditAndRelease',
      })
      const data = resp.data?.data
      if (resp.data?.code == 0) {
        status.value = 'published'
        message.value = data?.rlt || '发布成功！'
      } else {
        status.value = 'error'
        message.value = '发布失败：' + (data?.rlt || '未知错误')
      }
    } catch (e) {
      status.value = 'error'
      message.value = '发布请求失败：' + (e?.message || '')
    }
  }

  return {
    status: readonly(status),
    count: readonly(count),
    message: readonly(message),
    company: readonly(company),
    start,
    stop,
    dismiss,
  }
})
