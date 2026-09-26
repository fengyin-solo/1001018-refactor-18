<template>
  <section class="page" data-module="plan-detail">
    <header class="page-head">
      <div>
        <h2>养护计划详情</h2>
        <p class="page-desc">查看计划周期、预算金额与统一开工条件结论，并执行养护计划状态流转。</p>
      </div>
      <div class="page-actions">
        <RouterLink class="btn" to="/plan">返回列表</RouterLink>
      </div>
    </header>

    <div v-if="entry" class="detail-panel">
      <dl class="detail-grid">
        <div v-for="column in columns" :key="column" class="detail-item">
          <dt>{{ column }}</dt>
          <dd>{{ entry[column] ?? '—' }}</dd>
        </div>
      </dl>

      <div class="condition-panel" :class="condition?.allowed ? 'allowed' : 'blocked'">
        <strong>{{ condition?.allowed ? '允许开工' : '暂不能开工' }}</strong>
        <span>{{ condition?.reason }}</span>
      </div>

      <div class="detail-actions">
        <button
          v-for="action in actions"
          :key="action"
          class="btn"
          type="button"
          :disabled="Boolean(startBlockReason(entry, action))"
          :title="startBlockReason(entry, action)"
          @click="runAction(action)"
        >
          {{ action }}
        </button>
      </div>
    </div>

    <div v-else class="detail-empty">{{ errorMessage || '养护计划不存在或已归档' }}</div>

    <footer class="page-foot">
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { fetchJson } from '@/api/client'
import {
  PLAN_ACTIONS,
  PLAN_COLUMNS,
  PLAN_ENDPOINT,
  type PlanEntry,
  runPlanAction,
  startBlockReason,
  startCondition,
} from '@/views/plan/shared'

const route = useRoute()
const entry = ref<PlanEntry | null>(null)
const errorMessage = ref('')
const columns = PLAN_COLUMNS
const actions = PLAN_ACTIONS
const condition = computed(() => (entry.value ? startCondition(entry.value) : undefined))

async function load() {
  errorMessage.value = ''
  try {
    entry.value = await fetchJson<PlanEntry>(`${PLAN_ENDPOINT}/${route.params.id}`)
  } catch (error) {
    entry.value = null
    errorMessage.value = error instanceof Error ? error.message : '养护计划详情读取失败'
  }
}

async function runAction(action: string) {
  if (!entry.value) {
    return
  }
  const blockedReason = startBlockReason(entry.value, action)
  if (blockedReason) {
    errorMessage.value = blockedReason
    return
  }

  errorMessage.value = ''
  try {
    const result = await runPlanAction(entry.value.id, action)
    if (!result.ok) {
      throw new Error(result.message)
    }
    await load()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '养护计划操作失败'
  }
}

watch(() => route.params.id, load)
onMounted(load)
</script>

<style scoped>
.detail-panel {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 0;
}

.detail-item {
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}

.detail-item dt {
  color: var(--muted);
  font-size: 12px;
}

.detail-item dd {
  margin: 4px 0 0;
  font-size: 14px;
}

.condition-panel {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 16px;
  padding: 10px 12px;
  border-radius: 6px;
}

.condition-panel.allowed {
  background: #ecfdf3;
  color: #027a48;
}

.condition-panel.blocked {
  background: #fef3f2;
  color: #b42318;
}

.detail-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.detail-empty {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--muted);
  padding: 24px;
}
</style>
