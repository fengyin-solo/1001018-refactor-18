<template>
  <section class="page" data-module="plan">
    <header class="page-head">
      <div>
        <h2>养护计划详情</h2>
        <p class="page-desc">开工条件结论与列表按钮、动作接口共用后端同一份实现，页面不自行判断。</p>
      </div>
      <div class="page-actions">
        <button class="btn ghost" type="button" @click="goBack">返回列表</button>
      </div>
    </header>

    <table v-if="entry" class="data-table">
      <tbody>
        <tr v-for="field in fields" :key="field">
          <th>{{ field }}</th>
          <td>{{ entry[field] ?? '—' }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="startCheck" class="stat-row">
      <article class="stat-card">
        <span class="stat-label">开工条件</span>
        <strong class="stat-value">{{ startCheck.ok ? '满足' : '不满足' }}</strong>
        <p class="page-desc">{{ startCheck.message }}</p>
      </article>
    </div>

    <div v-if="entry" class="row-actions">
      <button
        v-for="action in actions"
        :key="action"
        class="link"
        type="button"
        :disabled="action === START_ACTION && startCheck !== null && !startCheck.ok"
        :title="action === START_ACTION && startCheck ? startCheck.message : ''"
        @click="runAction(action)"
      >
        {{ action }}
      </button>
    </div>

    <footer class="page-foot">
      <span v-if="entry">计划编号：{{ entry['计划编号'] ?? '—' }}</span>
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { request } from '@/api/client'

type Row = Record<string, string | number | null>
type StartCheck = { ok: boolean; message: string; reasons: string[] }

const ENDPOINT = '/api/plan'
const START_ACTION = '启动执行'
const fields = ["计划编号", "计划周期", "计划类型", "覆盖设施", "计划内容", "预算金额", "编制人", "计划状态"]
const actions = ["编制计划", "审批计划", "启动执行"]

const route = useRoute()
const router = useRouter()
const entry = ref<Row | null>(null)
const startCheck = ref<StartCheck | null>(null)
const errorMessage = ref('')

function goBack() {
  void router.push('/plan')
}

async function runAction(action: string) {
  errorMessage.value = ''
  try {
    const response = await request(`${ENDPOINT}/${route.params.id}/actions`, {
      method: 'POST',
      body: JSON.stringify({ values: { action } }),
    })
    const payload = await response.json()
    if (!response.ok || !payload.ok) {
      throw new Error(payload.message ?? '养护计划动作未生效，请稍后重试')
    }
    await reload()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '养护计划操作失败'
  }
}

async function reload() {
  errorMessage.value = ''
  try {
    const response = await request(`${ENDPOINT}/${route.params.id}`)
    const payload = await response.json()
    if (!response.ok) {
      throw new Error(payload.detail ?? '养护计划详情读取失败')
    }
    entry.value = payload
    const planNo = String(payload['计划编号'] ?? '')
    if (planNo) {
      const checkResponse = await request(`${ENDPOINT}/start-check?plan_no=${encodeURIComponent(planNo)}`)
      if (checkResponse.ok) {
        startCheck.value = (await checkResponse.json()) as StartCheck
      }
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '养护计划详情读取失败'
  }
}

onMounted(reload)
</script>
