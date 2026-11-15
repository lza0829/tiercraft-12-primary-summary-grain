<script setup>
import { onMounted, ref } from 'vue'
import { getJson, postJson } from '../api'

const domains = ref([])
const domainId = ref(1)
const jobs = ref([])
const err = ref('')
const busy = ref(false)

async function refresh() {
  jobs.value = await getJson(`/api/jobs?domain_id=${domainId.value}`)
}

onMounted(async () => {
  try {
    domains.value = await getJson('/api/domains')
    if (domains.value.length) domainId.value = domains.value[0].id
    await refresh()
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function call(url, body) {
  busy.value = true
  err.value = ''
  try {
    await postJson(url, { domain_id: domainId.value, ...body })
    await refresh()
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

const runPasteToDetail = () => call('/api/jobs/paste-to-detail')
const runMainSummary = () => call('/api/jobs/detail-to-summary')
const runBypass = (simulateFailure = false) =>
  call('/api/jobs/detail-to-category-summary', { simulate_failure: simulateFailure })

function laneClass(lane) {
  return lane === '品类旁路' ? 'lane-bypass' : 'lane-main'
}
function statusClass(status) {
  return status === '成功' || status === '一致' ? 'ok' : status === '失败' ? 'fail' : 'warn'
}
</script>
<template>
  <div>
    <h2>分层任务</h2>
    <p class="lead">
      主路径只写主汇总层（业务日+门店编码）；品类旁路是独立任务、独立旁路表、独立失败域，
      旁路失败只标记旁路任务并保留原因，不会回滚或锁死主汇总，也不会影响主对账结论。
    </p>
    <div class="toolbar">
      <label>
        主题域
        <select v-model.number="domainId" @change="refresh">
          <option v-for="d in domains" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </label>
    </div>

    <div class="lane-section">
      <h3><span class="lane-tag lane-main">主路径</span> 主汇总链</h3>
      <div class="toolbar">
        <button :disabled="busy" @click="runPasteToDetail">跑贴源到明细</button>
        <button class="secondary" :disabled="busy" @click="runMainSummary">跑明细到主汇总（业务日+门店）</button>
      </div>
    </div>

    <div class="lane-section">
      <h3><span class="lane-tag lane-bypass">品类旁路</span> 独立旁路任务</h3>
      <div class="toolbar">
        <button :disabled="busy" @click="runBypass(false)">跑品类旁路汇总（业务日+门店+品类）</button>
        <button class="danger" :disabled="busy" @click="runBypass(true)">模拟旁路失败（验证隔离）</button>
      </div>
      <p class="muted small">
        模拟失败时旁路写入整笔回滚，仅生成一条「失败」旁路任务记录；主汇总层与对账不受影响。
      </p>
    </div>

    <p v-if="err" class="err">{{ err }}</p>
    <div class="panel">
      <table>
        <thead>
          <tr>
            <th>编号</th><th>通道</th><th>步骤</th><th>状态</th><th>说明</th>
            <th>输入</th><th>写入</th><th>剔除</th><th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="j in jobs" :key="j.id">
            <td>{{ j.id }}</td>
            <td><span :class="['lane-tag', laneClass(j.lane)]">{{ j.lane || '主路径' }}</span></td>
            <td>{{ j.step_label || j.step }}</td>
            <td :class="statusClass(j.status)">{{ j.status }}</td>
            <td>{{ j.message }}</td>
            <td>{{ j.in_count }}</td>
            <td>{{ j.out_count }}</td>
            <td>{{ j.drop_count }}</td>
            <td>{{ j.created_at }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="!jobs.length" class="muted">还没有任务记录。</p>
    </div>
  </div>
</template>
