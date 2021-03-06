import re


def eq(a, b, attrs):
    """Compare two objects on named attributes"""
    for attr in re.split(r"\s*,\s*", attrs):
        left, right = (getattr(obj, attr) for obj in (a, b))
        if left != right:
            # print(f"eq False on attr '{attr}': {left!r} != {right!r}")
            return False
    return True


def _match(obj, what):
    """
    Test (bool) whether an object matches on a subset of its attributes.
    Any attribute value itself having a "match" method is tested with that
    method. This enables matching down a data structure hierarchy.
    All other attribute values are tested with equality.
    """
    return all(
        getattr(obj, attr).match(**value)
        if getattr(obj, attr) is not None
           and hasattr(getattr(obj, attr), "match")
        else getattr(obj, attr) == value
        for attr, value in what.items()
    )


def strict_join(seq, sep=" "):
    """Join a sequence of objects "strictly", which means ignoring None
    values."""
    return sep.join(s for s in seq if s is not None)


class CellMethods(list):
    def __str__(self):
        return " ".join(str(x) for x in self)

    def match(self,  *args):
        return all(cm.match(arg) for cm, arg in zip(self, args))


class CellMethod:
    def __init__(
        self, name, method, where=None, over=None, within=None, extra_info=None
    ):
        if (where is not None or over is not None) and within is not None:
            raise ValueError(
                "'where' and/or 'over' are mutually exclusive with 'within'"
            )
        self.name = name
        self.method = method
        self.where = where
        self.over = over
        self.within = within
        self.extra_info = extra_info

    def match(self,  **kwargs):
        return _match(self, kwargs)

    def __eq__(*args):
        return eq(*args, "name, method, where, over, within, extra_info")

    def __str__(self):
        return strict_join(
            (
                f"{self.name}: {self.method}",
                self.where and f"where {self.where}",
                self.over and f"over {self.over}",
                self.within and f"within {self.within}",
                self.extra_info and f"{self.extra_info}",
            )
        )


class ExtraInfo:
    def __init__(self, standardized, non_standardized):
        self.standardized = standardized
        self.non_standardized = non_standardized

    def match(self,  **kwargs):
        return _match(self, kwargs)

    def __eq__(*args):
        return eq(*args, "standardized, non_standardized")

    def __str__(self):
        if self.standardized is None and self.non_standardized is None:
            # This actually should never occur
            return ""
        return (
            f"("
            f"{self.standardized or ''}"
            f"{' comment: ' if self.standardized and self.non_standardized else ''}"
            f"{self.non_standardized or ''}"
            f")"
        )


class StandardizedExtraInfo:
    pass


class SxiInterval(StandardizedExtraInfo):
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def match(self,  **kwargs):
        return _match(self, kwargs)

    def __eq__(*args):
        return eq(*args, "value, unit")

    def __str__(self):
        return f"interval: {self.value} {self.unit}"


class Method:
    def __init__(self, name, params):
        self.name = name
        self.params = params or tuple()

    def signature(self):
        return self.name, len(self.params)

    def match(self,  **kwargs):
        return _match(self, kwargs)

    def __eq__(*args):
        return eq(*args, "name, params")

    def __str__(self):
        params = (
            f"[{','.join(str(p) for p in self.params)}]"
            if len(self.params) > 0
            else ""
        )
        return f"{self.name}{params}"
