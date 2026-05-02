"""
Schema差异计算引擎
"""
import json
from typing import List, Dict, Any, Optional
from app.schemas.api import VersionDiffChange


class SchemaDiffEngine:
    """版本差异计算"""

    HIGH_IMPACT_FIELDS = {"path", "method"}
    MEDIUM_IMPACT_FIELDS = {"body_type", "responses"}

    def compute_diff(self, old_snapshot: Dict[str, Any], new_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """计算两个版本快照的差异"""
        changes = []
        changes.extend(self._diff_basic(old_snapshot, new_snapshot))
        changes.extend(self._diff_params("path_params", old_snapshot, new_snapshot))
        changes.extend(self._diff_params("query_params", old_snapshot, new_snapshot))
        changes.extend(self._diff_params("header_params", old_snapshot, new_snapshot))
        changes.extend(self._diff_params("cookie_params", old_snapshot, new_snapshot))
        changes.extend(self._diff_body(old_snapshot, new_snapshot))
        changes.extend(self._diff_responses(old_snapshot, new_snapshot))

        impact_level = self._compute_impact(changes)
        summary = self._generate_summary(changes)

        return {
            "changes": [self._change_to_dict(c) for c in changes],
            "impact_level": impact_level,
            "summary": summary,
        }

    def _diff_basic(self, old: Dict, new: Dict) -> List[VersionDiffChange]:
        """基础字段差异"""
        changes = []
        for field in ("path", "method", "description", "body_type", "protocol"):
            old_val = old.get(field)
            new_val = new.get(field)
            if old_val != new_val:
                impact = "high" if field in self.HIGH_IMPACT_FIELDS else (
                    "medium" if field in self.MEDIUM_IMPACT_FIELDS else "low"
                )
                changes.append(VersionDiffChange(
                    type="field_changed",
                    field=field,
                    old_value=old_val,
                    new_value=new_val,
                    impact=impact,
                ))
        return changes

    def _diff_params(self, param_type: str, old: Dict, new: Dict) -> List[VersionDiffChange]:
        """参数差异"""
        changes = []
        old_params = {p.get("name"): p for p in (old.get(param_type) or [])}
        new_params = {p.get("name"): p for p in (new.get(param_type) or [])}

        for name, param in new_params.items():
            if name not in old_params:
                impact = "high" if param.get("required") else "low"
                changes.append(VersionDiffChange(
                    type="param_added",
                    field=f"{param_type}.{name}",
                    old_value=None,
                    new_value=param,
                    impact=impact,
                ))
            elif old_params[name] != param:
                old_required = old_params[name].get("required", False)
                new_required = param.get("required", False)
                if old_required != new_required:
                    impact = "high" if new_required else "medium"
                else:
                    impact = "medium"
                changes.append(VersionDiffChange(
                    type="param_changed",
                    field=f"{param_type}.{name}",
                    old_value=old_params[name],
                    new_value=param,
                    impact=impact,
                ))

        for name in old_params:
            if name not in new_params:
                changes.append(VersionDiffChange(
                    type="param_removed",
                    field=f"{param_type}.{name}",
                    old_value=old_params[name],
                    new_value=None,
                    impact="high",
                ))

        return changes

    def _diff_body(self, old: Dict, new: Dict) -> List[VersionDiffChange]:
        """请求体差异"""
        changes = []
        old_body = old.get("body_definition")
        new_body = new.get("body_definition")
        if old_body != new_body:
            changes.append(VersionDiffChange(
                type="body_changed",
                field="body_definition",
                old_value=old_body,
                new_value=new_body,
                impact="medium",
            ))
        return changes

    def _diff_responses(self, old: Dict, new: Dict) -> List[VersionDiffChange]:
        """响应定义差异"""
        changes = []
        old_responses = {r.get("status_code"): r for r in (old.get("responses") or [])}
        new_responses = {r.get("status_code"): r for r in (new.get("responses") or [])}

        for code, resp in new_responses.items():
            if code not in old_responses:
                changes.append(VersionDiffChange(
                    type="response_added",
                    field=f"responses.{code}",
                    old_value=None,
                    new_value=resp,
                    impact="low",
                ))
            elif old_responses[code] != resp:
                changes.append(VersionDiffChange(
                    type="response_changed",
                    field=f"responses.{code}",
                    old_value=old_responses[code],
                    new_value=resp,
                    impact="medium",
                ))

        for code in old_responses:
            if code not in new_responses:
                changes.append(VersionDiffChange(
                    type="response_removed",
                    field=f"responses.{code}",
                    old_value=old_responses[code],
                    new_value=None,
                    impact="medium",
                ))

        return changes

    def _compute_impact(self, changes: List[VersionDiffChange]) -> str:
        """计算整体影响等级"""
        if not changes:
            return "low"
        impacts = {c.impact for c in changes}
        if "high" in impacts:
            return "high"
        if "medium" in impacts:
            return "medium"
        return "low"

    def _generate_summary(self, changes: List[VersionDiffChange]) -> str:
        """生成变更摘要"""
        if not changes:
            return "无变更"
        parts = []
        added = [c for c in changes if c.type.endswith("_added")]
        removed = [c for c in changes if c.type.endswith("_removed")]
        changed = [c for c in changes if c.type.endswith("_changed")]

        if added:
            parts.append(f"新增 {len(added)} 项")
        if removed:
            parts.append(f"删除 {len(removed)} 项")
        if changed:
            parts.append(f"修改 {len(changed)} 项")

        return "，".join(parts)

    def _change_to_dict(self, change: VersionDiffChange) -> Dict[str, Any]:
        """VersionDiffChange转字典"""
        return {
            "type": change.type,
            "field": change.field,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "impact": change.impact,
        }
