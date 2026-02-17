from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from core.router import CommandResult, CommandRouter


@dataclass(frozen=True)
class RecipeStep:
    name: str
    command: str
    requires_approval: bool = False
    retries: int = 0
    expected_contains: str | None = None


@dataclass(frozen=True)
class TaskRecipe:
    name: str
    steps: list[RecipeStep]


@dataclass(frozen=True)
class StepExecution:
    step_name: str
    command: str
    success: bool
    attempts: int
    message: str
    status: str


@dataclass(frozen=True)
class WorkflowExecutionResult:
    recipe_name: str
    success: bool
    steps: list[StepExecution]


@dataclass
class WorkflowEngine:
    router: CommandRouter
    recipes_dir: Path = field(default_factory=lambda: Path("recipes"))

    def run_recipe(
        self,
        recipe_name: str,
        approve_step: Callable[[RecipeStep], bool] | None = None,
    ) -> WorkflowExecutionResult:
        recipe = self.load_recipe(recipe_name)
        approvals = approve_step or (lambda _step: True)
        executed: list[StepExecution] = []

        for step in recipe.steps:
            if step.requires_approval and not approvals(step):
                executed.append(
                    StepExecution(step.name, step.command, False, 0, "Step ditolak manual approval.", "cancelled")
                )
                return WorkflowExecutionResult(recipe.name, False, executed)

            step_result = self._execute_step(step)
            executed.append(step_result)
            if not step_result.success:
                return WorkflowExecutionResult(recipe.name, False, executed)

        return WorkflowExecutionResult(recipe.name, True, executed)

    def load_recipe(self, recipe_name: str) -> TaskRecipe:
        target = self.recipes_dir / f"{recipe_name}.json"
        if not target.exists():
            raise FileNotFoundError(f"Recipe tidak ditemukan: {target}")

        payload = json.loads(target.read_text(encoding="utf-8"))
        steps = [
            RecipeStep(
                name=item["name"],
                command=item["command"],
                requires_approval=item.get("requires_approval", False),
                retries=item.get("retries", 0),
                expected_contains=item.get("expected_contains"),
            )
            for item in payload.get("steps", [])
        ]
        return TaskRecipe(name=payload.get("name", recipe_name), steps=steps)

    def _execute_step(self, step: RecipeStep) -> StepExecution:
        attempt = 0
        while attempt <= step.retries:
            attempt += 1
            result = self.router.execute(step.command)
            if self._is_step_success(result, step):
                return StepExecution(step.name, step.command, True, attempt, result.message, "success")
        return StepExecution(step.name, step.command, False, attempt, result.message, "failed")

    def _is_step_success(self, result: CommandResult, step: RecipeStep) -> bool:
        if result.requires_confirmation:
            return False
        if step.expected_contains is None:
            return "ditolak" not in result.message.lower()
        return step.expected_contains.lower() in result.message.lower()
