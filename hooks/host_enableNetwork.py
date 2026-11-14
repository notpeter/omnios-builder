# A braich snapshot has no network configured for the CI slirp network.
if is_braich():
    string("ipadm create-if vioif0; ipadm create-addr -T dhcp vioif0/v4")
    enter()
    time.sleep(20)
