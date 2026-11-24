---
name: decide
description: This skill should be used when the user asks to "결정 기록해줘", "결정 번복", "이 결정 바꾸자", "재논의로 표시", answers a pending choice ("D3은 A로 확정"), "record a decision", "supersede D2", or when a design choice made during implementation must be added to a spec's decisions.md.
argument-hint: "[결정 내용 | 번복할 결정 번호와 이유]"
---

# 결정 기록

`decisions.md`에 결정을 추가하거나, `선택 대기`를 확정하거나, 기존 결정을 번복하거나, 재논의로 표시한다.

요청: $ARGUMENTS

규칙은 `${CLAUDE_PLUGIN_ROOT}/shared/core-rules.md`, 형식은 `${CLAUDE_PLUGIN_ROOT}/shared/decisions-template.md`를 따른다.

## 대상
진행 중인 스펙의 `decisions.md`에 기록한다. 진행 중인 스펙이 여럿이고 문맥으로 정할 수 없으면 묻는다. 스펙이 없으면 `/naver-like-sdd:spec`으로 만들지 확인한다.

## 작업
- **추가:** 다음 번호로 덧붙인다. 옵션이나 근거가 부족하면 묻는다.
- **확정:** `선택 대기` 결정은 같은 항목의 선택, 출처, 근거, 상태를 채운다. 새 번호를 만들지 않는다.
- **번복:** 새 결정을 덧붙여 무엇을 왜 뒤집는지 적고, 기존 결정은 상태 줄만 바꾼다.
- **재논의:** 상태를 바꾸고 재논의할 이유를 덧붙인다.

번복이 `plan.md`의 범위, 목표, 검증이나 이미 쓴 코드와 어긋나면 해당 위치를 찾아 알린다. 마지막에 기록한 번호, 라벨, 상태 변화를 보고한다.
