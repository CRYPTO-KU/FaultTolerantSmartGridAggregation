def main():
    sm_stats_headers = stats_headers(
        ["WORKING_SM", "PHASE_1_SM", "PHASE_2_SM"],
        [
            "TOTAL_TIME",
            "NET_SND_SUCC_COUNT",
            "NET_SND_SUCC_SIZE",
            "NET_SND_FAIL_COUNT",
            "NET_SND_FAIL_SIZE",
            "NET_RCV_COUNT",
            "NET_RCV_SIZE",
        ],
    )

    # Print CSV Headers
    print(
        "N",
        "N_MIN_CONST",
        "N_MIN",
        "PRIVACY_TYPE",
        "DC_LINK_FAIL_P",
        "SM_LINK_FAIL_P",
        "SM_FULL_FAIL_P",
        "DC_LINK_FAIL_E",
        "SM_LINK_FAIL_E",
        "SM_FULL_FAIL_E",
        "TERMINATED",
        "SUCCESS",
        "DC_TIME",
        "DC_TIME_P_1",
        "PHASE_1_CNT",
        "PHASE_2_CNT",
        "BROKEN_SMS_COUNT",
        "UNLINK_SMS_COUNT",
        "DISCON_SMS_COUNT",
        "DC_NET_SND_SUCC_COUNT",
        "DC_NET_SND_SUCC_SIZE",
        "DC_NET_SND_FAIL_COUNT",
        "DC_NET_SND_FAIL_SIZE",
        "DC_NET_RCV_COUNT",
        "DC_NET_RCV_SIZE",
        "MAX_CONSECUTIVE_FAILS",
        "SM_WITH_MAX_SND_FAILS_SND_SUCC",
        "SM_WITH_MAX_SND_FAILS_SND_SUCC_SIZE",
        "SM_WITH_MAX_SND_FAILS_SND_FAIL",
        "SM_WITH_MAX_SND_FAILS_SND_FAIL_SIZE",
        "SM_WITH_MAX_SND_FAILS_RCV",
        "SM_WITH_MAX_SND_FAILS_RCV_SIZE",
        *sm_stats_headers,
        "ISSUES",
        sep=",",
    )


def stats_headers(lists, funcs):
    res = []
    for lst in lists:
        for f in funcs:
            res.append(f"MAX_{lst}_{f}")
            res.append(f"MIN_{lst}_{f}")
            res.append(f"AVG_{lst}_{f}")
            res.append(f"STD_{lst}_{f}")

    return res
