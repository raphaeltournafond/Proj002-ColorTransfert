from OPTransporter import OPTransporter

ot = OPTransporter("pexelB-0.png", "pexelA-0.png", OPTransporter.RGB, True)
ot.opt_transport_v2(0.01, 1000)
