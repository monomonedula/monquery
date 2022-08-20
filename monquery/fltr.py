import json
from abc import abstractmethod, ABC
from typing import List, Dict, Tuple, Optional, Any, Callable


Conv = Callable[[str], Tuple[Any, Optional[str]]]


class Param(ABC):
    """
    The general interface for filtering parameter definition
    """

    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        """
        :return: the param name
        """
        pass

    @abstractmethod
    def filter_from(
        self, values: List[str]
    ) -> Tuple[Dict[str, Any], Optional[str]]:  # pragma: no cover
        """
        :param values: the values of the parameter from a query string
        :return: MongoDB filter and error
        """
        pass


class ParamMultiValue(Param):
    __slots__ = (
        "_name",
        "_target_field",
        "_conv",
        "_operator",
    )

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

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name={self._name!r}, "
            f"target_field={self._target_field}, conv={self._conv}, operator={self._operator})"
        )


class ParamSingleValue(Param):
    __slots__ = (
        "_name",
        "_target_field",
        "_conv",
        "_operator",
    )

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

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name={self._name!r}, "
            f"target_field={self._target_field}, conv={self._conv}, operator={self._operator})"
        )


class ParamEq(Param):
    __slots__ = ("_origin",)

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

    def __repr__(self):
        return f"{self.__class__.__name__}({self._origin!r})"


class ParamNe(Param):
    __slots__ = ("_origin",)

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
                operator="$nin",
            )
            if multi
            else ParamSingleValue(
                name=name,
                target_field=target_field or name,
                conv=conv,
                operator="$ne",
            )
        )

    def name(self) -> str:
        return self._origin.name()

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        return self._origin.filter_from(values)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._origin!r})"


class ParamMax(Param):
    __slots__ = ("_origin",)

    def __init__(self, name: str, conv: Conv, target_field: str, lte: bool = False):
        self._origin: Param = ParamSingleValue(
            name=name,
            target_field=target_field or name,
            conv=conv,
            operator="$lte" if lte else "$lt",
        )

    def name(self) -> str:
        return self._origin.name()

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        return self._origin.filter_from(values)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._origin!r})"


class ParamMin(Param):
    __slots__ = ("_origin",)

    def __init__(self, name: str, conv: Conv, target_field: str, gte: bool = False):
        self._origin: Param = ParamSingleValue(
            name=name,
            target_field=target_field or name,
            conv=conv,
            operator="$gte" if gte else "$gt",
        )

    def name(self) -> str:
        return self._origin.name()

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        return self._origin.filter_from(values)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._origin!r})"


class ParamArray(Param):
    __slots__ = (
        "_name",
        "_target_field",
        "_conv",
        "_operator",
    )

    def __init__(self, name: str, target_field: str, conv: Conv, operator: str):
        self._name: str = name
        self._target_field: str = target_field
        self._conv: Conv = conv
        self._operator: str = operator

    def name(self) -> str:
        return self._name

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        converted = []
        try:
            values = json.loads(values[0])
        except json.decoder.JSONDecodeError:
            return {}, f"Error while parsing {self._name!r} param. (Array format error)"
        for value in values:
            c, err = self._conv(value)
            if err:
                return {}, f"Error while parsing {self._name!r} param. {err}"
            converted.append(c)
        return {self._target_field: {self._operator: converted}}, None


class Filter(ABC):
    """
    An interface for query string to MongoDB filter translation
    """

    @abstractmethod
    def from_query(
        self, q: Dict[str, List[str]]
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        :param q: a parsed query string
        :return: MongoDB filter and error
        """
        pass


class FilterSimple(Filter):
    __slots__ = ("_fltrs", "_repr")

    def __init__(self, params: List[Param]):
        self._fltrs: Dict[str, Param] = {param.name(): param for param in params}
        self._repr: str = f"{self.__class__.__name__}({sorted(self._fltrs.values(), key=lambda i: i.name())!r})"

    def from_query(
        self, q: Dict[str, List[str]]
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        combined_filter = []
        for name, values in q.items():
            proc = self._fltrs.get(name)
            if proc:
                fltr, err = proc.filter_from(values)
                if err:
                    return {}, err
                combined_filter.append(fltr)
        if combined_filter:
            return {"$and": combined_filter}, None
        return {}, None

    def __repr__(self):
        return self._repr


class Naming(ABC):
    """
    A naming convention to derive parameter names for different types of filters
    """

    @abstractmethod
    def name_for(self, base: str, typ: str) -> str:
        pass


class NamingBasic(Naming):
    def __init__(
        self,
        pref_postf: Dict[str, Tuple[str, str]],
    ):
        self._pref_postf: Dict[str, Tuple[str, str]] = pref_postf

    def name_for(self, base: str, typ: str) -> str:
        prefix, postfix = self._pref_postf[typ]
        return f"{prefix}{base}{postfix}"


dollar_naming = NamingBasic(
    {
        "max": ("$lte-", ""),
        "min": ("$gte-", ""),
        "max-strict": ("$lt-", ""),
        "min-strict": ("$gt-", ""),
        "ne": ("$ne-", ""),
    }
)


def params_basic(
    base_name: str,
    conv: Conv,
    field: Optional[str] = None,
    include_range_filters: bool = False,
    include_equality_filter: bool = True,
    naming: Naming = dollar_naming,
) -> List[Param]:
    field = field or base_name
    return [
        *(
            [
                ParamEq(base_name, conv, target_field=field),
                ParamNe(naming.name_for(base_name, "ne"), conv, target_field=field),
            ]
            if include_equality_filter
            else []
        ),
        *(
            [
                ParamMin(
                    naming.name_for(base_name, "min-strict"), conv, target_field=field
                ),
                ParamMax(
                    naming.name_for(base_name, "max-strict"), conv, target_field=field
                ),
                ParamMin(
                    naming.name_for(base_name, "min"),
                    conv,
                    target_field=field,
                    gte=True,
                ),
                ParamMax(
                    naming.name_for(base_name, "max"),
                    conv,
                    target_field=field,
                    lte=True,
                ),
            ]
            if include_range_filters
            else []
        ),
    ]


class ParamOf(Param):
    __slots__ = (
        "_name",
        "_conv",
        "_cases",
        "_default_case",
    )

    def __init__(
        self,
        name: str,
        conv: Conv,
        cases: Dict[Any, Dict[str, Any]],
        default_case: Optional[Dict[str, Any]] = None,
    ):
        self._name: str = name
        self._conv: Conv = conv
        self._cases: Dict[Any, Dict[str, Any]] = cases
        self._default_case: Optional[Dict[str, Any]] = default_case

    def name(self) -> str:
        return self._name

    def filter_from(self, values: List[str]) -> Tuple[Dict[str, Any], Optional[str]]:
        converted, err = self._conv(values[0])
        if err:
            return {}, err
        if converted in self._cases:
            return self._cases[converted], None
        if self._default_case is not None:
            return self._default_case, None
        return {}, f"Unexpected value: {values[0]!r} of param {self._name!r}"
