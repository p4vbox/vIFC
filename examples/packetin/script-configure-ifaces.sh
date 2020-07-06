rmmod nfp
modprobe nfp nfp_pf_netdev=1
ifconfig enp1s0np0 10.0.0.1 up
ifconfig enp1s0np1 10.1.0.1 up
