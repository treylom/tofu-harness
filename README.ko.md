# tofu-harness (구 `tofable`)

> 🌐 English: **[README.md](README.md)**

**AI 에이전트 하네스를 정직하게 유지한다.** 일하는 방식을 규칙과 기계적 게이트로 옮기고, 그 하네스 문서들이 도구·경로·모델에 대해 계속 진실을 말하는지 감사한다.

![하네스 감사: 에이전트 문서를 훑어 죽은 링크와 낡은 라벨을 찾고, 게이트가 검증된 수리만 통과시키는 모습](./assets/hero-harness-audit.png)

## 두 기둥

| | 스킬 | 하는 일 |
|---|---|---|
| **이전·강제** | `/tofable` | 복사해 쓰는 규칙 층 + 근거가 없으면 턴을 되돌리는 검증 게이트. 이 레포의 원래 절반. |
| **감사·수리** | `/harness-audit` | 마감선이 있는 하네스 문서 전수 점검 — `CLAUDE.md`·스킬·규칙이 현실과 어긋난 곳을 찾고, 발견마다 독립 재검증한 뒤, 확정된 것만 수리한다. 2026-07 신규. |

플러그인 패키징은 **스킬 전용**이다. [`hooks/`](hooks/) 아래 게이트는 별도 설치한다 — [`hooks/README.md`](hooks/README.md) 참조.

## 여기서 시작

| 이런 분이라면 | 이렇게 |
|---|---|
| **새 모델이 나왔고** 내 하네스가 낡았을 수 있다 | [`/harness-audit`](skills/harness-audit/SKILL.md) 를 마감선 걸고 실행 |
| **Claude Code** 에서 검증 게이트를 쓰고 싶다 | [`hooks/`](hooks/) 복사 → [단계별 설치](hooks/README.md) (~5분) → [`rules/`](rules/) 에서 규칙 층 시드 |
| **Codex** 사용자다 | upstream 플러그인 [`fable-ish-codex`](https://github.com/Pandoll-AI/fable-ish-codex) 설치 — [`codex/README.md`](codex/README.md) |
| 하네스가 일하는 방식을 **정말 이전시키는지 재보고** 싶다 | [`bench/`](bench/) 를 내 모델에 실행 — 결과·방법은 [`bench/results.md`](bench/results.md) |

### 설치

```
claude plugin marketplace add treylom/tofu-harness
/plugin install tofu-harness@tofu-harness
```

나중에 갱신할 때:

```
claude plugin marketplace update tofu-harness
claude plugin update tofu-harness@tofu-harness
```

---

## `/harness-audit` — 내 하네스는 지금도 진실을 말하나

**2026-07-24 Claude Opus 5가 출시**됐고([TechCrunch](https://techcrunch.com/2026/07/24/anthropic-launches-opus-5/) · [Axios](https://www.axios.com/2026/07/24/anthropic-releases-new-model-opus-5)), "하네스를 어떻게 써야 하나"에 대한 앤트로픽 1차 문서도 함께 나왔다. 이 스킬 뒤의 감사가 실제로 대조한 것은 그 두 문서다: 공식 [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) 가이드(검증 지시는 과검증을 유발하니 제거하라, "심각한 것만 보고하라" 류 축소어는 산출을 문자 그대로 줄인다 — 전부 보고하고 후단에서 걸러라)와 [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) 블로그(`/doctor` 를 함께 실은 그 글). 아래 표는 이 지침을 점검 가능한 7원칙으로 압축한 커뮤니티 정리([@nextcocoai, Threads](https://www.threads.com/@nextcocoai/post/DbNuHBnlBrW))를 **교차 확인용**으로 따르되, 저자 스스로 남긴 "전문가가 아닙니다. 반드시 검증하세요"에 따라 **우리의 검증 소견을 병기**한 것이다:

| # | 원칙 (요약) | 내 하네스에 점검할 것 |
|---|---|---|
| 1 | 모델이 이미 하는 일은 쓰지 않는다 (검증·재확인 지시는 기본 동작과 중복) | ⚠️ **부분 채택** — *일반적인* "다시 확인하라" 문장은 지우되, 실제 회귀에서 태어난 게이트는 남긴다. 우리 감사에서는 규칙이 강제하는 바로 그 일을 모델이 반복해서 *안 했다*. 기준: 사건 이력이 없으면 삭제 후보, 있으면 존치 |
| 2 | 모델이 스스로 조절 않는 4가지만 명시 (응답 길이·보고 주기·문서 길이·위임 상한) | ✅ 신규 규칙마다 던질 좋은 진입 질문 (기존 문서 소급은 next-touch만) |
| 3 | 금지형 대신 긍정 예시 | ✅ 스타일 규칙엔 맞다. 단 정확히 한 실패 경로를 막는 금지형은 제 값을 한다 |
| 4 | 축소어 금지 ("심각한 것만") — 전부 모으고 다음 단계에서 거른다 | ✅ `/harness-audit` 의 2단 검증이 정확히 이 구조다 (전부 수집 → 독립 재검증) |
| 5 | 범위 확장을 막는다 — "요청받은 범위 그대로", 벗어나기 직전 멈춤 | ✅ 이 스킬의 가드 ①~③이 정확히 이 실패에서 태어났다 |
| 6 | 사양은 앞에 한 번에, 그다음엔 놔둔다. 승인 게이트는 되돌리기 어려운 행동에만 | ✅ 이 레포 규칙이 쓰는 자율성 가격 구조와 동일 |
| 7 | 긴 파일은 끝에 2~3줄 리마인더 | 🧪 실험해볼 만하다 — 긴 프롬프트의 희석은 실재한다 |

`/harness-audit` 은 "가서 점검해봐"의 체계화다: 하네스 문서 전부를 4축(도구 불일치 · 낡음 · 죽은 링크 · 문서 간 충돌)으로 전수하고, 발견을 독립 워커가 처음부터 재검증하고, 확정된 것만 수리한다 — 마감선 안에서. 원조 실행(한 하네스·252문서·하룻밤 1회)에서는 49건을 확정하고 **전부** 고쳤다 — 47개 파일에 걸친 한 커밋 + sibling 2건 추가. 이 집계에 범위 라벨이 붙어 있는 건 의도다: 신뢰 단위는 집계가 아니라 문서별 판정이다(스킬의 STEP 2 주의 참조).

**사용법:**

```
1. 에이전트에게: "harness-audit 돌려줘, 마감 2시간, 범위: 이 프로젝트 + 홈 설정"
2. 산출 3종(전수표 · 수리 커밋 · 처분 목록)을 먼저 선언하고, 파일 목록을 확정한다
3. 병렬 워커가 모든 문서를 4축으로 판정  →  다른 워커가 각 발견을 처음부터 재검증
4. CONFIRMED 만 중앙에서 수리(유일 매칭 안전장치), 나머지는 처분 목록으로
5. 선택(물어본다): 자주 쓰는 스킬의 비파괴 런타임 스모크
```

**다른 도구들 사이에서의 자리** — 네 층이 각각 다른 질문에 답한다:

| 층 | 도구 | 답하는 질문 |
|---|---|---|
| 계획 | Superpowers 브레인스토밍 / Ouroboros 인터뷰 / 스펙 도구 | *무엇을* 어느 범위로 언제까지 바꿀지 — 수백 개 파일을 만지기 **전에** 결정 |
| 설치 | Claude Code 내장 `/doctor` | *설치*가 멀쩡한가 — 설정 파싱, 중복 설치, 안 쓰는 확장 |
| 문서 | **`/harness-audit`** | 하네스 문서가 도구·경로·모델·서로에 대해 *진실을 말하는가* |
| 행동 | **게이트** (`hooks/`) | 에이전트가 문서대로 *실제로 하는가* — Stop·PreToolUse 시점에 기계적으로 |

고쳐놓고 발화되지 않는 규칙은 장식이다 — 배선하라(게이트). 낡은 규칙 위에서 발화하는 게이트는 어제의 진실을 강제한다 — 감사하라(스킬). 계획을 먼저 세워야 둘 다 밤을 안 먹고, `/doctor` 를 돌려야 망가진 설치를 감사하는 일이 없다.

---

## `/tofable` — 게이트

측정 사이클 전반에서 가장 많이 재현된 발견 하나: **적어둔 규칙은 강제가 아니다.** 모델은 산문 규칙을 훑고 지나가지만, 자기 Stop 을 되돌리는 훅은 훑고 지나갈 수 없다. 그래서 이 하네스의 활성 성분은 게이트 묶음이다:

| 게이트 | 발화 시점 | 잡는 것 |
|---|---|---|
| `verify-ledger` | 매 도구 호출 후 | 아무것도 안 잡는다 — 무엇이 바뀌고 무엇이 검증됐는지 *기록*한다 (다른 게이트가 판정할 근거) |
| `stop-verify-gate` | Stop | 코드·설정이 바뀌었는데 그 *뒤에* 성공한 검증이 없다 |
| — 부재 검사 | Stop | git 을 얕게 보고 "X 는 없다"고 단정 (`--all`·`branch -a` 경계 확장 없이) |
| — 주장-근거 검사 | Stop | 정확한 개수나 동일성 주장("바이트 단위로 같다")인데 도구 로그에 기계 검사(`wc -l`·`grep -c`·`diff`·`shasum`)가 없다 |
| — 하위작업 근거 검사 | Stop | 서브에이전트에 위임한 뒤 완료를 선언했는데, 위임분이 돌아온 *후* 검증 기록이 없다 — 위임자의 "됐다"는 근거가 아니라 주장이다 |
| `continuation-gate` | Stop | 작업이 남았고 사용자에 막힌 것도 없는데 "내일 이어서" 류 유예 표현 |
| `surfacing-gate` | Bash 직전 | 파괴적 명령(재귀 rm·force-push·hard reset)이 **조용히** 실행되려 한다 — 1회 차단, 응답에서 무엇이 파괴되고 왜 안전한지 밝혀야 통과 |
| `blind-retry-gate` | Bash 직전 | **방금 실패한 명령을 바이트 단위로 동일하게** 재실행 — 1회 차단("에러는 데이터다 — 한 번 더 쓰기 전에 읽어라") |
| `prompt-advance-gate` | Write/Edit/Task 직전 | 인터뷰·브레인스토밍·계획 직후 **프롬프트 엔지니어링 단계 없이** 실행으로 직행 |

모든 게이트는 **한 번만** 되돌리고, 언제나 통과 경로가 있고(근거를 보이거나, 왜 불가능한지 밝히거나), fail-open 이다 — 망가진 게이트가 세션을 막는 일은 없다. 게이트는 근거를 요구하지 행동을 금지하지 않는다. 킬 스위치: `FABLE_GATE_OFF=1`.

`prompt-advance-gate` 가 찾는 프롬프트 엔지니어링 단계는 계획과 실행 사이의 의도적인 프롬프트 결정화 과정이면 무엇이든 된다. 우리 참조 구현은 [prompt-engineering-skills](https://github.com/treylom/prompt-engineering-skills) (`/prompt`) 지만, 게이트는 그 단계를 일반적으로 탐지한다 — 동등한 스킬이면 통과한다.

### 실제로 효과가 있나

있다, 측정했다. 다만 숫자를 옮기기 전에 범위 라벨을 먼저 읽어야 한다.

> ⚠️ **이 측정치는 이전 세대 모델에서 나왔다**(`fable-5`·`sonnet-5` 급, 사이클 1~2, 셀당 시드 2~3). **Opus 5 세대는 다르게 움직인다** — 더 강한 모델은 이런 교정이 덜 필요하므로, 방향이 같더라도 효과의 *크기*는 줄어들 것으로 봐야 한다. 이 숫자는 방법이 작동한다는 증거지, 각자 환경에서 기대할 상수가 아니다. 과제별 전체 결과·루브릭·원자료: **[`bench/results.md`](bench/results.md)**.

세대 단서를 넘어서 남는 발견 셋:

- **하네스가 겨냥하는 격차는 능력이 아니라 지시 도달이다.** 하네스를 끈 상태에서, 정답이 특정 집 규칙에 적혀 있어야 풀리는 과제는 유능한 모델이면 그냥 맞히는 과제보다 약 30점 낮았다. 그 격차가 규칙·게이트 체계가 회복하려는 몫이고, "모델이 규칙을 본 적 없다"와 "모델이 그만큼 못 추론한다"를 갈라준다.
- **개선은 게이트를 단 자리에 정확히 얹힌다.** 픽스처 단위로 부재-주장 함정과 개수 함정은 해당 게이트가 생기자 뛰었고, 전체 평균은 거의 안 움직였다 — 게이트 이득은 게이트 걸린 함정에 몰리고 넓은 평균에서는 희석된다. **게이트 하나 ≈ 결함 축 하나 제거**가 두 사이클에서 재현됐다.
- **짧게 쓰는 건 강제가 아니다.** 규칙 파일의 압축본(내용 동일·약 40% 짧음)은 평균이 같았는데 결함은 *더* 많았다. 산문을 줄인다고 구속력이 생기지 않는다. 행동을 움직인 건 게이트다.

정직한 각주 둘. 모델 격차처럼 보이는 것 일부는 **계측(instrument) 격차**였다 — 모델 자기보고 대신 보존된 도구 사용 기록으로 채점했더니 한 벤치마크가 3점 올랐다. 모델이 다르게 한 게 아니다. 그리고 채점기 오탐 하나가 가르쳐준 것: 채점기에는 정답지만이 아니라 픽스처 **입력 자료**도 같이 줘야 한다.

### 게이트를 정직하게 유지하기

멀티 에이전트 플릿에서 일주일 라이브로 돌린 뒤, 실제 게이트 이벤트 94건 전부를 참양성·거짓양성·마찰로 라벨링하고, 게이트를 약화하는 대신 마찰 패턴을 고쳤다. 결과 둘이 직관을 뒤집었다:

- **게이트 하나당 비용은 노이즈다**(훅당 16~30ms, 진짜 비용은 되돌려진 턴 하나). 따라서 **게이트 체계의 속도 KPI 는 거짓양성률**이고, 검증 게이트는 대략 70~100% 참양성이었다. 플릿을 빠르게 만든 건 게이트 제거가 아니라 거짓양성 수리였다.
- **"이 에이전트는 어떤 게이트를 켜야 하나"는 취향이 아니라 분류 문제다.** 내용으로 발화하는 게이트(파괴적 명령·미검증 개수·완료 주장)는 스스로 범위를 잡으므로 전부에 켠다. 진짜 봇 전용 게이트만 에이전트별 가드를 두고, headless·cron 세션에는 명시적 자동화 예외가 필요하다.

이 절차는 각자 플릿에서 다시 돌릴 수 있게 묶여 있다: [`docs/gate-audit-playbook.md`](docs/gate-audit-playbook.md)(5단계, 각 단계마다 우리가 먼저 빠진 함정 포함), [`scripts/audit/scan_gate_events.py`](scripts/audit/scan_gate_events.py)(게이트 이름 grep 이 아닌 실이벤트 스캐너), [`profiles/gate-profiles.json`](profiles/gate-profiles.json)(에이전트별 프로파일 — 프로파일은 *배선*만 고르고 게이트 코드는 단일 원본으로 둔다. 에이전트마다 포크하는 게 1순위 드리프트 실패 경로다).

---

## 빠른 시작

**1. 규칙 층 시드.** [`rules/`](rules/) 를 하네스 작업공간(예: `.claude/rules/`)에 복사하고, 항상 로드되는 프롬프트가 인덱스를 가리키게 한 뒤, 예시 행을 자기 집 규칙으로 바꿔간다 — 상황 하나당 파일 하나. 설계 근거는 [`rules/README.md`](rules/README.md).

**2. 훅 설치.** 핵심 셋:

- **`fable_lib.py`** — 공용 라이브러리. 어떤 변경 파일이 검증 근거를 요구하는지 판정하고, 추가 전용 근거 원장을 유지하고(프로젝트 트리 밖에 둬서 커밋되지 않는다), 킬 스위치(`FABLE_GATE_OFF=1`, 또는 `FABLE_GATE_PILOT=<name>` 으로 한 세션에만 먼저 적용)를 쥔다.
- **`verify-ledger.py`** — `PostToolUse(Write|Edit|Bash)` 훅. 실제 검증을 근거로 기록한다. 차단하지 않는다. Fail-open.
- **`stop-verify-gate.py`** — `Stop` 훅. 세 검사(변경-검증·부재-주장·주장-근거)를 담는다. 구체적 체크리스트와 함께 한 번 되돌린다. 횟수 제한·루프가드·fail-open.

함께: `continuation-gate.py`, `surfacing-gate.py`, 그리고 선택 설치인 `cutover-review-gate.py` / `requirements-lock.py` / `branch-stray-guard.sh`.

**[`hooks/README.md`](hooks/README.md) 에 Claude Code 단계별 설치가 있다** — 정확한 `settings.json` 조각, 게이트가 살아 있는지 확인하는 법, 킬 스위치. 배선 후 `hooks/tests/test_gate.py` 를 돌린다(게이트 계약의 실행 가능한 명세). 두 동반 스위트가 시간이 지나도 게이트를 정직하게 유지해준다: `hooks/tests/replay/run.py` 는 보관된 위반 시나리오를 재생하고(차단률 100% 유지, 코퍼스 하한이 있어 픽스처 삭제로 속일 수 없다), `hooks/tests/probes/run.py` 는 파이프라인 자체 계약을 검사한다. 추론 모델을 바꿀 때는 `bench/substrate-check.sh` 가 전부를 JSON 한 줄로 스냅샷한다 — 전후로 돌려 델타 0 이면 배관이 전환에서 안 깨진 것이다.

**3. 벤치마크 실행.**

```bash
# 픽스처 하나를 모델 하나에 실행, 전체 도구 사용 기록 보존
bench/run.sh example-codefix <your-model-id> my-run

# 산출물은 $FABLE_BENCH_RUNS_DIR (기본 ~/.fable-bench/runs/) 에:
#   work/  transcript.jsonl  raw-output.json  meta.json
```

채점은 판정 모델로 — 되도록 **산출한 모델과 다른 계열** — `bench/rubric.md` + 픽스처 정답지 + 실행 기록을 `bench/judge-prompt.md` 템플릿으로 넣는다. 벤치마크는 같은 과제 묶음을 하네스 끄고/켜고 돌리므로, *내* 설치가 *내* 기반 모델에서 격차를 실제로 회복하는지 확인할 수 있다.

## 레포 구조

```
tofu-harness/
├── README.md              — 영문
├── README.ko.md           — 이 파일
├── LICENSE                — MIT (이 레포 자체 기여분)
├── NOTICE                 — 이식한 훅 설계의 Apache-2.0 저작자 표시
├── docs/
│   ├── method.md              — 이전 방법: 규칙 패턴, 원장/stop-gate, 벤치마크 루프, 마이닝 루프
│   ├── gate-audit-playbook.md — 감사 루프: 에이전트별로 어떤 게이트가 실제 필요한지, 측정과 함께
│   └── decision-history.md    — 위 조각들의 채택 근거
├── skills/
│   ├── tofable/           — 작업 규율 스킬 (`/tofable`)
│   └── harness-audit/     — 감사 스킬 (`/harness-audit`): 전수 → 독립 재검증 → 중앙 수리 (가드 7종)
├── rules/                 — 복사해 쓰는 예시 규칙 층 (상황 인덱스 + 트리거별 규칙 파일)
├── hooks/                 — 하네스 비의존 검증 훅 (근거 원장 + stop-gate); 별도 설치
│   └── tests/
│       ├── replay/            — 위반 코퍼스를 픽스처로 재생 (차단률 + 코퍼스 하한)
│       └── probes/            — 게이트 파이프라인 자체 계약, 결정적 검사
├── profiles/
│   └── gate-profiles.json — 에이전트별 게이트 프로파일: 도메인 프로파일을 고르고 그 그룹만 배선
├── scripts/audit/
│   └── scan_gate_events.py — 감사 루프용 실게이트 이벤트 스캐너
├── assets/                — README 일러스트
├── bench/                 — 과제 묶음, 채점, 원자료
│   └── substrate-check.sh — 모델 전환 리허설용 한 줄 기반 스냅샷
└── codex/
    └── README.md          — upstream fable-ish-codex 플러그인 경유 Codex 사용법
```

## 이 레포는 무엇이고 어디서 왔나

`fable-5` 는 우리가 좋은 세션에 즉흥적으로 붙인 별명이 아니라, 접근이 제한된 특정 모델이다. 단 며칠간의 실사용만으로도 이 모델과 손발 맞춘 방식이 제법 좋은 *작업 방식*으로 자리 잡았다: 목표를 정직하게 쪼개고, "완료"라 말하기 전에 검증하고, 막힌 데를 돌려 말하지 않고 그대로 보고했다. 그 방식의 상당 부분은 모델의 가중치(weight)에 있지 않다 — 모델 주변에 쌓인 습관과 스캐폴딩(scaffolding, 모델을 둘러싼 뼈대 구조물)에 산다. 이 레포는 그 스캐폴딩을 **외부에 인코딩**해 이식 가능한 하네스로 만들고, 하네스를 켰을 때 그 일하는 방식이 다른 — 대개 더 저렴한 — 모델에 **얼마나 실제로 이전되는지 측정**한다.

이 레포는 그 하네스의 공개·일반화 배포판이다. 개발 환경의 내부 이름·경로·식별자는 제거했고, 로직과 측정 방법론은 그대로다.

**[`fable-ish-codex`](https://github.com/Pandoll-AI/fable-ish-codex) 와의 관계**: 이 레포의 훅 설계는 Pandoll-AI 의 그 Codex 플러그인에서 차용했다([NOTICE](./NOTICE) 명시). 이 레포의 독자 기여는 **하네스가 일하는 방식을 실제로 이전시키는지 재는 측정 벤치마크**, 그리고 **게이트의 Claude Code 이식**이다. Codex 를 쓴다면 원본 플러그인 설치가 가장 빠르다 — [`codex/`](./codex/) 참조.

이전 방법의 전체 서술은 [`docs/method.md`](docs/method.md) 에 있다.

## 감사의 말

이 프로젝트는 한국 Claude/Codex 커뮤니티에서 아낌없이 공유된 작업들 위에 서 있다:

- **[fablize](https://github.com/fivetaku/fablize)** — gptaku님 ([@gptaku_ai](https://www.threads.com/@gptaku_ai)). Opus가 Fable처럼 행동하게 만드는 Claude Code 플러그인 — 완료·근거·검증을 절차로 강제한다. 같은 이전(transfer) 문제에 대한 병렬 접근으로, 우리의 접근을 벼려줬다.
- **[fable-ish-codex](https://github.com/Pandoll-AI/fable-ish-codex)** — voice / 현님 ([@voidlight00](https://www.threads.com/@voidlight00), Pandoll-AI, Apache-2.0). 이 프로젝트 훅 설계의 upstream (NOTICE 참조).
- **[Hugh Kim](https://github.com/jung-wan-kim)** 님 ([@hue_0525](https://www.threads.com/@hue_0525), [hugh-kim.space](https://hugh-kim.space)) — fable-week 시리즈 ([1일차](https://hugh-kim.space/fable-week.html), [2일차](https://hugh-kim.space/fable-week-2.html)). 이 레포가 평가 프레임으로 차용한 완료 게이트 / closed-loop / 정직한 측정 벤치마크의 출처.

고맙습니다 — 여러분이 없었으면 이 레포는 훨씬 얇았을 겁니다.

## 라이선스

이 레포 자체 기여분은 [MIT License](LICENSE) 를 따른다. `hooks/` 아래 훅 설계는 `fable-ish-codex` (Apache-2.0, Copyright Pandoll-AI) 에서 이식했다. 필수 저작자 표시는 [NOTICE](NOTICE) 참조.
