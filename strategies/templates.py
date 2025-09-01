from .legs import Leg

def long_call(delta=0.30, dte=(20,30)):
    return [Leg("call","long", {"type":"delta","value":delta}, list(dte), qty=1)]

def long_put(delta=0.30, dte=(20,30)):
    return [Leg("put","long", {"type":"delta","value":delta}, list(dte), qty=1)]

def vertical_credit_bull_put(short_delta=0.30, long_delta=0.15, dte=(20,30)):
    return [
        Leg("put","short", {"type":"delta","value":short_delta}, list(dte), qty=1),
        Leg("put","long",  {"type":"delta","value":long_delta},  list(dte), qty=1),
    ]

def straddle(atm_rule={"type":"delta","value":0.50}, dte=(20,30)):
    return [
        Leg("call","long", atm_rule, list(dte), qty=1),
        Leg("put","long",  atm_rule, list(dte), qty=1),
    ]

def iron_condor(call_short=0.30, call_long=0.15, put_short=0.30, put_long=0.15, dte=(20,30)):
    return [
        Leg("call","short", {"type":"delta","value":call_short}, list(dte), qty=1),
        Leg("call","long",  {"type":"delta","value":call_long},  list(dte), qty=1),
        Leg("put","short",  {"type":"delta","value":put_short},  list(dte), qty=1),
        Leg("put","long",   {"type":"delta","value":put_long},   list(dte), qty=1),
    ]
