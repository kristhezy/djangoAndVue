<template>
  <div class="uci-page">
    <div class="uci-cols">
      <!-- 左栏：企业信息修改 -->
      <el-card class="uci-panel uci-panel--main" shadow="never">
        <template #header>
          <div class="uci-title">企业信息修改</div>
        </template>
        <el-form label-width="auto" label-position="top">
          <el-form-item label="企业ID" required>
            <el-input
              v-model="form.cid"
              type="textarea"
              :rows="3"
              placeholder="请输入企业ID，多个换行分隔"
            />
          </el-form-item>

          <div class="uci-row">
            <el-form-item label="企业名称">
              <el-input v-model="form.cname" placeholder="请输入企业名称" />
            </el-form-item>
            <el-form-item label="管理员姓名">
              <el-input v-model="form.admname" placeholder="请输入管理员名称" />
            </el-form-item>
          </div>

          <div class="uci-row">
            <el-form-item label="企业类型">
              <el-select v-model="form.ctype" clearable placeholder="请选择" style="width: 100%">
                <el-option label="7" value="7" />
                <el-option label="0" value="0" />
              </el-select>
            </el-form-item>
            <el-form-item label="付款方式">
              <el-select v-model="form.payment" clearable placeholder="请选择" style="width: 100%">
                <el-option label="预充值" value="3" />
                <el-option label="线下" value="0" />
              </el-select>
            </el-form-item>
          </div>

          <div class="uci-row">
            <el-form-item label="有效期限">
              <el-date-picker v-model="form.etime" type="date" value-format="YYYY-MM-DD"
                placeholder="请选择日期" style="width: 100%" />
            </el-form-item>
            <el-form-item label="雷达总数">
              <el-input v-model="form.rnum" placeholder="请输入雷达数" />
            </el-form-item>
          </div>

          <div class="uci-row">
            <el-form-item label="人资ID">
              <el-select v-model="form.tpid" clearable placeholder="请选择" style="width: 100%">
                <el-option label="1" value="1" />
              </el-select>
            </el-form-item>
            <el-form-item label="企业状态">
              <el-input v-model="form.cstatus" placeholder="状态:0禁用,1正常,2注销" />
            </el-form-item>
          </div>

          <div class="uci-row">
            <el-form-item label="企业/销售席位">
              <el-input v-model="form.tseat" placeholder="企业/销售席位" />
            </el-form-item>
            <el-form-item label="推荐官席位">
              <el-input v-model="form.ptseat" placeholder="推荐官席位" />
            </el-form-item>
          </div>

          <div class="uci-row">
            <el-form-item label="员工IDs">
              <el-input v-model="form.cardids" type="textarea" :rows="2" placeholder="员工IDs" />
            </el-form-item>
            <el-form-item label="雷达状态">
              <el-select v-model="form.rs" clearable placeholder="请选择雷达状态" style="width: 100%">
                <el-option label="关闭" value="0" />
                <el-option label="AI雷达" value="1" />
                <el-option label="AI和BOSS雷达" value="3" />
              </el-select>
            </el-form-item>
          </div>

          <el-form-item label="环境">
            <el-radio-group v-model="form.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>

          <div class="uci-actions">
            <el-button type="primary" :loading="loading" @click="submit">提交</el-button>
            <el-button @click="reset">重置</el-button>
          </div>

          <div v-if="result1" class="uci-result" v-html="sanitize(result1)"></div>
        </el-form>
      </el-card>

      <!-- 右栏：最近更新记录 -->
      <OperationLog ref="log" :ds="[4]" :init-num="10" title="最近更新记录" />
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'
import OperationLog from '../../components/OperationLog.vue'

const form = reactive({
  cid: '', cname: '', admname: '', ctype: '', payment: '', etime: '',
  tpid: '', cstatus: '', rnum: '', tseat: '', ptseat: '', cardids: '', rs: '', env: 'prod',
})
const result1 = ref('')
const loading = ref(false)
const log = ref(null)

// 后端返回含 <br/> 与 <p style='color:red'> 等，转义后还原 <b>/<br/> 防 XSS
function sanitize(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/&lt;b&gt;/gi, '<b>')
    .replace(/&lt;\/b&gt;/gi, '</b>')
    .replace(/&lt;br\s*\/?&gt;/gi, '<br/>')
}

// 提交字段除 cid 全为空 → 报错（与模板一致）
function isEmpty() {
  const { cname, admname, ctype, payment, etime, tpid, cstatus, rnum, tseat, ptseat, cardids } = form
  return [cname, admname, ctype, payment, etime, tpid, cstatus, rnum, tseat, ptseat, cardids]
    .every(v => v === '')
}

async function submit() {
  if (!form.cid) {
    ElMessage.warning('企业id不能为空！')
    return
  }
  if (isEmpty()) {
    ElMessage.warning('修改类型不能全部为空！')
    return
  }
  loading.value = true
  try {
    const resp = await http.post('/sv/updateCInfo', { ...form })
    result1.value = resp.data?.data || ''
    // 提交成功后清空所有 text 字段与 select
    form.cname = ''
    form.admname = ''
    form.rnum = ''
    form.cstatus = ''
    form.tseat = ''
    form.ptseat = ''
    form.cardids = ''
    form.ctype = ''
    form.payment = ''
    form.etime = ''
    form.tpid = ''
    form.rs = ''
    log.value?.refresh(10)
  } catch (e) {
    result1.value = ''
    ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

function reset() {
  Object.assign(form, {
    cid: '', cname: '', admname: '', ctype: '', payment: '', etime: '',
    tpid: '', cstatus: '', rnum: '', tseat: '', ptseat: '', cardids: '', rs: '', env: 'prod',
  })
  result1.value = ''
}
</script>

<style scoped>
.uci-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.uci-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.uci-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.uci-panel--main {
  flex: 1.2;
}
.uci-panel :deep(.el-card__body) {
  overflow-y: auto;
}
.uci-title {
  text-align: center;
  font-weight: 600;
  font-size: 16px;
}
.uci-row {
  display: flex;
  gap: 16px;
}
.uci-row .el-form-item {
  flex: 1;
  min-width: 0;
}
.uci-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 12px 0;
}
.uci-result {
  margin-top: 12px;
  padding: 10px;
  font-size: 14px;
  color: #303133;
  word-break: break-all;
  border-top: 1px solid #e4e7ed;
}
.uci-result :deep(b) {
  font-weight: 700;
  color: #303133;
}
</style>
