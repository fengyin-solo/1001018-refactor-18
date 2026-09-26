"""养护计划业务规则：状态流转、字段校验与筛选口径都收在这里。"""
from __future__ import annotations

from typing import Any

from app.store import store

MODULE = "plan"
REQUIRED_FIELDS = ["计划编号", "计划周期", "计划类型"]
STATUS_ORDER = ["待编制", "已编制", "已审批", "执行中"]
ACTION_RULES = {"编制计划": "已编制", "审批计划": "已审批", "启动执行": "执行中"}
NEGATIVE_ACTIONS = []

# 开工条件只在这一处判定：计划周期已填写，且预算金额不超过上限（万元）。
# 列表按钮、详情页与动作接口都读 evaluate_start_condition 的结论，调整条件只改这里。
START_WORK_ACTION = "启动执行"
START_BUDGET_LIMIT = 50.0


class PlanService:
    def list_entries(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        rows = store.rows(MODULE)
        if keyword:
            rows = [row for row in rows if keyword in str(row.get("计划编号", ""))]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        total = len(rows)
        start = max(page - 1, 0) * size
        return rows[start:start + size], total

    def get_entry(self, entry_id: int) -> dict[str, Any] | None:
        return store.find(MODULE, entry_id)

    def find_by_plan_no(self, plan_no: str) -> dict[str, Any] | None:
        for row in store.rows(MODULE):
            if str(row.get("计划编号", "")) == plan_no:
                return row
        return None

    def evaluate_start_condition(self, plan_no: str) -> dict[str, Any]:
        """开工条件的唯一实现：用计划编号取出计划周期与预算金额，给出唯一结论。"""
        entry = self.find_by_plan_no(plan_no)
        if entry is None:
            message = f"养护计划 {plan_no} 不存在或已归档"
            return {"ok": False, "message": message, "reasons": [message], "plan_no": plan_no}
        period = str(entry.get("计划周期") or "").strip()
        budget = entry.get("预算金额")
        reasons: list[str] = []
        if not period:
            reasons.append("计划周期未填写")
        try:
            budget_value = float(budget)
        except (TypeError, ValueError):
            budget_value = None
            reasons.append("预算金额未填写或不是有效数字")
        if budget_value is not None and budget_value > START_BUDGET_LIMIT:
            reasons.append(f"预算金额 {budget_value} 万元超过开工上限 {START_BUDGET_LIMIT} 万元")
        ok = not reasons
        message = "开工条件满足，可以启动执行" if ok else "；".join(reasons)
        return {
            "ok": ok,
            "message": message,
            "reasons": reasons,
            "plan_no": plan_no,
            "计划周期": period or None,
            "预算金额": budget,
        }

    def create_entry(self, values: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
        missing = [field for field in REQUIRED_FIELDS if not str(values.get(field) or "").strip()]
        if missing:
            return None, missing
        rows = store.rows(MODULE)
        entry = {"id": max((int(row.get("id", 0)) for row in rows), default=0) + 1}
        entry.update({field: values.get(field) for field in REQUIRED_FIELDS})
        entry["status"] = STATUS_ORDER[0]
        entry["pending"] = True
        entry["abnormal"] = False
        rows.append(entry)
        return entry, []

    def run_action(self, entry_id: int, action: str) -> tuple[dict[str, Any] | None, str]:
        entry = store.find(MODULE, entry_id)
        if entry is None:
            return None, f"养护计划 {entry_id} 不存在或已归档"
        if action not in ACTION_RULES:
            return None, f"动作「{action}」不属于养护计划可执行范围"
        target = ACTION_RULES[action]
        if target not in STATUS_ORDER:
            return None, f"目标状态「{target}」不在允许的状态序列里"
        if action == START_WORK_ACTION:
            verdict = self.evaluate_start_condition(str(entry.get("计划编号") or ""))
            if not verdict["ok"]:
                return None, f"开工条件不满足：{verdict['message']}"
        entry["status"] = target
        entry["pending"] = target != STATUS_ORDER[-1]
        entry["abnormal"] = action in NEGATIVE_ACTIONS
        return entry, f"养护计划已{action}"
