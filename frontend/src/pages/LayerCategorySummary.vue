<script setup>
import { onMounted, ref } from 'vue'
import { getJson } from '../api'

const rows = ref([])
const err = ref('')

onMounted(async () => {
  try {
    rows.value = await getJson('/api/layers/品类旁路')
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>
<template>
  <div>
    <h2>品类旁路汇总 <span class="lane-tag">旁路</span></h2>
    <p class="lead">
      独立旁路表，粒度为业务日+门店编码+品类，由独立的品类旁路任务写入。
      旁路不写入主汇总层，也不参与层间对账；旁路失败不会回滚或锁死主汇总。
    </p>
    <p v-if="err" class="err">{{ err }}</p>
    <div class="panel bypass-panel">
      <table>
        <thead>
          <tr>
            <th>编号</th><th>主题域</th><th>业务日</th><th>门店编码</th><th>品类</th>
            <th>金额合计</th><th>件数合计</th><th>明细行数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id">
            <td>{{ r.id }}</td>
            <td>{{ r.domain_id }}</td>
            <td>{{ r.biz_day }}</td>
            <td>{{ r.store_code }}</td>
            <td>{{ r.category }}</td>
            <td>{{ r.amount_sum }}</td>
            <td>{{ r.qty_sum }}</td>
            <td>{{ r.line_count }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="!rows.length" class="muted">
        旁路表为空，请到「分层任务」执行品类旁路汇总；该表为空不影响主汇总对账。
      </p>
    </div>
  </div>
</template>
