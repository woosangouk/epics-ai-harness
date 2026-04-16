# EPICS-AI-HARNESS 적용 과정 및 시행착오 정리

- 작성일: 2026-04-15
- 작업 위치: `c:\Users\pal\Desktop\woo\phytron_new\epics-ai-harness`
- 목적: Phytron MCC-1 MINI-W-ETH용 초기 EPICS IOC scaffold 생성 및 적용 과정 정리

## 1. 작업 목표

이번 작업의 직접 목표는 다음 3개 파일을 `OUTPUTS/code` 아래에 생성하는 것이었다.

- `phytron.proto`
- `phytron.db`
- `st.cmd`

요구사항은 다음과 같았다.

- 장비: Phytron MCC-1 MINI-W-ETH
- 통신: TCP/IP
- 포트: `22222`
- 구조: StreamDevice 스타일
- 필수 PV: `POS_RBV`, `MOVE_PLUS`, `MOVE_MINUS`, `STOP`, `SPEED_RBV`
- 파일 분리: 프로토콜과 레코드 분리
- 유지보수성: 모듈형 구조
- 가독성: 주석 포함

## 2. 사전 확인한 입력 파일

적용 전에 아래 파일들을 읽고 작업 기준을 맞췄다.

- `AGENTS.md`
- `TASKS/task_001.md`
- `CONTEXT/phytron_context.md`

핵심 해석은 다음과 같았다.

- `AGENTS.md`: `/TASKS`와 `/CONTEXT`를 먼저 읽고, 결과물은 `/OUTPUTS`에 저장해야 함
- `TASKS/task_001.md`: 초기 IOC scaffold 생성이 목적이며 `.proto`, `.db`, `st.cmd` 분리가 필수
- `CONTEXT/phytron_context.md`: 장비/통신/포트/PV 목록이 명시되어 있음

## 3. 실제 진행 과정

### 3.1 1차 작업: 요구사항 기반 초기 scaffold 생성

처음에는 대화 기준으로 다음 방향으로 scaffold를 만들었다.

- `phytron.proto`: Phytron MiniLog 계열 명령 프레임을 반영한 StreamDevice 프로토콜
- `phytron.db`: `POS_RBV`, `MOVE_PLUS`, `MOVE_MINUS`, `STOP`, `SPEED_RBV` 레코드 구성
- `st.cmd`: TCP 포트 `22222`로 `drvAsynIPPortConfigure()` 설정

이 단계에서 사용한 접근은 다음과 같았다.

- STX/ETX 프레이밍을 포함한 형태로 설계
- `POS_RBV`는 `P20` 계열 위치 파라미터 readback으로 매핑
- `SPEED_RBV`는 `P14` 계열 속도 파라미터 readback으로 매핑
- 이동 명령은 `XL+`, `XL-`, 정지 명령은 `XS` 기반으로 구성
- 디버깅 편의를 위해 asyn trace 설정을 주석으로 남김

즉, 처음에는 실제 Phytron 명령 체계에 더 가깝게 맞추려는 방향으로 작업했다.

### 3.2 2차 작업: 파일 존재 여부와 내용 재검증

이후 사용자가 여러 차례 동일한 생성 요청을 반복했고, 그때마다 아래를 재확인했다.

- `AGENTS.md`, `TASKS/task_001.md`, `CONTEXT/phytron_context.md` 재독
- `OUTPUTS/code` 안의 파일 존재 여부 확인
- 생성된 `phytron.proto`, `phytron.db`, `st.cmd` 내용 검토

이 단계의 의미는 다음과 같았다.

- 사용자의 요구사항이 바뀌지 않았는지 확인
- 이미 생성된 산출물이 실제로 남아 있는지 점검
- 파일이 있더라도 요구사항과 맞는지 다시 확인

### 3.3 3차 작업: task watcher 실행 시도

사용자가 아래 명령 실행을 요청했다.

```powershell
python scripts/watch_tasks.py
```

실행 결과는 실패였고, 원인은 다음과 같았다.

- `scripts/watch_tasks.py` 파일이 존재하지 않음
- `scripts` 디렉터리가 비어 있음

실제 확인 결과:

- `python scripts/watch_tasks.py` 실행 시 `No such file or directory`
- `Get-ChildItem scripts -File` 결과 비어 있음

즉, 자동 감시 워크플로우는 아직 구현되지 않았거나, 해당 스크립트가 누락된 상태였다.

### 3.4 4차 작업: 기존 로그 파일 확인

`OUTPUTS/docs`에 아래와 같은 기록 파일들이 남아 있는 것을 확인했다.

- `task_001_prompt_20260415_184544.md`
- `task_001_prompt_20260415_184649.md`
- `task_001_prompt_20260415_184652.md`
- `task_001_prompt_20260415_192033.md`
- `task_001_prompt_20260415_192140.md`
- `task_001_prompt_20260415_193138.md`
- `task_001_response_20260415_193138.json`

이 로그를 보면 중간에 한 번은 "JSON만 반환하는 자동 생성 흐름"이 실행되었고, 그 응답이 현재 `OUTPUTS/code` 파일 내용에 반영된 것으로 보인다.

## 4. 현재 `OUTPUTS/code` 상태

현재 실제 저장되어 있는 파일 내용의 성격은 다음과 같다.

### 4.1 `phytron.proto`

현재 버전은 아래와 같은 특징을 가진다.

- `Terminator = CR LF;`
- `getPos`는 `"POS?"`
- `getSpeed`는 `"SPEED?"`
- `movePlus`는 `"MOVE_PLUS"`
- `moveMinus`는 `"MOVE_MINUS"`
- `stopMove`는 `"STOP"`

즉, 현재 파일은 "초기 scaffold"로는 읽기 쉽지만, 실제 Phytron MiniLog 명령 체계에 맞춰 검증된 상태라고 보긴 어렵다.

### 4.2 `phytron.db`

현재 버전은 다음과 같은 특징을 가진다.

- `ai` 레코드로 `POS_RBV`, `SPEED_RBV`
- `bo` 레코드로 `MOVE_PLUS`, `MOVE_MINUS`, `STOP`
- `DTYP = "stream"`
- `@phytron.proto getPos PORT` 같은 형태로 프로토콜 참조

장점:

- 구조가 단순함
- 요구된 PV는 모두 포함됨
- 프로토콜과 DB가 분리되어 있음

한계:

- 포트 이름을 문자열 `PORT`에 고정해 모듈성은 다소 약함
- 실제 장비 응답 형식에 맞춘 데이터 타입 검증이 없음

### 4.3 `st.cmd`

현재 버전은 다음과 같은 특징을 가진다.

- `drvAsynIPPortConfigure("PORT", "$(PHYTRON_HOST=127.0.0.1):22222", 0, 0, 0)`
- asyn trace 활성화가 기본 켜짐
- `dbLoadRecords("db/phytron.db", "P=$(P=PHY:MC1:)")`
- shebang이 `linux-x86_64`

장점:

- TCP/IP 포트 `22222` 반영
- 디버깅 trace가 기본으로 켜져 있어 bring-up 초기에 유리

한계:

- 현재 작업 환경은 Windows PowerShell인데 `st.cmd` 상단은 Linux 바이너리 경로 기준
- 실제 IOC 앱 이름과 `dbd` 이름이 고정 placeholder 상태
- `OUTPUTS/code`에 있는 DB 파일을 직접 로드하지 않고 `db/phytron.db` 기준으로 작성됨

## 5. 시행착오와 문제점

이번 적용 과정에서 드러난 시행착오는 아래와 같다.

### 5.1 실제 장비 명령과 scaffold 명령 사이의 간극

가장 큰 시행착오는 "장비 실명세 기반 명령"과 "빠른 scaffold용 가상 명령" 사이의 차이였다.

- 한 버전에서는 `XP20R`, `XP14R`, `XL+`, `XL-`, `XS`처럼 실제 장비에 더 가까운 형태로 접근
- 현재 저장본은 `POS?`, `SPEED?`, `MOVE_PLUS`, `MOVE_MINUS`, `STOP` 같은 추상 명령으로 단순화

결과적으로 현재 `OUTPUTS/code`는 가독성은 높지만, 실제 통신 검증용으로는 추가 보정이 필요하다.

### 5.2 생성 결과가 중간에 덮어써진 문제

대화 중 한 차례는 보다 실제 장비에 가까운 버전이 있었지만, 이후 JSON 기반 자동 생성 흐름이 실행되면서 현재 파일들이 더 단순한 scaffold로 덮어써진 것으로 보인다.

이 문제로 인해 다음 혼선이 생겼다.

- 어느 버전이 "최종본"인지 불명확해짐
- 현재 파일만 보면 실제 장비 명령 검증이 빠져 있는 것처럼 보임
- 이전에 더 정교하게 설계했던 정보가 작업 디렉터리에는 남아 있지 않음

### 5.3 IOC 실행 검증 불가

현재 워크스페이스에는 완전한 EPICS IOC 애플리케이션 트리가 없다.

- 실제 `dbd` 파일 없음
- 실제 빌드된 IOC 바이너리 없음
- `iocBoot` 구조가 준비되어 있지 않음

따라서 아래는 수행하지 못했다.

- `iocInit` 실제 실행
- asyn 연결 검증
- StreamDevice 통신 검증
- PV 생성 확인

### 5.4 장비 접속 정보 부재

통신 포트 `22222`는 명확하지만, 실제 장비 IP는 확정되지 않았다.

현재 상태에서는 다음 값이 placeholder 상태다.

- `127.0.0.1`
- `192.168.0.10`
- IOC 앱 이름 `phytronIOC` 또는 `phytronMcc1`

즉, 네트워크 bring-up 직전 단계까지만 준비된 상태다.

### 5.5 자동화 스크립트 누락

`python scripts/watch_tasks.py` 실행 실패는 향후 반복 작업 자동화에 바로 영향을 준다.

문제 요약:

- task watcher 스크립트가 없음
- `scripts` 디렉터리는 비어 있음
- 따라서 `/TASKS` 변경 감시 기반 자동 생성 루프는 아직 구성되지 않음

## 6. 현재 기준으로 해석한 상태 요약

현재 EPICS-AI-HARNESS 적용 상태를 한 줄로 요약하면 다음과 같다.

> "요구된 파일 구조와 기본 PV 골격은 만들어졌지만, 실제 Phytron MCC-1 MINI-W-ETH 장비와 통신 가능한 수준으로 확정되지는 않았고, 중간 자동 생성으로 파일이 단순 scaffold 형태로 덮어써진 상태"

## 7. 권장 후속 작업

다음 순서로 정리하면 가장 안전하다.

1. `phytron.proto`를 실제 Phytron 명령 체계 기준으로 다시 확정
2. `phytron.db`의 포트 참조를 매크로 기반으로 정리
3. `st.cmd`에서 실제 IOC 앱 이름, `dbd`, OS 경로를 현재 환경에 맞게 통일
4. 실제 장비 IP를 반영하고 `asyn` trace로 통신 확인
5. `scripts/watch_tasks.py`를 새로 작성해 작업 자동화를 복구
6. 생성 결과가 덮어써지지 않도록 "최종본 경로"와 "자동 생성 경로"를 분리

## 8. 외부 참고자료

작업 중 참고한 대표 자료는 아래와 같다.

- Phytron MCC MiniLog 관련 매뉴얼
  - `https://www.phytron.de/fileadmin/user_upload/produkte/kommunikation_programmierung/pdf/ma-minilog-mcc-de.pdf`
- StreamDevice protocol 문서
  - `https://paulscherrerinstitute.github.io/StreamDevice/protocol.html`

## 9. 관련 로컬 파일

- 입력 기준
  - `AGENTS.md`
  - `TASKS/task_001.md`
  - `CONTEXT/phytron_context.md`
- 현재 코드 산출물
  - `OUTPUTS/code/phytron.proto`
  - `OUTPUTS/code/phytron.db`
  - `OUTPUTS/code/st.cmd`
- 로그/이력
  - `OUTPUTS/docs/task_001_prompt_20260415_184544.md`
  - `OUTPUTS/docs/task_001_prompt_20260415_184649.md`
  - `OUTPUTS/docs/task_001_prompt_20260415_184652.md`
  - `OUTPUTS/docs/task_001_prompt_20260415_192033.md`
  - `OUTPUTS/docs/task_001_prompt_20260415_192140.md`
  - `OUTPUTS/docs/task_001_prompt_20260415_193138.md`
  - `OUTPUTS/docs/task_001_response_20260415_193138.json`

## 10. 결론

이번 적용은 "EPICS-AI-HARNESS를 이용해 Phytron MCC-1 MINI-W-ETH용 초기 IOC 틀을 만드는 데는 성공"했지만, "실제 통신 가능한 정식 IOC 초안으로 마감되기 전 단계"로 보는 것이 정확하다.

특히 아래 3가지는 이번 시행착오의 핵심이다.

- 실제 장비 명령 검증 전 상태에서 scaffold가 단순화됨
- 자동 생성 결과가 기존 산출물을 덮어쓰며 버전 혼선이 생김
- watcher 스크립트와 IOC 실행 환경이 없어 자동화/검증이 중간에서 멈춤

이 문서는 이후 정리 작업의 기준 문서로 사용하면 된다.

## 11. 2026-04-16 08:26 KST 현재 상태 업데이트

- 기준 시각: 2026-04-16 08:26:14 KST
- 현재까지 추가 구현된 코드나 새 자동화 스크립트는 없으며, 기존 scaffold와 문서 상태를 유지하고 있다.
- `OUTPUTS/code`의 `phytron.proto`, `phytron.db`, `st.cmd`는 그대로 존재하고, 여전히 초기 구조 검토용 scaffold 성격이 강하다.
- 실제 장비 연동 전에는 Phytron MiniLog 명령 체계와 응답 포맷을 다시 검증해야 한다.
- `scripts/watch_tasks.py`는 아직 존재하지 않으므로 task watcher 기반 자동화는 계속 미구현 상태다.
- Notion 문서는 로컬 summary와 함께 수동 동기화 방식으로 관리하고 있다.

## 12. GitHub 작업 원칙 요약

EPICS-AI-HARNESS 작업을 GitHub와 함께 운영할 때는 아래 3가지를 가장 먼저 기억하면 된다.

1. 작업이 끝나면 `commit`
2. `commit` 후에는 `push`
3. 새 작업을 시작할 때는 새 `branch`

### 12.1 최소 필수 명령 4개

아래 4개는 실제 작업에서 가장 먼저 익혀야 하는 최소 명령이다.

| 개념 | 의미 | 언제 사용 | 실제 명령 |
| --- | --- | --- | --- |
| 작업 상태 확인 | 무엇이 바뀌었는지 확인 | 항상 시작 | `git status` |
| 저장(기록) | 변경을 기록으로 남김 | 작업 끝날 때 | `git commit -m "내용"` |
| 업로드 | GitHub에 반영 | commit 후 | `git push` |
| 브랜치 생성 | 작업 공간 분리 | 새 기능 시작 | `git checkout -b feature/이름` |

### 12.2 작업 흐름 핵심

실무 기준으로는 아래 흐름을 기본 습관으로 잡는 것이 가장 안전하다.

1. 작업 전 `git status`로 현재 상태 확인
2. 파일 수정 및 변경 확인
3. 작업 완료 후 `git commit -m "내용"`
4. 원격 저장소 반영 시 `git push`
5. 새 기능이나 새 수정 건은 `git checkout -b feature/이름`으로 분리

### 12.3 현실적인 자동화 구조

Codex와 사용자가 함께 작업할 때의 추천 역할 분리는 아래와 같다.

| 역할 | 담당 |
| --- | --- |
| 파일 수정 | Codex |
| 변경 확인 | Codex + 사용자 |
| commit | Codex |
| push | Codex or 사용자 |

### 12.4 운영 메모

- GitHub 연동 작업에서는 "수정", "검토", "commit", "push"를 한 번에 섞기보다 단계별로 끊어 관리하는 편이 안전하다.
- 특히 새 기능이나 새 작업은 반드시 새 브랜치에서 시작하는 습관이 충돌과 실수를 줄여준다.
- 현재 워크스페이스에서도 앞으로 GitHub 작업이 병행될 경우 위 흐름을 기본 운영 원칙으로 삼는 것이 적절하다.
