def report(
    n,
    n_min_const,
    n_min,
    privacy_type,
    dc_link_fail_p,
    sm_link_fail_p,
    sm_full_fail_p,
    dc_link_fail_e,
    sm_link_fail_e,
    sm_full_fail_e,
    link_status,
    sm_status,
    dc_report,
    sm_reports,
):
    terminated = int(dc_report.terminated)
    success = int(dc_report.success)
    dc_time = dc_report.t_end - dc_report.t_start
    dc_time_p_1 = dc_report.t_phase_1 - dc_report.t_start

    all_sms = set([i for i in range(n)])

    phase_1_cnt = dc_report.phase_1_count
    phase_1_sms = dc_report.phase_1_sms
    phase_2_cnt = dc_report.phase_2_count
    phase_2_sms = dc_report.phase_2_sms

    broken_sms = set([i for i in range(n) if not sm_status[i]])
    unlink_sms = set(
        [i for i in range(n) if all([not link_status[(i, j)] for j in range(-1, n)])]
    )
    discon_sms = broken_sms.union(unlink_sms)

    dc_net_snd_succ_count = dc_report.net_snd_succ
    dc_net_snd_succ_size = dc_report.net_snd_succ_size
    dc_net_snd_fail_count = dc_report.net_snd_fail
    dc_net_snd_fail_size = dc_report.net_snd_fail_size
    dc_net_rcv_count = dc_report.net_rcv
    dc_net_rcv_size = dc_report.net_rcv_size

    max_consecutive_fails = 0
    if len(phase_1_sms) > 0:
        consecutive_fails = 0
        activated = phase_1_sms[0]
        for i in (*phase_1_sms[1:], -1):
            if link_status[(activated, i)]:
                activated = i
                if consecutive_fails > max_consecutive_fails:
                    max_consecutive_fails = consecutive_fails
                consecutive_fails = 0
            else:
                consecutive_fails += 1

    sm_with_max_snd_fails = max(
        [i for i in sm_reports if i], key=lambda i: i.net_snd_fail
    )
    sm_with_max_snd_fails_snd_succ = sm_with_max_snd_fails.net_snd_succ
    sm_with_max_snd_fails_snd_succ_size = sm_with_max_snd_fails.net_snd_succ_size
    sm_with_max_snd_fails_snd_fail = sm_with_max_snd_fails.net_snd_fail
    sm_with_max_snd_fails_snd_fail_size = sm_with_max_snd_fails.net_snd_fail_size
    sm_with_max_snd_fails_rcv = sm_with_max_snd_fails.net_rcv
    sm_with_max_snd_fails_rcv_size = sm_with_max_snd_fails.net_rcv_size

    working_reports = [i for i in sm_reports if i]
    phase_1_reports = [i for i in sm_reports if i and i.id in phase_1_sms]
    phase_2_reports = [i for i in sm_reports if i and i.id in phase_2_sms]
    sm_stats = stats(
        [working_reports, phase_1_reports, phase_2_reports],
        [
            lambda i: i.t_end - i.t_start,
            lambda i: i.net_snd_succ,
            lambda i: i.net_snd_succ_size,
            lambda i: i.net_snd_fail,
            lambda i: i.net_snd_fail_size,
            lambda i: i.net_rcv,
            lambda i: i.net_rcv_size,
        ],
    )

    # Check for issues

    # SMs that should not participate in phase 1, but participated
    should_not_phase_1 = discon_sms.union(
        set([i for i in range(n) if not link_status[(i, -1)]])
    )
    should_not_phase_1_part = sum([i in phase_1_sms for i in should_not_phase_1])
    issue_should_not_phase_1 = 1 if should_not_phase_1_part > 0 else 0

    # SMs that should participate in phase 1, but did not
    should_phase_1 = all_sms - should_not_phase_1
    should_phase_1_no_part = sum([i not in phase_1_sms for i in should_phase_1])
    issue_should_phase_1 = 2 if should_phase_1_no_part > 0 else 0

    # No SM should send more than two successful messages
    sm_sent_more_than_2_succ = sum([i.net_snd_succ > 2 for i in sm_reports if i])
    issue_sm_sent_more_than_2_succ = 4 if sm_sent_more_than_2_succ > 0 else 0

    # Combine detected issues into a bitfield
    issues = (
        issue_should_not_phase_1 | issue_should_phase_1 | issue_sm_sent_more_than_2_succ
    )

    print(
        n,
        n_min_const,
        n_min,
        privacy_type,
        dc_link_fail_p,
        sm_link_fail_p,
        sm_full_fail_p,
        int(dc_link_fail_e),
        int(sm_link_fail_e),
        int(sm_full_fail_e),
        terminated,
        success,
        dc_time,
        dc_time_p_1,
        phase_1_cnt,
        phase_2_cnt,
        len(broken_sms),
        len(unlink_sms),
        len(discon_sms),
        dc_net_snd_succ_count,
        dc_net_snd_succ_size,
        dc_net_snd_fail_count,
        dc_net_snd_fail_size,
        dc_net_rcv_count,
        dc_net_rcv_size,
        max_consecutive_fails,
        sm_with_max_snd_fails_snd_succ,
        sm_with_max_snd_fails_snd_succ_size,
        sm_with_max_snd_fails_snd_fail,
        sm_with_max_snd_fails_snd_fail_size,
        sm_with_max_snd_fails_rcv,
        sm_with_max_snd_fails_rcv_size,
        *sm_stats,
        issues,
        sep=","
    )


# Calculate the mean
def avg(lst):
    return sum(lst) / len(lst)


# Calculate sample standard deviation
def std(lst):
    n = len(lst)
    a = avg(lst)
    return (sum((x - a) ** 2 for x in lst) / n) ** 0.5


def stats(lists, funcs):
    res = []
    for lst in lists:
        for f in funcs:
            lst_f = [f(i) for i in lst]
            res.append(max(lst_f) if len(lst_f) > 0 else "N/A")
            res.append(min(lst_f) if len(lst_f) > 0 else "N/A")
            res.append(avg(lst_f) if len(lst_f) > 0 else "N/A")
            res.append(std(lst_f) if len(lst_f) > 0 else "N/A")

    return res
