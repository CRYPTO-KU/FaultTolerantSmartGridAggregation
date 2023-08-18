# `aggft-sim` and `aggft-sim-fig` Ouput Format

- `N`: Number of smart meters.
- `N_MIN_CONST`: `N_MIN` Constant.
- `N_MIN`: Minimum number of participating smart meters in a round.
- `PRIVACY_TYPE`: `mask` or `encr`.
- `DC_LINK_FAIL_P`: Probability of DC link failure (see spec documentation).
- `SM_LINK_FAIL_P`: Probability of DC link failure (see spec documentation).
- `SM_FULL_FAIL_P`: Probability of DC link failure (see spec documentation).
- `DC_LINK_FAIL_E`: Whether the failure probability is exact or not (see spec
  documentation).
- `SM_LINK_FAIL_E`: Whether the failure probability is exact or not (see spec
  documentation).
- `SM_FULL_FAIL_E`: Whether the failure probability is exact or not (see spec
  documentation).
- `TERMINATED`: Whether the round terminated (aggregate not necessarily
  obtained) or not.
- `SUCCESS`: Whether the round was successful (aggregate calculated) or not.
- `DC_TIME`: Total time from round start till round end on the DC.
- `DC_TIME_P_1`: Total time from round start till `phase-1` end on the DC. We
  can get the time of `phase-2` by `DC_TIME - DC_TIME_P_1`.
- `PHASE_1_CNT`: Number of smart meters who sent data to DC in `phase-1`.
- `PHASE_2_CNT`: Number of smart meters who were in `L_ACT` at the end of the
  round.
- `BROKEN_SMS_COUNT`: Number of broken SMs.
- `UNLINK_SMS_COUNT`: Number of SMs with all links failed.
- `DISCON_SMS_COUNT`: Number of SMs that are either broken or have all their
  links failed. In other words, the size of the union of broken and unlink SMs.
- `DC_NET_SND_SUCC_COUNT`: Number of successful messages sent by DC.
- `DC_NET_SND_SUCC_SIZE`: Size (in bytes) of successful messages sent by DC.
- `DC_NET_SND_FAIL_COUNT`: Number of failed messages sent by DC.
- `DC_NET_SND_FAIL_SIZE`: Size (in bytes) of failed messages sent by DC.
- `DC_NET_RCV_COUNT`: Number of messages received by DC.
- `DC_NET_RCV_SIZE`: Size (in bytes) of messages received by DC.
- `MAX_CONSECUTIVE_FAILS`: Max consecutive link failures in `phase-2`.
- `SM_WITH_MAX_SND_FAILS_SND_SUCC`, `SM_WITH_MAX_SND_FAILS_SND_SUCC_SIZE`,
  `SM_WITH_MAX_SND_FAILS_SND_FAIL`, `SM_WITH_MAX_SND_FAILS_SND_FAIL_SIZE`,
  `SM_WITH_MAX_SND_FAILS_RCV`, `SM_WITH_MAX_SND_FAILS_RCV_SIZE`: Similar to the
  DC stats explained above, but for the SM with max send fails.
- `ISSUES`: Bitfield describing issues that happened in a simulation. If `0`,
  then no issues were detected. `1` means that some SMs that should not
  participate in `phase-1` participated in it. `2` means that SMs that should
  participate in `phase-1`, did not. `4` means that some SMs sent more than two
  successful messages. A combination of these issues can happen. For example:
  `5` means that `1` and `4` both happened.
- The following stats are similar to the DC stats explained above. But considers
  four (possibly overlapping) groups of SMs: Working SMs, Phase-1 SMs, and
  Phase-2 SMs. Working SMs are all non-broken SMs. Phase-1 SMs are SMs
  that participated in `phase-1`. Phase-2 SMs are SMs that participated in
  `phase-2`.
  + `MAX_WORKING_SM_TOTAL_TIME`
  + `MIN_WORKING_SM_TOTAL_TIME`
  + `AVG_WORKING_SM_TOTAL_TIME`
  + `STD_WORKING_SM_TOTAL_TIME`
  + `MAX_WORKING_SM_NET_SND_SUCC_COUNT`
  + `MIN_WORKING_SM_NET_SND_SUCC_COUNT`
  + `AVG_WORKING_SM_NET_SND_SUCC_COUNT`
  + `STD_WORKING_SM_NET_SND_SUCC_COUNT`
  + `MAX_WORKING_SM_NET_SND_SUCC_SIZE`
  + `MIN_WORKING_SM_NET_SND_SUCC_SIZE`
  + `AVG_WORKING_SM_NET_SND_SUCC_SIZE`
  + `STD_WORKING_SM_NET_SND_SUCC_SIZE`
  + `MAX_WORKING_SM_NET_SND_FAIL_COUNT`
  + `MIN_WORKING_SM_NET_SND_FAIL_COUNT`
  + `AVG_WORKING_SM_NET_SND_FAIL_COUNT`
  + `STD_WORKING_SM_NET_SND_FAIL_COUNT`
  + `MAX_WORKING_SM_NET_SND_FAIL_SIZE`
  + `MIN_WORKING_SM_NET_SND_FAIL_SIZE`
  + `AVG_WORKING_SM_NET_SND_FAIL_SIZE`
  + `STD_WORKING_SM_NET_SND_FAIL_SIZE`
  + `MAX_WORKING_SM_NET_RCV_COUNT`
  + `MIN_WORKING_SM_NET_RCV_COUNT`
  + `AVG_WORKING_SM_NET_RCV_COUNT`
  + `STD_WORKING_SM_NET_RCV_COUNT`
  + `MAX_WORKING_SM_NET_RCV_SIZE`
  + `MIN_WORKING_SM_NET_RCV_SIZE`
  + `AVG_WORKING_SM_NET_RCV_SIZE`
  + `STD_WORKING_SM_NET_RCV_SIZE`
  + `MAX_PHASE_1_SM_TOTAL_TIME`
  + `MIN_PHASE_1_SM_TOTAL_TIME`
  + `AVG_PHASE_1_SM_TOTAL_TIME`
  + `STD_PHASE_1_SM_TOTAL_TIME`
  + `MAX_PHASE_1_SM_NET_SND_SUCC_COUNT`
  + `MIN_PHASE_1_SM_NET_SND_SUCC_COUNT`
  + `AVG_PHASE_1_SM_NET_SND_SUCC_COUNT`
  + `STD_PHASE_1_SM_NET_SND_SUCC_COUNT`
  + `MAX_PHASE_1_SM_NET_SND_SUCC_SIZE`
  + `MIN_PHASE_1_SM_NET_SND_SUCC_SIZE`
  + `AVG_PHASE_1_SM_NET_SND_SUCC_SIZE`
  + `STD_PHASE_1_SM_NET_SND_SUCC_SIZE`
  + `MAX_PHASE_1_SM_NET_SND_FAIL_COUNT`
  + `MIN_PHASE_1_SM_NET_SND_FAIL_COUNT`
  + `AVG_PHASE_1_SM_NET_SND_FAIL_COUNT`
  + `STD_PHASE_1_SM_NET_SND_FAIL_COUNT`
  + `MAX_PHASE_1_SM_NET_SND_FAIL_SIZE`
  + `MIN_PHASE_1_SM_NET_SND_FAIL_SIZE`
  + `AVG_PHASE_1_SM_NET_SND_FAIL_SIZE`
  + `STD_PHASE_1_SM_NET_SND_FAIL_SIZE`
  + `MAX_PHASE_1_SM_NET_RCV_COUNT`
  + `MIN_PHASE_1_SM_NET_RCV_COUNT`
  + `AVG_PHASE_1_SM_NET_RCV_COUNT`
  + `STD_PHASE_1_SM_NET_RCV_COUNT`
  + `MAX_PHASE_1_SM_NET_RCV_SIZE`
  + `MIN_PHASE_1_SM_NET_RCV_SIZE`
  + `AVG_PHASE_1_SM_NET_RCV_SIZE`
  + `STD_PHASE_1_SM_NET_RCV_SIZE`
  + `MAX_PHASE_2_SM_TOTAL_TIME`
  + `MIN_PHASE_2_SM_TOTAL_TIME`
  + `AVG_PHASE_2_SM_TOTAL_TIME`
  + `STD_PHASE_2_SM_TOTAL_TIME`
  + `MAX_PHASE_2_SM_NET_SND_SUCC_COUNT`
  + `MIN_PHASE_2_SM_NET_SND_SUCC_COUNT`
  + `AVG_PHASE_2_SM_NET_SND_SUCC_COUNT`
  + `STD_PHASE_2_SM_NET_SND_SUCC_COUNT`
  + `MAX_PHASE_2_SM_NET_SND_SUCC_SIZE`
  + `MIN_PHASE_2_SM_NET_SND_SUCC_SIZE`
  + `AVG_PHASE_2_SM_NET_SND_SUCC_SIZE`
  + `STD_PHASE_2_SM_NET_SND_SUCC_SIZE`
  + `MAX_PHASE_2_SM_NET_SND_FAIL_COUNT`
  + `MIN_PHASE_2_SM_NET_SND_FAIL_COUNT`
  + `AVG_PHASE_2_SM_NET_SND_FAIL_COUNT`
  + `STD_PHASE_2_SM_NET_SND_FAIL_COUNT`
  + `MAX_PHASE_2_SM_NET_SND_FAIL_SIZE`
  + `MIN_PHASE_2_SM_NET_SND_FAIL_SIZE`
  + `AVG_PHASE_2_SM_NET_SND_FAIL_SIZE`
  + `STD_PHASE_2_SM_NET_SND_FAIL_SIZE`
  + `MAX_PHASE_2_SM_NET_RCV_COUNT`
  + `MIN_PHASE_2_SM_NET_RCV_COUNT`
  + `AVG_PHASE_2_SM_NET_RCV_COUNT`
  + `STD_PHASE_2_SM_NET_RCV_COUNT`
  + `MAX_PHASE_2_SM_NET_RCV_SIZE`
  + `MIN_PHASE_2_SM_NET_RCV_SIZE`
  + `AVG_PHASE_2_SM_NET_RCV_SIZE`
  + `STD_PHASE_2_SM_NET_RCV_SIZE`
