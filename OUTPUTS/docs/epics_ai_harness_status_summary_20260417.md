# EPICS-AI-HARNESS Status Summary (2026-04-17)

- 작업 위치: `C:\Users\pal\Desktop\woo\phytron_new\epics-ai-harness`
- 정리 범위: 최근 EPICS/Phytron IOC, Phoebus GUI, 작업 백업, GitHub/Notion 정리
- 기준 시각: 2026-04-17

## 1. 지금까지 진행된 핵심 작업

- `epics/db/phytron.db`
  - 수동 이동 체인과 HOME 소프트 동작 경로를 정리했다.
  - `SPD_SET`, `ACC_SET`, `BM_SET`, `SC_SET`, `RC_SET`, `BC_SET`, `RES_SET` 파라미터 PV를 추가했다.
  - 파라미터 readback은 Passive로 두어 공유 TCP 포트를 불필요하게 점유하지 않도록 설계했다.
- `epics/proto/phytron.proto`
  - 기존 위치/속도 readback과 수동 이동 관련 프로토콜 블록을 보강했다.
  - 파라미터 P14/P15/P17/P40/P41/P42/P45 read/write 블록이 추가된 상태다.
  - 일부 파라미터 write/read는 아직 live hardware TX/RX 증거가 부족해 하드웨어 검증이 남아 있다.
- `gui/phoebus/tuner_main.bob`
  - `CONTROLLER PARAMETERS` 편집 영역과 축약 요약 영역이 추가된 상태다.
  - 수동 이동, HOME, STOP, 위치 표시, 파라미터 편집이 한 화면에 통합됐다.
  - 이번 수정으로 GUI 재실행 시 마지막 파라미터 값을 다시 PV에 적용하는 화면 로컬 persistence 경로를 추가했다.

## 2. 이번에 확인된 문제와 원인

### 2.1 사용자 증상

- `tuner_main.bob`를 다시 실행하면 `CONTROLLER PARAMETERS`의 최종 값이 기억되지 않고, 재적용도 되지 않았다.

### 2.2 실제 확인 결과

- IOC 쪽에는 `epics/db/phytron_settings.req` 파일이 생겨 있었지만,
  `epics/iocBoot/st.cmd`에는 `save_restore` 초기화와 `create_monitor_set(...)`가 전혀 없었다.
- 따라서 IOC 재기동 기준의 autosave/restore는 설계 메모만 있었고 실제 동작 경로는 없었다.
- 동시에 `tuner_main.bob` 내부에도 마지막 값을 저장하고 화면 재실행 시 다시 PV에 쓰는 GUI 측 persistence 스크립트가 없었다.

### 2.3 결론

- 이번 증상은 "기억 기능이 구현된 줄 알았지만 실제로는 구현되지 않은 상태"였다.
- 즉 원인은 `Phoebus GUI persistence 부재`와 `IOC autosave 미배선` 두 가지였고,
  사용자가 바로 체감한 증상은 GUI 재실행 경로에서 발생했다.

## 3. 이번 보완 내용

- `tuner_main.bob`에 다음을 추가했다.
  - 마지막 파라미터 값 저장 스크립트
  - 화면 시작 시 저장값을 다시 `SPD_SET`, `ACC_SET`, `BM_SET`, `SC_SET`, `RC_SET`, `BC_SET`, `RES_SET` PV에 쓰는 복원 스크립트
  - `PERSIST: ...` 상태 표시 라인
- 저장 위치는 Phoebus 실행 사용자 기준 Java Preferences 노드다.
- 키는 장치 매크로 `$(P)$(M)` 기준으로 분리되므로 다른 축과 충돌하지 않도록 했다.

## 4. 백업 결과

- 전체 작업 스냅샷 백업 경로:
  - `C:\Users\pal\Desktop\woo\phytron_new\backups\epics-ai-harness_20260417_225048`
- 포함 항목:
  - 현재 작업트리 전체 복사본
  - `repo_history.bundle`
  - `git_status.txt`
  - `working_tree_from_HEAD.patch`

## 5. 남은 검증 항목

- Phoebus 실제 실행 환경에서:
  - 파라미터 하나를 변경
  - 화면 종료
  - `tuner_main.bob` 재실행
  - `PERSIST: RESTORED ...` 표시와 함께 PV 값이 다시 써지는지 확인
- IOC 재기동 후에도 같은 값이 유지되어야 한다면,
  별도로 `save_restore` 모듈이 IOC executable에 링크되어 있는지 확인한 뒤
  `st.cmd`에 autosave 초기화를 추가해야 한다.

## 6. 현재 판단

- GUI 재실행 기준 "마지막 파라미터 기억 후 재적용" 문제는 `tuner_main.bob` 내부에서 직접 처리하도록 보완했다.
- IOC 재부팅까지 포함한 영구 복원은 아직 별도 작업이다.
