from abc import abstractmethod, ABC
from typing import List, Dict, Tuple, Optional, Any, Callable


Conv = Callable[[str], Tuple[Any, Optional[str]]]


class Param(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        pass


class ParamMultiValue(Param):
    def __init__(self, name: str, target_field: str, conv: Conv, operator: str):
        self._name: str = name
        self._target_field: str = target_field
        self._conv: Conv = conv
        self._operator: str = operator

    def name(self) -> str:
        return self._name

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        converted = []
        for value in values:
            c, err = self._conv(value)
            if err:
                return {}, f"Error while parsing {self._name!r} param. {err}"
            converted.append(c)
        return {self._target_field: {self._operator: converted}}, None


class ParamSingleValue(Param):
    def __init__(self, name: str, target_field: str, conv: Conv, operator: str):
        self._name: str = name
        self._target_field: str = target_field
        self._conv: Conv = conv
        self._operator: str = operator

    def name(self) -> str:
        return self._name

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        converted, err = self._conv(values[0])
        if err:
            return {}, f"Error while parsing {self._name!r} param. {err}"
        return {self._target_field: {self._operator: converted}}, None


class ParamSimple(Param):
    def __init__(
        self,
        name: str,
        conv: Conv,
        multi: bool = True,
        target_field: Optional[str] = None,
    ):
        self._origin = (
            ParamMultiValue(
                name=name,
                target_field=target_field or name,
                conv=conv,
                operator="$in",
            )
            if multi
            else ParamSingleValue(
                name=name,
                target_field=target_field or name,
                conv=conv,
                operator="$eq",
            )
        )

    def name(self) -> str:
        return self._origin.name()

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        return self._origin.filter_from(values)


class ParamMax(Param):
    def __init__(self, name: str, conv: Conv, target_field: str, lte: bool = False):
        self._origin: Param = ParamSingleValue(
            name=name,
            target_field=target_field,
            conv=conv,
            operator="$lte" if lte else "$lt",
        )

    def name(self) -> str:
        return self._origin.name()

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        return self._origin.filter_from(values)


class ParamMin(Param):
    def __init__(self, name: str, conv: Conv, target_field: str, gte: bool = False):
        self._origin: Param = ParamSingleValue(
            name=name,
            target_field=target_field,
            conv=conv,
            operator="$gte" if gte else "$gt",
        )

    def name(self) -> str:
        return self._origin.name()

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        return self._origin.filter_from(values)


class Filter:
    def __init__(self, params: List[Param]):
        self._fltrs: Dict[str, Param] = {}
        for param in params:
            self._fltrs[param.name()] = param

    def from_query(
        self, q: Dict[str, List[str]]
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        combined_filter = {}
        for name, values in q.items():
            proc = self._fltrs.get(name)
            if proc:
                fltr, err = proc.filter_from(values)
                if err:
                    return {}, err
                combined_filter.update(fltr)
        return combined_filter, None
