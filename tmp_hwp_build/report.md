# KLS LLRF Detuning 기반 Reference-Tracking
# Cavity Tuner 제어 시스템 개발 및 검증 보고서

## KLS LLRF Detuning-Driven Reference-Tracking Cavity Tuner Control

**우 상 욱**

Pohang Accelerator Laboratory  
POSTECH

**POHANG ACCELERATOR LABORATORY**  
**INTERNAL REPORT**

| Report Number | PAL-INT/EE-2026-___ |
|---|---|
| Pages | 최종 한컴 조판 후 확정 |
| Date | 2026.08.21 |
| Classification | EE – Electrical Engineering |
| Author | 우상욱 |
| Title | KLS LLRF Detuning 기반 Reference-Tracking Cavity Tuner 제어 시스템 개발 및 검증 |
| Reviewer |  |
| Keywords | KLS, LLRF, Cavity Detuning, Cavity Tuner, Reference Tracking, EPICS, Phoebus, PHYTRON MCC-1 |

본 보고서는 V12 기술 초안의 확인된 근거를 기반으로 작성하였다. 실제 cavity 검증이 완료되지 않은 항목은 임의의 결과로 채우지 않고 확인 필요 또는 추후 검증으로 구분하였다.

**목 차**

**1. 서론** 4

1.1 보고서 목적 및 범위 4

1.2 개발 배경과 문제 정의 4

1.3 근거 수준과 용어 사용 원칙 5

**2. KLS RF Cavity-Tuner 제어 시스템 구성** 5

2.1 전체 제어 체인 5

2.2 LLRF Detuning 및 Readiness 신호 7

2.3 PHYTRON MCC-1 위치 경로와 좌표계 8

2.4 모션 파라미터 및 입력 검증 정책 8

**3. Detuning 기반 Reference-Tracking 제어 구조** 9

3.1 Baseline Threshold-Reaction AUTO 9

3.2 Reference 생성 및 Tracking Error 10

3.3 STEP 좌표계와 P45 정규화 10

3.4 Motion Scheduler와 Busy/Completion 10

3.5 Command Ownership 및 Safety Priority 11

**4. EPICS/Phoebus 및 MCC-1 구현 구조** 12

4.1 기능 계층과 Source Mapping 12

4.2 MANUAL/AUTO 운용 구조 12

4.3 통신 및 Position Readback 13

4.4 Logging / Provenance 관리 13

**5. 실험 및 검증 방법** 14

5.1 검증 절차 14

5.2 Configuration Freeze와 동기 로깅 15

5.3 Actuator / Position Characterization 15

5.4 Cavity-Tuner Calibration 15

5.5 Closed-loop A/B Test 16

5.6 STOP / AUTO_ABORT 검증 17

**6. 현재 개발 근거 및 검증 상태** 17

**7. 정량 평가 지표 및 데이터 유효성** 19

**8. 결론 및 향후 수행 항목** 21

**9. 참고 문헌** 22

**10. 부록** 22

# 1. 서론

## 1.1 보고서 목적 및 범위

본 보고서는 Korea Light Source(KLS) RF cavity의 기계식 tuner를 대상으로 개발 중인 LLRF detuning 기반 reference-tracking 제어 구조를 내부 기술 보고서 형식으로 정리한 것이다. 학술 논문 V12 초안에 기술된 제어 개념, EPICS/Phoebus–PHYTRON MCC-1 연동 구조, 위치 좌표계, 모션 파라미터 정책, 검증 방법 및 미해결 항목을 하나의 개발·검증 문서로 재구성하였다.

보고서의 목적은 단순히 GUI나 모터 통신 기능을 설명하는 데 있지 않다. 각 tuner motion이 어떤 LLRF 상태에서 생성되었는지, 생성된 target coordinate가 무엇인지, controller-position readback과의 오차가 어떻게 사용되는지, 그리고 안전 조건이 모션 명령보다 어떤 우선순위를 갖는지를 추적 가능한 형태로 정리하는 것이 핵심이다. 따라서 controller-coordinate convergence와 실제 RF/cavity 성능 개선은 서로 다른 증거 수준으로 분리하여 기술한다.

최종 적용 대상 LLRF는 INTEC이며, JLAB LLRF는 개발 단계에서 사용된 provisional source로만 취급한다. V12 초안에서 실제 cavity 시험, INTEC signal semantics, 최종 q_RF, STEP_REF의 물리적 target basis 및 end-to-end stop confirmation이 완료되지 않았으므로, 본 보고서도 이 항목들을 사실처럼 확정하지 않고 “확인 필요” 또는 “추후 검증”으로 유지한다.

| **[확인 필요]** 초기 공개 RF-system 문헌에는 Korea-4GSR 명칭이 사용된다. KLS와 Korea-4GSR의 공식 명칭 관계 문구는 기관 기준으로 별도 확정해야 하며, 본 보고서에서는 이를 임의로 단정하지 않는다. |
|---|

## 1.2 개발 배경과 문제 정의

Mechanical cavity tuner는 RF cavity의 공진 조건을 조정하는 actuator이다. 그러나 motor command나 controller counter가 정상적으로 변화했다는 사실만으로 RF 상태가 목표 조건으로 수렴했는지 또는 실제 기계 변위가 명령량과 동일하게 발생했는지를 모두 입증할 수 없다. 반대로 LLRF가 제공하는 detuning-related quantity는 RF-side condition을 관찰할 수 있지만, 이것을 actuator의 위치 제어와 연결하려면 신호 의미, 좌표계, feedback provenance 및 command ownership이 명확해야 한다.

개발 초기 AUTO 경로는 detuning-related value가 threshold band를 벗어나면 direction과 bounded relative move를 선택하는 condition-reaction 구조였다. 이 구조는 명시적 controller-position reference를 목표로 두거나 reference와 controller-reported position 사이의 tracking error를 제어 변수로 사용하는 구조가 아니다. 또한 detuning path와 correction path가 동시에 motor command를 요청할 수 있는 구조는 command ownership이 중복될 위험이 있으므로, 개발 단계에서 제어 아키텍처 위험으로 식별되었다.

이를 개선하기 위해 detuning-related quantity에서 STEP_REF를 생성하고, STEP_REF와 controller-position input인 STEP_ACT의 차이 STEP_ERR를 observable controller variable로 사용하는 reference-tracking 계층을 구성하였다. 다만 V12 근거는 gain/offset 형태의 reference generator software form이 존재함을 보여주는 수준이며, measured detuning을 desired RF operating state의 절대 target coordinate로 변환하는 물리적 의미는 아직 최종 검증되지 않았다.

## 1.3 근거 수준과 용어 사용 원칙

본 보고서는 개발 근거의 수준을 DEVELOPMENT VERIFIED, DEVICE VERIFIED, NOT VERIFIED로 구분한다. Software source 또는 control-flow에서 확인된 기능은 DEVELOPMENT VERIFIED로, 장치 통신이나 controller coordinate의 동작을 실장 시험에서 확인한 경우 DEVICE VERIFIED로 표현한다. 실제 RF cavity에서의 성능 또는 독립 기계 변위를 확인하지 못한 항목은 NOT VERIFIED로 유지한다.

표 1. 본 보고서의 주요 용어 및 증거 수준 사용 원칙

| **용어** | **본 보고서의 의미** | **주의 사항** |
|---|---|---|
| Controller-position readback | MCC-1 P20 계열 counter 및 project-side HOME/P45 normalization을 통해 얻는 위치 계열 값 | 독립 encoder 또는 실제 tuner 변위와 동일시하지 않음 |
| STEP_REF | 개발 reference generator가 생성하는 controller-position reference | 물리적 desired-target basis는 P0 검증 항목 |
| STEP_ACT | STEP_REF와 비교되는 controller-position quantity | 최종 PV/좌표계/provenance 확정 필요 |
| STEP_ERR | STEP_REF − STEP_ACT | controller-coordinate tracking metric |
| q_RF | Baseline/Reference 공통 비교용 RF-side outcome | 물리적 의미, 단위, target/band, 허용오차, dwell 확정 필요 |
| Actual tuner position | 독립 sensor/encoder 또는 검증된 mechanical conversion으로 확인된 기계 위치 | 현재 주 P20 경로만으로는 주장하지 않음 |

# 2. KLS RF Cavity-Tuner 제어 시스템 구성

## 2.1 전체 제어 체인

전체 제어 체인은 LLRF source, operator interface, tuner-control IOC, StreamDevice/TCP communication, PHYTRON MCC-1, stepper motor, mechanical tuner 및 RF cavity로 구성된다. 제어 입력과 성능 결과는 분리하여 관리하며, LLRF source의 외부 PV는 source-specific mapping layer에서 공통 내부 quantity로 변환한다.

그림 1. KLS RF cavity-tuner control 및 evidence architecture

표 2. Tuner-control 시스템 구성 및 상태

| **구성 요소** | **구현/역할** | **상태 및 확인 항목** |
|---|---|---|
| Supervisory control | EPICS IOC + Phoebus | 최종 validation에 사용한 IOC/GUI release 고정 필요 |
| Motor controller | PHYTRON MCC-1 | 정확한 model/firmware 기록 필요 |
| LLRF interface | JLAB 개발 → INTEC 최종 | INTEC live compatibility와 DETA/TDOFF semantics 검증 필요 |
| RF cavity/tuner | Mechanical cavity-tuner system | 실제 cavity/tuner ID 및 drawing reference 기록 필요 |
| Position feedback | P20/0XP20R → RAW_POS_RBV → HOME/P45 normalized coordinate | final STEP_ACT 및 independent sensor 여부 확정 필요 |
| Safety path | MOTION_PERMIT / limits / STOP / AUTO_ABORT | priority와 end-to-end stop confirmation 검증 필요 |

전체 control/evidence chain은 다음과 같이 정리할 수 있다.

LLRF (DETA/TDOFF/readiness) → normalization → D_c/D_f → reference-generator semantics → STEP_REF → controller-position input → STEP_ERR → scheduler → busy/completion + dispatch gate → safety gate → MCC-1 → motor/tuner → RF cavity → LLRF feedback

이때 LLRF control-input quantity와 RF 성능평가 quantity는 개념적으로 분리한다. DETA, DETA_CAL, D_c, D_f는 reference generator의 입력 후보이며, baseline/reference-tracking의 공통 성능 비교에는 별도로 검증된 q_RF를 사용한다.

## 2.2 LLRF Detuning 및 Readiness 신호

LLRF source interface는 source별 external PV와 readiness decoding을 mapping layer에서 처리하여 공통 tuner-control quantity를 제공하도록 구성한다. 개발 초기에는 JLAB LLRF를 provisional interface로 사용했으며, 최종 cavity experiment에서는 INTEC mapping으로 전환하는 것을 전제로 한다. 단순한 PV 이름 치환만으로 두 source의 functional equivalence를 가정하지 않는다.

DETA_CAL은 development GUI/local layer에서 다음과 같이 계산되는 것으로 확인되어 있다.

DETA_CAL(t) = DETA(t) − TDOFF(t)

그러나 이 식의 존재만으로 DETA_CAL이 INTEC에서 물리적으로 올바른 detuning error 또는 desired target quantity임을 의미하지 않는다. 최종 적용 전에 DETA와 TDOFF의 physical definition, engineering unit, sign convention, valid range, calibration state, native update rate, timestamp behavior, offset/reference inclusion 여부, readiness semantics 및 failure/disconnect behavior를 live signal과 LLRF documentation을 통해 확인해야 한다.

표 3. LLRF 및 제어 주요 신호

| **신호/quantity** | **역할** | **현재 상태/주의 사항** |
|---|---|---|
| DETA | Source-native detuning-related quantity | INTEC semantics 검증 후 control candidate로 사용 |
| TDOFF | Source-native offset/reference-related quantity | PV 이름만으로 offset/target 의미를 가정하지 않음 |
| DETA_CAL | DETA − TDOFF development 계산값 | 계산식은 확인, INTEC physical semantics는 검증 필요 |
| D_c | Reference generator로 입력되는 selected control input | DETA 또는 DETA_CAL 중 최종 source trace 후 확정 |
| D_f | Filtered control input | filtering 미사용 시 D_f = D_c |
| GMES / RFON / GDR | READY/readiness quantities | unit/threshold/live transition/failure behavior 검증 필요 |
| STEP_REF | Controller-position reference | software form 확인, physical target basis 검증 필요 |
| STEP_ACT | Tracking 비교용 controller-position input | P20/RAW/POS-derived, 최종 provenance 확정 필요 |
| MOTION_PERMIT / limits | Motion inhibition/safety gate | final direction/priority response 검증 필요 |
| q_RF | Baseline/Reference 공통 RF-side outcome | 의미/단위/target/band/ε_RF/dwell 확정 필요 |

## 2.3 PHYTRON MCC-1 위치 경로와 좌표계

현재 확인된 주 position path는 MCC-1의 P20 계열 position/pulse-counter query인 0XP20R을 통해 RAW_POS_RBV를 취득하고, project-side HOME_OFFSET 및 P45-aware normalization을 적용하여 controller/user coordinate를 구성하는 구조이다. 제조사 문서에서 P20은 mechanical-zero-point pulse counter로 정의되고 P22는 별도의 encoder-position counter로 구분되므로, 0XP20R/RAW_POS_RBV 경로를 독립 encoder feedback으로 표현해서는 안 된다.

Project-side soft HOME은 H.SET 시 현재 RAW_POS_RBV를 HOME_OFFSET에 저장하여 home-relative coordinate를 재계산한다. P45-aware user-step normalization에서는 USER_STEP을 motor full-step-equivalent project coordinate로 유지하며 hardware pulse는 다음 관계를 갖는다.

HW_PULSE = USER_STEP × P45

V12 근거에서 P45=16, USER_STEP=100 조건에서 RAW counter +1600 pulse와 POS_USER_RBV +100 behavior가 확인되었다. 이는 commanded/controller pulse-coordinate consistency를 지지하는 device-level evidence이며, lost step이나 실제 shaft/tuner displacement accuracy를 독립적으로 검증한 결과는 아니다.

표 4. STEP 좌표계 및 provenance

| **Quantity** | **의미** | **좌표/관계** |
|---|---|---|
| STEP_REF | Development controller-position reference | 최종 USER_STEP 또는 RAW/HW-pulse domain 확정 필요 |
| STEP_ACT | Tracking controller가 STEP_REF와 비교하는 controller-position quantity | STEP_REF와 동일 좌표계 필요 |
| STEP_ERR | STEP_REF − STEP_ACT | REF/ACT 동일 좌표계 |
| USER_STEP | Project full-step-equivalent coordinate | 200 USER_STEP = motor shaft 1 rev로 runtime normalization 확인 |
| HW_PULSE | Resolution-applied move pulse | USER_STEP × P45 |
| P45 / RES | MCC-1 step-resolution parameter | 제조사 1–256, project accepted set {1,2,4,8,16} |

## 2.4 모션 파라미터 및 입력 검증 정책

Legacy JLAB/MD2S에서 사용하던 TVELS, TACCS, DIR, TSTPS 및 GO의 motion semantics는 MCC-1의 run frequency/ramp, direction, relative movement amount 및 execution으로 기능적 대응을 구성하였다. 제조사 MINILOG programming manual 기준으로 P04는 start/stop frequency, P14는 positioning run frequency, P15는 P14 ramp, P40/P41은 stop/run current, P45는 step resolution parameter이다.

제조사 capability와 project-side GUI/IOC 허용 범위는 반드시 구분한다. 현재 project requirement에서는 허용범위 밖의 입력을 clamp하지 않고 전체 reject하여 last-valid setpoint와 hardware state를 유지하고 MCC-1 write가 발생하지 않도록 한다.

표 5. Motion parameter policy

| **Parameter** | **Manufacturer semantics** | **Project allowed policy** | **최종 검증** |
|---|---|---|---|
| P04 / START.f | Start/stop frequency | 0–400 | SET/RBV/TX 및 boundary behavior 확인 필요 |
| P14 / SPD | Positioning run frequency | 0–4000 | SET/RBV/TX 확인 필요 |
| P15 / ACC | Ramp parameter for P14 | 0–25000 | Ramp/STEP pulse profile과 교차검증 필요 |
| P40 / STOP.c | Stop-current setting | 0–25 | SET/RBV/TX 확인 필요 |
| P41 / RUN.c | Run-current setting | 0–25 | SET/RBV/TX 확인 필요 |
| P45 / RES | Step resolution, manufacturer 1–256 | {1,2,4,8,16} | readback 및 USER/HW scaling 확인 필요 |

# 3. Detuning 기반 Reference-Tracking 제어 구조

## 3.1 Baseline Threshold-Reaction AUTO

Baseline AUTO path는 detuning 또는 detuning-related value를 threshold band와 비교하여 상태에 따라 direction, speed gain 및 bounded relative step motion을 선택하는 threshold-reaction 구조이다. Stable band 내부에서는 새로운 motion command를 발생시키지 않는다.

Baseline CORR OFF development mode에서는 STEP_REF가 controller variable로 생성되지 않고 target-step local variable이 NaN으로 유지되는 것으로 문서화되어 있다. 따라서 baseline에는 position-domain STEP_ERR가 존재하지 않는다. 두 mode의 공통 성능 비교에는 양쪽에서 동일하게 정의 가능한 RF-side outcome q_RF를 primary metric으로 사용해야 한다.

Command count, direction reversal, accumulated commanded movement 및 provenance가 명확한 controller-coordinate activity는 secondary engineering metric으로 사용할 수 있다. STEP_ERR, controller-coordinate settling time, MAE_s, RMSE_s, max|e_s|는 reference-tracking mode의 내부 controller-coordinate metric으로만 사용한다.

## 3.2 Reference 생성 및 Tracking Error

Reference-generation chain에서는 source-specific DETA와 TDOFF를 취득하고 development layer에서 DETA_CAL을 계산한다. 최종 control input D_c는 INTEC signal semantics와 실제 deployed source를 확인한 후 DETA 또는 DETA_CAL 중 하나로 고정해야 한다.

Filtering을 사용하지 않는 경우 D_f(t)=D_c(t)로 두며, filtering을 활성화하는 경우에만 filter type, equation, coefficient/window/time constant, update period 및 induced delay를 고정 기록한다.

Development record에서 확인되는 STEP_REF generator의 affine software form은 다음과 같이 표현할 수 있다.

S_ref(t) = G_D · D_f(t) + S_0

e_s(t) = S_ref(t) − S_act(t)

여기서 이 식은 현재 단계에서 final physical control law로 확정된 것이 아니다. Gain/offset 형태의 AutoTargetStepValue 생성과 STEP_ERR 계산 구조는 development evidence가 있으나, D_f가 current measurement인지 desired target에 대한 error인지, 혹은 S_0/G_D에 desired operating-point information이 포함되어 있는지는 최종 source와 actual-cavity calibration을 통해 검증해야 한다.

## 3.3 STEP 좌표계와 P45 정규화

Reference-tracking에서 STEP_REF와 STEP_ACT는 반드시 동일한 coordinate를 사용해야 한다. Final tracking coordinate가 USER_STEP-equivalent coordinate라면 P45는 hardware pulse conversion을 변경하지만 reference coordinate 자체를 자동으로 재스케일하지 않는다. 반대로 RAW/HW-pulse domain을 tracking coordinate로 사용한다면 G_D 및 STEP_REF scaling도 P45에 따라 변환되어야 한다.

따라서 최종 experiment에서는 “STEP_REF=100”과 같은 숫자를 단독으로 표기하지 않고, coordinate definition, HOME reference 및 P45 context를 함께 기록해야 한다. G_D의 unit도 동일 coordinate를 기준으로 명시한다.

Deadband condition은 다음과 같이 개념적으로 정리한다.

|e_s(t)| ≤ B_s ⇒ HOLD

단 B_s의 최종 값은 frozen controller configuration에서 확정해야 한다.

## 3.4 Motion Scheduler와 Busy/Completion

Reference-tracking development logic에는 deadband/hold, settling 및 large-error/override behavior가 문서화되어 있다. Deadband에서는 새로운 tracking output을 0으로 유지하고, settling region에서는 reduced speed/acceleration을 사용하며, large error에서는 remaining follow error를 넘지 않는 bounded incremental command 및 bounded SPD/ACC override를 적용하는 방향으로 구성한다.

Scheduler decision interval과 MCC-1 motion duration은 서로 다른 시간 척도이다. 따라서 AUTO loop period가 짧다는 사실만으로 command overlap이 방지된다고 볼 수 없다. Final deployed runtime에서 previous command active 시 새 decision을 block, overwrite, STOP-and-redispatch, queue, remaining-error update 또는 다른 deterministic rule로 처리하는지 source/PV level에서 확인해야 한다.

최종 scheduler 흐름은 다음과 같은 순서를 기준으로 기록한다.

Tracking Error Calculation → Scheduler Decision → Busy/Completion Check → Dispatch Eligibility → P14/STEP/ACC Parameter Load → Direction/Move Fire → MCC-1 Motion → Motion Completion Confirmation → Next Decision

표 6. Scheduler condition과 action

| **상태** | **STEP rule** | **SPD/ACC rule** | **Dispatch** |
|---|---|---|---|
| Safety invalid / abort | 0 / STOP path | new override 없음 | Tracking prohibited, STOP/abort 우선 |
| |e_s| ≤ B_s / HOLD | 0 | new override 없음 | No move |
| Fine region | remaining |e_s| 이내 bounded step | reduced SPD/ACC | completion gate 확인 후 dispatch |
| Large error | bounded/saturated increment | bounded max 방향 | completion gate 확인 후 dispatch |
| Previous command active | final rule이 허용하지 않으면 새 command 없음 | parameter overwrite 금지 | final busy rule 확인 필요 |

## 3.5 Command Ownership 및 Safety Priority

Command ownership과 safety priority는 tracking performance와 분리하여 검증한다. Development IOC architecture에서는 STOP/AUTO_ABORT가 AUTO latch/trigger를 clear하고 pending AUTO command를 차단한 뒤 STOP path로 연결되며, normal motion output은 MOTION_PERMIT 및 directional limit gate를 통과하도록 구성되어 있다.

STOP은 normal MOTION_PERMIT gate에 의해 차단되지 않아야 한다. Detuning/correction arbitration에서는 detuning active 시 detuning path가 motor ownership을 갖고 correction path는 neutral/STOP condition에서만 motion을 요청하도록 정리된 development evidence가 있다.

표 7. Command/Safety ownership priority

| **우선 조건** | **허용 모션** | **Software action** | **검증 수준** |
|---|---|---|---|
| STOP / AUTO_ABORT | 없음 | AUTO clear/block + STOP + confirmation chain | DEV 확인, T3 추후 검증 |
| Directional limit | 검증된 안전 방향만 | 금지 방향 inhibit | direction semantics 확인 필요 |
| MOTION_PERMIT=0 / NOT READY / disconnect | 없음 | normal MANUAL/AUTO write block | Development IOC gate |
| MANUAL owner | validated MANUAL만 | AUTO inhibit | 최종 exclusivity 확인 필요 |
| AUTO valid | bounded AUTO move | scheduler → dispatch → MCC-1 | INTEC execution 확인 필요 |

# 4. EPICS/Phoebus 및 MCC-1 구현 구조

## 4.1 기능 계층과 Source Mapping

Implementation layer는 LLRF source normalization, operator command, baseline AUTO state, development reference/error computation, dispatch eligibility, safety gate, device communication 및 plant/readback feedback을 기능적으로 분리한다.

JLAB은 provisional development source이며 최종 source는 INTEC이다. Source mapping layer는 외부 PV 차이를 흡수하되 downstream logic이 특정 LLRF에 종속되지 않도록 구성한다. 다만 JLAB에서 INTEC로 PV 이름만 바꾸는 방식은 functional validation이 아니다. INTEC의 unit, sign, readiness semantics 및 live bridge behavior를 최종 환경에서 확인해야 한다.

Development review에서는 reference-tracking GUI/local implementation evidence가 있으나, selected LLRF DETA의 DETUNE_ANGLE_RBV bridge 및 GUI-local threshold-to-IOC authority가 최종 INTEC IOC path까지 완전히 닫힌 것으로 확인되지 않았다. 따라서 final runtime은 source mapping → live D_c/D_f → STEP_REF → STEP_ACT → scheduler → busy/completion → safety → MCC-1 → completion/readback → RF response 순서로 frozen source와 log에서 다시 추적해야 한다.

## 4.2 MANUAL/AUTO 운용 구조

MANUAL mode는 operator가 지정한 상대 이동량과 방향을 MCC-1에 전달하는 기본 운용 경로이다. MANUAL command는 MOTION_PERMIT 및 방향별 limit gate를 만족할 때만 허용되어야 하며, AUTO mode가 active인 동안 MANUAL command가 동시에 motor ownership을 갖지 않도록 exclusivity를 명확히 해야 한다.

AUTO mode는 selected LLRF quantity와 readiness state를 기반으로 threshold-reaction 또는 reference-tracking logic을 수행한다. Reference-tracking mode에서는 STEP_REF/STEP_ERR 및 scheduler state가 command generation의 근거가 된다. STOP/AUTO_ABORT는 MANUAL/AUTO보다 상위 우선순위로 관리한다.

Operator GUI는 command button만 표시하는 화면이 아니라 다음 정보를 함께 관찰할 수 있도록 구성하는 것이 바람직하다.

- LLRF source 및 readiness
- DETA/TDOFF/DETA_CAL 또는 최종 D_c/D_f
- STEP_REF / STEP_ACT / STEP_ERR
- P14/P15/P45 및 STEP command
- MANUAL/AUTO state와 motor ownership
- MOTION_PERMIT 및 IN/OUT limit
- STOP/AUTO_ABORT 및 stop-confirmation state
- Controller-position trend와 RF-side outcome trend

## 4.3 통신 및 Position Readback

EPICS IOC와 MCC-1은 StreamDevice/TCP communication 경로를 사용한다. Device-level position readback의 핵심은 0XP20R 기반 P20 counter query이다. 해당 값은 RAW_POS_RBV로 수집되며 HOME_OFFSET과 P45 normalization을 거쳐 POS_RBV/POS_USER_RBV 등의 project coordinate로 사용된다.

STOP communication은 Wireshark capture에서 MCC-1 STOP telegram payload '01S'와 ACK pattern이 관찰된 development/device evidence가 있다. 그러나 command transmission 또는 ACK만으로 실제 motor/tuner motion이 정지했다고 할 수 없다. STOP 검증에서는 transmission/ACK와 stop confirmation을 분리한다.

## 4.4 Logging / Provenance 관리

Final validation에서 가장 중요한 요구사항 중 하나는 동일한 control chain을 재구성할 수 있는 logging과 provenance이다. 각 run 전 최소한 다음 configuration을 고정 및 기록한다.

- cavity/tuner/motor ID와 drive train
- position-feedback mechanism 및 independent sensor 사용 여부
- MCC-1 model/firmware
- IOC build/version
- Phoebus GUI version
- StreamDevice protocol file/version
- INTEC LLRF source/version
- P04/P14/P15/P40/P41/P45
- HOME/OFFSET
- reference-generator model/semantics
- scheduler/busy/completion logic
- safety state
- logger/analysis software version과 time-base rule

DETA_CAL, D_c, D_f, STEP_REF, STEP_ERR가 local quantity일 경우 Archiver PV 존재를 가정하지 않는다. 동일 runtime logger로 직접 기록하거나, 재현 가능한 reconstruction input과 timestamp를 저장해야 한다.

# 5. 실험 및 검증 방법

## 5.1 검증 절차

Experimental validation은 네 단계로 구성한다.

1. Device/communication 및 position-provenance verification
2. Cavity/tuner calibration
3. Frozen closed-loop reference-tracking A/B validation
4. Safety-response evaluation

JLAB test와 simulated input은 development evidence로만 사용하고, 최종 RF performance claim은 INTEC LLRF와 actual cavity에서 수집한 frozen-controller validation dataset으로 제한한다.

그림 4. KLS cavity-tuner 최종 검증 절차

## 5.2 Configuration Freeze와 동기 로깅

Closed-loop test 전 LLRF live mapping과 readiness transition을 확인하고, configuration snapshot을 저장한다. Logger는 native PV update behavior, acquisition interval, timestamp source, clock source, analysis time base, missing-sample rule 및 different-rate signal handling을 명시해야 한다.

사전에 정의되지 않은 interpolation은 사용하지 않는다. Analysis script 또는 notebook을 사용할 경우 file/version/hash 등 실제 관리 가능한 identifier를 기록한다.

표 8. 최종 validation 기록 신호

| **Group** | **Recorded signals** | **목적** |
|---|---|---|
| LLRF | DETA, TDOFF, GMES, RFON, GDR | Control input/readiness 및 DETA_CAL reconstruction |
| Reference | D_c/D_f, STEP_REF, STEP_ERR 또는 reconstructable input | Reference tracking 근거 |
| Position | RAW_POS_RBV, POS_RBV, POS_USER_RBV, independent sensor if used | Controller coordinate와 independent mechanical evidence 분리 |
| Command | STEP_SET, SPD_SET, ACC_SET, mode/state/dir | Controller action 추적 |
| Safety | MOTION_PERMIT, limits, STOP/ABORT, stopped state | Safety timing 및 command blocking 검증 |
| RF/environment | Forward/reflected power, cavity field, vacuum, temperature if available | Operating-condition 기록 |

## 5.3 Actuator / Position Characterization

MANUAL mode에서 safe travel 범위 내 상대 이동을 양방향 반복하여 commanded USER_STEP/HW_PULSE와 MCC-1 P20-derived RAW/POS readback의 sign, scaling 및 repeatability를 확인한다. 이 시험은 controller-coordinate consistency를 검증하는 것이며, independent sensor가 없다면 mechanical backlash 또는 lost step을 직접 측정하는 시험으로 해석하지 않는다.

STEP pulse에 접근할 수 있다면 oscilloscope 또는 logic analyzer를 이용하여 P04/P14/P15 설정에 따른 start frequency, plateau frequency, acceleration time t_ACC, deceleration time t_DEC 및 move duration을 계측한다.

기존 MD2S에서 측정된 t_ACC가 확보된다면 MCC-1 P15 후보값의 초기 산정 근거로 사용할 수 있다. 다만 최종 P15는 MCC-1 readback 및 STEP-pulse profile을 실측해 확정한다.

## 5.4 Cavity-Tuner Calibration

Actual cavity에 tuner system과 INTEC LLRF를 연결하고 small bounded tuner motion을 적용하여 IN/OUT direction과 최종 verified RF-side quantity의 sign을 측정한다. Plant characterization에서는 controller-position coordinate S를 independent variable로 두고 RF-side quantity D를 dependent variable로 취급하는 D=f(S) relation을 우선 기록한다.

Controller가 S_ref=g(D) 형태의 reference를 요구한다고 해서 D-versus-S least-squares fit을 단순 역변환하는 것이 항상 물리적으로 동등하다고 가정해서는 안 된다. Final controller output coordinate에 맞는 fitting direction과 measurement uncertainty를 명시해야 한다.

각 branch의 fitting method, weighting/uncertainty treatment, residual definition 및 model-acceptance criterion을 결과 확인 전에 고정한다. Single affine model은 calibration range 내 linearity, run-to-run repeatability, direction-dependent slope/intercept difference와 controller-coordinate residual이 요구 accuracy/deadband에 비해 충분히 작을 경우에만 채택한다.

IN-to-OUT/OUT-to-IN 차이는 measured bidirectional difference로 보고하며, independent mechanical evidence 없이 이를 backlash로 단정하지 않는다.

## 5.5 Closed-loop A/B Test

Baseline threshold mode와 reference-tracking mode는 동일 INTEC LLRF interface와 frozen hardware/controller configuration에서 controlled and comparable conditions로 비교한다.

가능하면 validation unit을 matched pair로 정의하여 A_i와 B_i가 동일한 primary initial-condition band에 포함되도록 한다. Pairing rule과 tolerance는 결과 확인 전에 고정한다. Primary matching variable은 final q_RF 또는 calibration으로 정당화된 RF-side initial condition을 우선 검토하고 controller-position은 secondary condition으로 기록한다.

Run-order bias를 줄이기 위해 paired alternating ABAB/BABA 또는 randomized paired order 중 실제 운전 조건에 적합한 sequence를 사전에 확정한다. Repetition count, minimum valid pairs, invalid-pair handling, D_c/D_f/reference generator, P14/P15/P45, scheduler, logger, q_RF tolerance/dwell 및 analysis windows를 dataset 취득 전에 freeze한다.

Poor performance 자체는 exclusion reason으로 사용하지 않는다. Parameter tuning dataset과 frozen-controller validation dataset은 파일/manifest 수준에서 분리한다.

## 5.6 STOP / AUTO_ABORT 검증

STOP/AUTO_ABORT response는 performance A/B metric과 분리된 system-level validation으로 관리한다.

STOP chain은 다음 event로 구분한다.

T0 = operator/IOC STOP or AUTO_ABORT request

T1 = MCC-1 STOP telegram transmission

T2 = MCC-1 ACK receipt

T3 = verified stop-confirmation event

T1/T2는 communication evidence이며 motion completion을 뜻하지 않는다. P20-derived RAW/POS stability를 T3로 사용할 경우 “controller-position stop confirmation”으로 기술하고, 독립 encoder/sensor 또는 independently verified STEP-pulse cessation을 사용할 때만 해당 provenance에 맞는 physical motion-stop confirmation으로 표현한다.

그림 5. STOP/AUTO_ABORT T0–T3 evidence chain

표 9. Safety-response timing

| **Event** | **정의** | **증거** |
|---|---|---|
| T0 | Operator/IOC STOP or AUTO_ABORT request | 공통 time base timestamp |
| T1 | MCC-1 STOP telegram transmission | wire/TCP capture |
| T2 | MCC-1 ACK receipt | wire/TCP capture |
| T3 | Verified stop confirmation | final provenance에 따라 controller-position stability / pulse cessation / encoder / independent sensor |

Final result에는 T1−T0, T2−T1, T3−T0, repetitions, timeout/invalid event 및 T3 provenance를 함께 기록한다.

# 6. 현재 개발 근거 및 검증 상태

V12 master draft는 claim과 required evidence를 분리하여 관리한다. 현재 상태를 내부 보고 관점에서 정리하면 다음과 같다.

표 10. Claim–Evidence 상태

| **Claim** | **필요 증거** | **현재 상태** |
|---|---|---|
| Baseline에 explicit position-reference objective가 없음 | CORR OFF source/state | DEVELOPMENT VERIFIED |
| Development controller가 detuning-derived STEP_REF 생성 | Source/docs + target/error logs | DEVELOPMENT VERIFIED |
| 현재 main STEP_ACT path provenance 식별 | P20/0XP20R → RAW/HOME/P45 + runtime test | DEVICE VERIFIED for current P20 path |
| Scheduler가 bounded command 생성 | STEP_REF/STEP_ERR scheduler source + command trace | DEVELOPMENT VERIFIED, final frozen law 미검증 |
| Busy/dispatch behavior deterministic | motion-active/completion + dispatch gate + timing | NOT VERIFIED |
| Safety/abort가 tracking보다 우선 | IOC gate/abort flow + blocked-command + STOP chain | Development verified, end-to-end T3 미검증 |
| Calibration이 reference model을 지지 | Actual-cavity bidirectional calibration | NOT VERIFIED |
| Reference tracking이 controller coordinate에서 수렴 | Repeated synchronized STEP_REF/ACT/ERR | NOT VERIFIED |
| q_RF를 통한 RF-side outcome 측정 | INTEC semantics + target/band + logger | NOT VERIFIED |
| Baseline/Reference RF outcome 비교 | Frozen paired A/B dataset | NOT VERIFIED |
| JLAB→INTEC source transition functional validation | INTEC unit/sign/readiness/live bridge | NOT VERIFIED |
| Stop response T3 검증 | T0–T3 synchronized provenance capture | NOT VERIFIED |

Actual cavity test 전에 해결해야 하는 P0 항목은 다음과 같다.

- Eq. (2) target semantics 및 STEP_REF source trace
- INTEC DETA/TDOFF physical semantics
- Final D_c
- Primary RF-side outcome q_RF
- Final STEP_ACT coordinate/provenance
- P45/G_D scaling
- Busy/completion/dispatch rule
- q_RF target/tolerance/dwell
- Logger/time alignment
- A/B pairing/order/repetitions/validity rules
- T3 provenance

Calibration 전에 P1으로 고정할 항목은 RF operating condition, S/D coordinates 및 unit, calibration range/points, branch order, settling window, repetitions, fit direction, uncertainty treatment, model/residual acceptance criterion 및 G_D unit이다.

Frozen A/B validation 전에 P2로 controller/scheduler, initial-condition matching, paired protocol, analysis windows, q_RF metric, minimum valid pairs 및 safety validation method를 freeze해야 한다.

# 7. 정량 평가 지표 및 데이터 유효성

Reference-tracking mode에서는 controller-coordinate tracking error e_s를 기반으로 다음 metric을 계산할 수 있다.

MAE_s = (1/N) Σ |e_s,i|

RMSE_s = √[(1/N) Σ e_s,i²]

e_s,max = max |e_s,i|

Controller-coordinate settling time은 STEP_REF가 존재하는 reference-tracking mode에 한해 정의한다. Final STEP_ACT가 P20/user coordinate라면 이를 controller-coordinate settling time으로 표현하고 independent mechanical-position settling time으로 부르지 않는다.

Baseline에는 internal STEP_REF가 없으므로 동일한 position-domain metric을 강제로 부여하지 않는다. Baseline/Reference 공통 성능평가는 final INTEC semantics와 target definition이 확정된 q_RF를 primary metric으로 사용한다.

표 11. Baseline vs Reference 비교 metric

| **Metric** | **Baseline** | **Reference Tracking** |
|---|---|---|
| Primary q_RF initial/final | 최종 시험 후 기록 | 최종 시험 후 기록 |
| RF-side settling/steady-state | 최종 protocol에 따라 계산 | 최종 protocol에 따라 계산 |
| Command count / direction reversal | 기록 가능 | 기록 가능 |
| Accumulated commanded movement Σ|ΔS_cmd,k| | 기록 가능 | 기록 가능 |
| Cumulative controller-position movement Σ|ΔS_act,i| | 기록 가능 | 기록 가능 |
| Controller-coordinate settling | N/A – no internal STEP_REF | 계산 |
| MAE_s / RMSE_s / max|e_s| | N/A | 계산 |
| STOP safety latency | 별도 safety table | 별도 safety table |

Accumulated commanded movement는 logged relative command의 절대합 Σ|ΔS_cmd,k|로 정의한다. Cumulative controller-position movement는 synchronized valid STEP_ACT sample에서 Σ|S_act,i−S_act,i−1|로 계산한다. 두 quantity는 실제 mechanical tuner travel과 동일하지 않으므로 그렇게 표기하지 않는다.

Run validity는 결과를 본 뒤 임의로 결정하지 않는다. Logging gap, missing timestamp, corruption, readiness loss, RF trip, operator intervention, initial-condition mismatch, saturation 등의 처리 rule을 validation 전에 명시한다.

Poor performance, command count 증가 또는 scheduler saturation 그 자체는 data exclusion 사유가 아니다. Data validity가 유지되는 한 negative/neutral result도 그대로 보고한다.

# 8. 결론 및 향후 수행 항목

본 보고서는 LLRF detuning-related information에서 controller-position reference STEP_REF를 생성하고 controller-position readback과의 STEP_ERR를 사용하여 bounded motion을 결정하는 KLS cavity tuner reference-tracking development architecture를 정리하였다.

현재 확보된 근거는 gain/offset 기반 reference-generator software form, controller-coordinate tracking structure, P20-derived position path, HOME/P45 normalization, MANUAL/AUTO command architecture, parameter validation policy 및 STOP communication chain을 지지한다.

반면 다음 항목은 현재 확보된 자료만으로 최종 사실로 확정할 수 없다.

- Eq. (2)가 desired RF operating state를 absolute target coordinate로 encode하는 physical semantics
- INTEC DETA/TDOFF 및 최종 D_c semantics
- q_RF의 physical meaning, unit 및 target/band
- Final STEP_ACT coordinate와 independent position sensor provenance
- Busy/completion 및 overlapping command 처리 rule
- Actual-cavity D=f(S) calibration 및 accepted model
- Repeated closed-loop controller-coordinate convergence result
- Frozen paired Baseline/Reference A/B RF performance result
- End-to-end T3 stop-confirmation result

따라서 다음 단계에서는 먼저 INTEC live signal semantics와 final position coordinate를 고정하고 actual-cavity bidirectional calibration을 수행한다. 이후 reference generator의 physical target/correction semantics를 검증하여 final control law를 확정한다.

그 다음 frozen controller와 paired A/B protocol을 적용하여 baseline/reference-tracking의 RF-side result를 비교한다. Controller-coordinate success와 cavity/RF-level success를 별도로 평가하여 한쪽의 결과를 다른 쪽의 증거로 확대 해석하지 않는다.

Safety validation은 performance 결과와 분리하고 T0–T3 provenance와 latency를 기록한다. 최종 보고서와 논문에는 positive result뿐 아니라 neutral 또는 negative result도 validity rule을 만족하는 경우 그대로 반영한다.

## 향후 수행 우선순위

1. INTEC DETA/TDOFF/GMES/RFON/GDR semantics 및 live transition 검증
2. Final D_c/D_f와 q_RF 정의 고정
3. STEP_ACT coordinate 및 P45/G_D scaling 고정
4. Busy/completion/dispatch source-level verification
5. Actual-cavity D=f(S) bidirectional calibration
6. Final STEP_REF target/correction law acceptance
7. Frozen closed-loop paired A/B 시험
8. T0–T3 STOP/AUTO_ABORT end-to-end validation
9. Raw data, configuration snapshot, analysis version 및 claim-evidence manifest 보존
10. Actual result에 기반한 최종 보고서/논문 개정

# 9. 참고 문헌

[1] M. Lee et al., “Preliminary design of control system for storage ring RF in Korea 4GSR,” Proc. IPAC'23, Venice, Italy, 2023, MOPA079, pp. 215–217, doi: 10.18429/JACoW-IPAC2023-MOPA079.

[2] B. H. Choi et al., “Design status of RF system for the Korea 4th generation storage ring,” Proc. IPAC'23, Venice, Italy, 2023, MOPA078, pp. 212–214, doi: 10.18429/JACoW-IPAC2023-MOPA078.

[3] Y.-S. Lee et al., “Preliminary design study of prototype LLRF system for Korean-4GSR,” Journal of the Korean Physical Society, vol. 83, pp. 640–646, 2023, doi: 10.1007/s40042-023-00849-z.

[4] T. E. Plawski et al., “CEBAF New Digital LLRF System Extended Functionality,” Proc. PAC'07, Albuquerque, NM, USA, 2007, WEPMS065, pp. 2490–2492.

[5] T. Kobayashi et al., “Progress in Development of New LLRF Control System for SuperKEKB,” Proc. IPAC'13, Shanghai, China, 2013, WEPME014, pp. 2953–2955.

[6] F. Qiu et al., “Progress in the Work on the Tuner Control System of the cERL at KEK,” Proc. IPAC'16, Busan, Korea, 2016, WEPOR033, pp. 2742–2745, doi: 10.18429/JACoW-IPAC2016-WEPOR033.

[7] Phytron GmbH, “Programmiermanual MINILOG für die Steuerungen MCC-1, MCC-2 und MCC-2 LIN,” Manual MA 1238-A008 DE, Version 8, Nov. 2018.

# 10. 부록

## 부록 A. Configuration Freeze Checklist

| **구분** | **기록 항목** | **최종 값/파일** |
|---|---|---|
| Hardware | Cavity/tuner/motor ID, drive train | 확인 필요 |
| Position | P20/P22/independent sensor, coordinate, HOME/OFFSET | 확인 필요 |
| MCC-1 | Model/firmware | 확인 필요 |
| EPICS | IOC build/version, DB/Protocol version | 확인 필요 |
| GUI | Phoebus release/display version | 확인 필요 |
| LLRF | INTEC source/version, DETA/TDOFF/readiness semantics | 확인 필요 |
| Parameter | P04/P14/P15/P40/P41/P45 | 확인 필요 |
| Reference | D_c/D_f, gain/offset, target semantics | 확인 필요 |
| Scheduler | deadband, STEP/SPD/ACC, busy/completion | 확인 필요 |
| Safety | Permit/limit/STOP/AUTO_ABORT/T3 source | 확인 필요 |
| Logger | Software/version, sample time, clock/timestamp | 확인 필요 |
| Analysis | Script/notebook version/hash, window rule | 확인 필요 |

## 부록 B. Experimental Run 기록지

| **항목** | **기록 내용** |
|---|---|
| Run ID / Date / Operator |  |
| Mode | Baseline / Reference Tracking |
| Pair ID / Run order |  |
| Cavity / Tuner / Motor |  |
| INTEC source / readiness |  |
| Initial q_RF / tolerance |  |
| Initial controller position |  |
| P04 / P14 / P15 / P40 / P41 / P45 |  |
| Reference model / scheduler version |  |
| Logger / sampling / timestamp |  |
| Abort / Limit / Interlock event |  |
| Run validity | Valid / Metric-specific invalid / Entire-run invalid |
| Invalid reason |  |
| Data path / file identifier |  |

## 부록 C. T0–T3 Safety Event 기록지

| **Event** | **Timestamp** | **Evidence / Source** | **비고** |
|---|---|---|---|
| T0 STOP/AUTO_ABORT request |  | Operator/IOC |  |
| T1 STOP telegram TX |  | TCP/Wire capture |  |
| T2 MCC-1 ACK |  | TCP/Wire capture |  |
| T3 stop confirmation |  | 최종 provenance |  |
| T1−T0 |  | 계산 |  |
| T2−T1 |  | 계산 |  |
| T3−T0 |  | 계산 |  |

## 부록 D. 문서 개정 시 반드시 확정할 항목

- Report Number / Reviewer / 최종 page count
- KLS와 초기 Korea-4GSR 명칭 관계의 기관 공식 표현
- Cavity/tuner/motor ID 및 실제 drawing reference
- INTEC DETA/TDOFF/readiness semantics와 units
- Final D_c / D_f / q_RF
- STEP_REF physical target semantics 및 final law
- STEP_ACT coordinate/provenance 및 independent sensor 여부
- P45/G_D scaling
- Busy/completion/dispatch semantics
- Actual-cavity calibration 결과와 model acceptance
- Frozen A/B run count, paired result 및 validity statistics
- T0–T3 stop response result
- Final figure/table numbering, acknowledgments 및 institutional review
