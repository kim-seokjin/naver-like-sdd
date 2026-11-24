---
name: wrap
description: This skill should be used when the user asks to "스펙 마무리", "스펙과 코드 대조", "스펙 완료 기준 확인", "wrap up the spec", "check the code against the spec", or asks to finish work or check before a PR ("작업 마무리", "PR 전 점검") when that work has a plan.md under specs/.
argument-hint: "[스펙 폴더]"
---

# 작업 마무리

구현을 스펙과 대조하고, 세션에서 사라질 결정과 시행착오를 문서에 남긴다.

대상: $ARGUMENTS (없으면 진행 중인 스펙. 여럿이거나 없으면 목록을 보여주고 묻는다)

규칙은 `${CLAUDE_PLUGIN_ROOT}/shared/core-rules.md`, 결정 형식은 `${CLAUDE_PLUGIN_ROOT}/shared/decisions-template.md`를 따른다.

## 대조
- 완료 기준마다 검증 방법을 실행해 충족, 미충족, 확인 불가로 판정하고 해당 단계의 `확인`을 `충족 (2026-11-24): 근거` 형식의 최신 판정으로 교체한다. 이력은 git에 남으므로 덧붙이지 않는다. 실행하지 못한 검증은 확인 불가로 둔다.
- 변경 내용에서 범위를 벗어난 변경, 유효한 결정과 다른 구현을 찾는다. 변경 내용은 기준 브랜치 이후의 커밋, 아직 커밋하지 않은 수정, 추적되지 않는 새 파일을 포함한다. git으로 알 수 없으면 현재 코드와 대조한다.
- 코드와 대화에서 드러났지만 기록되지 않은 결정 중 핵심 규칙의 기록 대상을 찾는다. 이유가 대화나 문서에 없고 코드에서만 드러나는 `local` 선택은 결정으로 만들지 않고, 스펙에 없는 동작이면 보고에만 적는다. 막혔던 문제와 해결 방법도 다음 작업에 도움이 되면 적는다.

## 갱신
- `plan.md`의 진행 상황을 실제 판정에 맞춘다. 상태는 모든 완료 기준이 충족되고 사용자가 동의할 때 `완료`로 바꾼다.
- 빠진 결정을 추가한다. 누가 선택했는지 확인되지 않으면 묻는다.
- 스펙과 코드가 어긋난 곳은 양쪽을 그대로 두고 어느 쪽을 고칠지 묻는다.

현황 문서의 갱신은 이 스킬의 범위가 아니다.

## 보고
다음 순서로 짧게 보고한다.
1. 완료 기준 판정과 근거
2. 우선 검토: `ai-selected`인 `foundation`·`significant` 결정, 스펙과 코드의 불일치, 범위를 벗어난 변경, 스펙에 없는 동작
3. `ai-selected`인 `local` 결정 목록
4. `선택 대기`, `미정`, `재논의` 항목과 사용자에게 필요한 답
