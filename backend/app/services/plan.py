"""养护计划业务规则：状态流转、字段校验与筛选口径都收在这里。"""
from __future__ import annotations

from typing import Any

from app.store import store

MODULE = "plan"
REQUIRED_FIELDS = ["计划编号", "计划周期", "计划类型"]
STATUS_ORDER = ["待编制", "已编制", "已审批", "执行中"]
ACTION_RULES = {"编制计划": "已编制", "审批计划": "已审批", "启动执行": "执行中"}
NEGATIVE_ACTIONS = []
START_ACTION = "启动执行"
CONDITION_CHECKED_ACTIONS = {"审批计划", START_ACTION}
START_BUDGET_LIMIT = 30.0
START_CONDITION_FIELD = "开工条件"


class PlanService:
    def list_entries(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
        include_start_condition: bool = False,
    ) -> tuple[list[dict[str, Any]], int]:
        rows = store.rows(MODULE)
        if keyword:
            rows = [row for row in rows if keyword in str(row.get("计划编号", ""))]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        total = len(rows)
        start = max(page - 1, 0) * size
        items = rows[start:start + size]
        if include_start_condition:
            items = [self._with_start_condition(row) for row in items]
        return items, total

    def get_entry(self, entry_id: int) -> dict[str, Any] | None:
        entry = store.find(MODULE, entry_id)
        if entry is None:
            return None
        return self._with_start_condition(entry)

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

    def evaluate_start_condition(self, plan_code: str) -> dict[str, Any]:
        """按计划编号读取计划周期和预算金额，返回全系统唯一的开工条件结论。"""
        plan = next(
            (
                row
                for row in store.rows(MODULE)
                if str(row.get("计划编号") or "") == plan_code
            ),
            None,
        )
        if plan is None:
            return {
                "planCode": plan_code,
                "period": None,
                "budget": None,
                "allowed": False,
                "reason": f"养护计划 {plan_code} 不存在或已归档",
            }

        period = str(plan.get("计划周期") or "").strip()
        budget = self._parse_budget(plan.get("预算金额"))
        if not period:
            allowed = False
            reason = "计划周期为空，不满足开工条件"
        elif budget is None:
            allowed = False
            reason = "预算金额不是有效数字，不满足开工条件"
        elif budget > START_BUDGET_LIMIT:
            allowed = False
            reason = (
                f"预算金额{budget:g}超过开工上限"
                f"{START_BUDGET_LIMIT:g}，不满足开工条件"
            )
        else:
            allowed = True
            reason = "满足开工条件"

        return {
            "planCode": plan_code,
            "period": period,
            "budget": budget,
            "allowed": allowed,
            "reason": reason,
        }

    def run_action(self, entry_id: int, action: str) -> tuple[dict[str, Any] | None, str]:
        entry = store.find(MODULE, entry_id)
        if entry is None:
            return None, f"养护计划 {entry_id} 不存在或已归档"
        if action not in ACTION_RULES:
            return None, f"动作「{action}」不属于养护计划可执行范围"
        target = ACTION_RULES[action]
        if target not in STATUS_ORDER:
            return None, f"目标状态「{target}」不在允许的状态序列里"
        if action in CONDITION_CHECKED_ACTIONS:
            condition = self.evaluate_start_condition(str(entry.get("计划编号") or ""))
            if not condition["allowed"]:
                return None, str(condition["reason"])
        entry["status"] = target
        entry["pending"] = target != STATUS_ORDER[-1]
        entry["abnormal"] = action in NEGATIVE_ACTIONS
        return entry, f"养护计划已{action}"

    def _with_start_condition(self, entry: dict[str, Any]) -> dict[str, Any]:
        plan_code = str(entry.get("计划编号") or "")
        presented = dict(entry)
        presented[START_CONDITION_FIELD] = self.evaluate_start_condition(plan_code)
        return presented

    @staticmethod
    def _parse_budget(value: Any) -> float | None:
        text = str(value or "").strip().replace(",", "")
        if text.endswith("万元"):
            text = text[:-2]
        elif text.endswith("元"):
            text = text[:-1]
        try:
            budget = float(text)
        except (TypeError, ValueError):
            return None
        return budget if budget >= 0 else None
