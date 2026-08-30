class InvocationClosed(RuntimeError):
    pass


class SingleUseInvocationLatch:
    """Cardinality guard only. It grants no invocation or admission authority."""

    UNCONSUMED = "UNCONSUMED"
    CONSUMED = "CONSUMED"

    def __init__(self):
        self._state = self.UNCONSUMED
        self._invocation_count = 0

    @property
    def state(self):
        return self._state

    @property
    def invocation_count(self):
        return self._invocation_count

    @property
    def permanently_closed(self):
        return self._state == self.CONSUMED

    def consume(self):
        if self._state != self.UNCONSUMED:
            raise InvocationClosed("SECOND_INVOCATION_REJECTED: single-use latch permanently closed")
        self._state = self.CONSUMED
        self._invocation_count = 1
        return self._state

    def reset(self):
        raise InvocationClosed("RESET_PROHIBITED: consumed invocation latch cannot re-open")
