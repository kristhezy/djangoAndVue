<template>
  <div class="home-page">
    <!-- 快捷入口 -->
    <section class="panel panel--centered">
      <h2 class="panel__title">快捷入口</h2>
      <div class="quick-grid">
        <div v-for="c in quickCards" :key="c.name" class="quick-card" :class="{ 'quick-card--highlight': c.highlight }">
          <div class="quick-card__name">{{ c.name }}</div>
          <div v-for="r in c.rows" :key="r.env" class="quick-card__row">
            <span class="quick-card__env">{{ r.env }}</span>
            <span v-if="!r.href" class="empty">/</span>
            <a v-else :class="r.avail ? 'useable' : 'notavailable'"
              :href="r.href" target="_blank" rel="noopener noreferrer"
              @click="!r.avail && $event.preventDefault()">{{ r.label }}</a>
          </div>
        </div>
      </div>
    </section>

    <!-- 常用工具 -->
    <section class="panel panel--centered">
      <h2 class="panel__title">常用工具</h2>
      <div class="link-grid">
        <a v-for="l in commonTools" :key="l.label" class="tool-link"
          :href="l.href" target="_blank" rel="noopener noreferrer">{{ l.label }}</a>
      </div>
    </section>

    <!-- 工作相关 -->
    <section class="panel panel--centered">
      <h2 class="panel__title">工作相关</h2>
      <div class="link-grid">
        <div v-for="r in resources" :key="r.title" class="resource-card">
          <div class="resource-card__title">{{ r.title }}</div>
          <div class="resource-card__links">
            <a v-for="l in r.links" :key="l.label" :href="l.href" target="_blank"
              rel="noopener noreferrer">{{ l.label }}</a>
          </div>
        </div>
        <a v-for="l in workLinks" :key="l.label" class="tool-link" :class="{ 'tool-link--danger': l.danger }"
          :href="l.href" target="_blank" rel="noopener noreferrer">{{ l.label }}</a>
      </div>
    </section>
  </div>
</template>

<script setup>
// 快捷入口：每卡片三个环境行，href 为空表示「无入口」
const quickCards = [
  {
    name: 'k8s平台',
    rows: [
      { env: '测试', label: 'msr-test', href: 'http://msr.jiatuitest.com/service-envdirect/index.html', avail: false },
      { env: '生产', label: '', href: '' },
      { env: '灰度', label: '', href: '' },
    ],
  },
  {
    name: 'kibana',
    rows: [
      { env: '测试', label: 'kibana-test', href: 'http://dev-kibana-log.jiatuiyun.net/app/kibana#/discover', avail: false },
      { env: '生产', label: '', href: '' },
      { env: '灰度', label: '', href: '' },
    ],
  },
  {
    name: '老企管后台',
    rows: [
      { env: '测试', label: 'bms-test', href: 'https://test.aijiatui.com/bms/#/', avail: false },
      { env: '生产', label: 'bms-business', href: 'https://business.aijiatui.com/bms/#/', avail: true },
      { env: '灰度', label: 'bms-shop', href: 'https://business.aijiatui.com/bms-shop/#/', avail: false },
    ],
  },
  {
    name: '私域流量后台',
    rows: [
      { env: '测试', label: 'refactor-test', href: 'https://test.aijiatui.com/refactor/#/', avail: false },
      { env: '生产', label: 'refactor-business', href: 'https://business.aijiatui.com/refactor/#/', avail: true },
      { env: '灰度', label: 'refactor-gray', href: 'https://business.aijiatui.com/refactor-gray/#/', avail: false },
    ],
  },
  {
    name: '招商版企管后台',
    rows: [
      { env: '测试', label: 'refactor-zs-test', href: 'https://test.aijiatui.com/refactor-zs/#/', avail: false },
      { env: '生产', label: 'refactor-zs-business', href: 'https://business.aijiatui.com/refactor-zs/#/', avail: true },
      { env: '灰度', label: 'refactor-zs-gray', href: 'https://business.aijiatui.com/refactor-zs-gray/#/', avail: false },
    ],
  },
  {
    name: '家装版企管后台',
    rows: [
      { env: '测试', label: 'refactor-jz-test', href: 'https://test.aijiatui.com/refactor-jz/#/', avail: false },
      { env: '生产', label: 'refactor-jz-business', href: 'https://business.aijiatui.com/refactor-jz/#/', avail: true },
      { env: '灰度', label: 'refactor-jz-gray', href: 'https://business.aijiatui.com/refactor-jz-gray/#/', avail: false },
    ],
  },
  {
    name: '电脑导入文件',
    highlight: true,
    rows: [
      { env: '测试', label: 'file-test', href: 'https://test-file.jiatui.com', avail: false },
      { env: '生产', label: 'file-business', href: 'https://file.jiatui.com', avail: true },
      { env: '灰度', label: 'file-gray', href: 'https://gray-file.jiatui.com', avail: false },
    ],
  },
  {
    name: '代理商后台',
    rows: [
      { env: '测试', label: 'agent-test', href: 'https://test-agent.aijiatui.com/agent/home#/login', avail: false },
      { env: '生产', label: 'agent-business', href: 'https://agent.aijiatui.com/agent/login', avail: true },
      { env: '灰度', label: '', href: '' },
    ],
  },
  {
    name: '小程序发版系统',
    rows: [
      { env: '测试', label: 'applet-test', href: 'https://test-code-publish.aijiatui.com/code-publish-h5/#/login', avail: false },
      { env: '生产', label: 'applet-online', href: 'https://code-publish.aijiatui.com/code-publish-h5/#/login', avail: true },
      { env: '灰度', label: '', href: '' },
    ],
  },
  {
    name: '运营后台',
    rows: [
      { env: '测试', label: 'bob-test', href: 'https://checkout-bob.aijiatui.com/#/user/login', avail: false },
      { env: '生产', label: 'bob-online', href: 'https://bob.aijiatui.com/#/user/login', avail: true },
      { env: '灰度', label: '', href: '' },
    ],
  },
  {
    name: 'SQL审核查询平台',
    rows: [
      { env: '测试', label: '', href: '' },
      { env: '生产', label: 'SqlProd', href: 'https://sqlprod.jiatuiyun.net/sqlquery/', avail: true },
      { env: '灰度', label: '', href: '' },
    ],
  },
  {
    name: '云端SSL VPN',
    rows: [
      { env: '测试', label: '', href: '' },
      { env: '生产', label: 'EASY CONNECT', href: 'https://wiki.jiatuiyun.net/pages/viewpage.action?pageId=30638081', avail: true },
      { env: '灰度', label: '', href: '' },
    ],
  },
]

const commonTools = [
  { label: '百度baidu', href: 'https://www.baidu.com/' },
  { label: '百度翻译', href: 'https://fanyi.baidu.com/' },
  { label: '时间戳工具', href: 'https://tool.lu/timestamp/' },
  { label: 'iOS证书信任设置', href: 'https://www.jianshu.com/p/abf793f91973?from=singlemessage' },
  { label: 'charles基本使用', href: 'https://jiatui.feishu.cn/docs/doccnVJbRfdIXZt0NRnC6tpcTzc' },
  { label: 'kibana之日志搜索', href: 'https://jiatui.feishu.cn/docs/doccnavbo3RLvyQ5JUM3E8tugBe' },
  { label: 'Jmeter在mac上的安装方法', href: 'https://www.jianshu.com/p/bce9077d883c' },
  { label: 'Jmeter组件简介', href: 'https://www.cnblogs.com/hle030609/p/9579805.html' },
  { label: '使用Jmeter进行接口测试', href: 'https://edu.csdn.net/course/detail/19762' },
  { label: 'UTF-8 编码转换工具', href: 'http://www.jsons.cn/utf8/' },
  { label: 'MD5在线加密', href: 'https://www.cmd5.com/' },
  { label: 'HTTP请求返回状态码详解', href: 'https://www.cnblogs.com/molson/p/7000841.html' },
  { label: '身份证查询大全', href: 'https://sfz.tool90.com/sfz/generate.html' },
  { label: '银行卡号查询', href: 'https://ddu1222.github.io/bankcard-validator/bcBuilder.html' },
  { label: '统一社会信用代码查询', href: 'https://www.creditchina.gov.cn/' },
]

const resources = [
  {
    title: '测试企业信息',
    links: [
      { label: '『飞书链接』', href: 'https://jiatui.feishu.cn/sheets/shtcnVgCQKJ2yoHk1OyjjQuCCBb?sheet=a95b37' },
      { label: '『钉钉链接』', href: 'https://alidocs.dingtalk.com/i/nodes/ZgpG2NdyVXrGP2j1TvBxnDoe8MwvDqPk' },
    ],
  },
  {
    title: '测试用例',
    links: [
      { label: '『飞书链接』', href: 'https://jiatui.feishu.cn/drive/folder/fldcnbgcCZMxzaCMRNKZJdsZaxx' },
      { label: '『钉钉链接』', href: 'https://qr.dingtalk.com/page/yunpan?route=previewDentry&spaceId=21592115021&fileId=104770321197&type=folder' },
    ],
  },
]

const workLinks = [
  { label: '测试新员工入职指引', href: 'https://jiatui.feishu.cn/docs/doccniDoBZ4OsOzpKzyztaxjZvt#' },
  { label: '企微绑定流程(钉钉)', href: 'https://alidocs.dingtalk.com/i/nodes/KGZLxjv9VG37nPYet9Xbyg4XV6EDybno', danger: true },
  { label: '企微绑定流程(旧-飞书)', href: 'https://jiatui.feishu.cn/docx/OChedR134oswndxFrPSc7ZVHnRd' },
  { label: '数据库表相关', href: 'https://jiatui.feishu.cn/docs/doccnIMKwfy5TQ2uZkgvM8Sx6Ah' },
  { label: 'OpenVPN客户端', href: 'https://wiki.jiatuiyun.net/pages/viewpage.action?pageId=41746439' },
  { label: '清除app登录token', href: 'https://jiatui.feishu.cn/docs/doccnQsky96ROBEzc2bRTeoTUxb' },
]
</script>

<style scoped>
.home-page {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  background: #f0f2f5;
}

.panel {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  padding: 24px;
  margin-bottom: 16px;
}
.panel:last-child { margin-bottom: 0; }
.panel--centered {
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
}
.panel__title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  padding-bottom: 8px;
  margin-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.useable { color: #409eff; }
.notavailable { color: #c0c4cc; text-decoration: line-through; cursor: not-allowed; }
.empty { color: #c0c4cc; }

.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.quick-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}
.quick-card--highlight { background: #ecf5ff; }
.quick-card__name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}
.quick-card--highlight .quick-card__name { color: #f56c6c; }
.quick-card__row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
  font-size: 14px;
}
.quick-card__env {
  width: 36px;
  flex-shrink: 0;
  font-size: 12px;
  color: #909399;
}

.link-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}
.tool-link {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
  color: #409eff;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.2s;
}
.tool-link:hover {
  border-color: #6366f1;
  background: #fafafa;
}
.tool-link--danger { color: #f56c6c; }

.resource-card {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
}
.resource-card__title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 10px;
}
.resource-card__links {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.resource-card__links a {
  font-size: 13px;
  color: #409eff;
}
</style>
