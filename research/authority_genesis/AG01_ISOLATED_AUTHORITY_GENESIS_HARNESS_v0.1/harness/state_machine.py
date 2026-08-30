Q_0 = "Q_0"
Q_I = "Q_I"
Q_G = "Q_G"
Q_M = "Q_M"
Q_E = "Q_E"
Q_S = "Q_S"
Q_H = "Q_H"

_TRANSITIONS = {
    Q_0: (Q_I,),
    Q_I: (Q_G, Q_H),
    Q_G: (Q_M, Q_H),
    Q_M: (Q_E, Q_H),
    Q_E: (Q_S, Q_H),
    Q_S: (Q_H,),
    Q_H: (),
}


def successors(state):
    return _TRANSITIONS[state]


def transition(state, target):
    if state == Q_H:
        raise RuntimeError("TERMINAL_HALT_IRREVERSIBLE: Q_H has no successors")
    if target not in successors(state):
        raise RuntimeError(f"ILLEGAL_TRANSITION: {state} -> {target}")
    return target


def reset_same_run(state):
    if state == Q_H:
        raise RuntimeError("RESET_PROHIBITED: Q_H cannot re-enter Q_0 under the same run identity")
    raise RuntimeError("RESET_NOT_AUTHORIZED_BY_STATE_MACHINE")
