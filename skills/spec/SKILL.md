---
name: spec
description: This skill should be used when the user asks to "스펙 작성", "스펙 만들어줘", "스펙으로 구체화해줘", "plan.md 만들어줘", "기존 문서를 plan.md로 변환", "write a spec", "start spec-driven development", or wants to convert already written design docs into plan.md and decisions.md. For designing with Superpowers, the superpowers skill applies instead.
argument-hint: "[작업 설명 | 변환할 문서 경로]"
---

# 스펙 작성

대화로 의도를 구체화해 `plan.md`와 `decisions.md`를 만든다. 이 스킬의 결과물은 두 문서이며, 구현은 사용자가 스펙을 확인한 뒤 시작한다.

요청: $ARGUMENTS

공통 기준을 먼저 읽는다.
- 규칙: `${CLAUDE_PLUGIN_ROOT}/shared/core-rules.md`
- 템플릿: `${CLAUDE_PLUGIN_ROOT}/shared/plan-template.md`, `${CLAUDE_PLUGIN_ROOT}/shared/decisions-template.md`

## 맥락 파악
- 기존 `specs/*/`에서 관련 스펙과 현재 유효한 결정을 찾는다. 같은 작업이 진행 중이면 새 폴더 대신 그 스펙을 이어 쓸지 확인한다.
- 기존 코드베이스라면 데이터 구조, 리소스, 연동 시스템, 관례를 조사해 외부 제약으로 삼는다. 신규 프로젝트라면 환경, 배포, 데이터의 제약을 질문으로 확인한다.
- 코드나 문서에서 알 수 있는 것은 직접 확인하고, 사람만 정할 수 있는 의도와 선택을 묻는다.

## 구체화
- 의도, 범위(특히 하지 않을 것), 완료 기준과 사람이 선택할 설계 분기를 질문한다. AI가 선택할 수 있는 분기는 묻지 않는다. 다음 질문이 앞의 답에 달려 있으면 나누어 묻는다.
- 질문하는 설계 분기에는 선택지, 장단점, 추천과 이유를 함께 제시한다. `AskUserQuestion`을 쓸 수 있으면 사용하고, 아니면 번호를 매겨 묻고 답을 기다린다.
- 남은 모호함이 구현 결과를 바꾸지 않을 때까지 이어간다. 답을 받을 수 없는 실행이라면 질문을 남기고 멈추되, 사용자가 문서까지 요청했으면 핵심 규칙대로 기록한다.

## 문서화
- `specs/YYYY-MM-DD-작업명/`에 두 문서를 쓴다. 날짜는 오늘, 작업명은 짧은 kebab-case로 한다.
- 완료 기준은 예/아니오로 판정할 수 있게 쓴다. 해당 없는 섹션은 "없음"으로 남긴다.
- 사람이 한 선택과 AI가 한 선택 중 핵심 규칙의 기록 대상을 라벨과 함께 남긴다.
- 기존 문서를 변환할 때는 원본을 그대로 두고 배경에 원본 경로를 적는다. 출처를 알 수 없는 결정은 사용자에게 확인한다.

마지막에 범위, 완료 기준, 결정 목록(라벨 포함)을 짧게 요약하고 `선택 대기`·`미정` 항목과 우선 검토할 결정을 짚어 확인을 요청한다.
