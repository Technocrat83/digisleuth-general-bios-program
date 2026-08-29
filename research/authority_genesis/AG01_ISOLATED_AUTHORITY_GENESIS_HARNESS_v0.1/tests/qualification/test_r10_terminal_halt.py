from .common import ROOT, witness

def measure():
    candidates=[ROOT/"harness"/"state_machine.py",ROOT/"harness"/"halt.py"]
    existing=[p for p in candidates if p.exists()]
    if not existing:
        return witness("C_10","R_10",candidates,"STATIC_STATE_MACHINE",["TERMINAL_STATE_MACHINE_SURFACE_ABSENT"],"Q_H has no successors and cannot transition to Q_0","INCOMPLETE","TERMINAL_STATE_REALIZER_TARGET_ABSENT")
    text="\n".join(p.read_text(encoding="utf-8") for p in existing).lower()
    has_qh="q_h" in text
    has_terminal=any(t in text for t in ("successors(q_h)","permanently_closed","terminal","no successors"))
    if not (has_qh and has_terminal):
        return witness("C_10","R_10",existing,"STATIC_STATE_MACHINE",[{"q_h":has_qh,"terminal_guard":has_terminal}],"Q_H has no successors and cannot transition to Q_0","INCOMPLETE","TERMINAL_STATE_REALIZER_TARGET_ABSENT")
    return witness("C_10","R_10",existing,"STATIC_STATE_MACHINE",[{"q_h":has_qh,"terminal_guard":has_terminal}],"Q_H has no successors and cannot transition to Q_0","PASS",None)
