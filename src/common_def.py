def _assert(pred, hint):
    if not pred:
        raise AssertionError(hint)