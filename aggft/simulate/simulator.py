import threading

from time     import time as now

from simulate import factories

################################################################################
# Simulation Logic
################################################################################

def simulate(
    sm_count,
    startup_wait,
    configurations,
    make_net_mngr,
    base_dc_meta,
    base_sm_meta,
):
    for c in configurations:
        net_mngr = make_net_mngr()

        test_start = now()

        threads = ()

        dc = factories.dc_factory(
            sm_count,
            test_start,
            startup_wait,
            base_dc_meta(),
            net_mngr,
            c
        )
        dc_thread = threading.Thread(target = dc.run_once)
        threads = (*threads, dc_thread)

        sms = ()
        for id in range(sm_count):
            sm = factories.sm_factory(
                id,
                sm_count,
                test_start,
                startup_wait,
                base_sm_meta(id),
                net_mngr,
                c
            )
            sm_thread = threading.Thread(target = sm.run_once)
            threads = (*threads, sm_thread)
            sms = (*sms, sm)

        # Start all threads
        for thread in threads: thread.start()

        # Wait for all threads
        for thread in threads: thread.join()

        dc_report  = dc.reports[0]
        sm_reports = tuple([sm.reports[0] for sm in sms])

        yield dc_report, sm_reports
