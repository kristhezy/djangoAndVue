<template>
  <div class="delcp-page">
    <div class="delcp-cols">
      <!-- 卡片1: 删除线索/合伙人 -->
      <el-card class="delcp-card" shadow="never">
        <template #header>
          <div class="delcp-title">删除线索/合伙人</div>
        </template>
        <el-form label-width="90px">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form1.companyName" placeholder="请输入企业ID" />
          </el-form-item>
          <el-form-item label="企业名称" required>
            <el-select v-model="form1.companyId" placeholder="输入企业ID" style="width:100%" @change="onCompanyChange">
              <el-option label="输入企业ID" value="" />
              <el-option-group label="🔽【prod】">
                <el-option v-for="c in companies.prod" :key="c.id" :label="c.name" :value="c.id" />
              </el-option-group>
              <el-option-group label="🔽【test】">
                <el-option v-for="c in companies.test" :key="c.id" :label="c.name" :value="c.id" />
              </el-option-group>
            </el-select>
          </el-form-item>
          <el-form-item label="用户 ID" required>
            <el-input v-model="form1.userId" />
          </el-form-item>
          <el-form-item label="合伙人 ID">
            <el-input v-model="form1.ppidcontent" :disabled="form1.delcheck !== 'delpartner'" />
          </el-form-item>
          <el-form-item label="删除类型">
            <el-radio-group v-model="form1.delcheck">
              <el-radio value="delclue">删除线索</el-radio>
              <el-radio value="delpartner">删除合伙人</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form1.env" :disabled="envLocked">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="delcp-actions">
            <el-button type="primary" :loading="loading1" @click="cleanClue">提交</el-button>
            <el-button @click="resetForm1">重置</el-button>
          </div>
          <div class="delcp-note">※ 删除合伙人时:【先删除合伙人，再删除线索数据】</div>
          <div class="result">{{ result1 }}</div>
        </el-form>
      </el-card>

      <!-- 卡片2: 根据手机号查询用户ID -->
      <el-card class="delcp-card" shadow="never">
        <template #header>
          <div class="delcp-title">根据手机号查询用户ID</div>
        </template>
        <el-form label-width="90px">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form2.cid" />
          </el-form-item>
          <el-form-item label="手机号" required>
            <el-input v-model="form2.tel" maxlength="11" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form2.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="delcp-actions">
            <el-button type="primary" :loading="loading2" @click="queryByCp">提交</el-button>
            <el-button @click="resetForm2">重置</el-button>
          </div>
          <div class="result">{{ result2 }}</div>
        </el-form>
      </el-card>

      <!-- 卡片3: 销售添加线索 -->
      <el-card class="delcp-card" shadow="never">
        <template #header>
          <div class="delcp-title">销售添加线索</div>
        </template>
        <el-form label-width="90px">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form3.companyId" />
          </el-form-item>
          <el-form-item label="员工 ID" required>
            <el-input v-model="form3.cardId" />
          </el-form-item>
          <el-form-item label="用户姓名" required>
            <el-input v-model="form3.userName" />
          </el-form-item>
          <el-form-item label="用户手机" required>
            <el-input v-model="form3.userTel" maxlength="11" />
          </el-form-item>
          <el-form-item label="合伙人 ID">
            <el-input v-model="form3.pId" />
          </el-form-item>
          <el-form-item label="是否批量">
            <el-checkbox v-model="form3.batch" />
            <el-input v-model="form3.batchNum" :disabled="!form3.batch" placeholder="输入2~1000的整数" class="batch-input" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form3.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="delcp-actions">
            <el-button type="primary" :loading="loading3" @click="addClue">提交</el-button>
            <el-button @click="resetForm3">重置</el-button>
          </div>
          <div class="result">{{ result3 }}</div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

// 硬编码企业列表（复刻旧模板 AT_delCP.html 第 78-100 行）
const companies = {
  prod: [
    { id: '1021060956165488640', name: '招商版小程序测试企业1' },
    { id: '839508475783573504', name: '加推（测试）' },
    { id: '1040268843043500032', name: '超级推广部' },
    { id: '1012037449188364288', name: '深圳灰度测试企业5' },
    { id: '532972735412850688', name: '铁岭县供销合作社联合社' },
    { id: '1069929980139683840', name: '深圳市加推科技有限公司' },
    { id: '1189258248478707712', name: '红蚂蚁测试企业1' },
    { id: '1189258337557340160', name: '点石测试企业1' },
    { id: '1192136192859492352', name: '红蚂蚁装饰股份有限公司' },
    { id: '693225071459762176', name: '石家庄七度文化传播有限公司' },
    { id: '844635664262787073', name: '石家庄七度文化传播有限公司转介绍' },
  ],
  test: [
    { id: '1017368198385172480', name: '招商版测试企业7' },
    { id: '755550234976985088', name: '百度（中国）有限公司' },
    { id: '1035144123776442368', name: '招商版小程序测试企业8' },
    { id: '846400679986987008', name: '云盘版转介绍3' },
    { id: '870366245806292992', name: '北京积木世纪教育科技' },
    { id: '874593368431542272', name: '深圳市兴光电子有限公司' },
    { id: '1181172541784809472', name: '红蚂蚁家装' },
    { id: '1185152155297222656', name: '点石家装' },
  ],
}

const envLocked = ref(false)

const form1 = reactive({
  companyName: '',
  companyId: '',
  userId: '',
  ppidcontent: '',
  delcheck: 'delclue',
  env: 'prod',
})
const form2 = reactive({ cid: '', tel: '', env: 'prod' })
const form3 = reactive({
  companyId: '', cardId: '', userName: '', userTel: '', pId: '',
  batch: false, batchNum: '', env: 'prod',
})

const result1 = ref('')
const result2 = ref('')
const result3 = ref('')
const loading1 = ref(false)
const loading2 = ref(false)
const loading3 = ref(false)

function onCompanyChange(val) {
  if (val === '') {
    form1.companyName = ''
    form1.env = 'test'
    form2.env = 'test'
    envLocked.value = false
  } else {
    form1.companyName = val
    form2.cid = val
    const isProd = companies.prod.some(c => c.id === val)
    form1.env = isProd ? 'prod' : 'test'
    form2.env = isProd ? 'prod' : 'test'
    envLocked.value = true
  }
}

async function cleanClue() {
  const compid = form1.companyName || form1.companyId
  if (!compid) { ElMessage.warning('请先选择企业！'); return }
  if (!form1.userId) { ElMessage.warning('用户ID不能为空！'); return }
  if (form1.delcheck === 'delpartner' && !form1.ppidcontent) {
    ElMessage.warning('合伙人ID不能为空！'); return
  }
  loading1.value = true
  try {
    const resp = await http.post('/sv/delclueinfo', {
      companyId: compid, userId: form1.userId, ppc: form1.ppidcontent,
      delcheck: form1.delcheck, env: form1.env, check: 'del',
    })
    result1.value = resp.data?.data || ''
  } catch (e) {
    result1.value = ''
    ElMessage.error('删除失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading1.value = false
  }
}

async function queryByCp() {
  const cid = form2.cid
  const tel = form2.tel
  if (cid.length < 18 || isNaN(cid)) { ElMessage.warning('企业ID只能是大于等于18位的纯数字！'); return }
  if (tel.length !== 11 || isNaN(tel)) { ElMessage.warning('手机号只能为11位纯数字！'); return }
  loading2.value = true
  try {
    const resp = await http.post('/sv/queryuibycp', { cid, tel, env: form2.env })
    const d = resp.data?.data
    if (d) {
      result2.value = d.partnerId ? `userId: ${d.userId}, partnerId: ${d.partnerId}` : `userId: ${d.userId}`
      form1.userId = d.userId || ''
      form1.ppidcontent = d.partnerId || ''
    }
  } catch (e) {
    result2.value = ''
    ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading2.value = false
  }
}

async function addClue() {
  const { companyId, cardId, userName, userTel, pId, batch, batchNum, env } = form3
  let bn = 1
  if (batch) {
    if (!batchNum || isNaN(batchNum) || batchNum <= 1 || batchNum > 1000) {
      ElMessage.warning('批量数为[2~1000]之间的整数！'); return
    }
    bn = batchNum
  }
  if (!companyId || !cardId || !userName || !userTel) { ElMessage.warning('必填项不能为空！'); return }
  if (companyId.length < 18 || companyId.length > 19 || isNaN(companyId)) { ElMessage.warning('企业ID只能是18或19位的纯数字！'); return }
  if (userTel.length !== 11 || isNaN(userTel)) { ElMessage.warning('手机号只能是11位的纯数字！'); return }
  loading3.value = true
  try {
    const resp = await http.post('/sv/saci', { cid: companyId, cardid: cardId, uname: userName, utel: userTel, bn, pId, env })
    result3.value = resp.data?.data || ''
  } catch (e) {
    result3.value = ''
    ElMessage.error('添加失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading3.value = false
  }
}

function resetForm1() {
  form1.companyName = ''; form1.companyId = ''; form1.userId = ''
  form1.ppidcontent = ''; form1.delcheck = 'delclue'; form1.env = 'prod'
  envLocked.value = false
  result1.value = ''
}
function resetForm2() {
  form2.cid = ''; form2.tel = ''; form2.env = 'prod'
  result2.value = ''
}
function resetForm3() {
  form3.companyId = ''; form3.cardId = ''; form3.userName = ''; form3.userTel = ''
  form3.pId = ''; form3.batch = false; form3.batchNum = ''; form3.env = 'prod'
  result3.value = ''
}
</script>

<style scoped>
.delcp-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}

.delcp-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}

.delcp-card {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.delcp-card :deep(.el-card__body) {
  overflow-y: auto;
}

.delcp-title {
  text-align: center;
  font-weight: 600;
  font-size: 18px;
}

.delcp-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 12px 0;
}

.delcp-note {
  font-size: 12px;
  color: #f56c6c;
  text-align: center;
  margin: 6px 0;
}

.result {
  margin-top: 12px;
  font-size: 14px;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
  text-align: center;
}

.batch-input {
  width: 140px;
  margin-left: 8px;
}
</style>
