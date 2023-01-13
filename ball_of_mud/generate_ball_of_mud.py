from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import shutil
import textwrap


@dataclass
class Module:
    """
    A module to generate. Used for keeping track of the ball of mud
    """

    name: str
    path: Path
    parent: Module

    @property
    def init_file_path(self) -> Path:
        return self.path / "__init__.py"

    @property
    def python_path(self) -> str:
        return str(self.path).replace("/", ".")


class BallOfMud:
    """
    Used for generating and managing a ball of mud
    """

    root_dir: str
    modules: list[Module]

    def __init__(self, root_dir: str, modules: list[Module]) -> None:
        self.root_dir = root_dir
        self.modules = modules
        self._built: bool = False

    @staticmethod
    def _random_name() -> str:
        return "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(12))

    @staticmethod
    def generate(
        target_dir: str | Path = "./ball_of_mud_test_dir",
        num_modules: int = 1000,
        delete_existing: bool = False,
        build: bool = True,
    ) -> BallOfMud:
        """
        Generate a ball of mud in the target directory for testing mypy performance.

        :param target_dir: The target directory to generate the ball of mud in
        :param num_modules: The number of fake modules to create
        :param delete_existing: If an existing ball of mud exists in the target directory, delete it
        :param build: Create the ball of mud
        """
        target_path = Path(target_dir)
        if not target_path.exists():
            target_path.mkdir()
        if not len(list(target_path.iterdir())) == 0:
            if not delete_existing:
                raise Exception(f"Cannot create ball of mud at {target_dir} is not empty!")
            shutil.rmtree(target_dir)
        modules = [Module(".", Path(target_dir), None)]

        def choose_parent_module() -> Module:
            """
            Choose a parent module with a bias towards the root of the module tree
            """
            module = random.choice(modules)
            while module.parent is not None and random.random() < 0.4:
                module = module.parent
            return module

        while len(modules) < num_modules:
            parent_module = choose_parent_module()
            name = BallOfMud._random_name()
            modules.append(Module(name, parent_module.path / name, parent_module))

        mud = BallOfMud(root_dir=target_dir, modules=modules)

        if build:
            mud.build()

        return mud

    def build(self) -> None:
        """
        Build the ball of mud
        """
        if self._built:
            return
        self._built = True

        for module in self.modules:
            if not module.path.exists():
                module.path.mkdir()  # parents=True, exist_ok=True possibly needed
            if not module.init_file_path.exists():
                with module.init_file_path.open("w") as ofile:
                    ofile.write(
                        textwrap.dedent(
                            """
                        class A:
                            def val(self) -> int:
                                return 8

                        class B:
                            def val(self) -> str:
                                return "s"
                        """
                        )
                    )
            if module.parent is not None:
                self._add_import_to_file(module.parent.init_file_path, module.name)

        self._muddy_up()

    def _add_import_to_file(self, init_file: Path, name: str) -> None:
        with init_file.open("a") as ofile:
            varname = BallOfMud._random_name()
            ofile.write(f"from .{name} import A as {varname}\nfoo = {varname}().val()\n")

    def _muddy_up(self, iterations=100) -> None:
        for _ in range(iterations):
            module = random.choice(self.modules)
            target = random.choice(self.modules)
            if module != target:
                if not self._is_parent_of_module(module, target):
                    with module.init_file_path.open("a") as ofile:
                        ofile.write(
                            f"from {target.python_path} import B as C\nassert C().val() == 3\n"
                        )

    def _is_parent_of_module(self, module: Module, target: Module):
        while module.parent is not None:
            if module.parent == target:
                return True
            module = module.parent
        return False


if __name__ == "__main__":
    BallOfMud.generate(num_modules=1000, delete_existing=True)
