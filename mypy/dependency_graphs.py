import collections
from typing import Any, Iterable


class DependencyGraph:
    def __init__(
        self,
        dependency_map: dict[str, set[str]] | None = None,
        module_files: set[str] | None = None,
    ) -> None:
        self._deps: dict[str, set[str]] = collections.defaultdict(set)
        self._parent_modules: dict[str, set[str]] = collections.defaultdict(set)
        self._reverse_deps: dict[str, set[str]] = collections.defaultdict(set)
        self._module_files = module_files or set()
        if dependency_map:
            for k, v in dependency_map.items():
                self.update(k, v)

    @property
    def module_files(self) -> set[str]:
        return self._module_files

    def __get__(self, key: str) -> set[str]:
        return self._deps[key]

    def __contains__(self, key: str) -> bool:
        return key in self._deps

    def get(self, key: str, default: Any = None) -> set[str]:
        return self._deps.get(key, default)

    def get_reverse(self, key: str, default: Any = None) -> set[str]:
        return self._reverse_deps.get(key, default)

    def add_module_file(self, module: str) -> None:
        self._module_files.add(module)

    def update(self, key: str, values: set[str]) -> None:
        # previous_deps = copy.copy(self._deps[key])
        self._deps[key].update(values)
        for value in values:
            if self._module_files and not value.startswith("<"):
                cur = value
                while "." in cur:
                    parent, _ = cur.rsplit(".", 1)
                    if parent in self._module_files:
                        self._parent_modules[parent].add(value)
                        break
                    cur = parent
            self._reverse_deps[value].add(key.replace("[wildcard]", ""))

    def items(self) -> Iterable[tuple[str, set[str]]]:
        return self._deps.items()

    def get_others_in_module(self, module: str) -> set[str]:
        return self._parent_modules[module]

    def get_dependencies(self, targets: Iterable[str]) -> set[str]:
        result = set()
        for target in targets:
            result |= self._deps[target]
        return result

    def get_reverse_dependencies(self, targets: Iterable[str]) -> set[str]:
        result = set()
        for target in targets:
            result |= self._reverse_deps[target]
        return result

    # def __set__(self, key: str, value: set[str]) -> None:
    #     previous_value = self._deps[key]
    #     self._deps[key] = value
    #     self._update_reverse_deps(key, value, previous_value)

    # def _update_reverse_deps(self, key: str, value: str) -> None:
    #     for dep in value:
    #         self._reverse_deps
