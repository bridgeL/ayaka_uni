"""本模块包含了 nonebot2 的一些工具函数，现在拿来给ayaka用了"""

import json
import asyncio
import inspect
import dataclasses
from functools import wraps, partial
from contextlib import asynccontextmanager
from typing_extensions import ParamSpec, get_args, get_origin
from typing import (
    Any,
    Type,
    Tuple,
    Union,
    TypeVar,
    Callable,
    Optional,
    Coroutine,
    AsyncGenerator,
    ContextManager,
)

from pydantic.typing import is_union, is_none_type

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def generic_check_issubclass(
    cls: Any, class_or_tuple: Union[Type[Any], Tuple[Type[Any], ...]]
) -> bool:
    """检查 cls 是否是 class_or_tuple 中的一个类型子类。

    特别的，如果 cls 是 `typing.Union` 或 `types.UnionType` 类型，
    则会检查其中的类型是否是 class_or_tuple 中的一个类型子类。（None 会被忽略）
    """
    try:
        return issubclass(cls, class_or_tuple)
    except TypeError:
        origin = get_origin(cls)
        if is_union(origin):
            for type_ in get_args(cls):
                if not is_none_type(type_) and not generic_check_issubclass(
                    type_, class_or_tuple
                ):
                    return False
            return True
        elif origin:
            return issubclass(origin, class_or_tuple)
        return False


def is_coroutine_callable(call: Callable[..., Any]) -> bool:
    """检查 call 是否是一个 callable 协程函数"""
    if inspect.isroutine(call):
        return inspect.iscoroutinefunction(call)
    if inspect.isclass(call):
        return False
    func_ = getattr(call, "__call__", None)
    return inspect.iscoroutinefunction(func_)


def is_gen_callable(call: Callable[..., Any]) -> bool:
    """检查 call 是否是一个生成器函数"""
    if inspect.isgeneratorfunction(call):
        return True
    func_ = getattr(call, "__call__", None)
    return inspect.isgeneratorfunction(func_)


def is_async_gen_callable(call: Callable[..., Any]) -> bool:
    """检查 call 是否是一个异步生成器函数"""
    if inspect.isasyncgenfunction(call):
        return True
    func_ = getattr(call, "__call__", None)
    return inspect.isasyncgenfunction(func_)


def run_sync(call: Callable[P, R]) -> Callable[P, Coroutine[None, None, R]]:
    """一个用于包装 sync function 为 async function 的装饰器

    参数:
        call: 被装饰的同步函数
    """

    @wraps(call)
    async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        loop = asyncio.get_running_loop()
        pfunc = partial(call, *args, **kwargs)
        result = await loop.run_in_executor(None, pfunc)
        return result

    return _wrapper


@asynccontextmanager
async def run_sync_ctx_manager(
    cm: ContextManager[T],
) -> AsyncGenerator[T, None]:
    """一个用于包装 sync context manager 为 async context manager 的执行函数"""
    try:
        yield await run_sync(cm.__enter__)()
    except Exception as e:
        ok = await run_sync(cm.__exit__)(type(e), e, None)
        if not ok:
            raise e
    else:
        await run_sync(cm.__exit__)(None, None, None)


def get_name(obj: Any) -> str:
    """获取对象的名称"""
    if inspect.isfunction(obj) or inspect.isclass(obj):
        return obj.__name__
    return obj.__class__.__name__


class DataclassEncoder(json.JSONEncoder):
    """在JSON序列化 `Message` (List[Dataclass]) 时使用的 `JSONEncoder`"""

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


import sys
import asyncio
from typing import Any, Dict, Tuple, Optional


def escape(s: str, *, escape_comma: bool = True) -> str:
    """
    :说明:

      对字符串进行 CQ 码转义。

    :参数:

      * ``s: str``: 需要转义的字符串
      * ``escape_comma: bool``: 是否转义逗号（``,``）。
    """
    s = s.replace("&", "&amp;").replace("[", "&#91;").replace("]", "&#93;")
    if escape_comma:
        s = s.replace(",", "&#44;")
    return s


def unescape(s: str) -> str:
    """
    :说明:

      对字符串进行 CQ 码去转义。

    :参数:

      * ``s: str``: 需要转义的字符串
    """
    return (
        s.replace("&#44;", ",")
        .replace("&#91;", "[")
        .replace("&#93;", "]")
        .replace("&amp;", "&")
    )


def _b2s(b: Optional[bool]) -> Optional[str]:
    """转换布尔值为字符串。"""
    return b if b is None else str(b).lower()


def _handle_api_result(result: Optional[Dict[str, Any]]) -> Any:
    """
    :说明:

      处理 API 请求返回值。

    :参数:

      * ``result: Optional[Dict[str, Any]]``: API 返回数据

    :返回:

        - ``Any``: API 调用返回数据

    :异常:

        - ``ActionFailed``: API 调用失败
    """
    if isinstance(result, dict):
        if result.get("status") == "failed":
            raise
        return result.get("data")


class ResultStore:
    _seq = 1
    _futures: Dict[Tuple[str, int], asyncio.Future] = {}

    @classmethod
    def get_seq(cls) -> int:
        s = cls._seq
        cls._seq = (cls._seq + 1) % sys.maxsize
        return s

    @classmethod
    def add_result(cls, self_id: str, result: Dict[str, Any]):
        if isinstance(result.get("echo"), dict) and isinstance(
            result["echo"].get("seq"), int
        ):
            future = cls._futures.get((self_id, result["echo"]["seq"]))
            if future:
                future.set_result(result)

    @classmethod
    async def fetch(
        cls, self_id: str, seq: int, timeout: Optional[float]
    ) -> Dict[str, Any]:
        future = asyncio.get_event_loop().create_future()
        cls._futures[(self_id, seq)] = future
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            raise
        finally:
            del cls._futures[(self_id, seq)]
