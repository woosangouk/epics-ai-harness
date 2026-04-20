# EPICS-AI-HARNESS progress update (2026-04-20 15:47:04 KST)

- 작성일: 2026-04-20 15:47:04 KST
- 작업 위치: `C:\Users\pal\Desktop\woo\phytron_new\epics-ai-harness`
- 기준 브랜치: `main`
- 기준 HEAD: `a57aa1b`
- 목적: 2026-04-20 기준 Phoebus GUI / AUTO-SIM / 문서화 진행 상황을 GitHub와 Notion에 동기화

## 1. 완료 또는 반영된 항목

- `CONTROLLER PARAMETERS` persistence는 Phoebus 재실행 후에도 마지막 값이 다시 로딩되도록 보완되었고, 사용자 확인 기준으로 정상 동작 상태다.
- `SHOW POSITION` X축 autoscaling은 `POS_RBV` 기준으로 재정리되어 현재 위치에 따라 축이 줄고 늘어나며, 최소 범위 `+-100`을 유지하도록 보정되었다.
- `CONTROLLER PARAMETERS`는 초기 화면에서 folded 상태로 시작하고, 필요할 때만 `EDIT`로 펼치는 구조로 정리되었다.
- `AUTO` 화면에는 `LLRF SOURCE`, `GMES/MIN`, `GO/STOP`, `DETA MANUAL`, `DETUNE TREND`, `PARAM RBV`가 포함된 제어 UI가 추가되었다.
- `MOVE LOG`는 `MANUAL`뿐 아니라 `AUTO` 화면에서도 표시되도록 visibility를 확장했다.
- `DETUNE TREND` 우측에는 threshold speed와 over-limit speed를 설정하는 입력란을 추가했고, 안정 구간 진입 시 약 2초 dwell 및 `HAPPY` 표시 로직을 연결했다.
- `HIHI/HIGH/LOW/LOLO` 값은 sign normalization과 persistence 경로를 갖도록 정리되었다.

## 2. AUTO / SIM 진행 내용

- `AUTO` 동작은 현재 `SIM`만 실제 구현 대상으로 유지하고, `JLAB / INTEC / NEO`는 UI와 PV 구조만 준비된 standby 상태로 두고 있다.
- `DETA PERIOD`와 `DETA STEP`는 `SIM`에서 Detune Angle 생성 시간 스케일과 변화량에 반영되도록 연결되어 있다.
- `DETUNE TREND` 최신값 숫자 표시와 상단 Detune 박스, 모터 판단 로직은 동일한 detune source를 참조하도록 맞추는 방향으로 계속 보강 중이다.
- `AUTO` motor speed는 최근 조정 기준으로 threshold zone `40`, over-limit zone `200`을 사용하도록 보강했다.

## 3. 현재 남아 있는 live 확인 이슈

- 최신 사용자 확인 기준으로는 `DETUNE TREND` horizontal grid가 아직 live Phoebus 화면에서 충분히 보이지 않는다.
- 최신 사용자 확인 기준으로는 `SIM + GO` 이후에도 `Detune Angle` 값이 `0.00`에 머무는 증상이 남아 있다.
- 따라서 현재 AUTO / SIM detune generation 로직은 로컬 `.bob` 수정과 XML 검증은 반복 수행되었지만, live Phoebus runtime에서 최종 수렴 확인이 아직 끝나지 않은 상태다.
- 특히 이 구간은 local file과 실제 Phoebus가 로드한 `.bob` 경로가 다를 가능성, 또는 embedded runtime thread/local PV writeback 차이가 남아 있을 가능성을 계속 열어두고 확인 중이다.

## 4. 운영상 안전 조치

- AUTO 본격 작업 전 전체 스냅샷 백업은 이미 생성되어 있다.
- 백업 경로:
  - `C:\Users\pal\Desktop\woo\phytron_new\backups\epics-ai-harness_20260420_093140`
- 복구 안내 문서:
  - `OUTPUTS/docs/auto_work_backup_restore_20260420_093140.md`

## 5. 이번 GitHub / Notion 동기화 원칙

- 현재 작업트리에는 문서 외에도 여러 in-progress 코드 변경이 함께 존재한다.
- 따라서 이번 GitHub 반영은 전체 작업트리를 push하는 방식이 아니라, 진행 현황 summary 문서만 별도로 commit/push 하는 방식으로 처리한다.
- Notion은 canonical page `EPICS-AI-HARNESS 적용 과정 및 시행착오 정리 (2026-04-15)`에 최신 업데이트 섹션을 추가하는 방식으로 유지한다.

## 6. 다음 확인 우선순위

1. live Phoebus에서 실제로 로드 중인 `.bob` 경로 재확인
2. `SIM + GO` 후 detune local PV writeback이 runtime에서 살아 있는지 확인
3. horizontal grid visibility를 live renderer 기준으로 재확인
4. detune가 threshold 구간을 실제로 오가며 `STOP / CW20 / CW100 / CCW20 / CCW100`을 반복하는지 확인
