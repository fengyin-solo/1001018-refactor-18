<template>
  <section class="page" data-module="plan">
    <header class="page-head">
      <div>
        <h2>养护计划管理</h2>
        <p class="page-desc">维护养护计划，围绕计划编号、计划周期、计划类型、覆盖设施做登记、筛选与状态流转。</p>
      </div>
      <div class="page-actions">
        <button class="btn primary" type="button" @click="openCreate">登记养护计划</button>
        <button class="btn" type="button" @click="exportRows">导出养护计划清单</button>
      </div>
    </header>

    <div class="stat-row">
      <article v-for="item in stats" :key="item.label" class="stat-card">
        <span class="stat-label">{{ item.label }}</span>
        <strong class="stat-value">{{ item.value }}</strong>
      </article>
    </div>

    <form class="filter-bar" @submit.prevent="reload">
      <label v-for="field in filterFields" :key="field" class="filter-item">
        <span>{{ field }}</span>
        <input v-model="filters[field]" :placeholder="`按${field}检索`" />
      </label>
      <button class="btn" type="submit">查询</button>
      <button class="btn ghost" type="button" @click="resetFilters">重置条件</button>
    </form>

    <table class="data-table">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column">{{ column }}</th>
          <th>可执行动作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="String(row.id)">
          <td v-for="column in columns" :key="column">{{ row[column] ?? '—' }}</td>
          <td class="row-actions">
            <button
              v-for="action in actions"
              :key="action"
              class="link"
              type="button"
              :disabled="action === START_ACTION && !canStart(row)"
              :title="action === START_ACTION ? startTip(row) : ''"
              @click="runAction(action, row)"
            >
              {{ action }}
            </button>
            <RouterLink class="link" :to="`/plan/${row.id}`">详情</RouterLink>
          </td>
        </tr>
        <tr v-if="!rows.length">
          <td :colspan="columns.length + 1" class="empty-state">暂无养护计划数据，可先登记养护计划</td>
        </tr>
      </tbody>
    </table>

    <footer class="page-foot">
      <span>共 {{ total }} 条养护计划记录</span>
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { request } from '@/api/client'

type Row = Record<string, string | number | null>
type StartCheck = { ok: boolean; message: string; reasons: string[] }

const ENDPOINT = '/api/plan'
const START_ACTION = '启动执行'
const columns = ["计划编号", "计划周期", "计划类型", "覆盖设施", "计划内容", "预算金额", "编制人", "计划状态"]
const actions = ["编制计划", "审批计划", "启动执行"]
const statuses = ["待编制", "已编制", "已审批", "执行中"]
const stats = [{"label": "待编制计划", "value": 0}, {"label": "已审批计划", "value": 0}, {"label": "执行中计划", "value": 0}]

const rows = ref<Row[]>([])
const total = ref(0)
const errorMessage = ref('')
const filters = ref<Record<string, string>>({})
const filterFields = columns.slice(0, 3)
// 开工条件结论全部来自后端同一份实现，前端只展示、不自行判断
const startChecks = ref<Record<string, StartCheck>>({})

function planNo(row: Row) {
  return String(row['计划编号'] ?? '')
}

function canStart(row: Row) {
  const check = startChecks.value[planNo(row)]
  return check ? check.ok : true
}

function startTip(row: Row) {
  const check = startChecks.value[planNo(row)]
  return check ? check.message : '开工条件确认中'
}

function resetFilters() {
  filters.value = {}
  void reload()
}

function exportRows() {
  window.open(`${ENDPOINT}/export`, '_blank')
}

function openCreate() {
  errorMessage.value = '养护计划登记入口尚未接入审批流'
}

async function runAction(action: string, row: Row) {
  errorMessage.value = ''
  try {
    const response = await request(`${ENDPOINT}/${row.id}/actions`, {
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
  const query = new URLSearchParams(filters.value as Record<string, string>).toString()
  try {
    const response = await request(`${ENDPOINT}?${query}`)
    if (!response.ok) {
      throw new Error('养护计划列表读取失败')
    }
    const payload = await response.json()
    rows.value = payload.items ?? []
    total.value = payload.total ?? rows.value.length
    await refreshStartChecks(rows.value)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '养护计划列表读取失败'
  }
}

async function refreshStartChecks(items: Row[]) {
  const results = await Promise.all(
    items.map(async (row) => {
      const no = planNo(row)
      if (!no) {
        return null
      }
      try {
        const response = await request(`${ENDPOINT}/start-check?plan_no=${encodeURIComponent(no)}`)
        if (!response.ok) {
          return null
        }
        return [no, (await response.json()) as StartCheck] as const
      } catch {
        return null
      }
    }),
  )
  const map: Record<string, StartCheck> = {}
  for (const result of results) {
    if (result) {
      map[result[0]] = result[1]
    }
  }
  startChecks.value = map
}

onMounted(reload)
</script>
