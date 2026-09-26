import { request } from '@/api/client'

export const PLAN_ENDPOINT = '/api/plan'
export const PLAN_COLUMNS = [
  '计划编号',
  '计划周期',
  '计划类型',
  '覆盖设施',
  '计划内容',
  '预算金额',
  '编制人',
  '计划状态',
] as const
export const PLAN_ACTIONS = ['编制计划', '审批计划', '启动执行']
export const SUBMIT_APPROVAL_ACTION = '审批计划'
export const START_ACTION = '启动执行'
export const CONDITION_CHECKED_ACTIONS = new Set([SUBMIT_APPROVAL_ACTION, START_ACTION])
export const START_CONDITION_FIELD = '开工条件'

export type PlanRow = Record<string, string | number | null>

export type StartCondition = {
  planCode: string
  period: string | null
  budget: number | null
  allowed: boolean
  reason: string
}

export type PlanEntry = PlanRow & {
  id: number
  status: string
  [START_CONDITION_FIELD]?: StartCondition
}

export function startCondition(row: PlanRow): StartCondition | undefined {
  const condition = row[START_CONDITION_FIELD]
  return typeof condition === 'object' && condition !== null
    ? (condition as StartCondition)
    : undefined
}

export function startBlockReason(row: PlanRow, action: string): string {
  if (!CONDITION_CHECKED_ACTIONS.has(action)) {
    return ''
  }
  return startCondition(row)?.allowed ? '' : (startCondition(row)?.reason ?? '开工条件未确认')
}

export async function runPlanAction(
  entryId: number,
  action: string,
): Promise<{ ok: boolean; message: string }> {
  const response = await request(`${PLAN_ENDPOINT}/${entryId}/actions`, {
    method: 'POST',
    body: JSON.stringify({ action }),
  })
  if (!response.ok) {
    throw new Error('养护计划动作未生效，请稍后重试')
  }
  const payload = (await response.json()) as { ok?: boolean; message?: string }
  return {
    ok: Boolean(payload.ok),
    message: payload.message ?? (payload.ok ? '养护计划动作已生效' : '养护计划动作未生效'),
  }
}
