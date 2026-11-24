# naver-like-sdd

AI와 일할 때 사라지기 쉬운 의도, 결정의 맥락, 시행착오를 코드 옆의 두 문서에 남기는 Claude Code 플러그인입니다.

> NAVER D2 [우리 팀만의 스펙 주도 개발 정착기](https://youtu.be/6R1V_PFJdUw)(NAVER Engineering Day 10th, 네이버 파이낸셜 AI 데이터랩 류성균) 발표에서 영감을 받았습니다. 원칙을 참고해 새로 만든 **비공식** 플러그인이며 네이버와 관련이 없습니다.

## 설치
필요한 것: Claude Code, PATH에서 실행되는 `python3` 3.9 이상

```bash
claude --plugin-dir /path/to/naver-like-sdd
```

## 사용
| 명령 | 하는 일 |
|---|---|
| `/naver-like-sdd:spec [설명 또는 문서 경로]` | 질문으로 구체화해 두 문서 작성, 기존 문서 변환 |
| `/naver-like-sdd:superpowers [설명]` | [Superpowers](https://github.com/obra/superpowers)를 호출해 설계부터 구현까지 진행하고, 스펙은 두 문서로 남김 |
| `/naver-like-sdd:decide [내용]` | 결정 추가, 번복, 재논의 표시 |
| `/naver-like-sdd:wrap [스펙 폴더]` | 완료 기준과 코드 대조, 빠진 결정 기록 |

```
specs/2026-11-24-작업명/
├── plan.md        # 무엇을: 의도, 범위, 목표, 완료 기준
└── decisions.md   # 왜: 문제, 옵션, 선택, 근거
```

두 문서를 만드는 방법은 자유입니다. `spec`은 단독으로 동작하고, `superpowers`는 설치된 Superpowers를 **수정하지 않고** 호출합니다(7.0.2에서 작성). 이때 작업 분해는 같은 폴더의 `tasks.md`에 남고, 커밋하지 않으면 실행 장부가 `.superpowers/sdd/`에 남습니다.

결정의 라벨과 규칙은 [shared/core-rules.md](shared/core-rules.md)에 있습니다.

## 훅
`specs/*/decisions.md`가 있는 프로젝트에서만 동작합니다.

- **SessionStart:** 핵심 규칙과 진행 중인 스펙 목록을 Claude에게 전달합니다.
- **SubagentStart:** 진행 중인 스펙이 있으면 서브에이전트에도 규칙을 전달하고, 결정을 메인 세션에 보고하게 합니다.
- **PreToolUse:** `상태: 진행중`인 `plan.md` 없이 Write/Edit로 코드 파일을 고치려 하면 미리 경고합니다.
- **Stop:** 응답이 끝날 때 코드 파일의 변화를 비교해, 셸 명령 등으로 고친 코드도 사후에 경고합니다. git 저장소에서만 동작합니다.

경고는 둘을 합쳐 세션당 한 번이며 작업을 막지 않습니다.

한계: Stop은 세션 중에 사람이 직접 고친 코드나 `git pull`, 브랜치 전환으로 바뀐 코드도 구분하지 않고 알립니다. 수정한 코드가 그 스펙에 속하는지는 판단하지 않습니다.

## 규칙을 고칠 때
규칙과 템플릿은 `shared/`에서만 고치고, 고친 뒤 eval로 확인합니다.

```bash
claude plugin eval . --runs 1 --ablation none --judge-model sonnet --scaffold --allow-tools Write Edit --no-publish
```

한 번 돌리는 데 약 $1.3이 듭니다. 기본 채점 모델(Haiku)은 맞는 출력을 실패로 채점한 적이 있으므로, 실패하면 리포트의 출력을 직접 확인합니다. 결과가 흔들리면 `--case 이름 --runs 3`으로 반복합니다. 규칙을 일부러 바꿔 실패했다면 eval의 기대값도 함께 확인합니다.

## 아직 정하지 않은 것
현황 문서의 갱신 주기와 방식, 팀 배포와 자동 업데이트
