from pathlib import Path
from unittest import TestCase
import pytest

from ball_of_mud.generate_ball_of_mud import BallOfMud


class TestGenerateBallOfMud(TestCase):
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path) -> None:
        self.target_path = tmp_path

    def test_first_module_has_no_parent(self) -> None:
        mud = BallOfMud.generate(self.target_path, 2, build=False)

        assert mud.modules[0].parent is None
        assert mud.modules[0].name == "."

    def test_second_module_has_first_as_parent(self) -> None:
        mud = BallOfMud.generate(self.target_path, 2, build=False)

        assert mud.modules[1].parent is mud.modules[0]
        assert mud.modules[1].name != "."

    def test_generated_module_count_matches_target(self) -> None:
        num_to_generate = 3
        result = BallOfMud.generate(self.target_path, num_to_generate, build=False)

        assert len(result.modules) == num_to_generate

    def test_generated_file_structure(self) -> None:
        num_to_generate = 15
        mud = BallOfMud.generate(self.target_path, num_to_generate)

        for module in mud.modules:
            assert module.path.exists()
            if module.parent:
                assert module.parent.path.exists()

    def test_generated_init_files(self) -> None:
        mud = BallOfMud.generate(self.target_path, 1)
        module_file = mud.modules[0].init_file_path
        mud._add_import_to_file(module_file, "foo")
        mud._add_import_to_file(module_file, "bar")

        with open(module_file) as ifile:
            assert ifile.read() == "from . import foo\nfrom . import bar\n"
