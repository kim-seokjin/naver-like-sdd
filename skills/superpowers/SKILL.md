---
name: superpowers
description: This skill should be used when the user asks to "superpowers로 스펙 작성", "superpowers로 설계하고 구현", "superpowers로 개발", "use superpowers with our spec format", or wants Superpowers to drive design and implementation while plan.md and decisions.md remain the spec.
argument-hint: "[작업 설명 | 이어갈 스펙 폴더]"
---

# Superpowers로 스펙 작성과 구현

Superpowers의 스킬을 원본 그대로 호출해 설계부터 구현까지 진행하고, 스펙은 `plan.md`와 `decisions.md`로 남긴다. 사용자가 이 스킬을 실행한 것은 아래의 저장 위치, 문서 형식, 결정 방식을 Superpowers의 기본값보다 우선하라는 직접 요청이다. 나머지 절차와 승인 단계는 Superpowers를 따른다.

요청: $ARGUMENTS

`superpowers:brainstorming` 스킬을 쓸 수 없으면 Superpowers 설치(`claude plugin install superpowers@claude-plugins-official`)나 `/naver-like-sdd:spec`을 안내하고 멈춘다.

공통 기준을 먼저 읽는다.
- 규칙: `${CLAUDE_PLUGIN_ROOT}/shared/core-rules.md`
- 템플릿: `${CLAUDE_PLUGIN_ROOT}/shared/plan-template.md`, `${CLAUDE_PLUGIN_ROOT}/shared/decisions-template.md`

기존 스펙 폴더를 이어간다면 문서의 상태를 보고 해당 단계부터 시작한다.

## 산출물
| Superpowers의 산출물 | 남길 곳 |
|---|---|
| 설계 문서 (`docs/superpowers/specs/…`) | `specs/YYYY-MM-DD-작업명/plan.md`와 `decisions.md` |
| 설계 문서의 Approaches, AI가 정한 사항 | `decisions.md`의 결정 |
| 구현 계획 (`docs/superpowers/plans/…`) | 같은 폴더의 `tasks.md`. 형식은 Superpowers를 따르고 `Spec`에 두 문서의 경로를 적는다 |
| 실행 장부의 `Ruling`, 검토에서 나온 판단 | 핵심 규칙의 기록 대상을 `decisions.md`의 결정으로 |

두 문서가 설계 문서를 대신하므로 설계 문서를 따로 만들지 않는다. 설계 승인과 builder check도 두 문서를 대상으로 한다.

## 설계
`superpowers:brainstorming`을 호출한다.
- Superpowers가 AI의 판단에 맡기는 사항이라도 핵심 규칙에서 사람이 선택할 결정은 선택지와 추천을 제시하고 선택을 받는다.
- 두 문서는 템플릿 형식으로 쓴다. Superpowers의 설계 항목(의도, 목표와 비목표, 제약, 접근법)은 해당하는 섹션에 담는다.

## 작업 분해
두 문서가 승인되면 `superpowers:writing-plans`를 호출한다. 구현을 시작하기 전에 실행 방식과 함께 커밋 여부를 사용자에게 묻는다.

## 구현
사용자가 고른 Superpowers 실행 스킬을 호출한다.
- **커밋하기로 했으면** Superpowers의 절차를 따른다.
- **커밋하지 않기로 했으면** 커밋, 브랜치와 워크트리 만들기를 생략하고 현재 작업 폴더에서 진행한다. `task-start`, `task-done`, `review-package`처럼 커밋 범위에 기대는 스크립트 대신 `tasks.md`의 해당 작업을 읽는다. 최종 검토는 생략하지 않고, 검토자에게 `git status`로 확인한 변경 파일 전체와 두 문서를 전달한다. `tasks.md`에는 커밋 단계를 넣지 않는다.
- 커밋 여부와 관계없이 첫 작업 전에 Superpowers의 `sdd-workspace`로 실행 장부(`progress.md`)를 만들고, 작업이 끝날 때마다 완료 줄과 `Ruling`을 적는다. 대화가 압축되어도 이어갈 수 있게 하는 기록이다. 커밋하지 않는다면 완료 줄에 커밋 범위 대신 테스트 명령과 결과를 적는다.
- 작업이 끝날 때마다 `plan.md`의 진행 상황을 갱신한다. 서브에이전트가 보고한 결정은 메인 세션이 `decisions.md`에 기록한다.
- 마무리 전에 장부의 `Ruling`을 검토해 `decisions.md`로 옮긴다. 커밋하지 않았으면 git 이력이 없으므로 장부를 지우지 않고 위치를 보고한다.

## 마무리
`superpowers:finishing-a-development-branch`로 넘어가기 전에 `/naver-like-sdd:wrap`을 호출해 스펙과 대조한다. 커밋하지 않기로 했으면 wrap의 보고로 마친다.
