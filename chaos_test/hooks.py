import pytest

from .parser import TomlChaosFile, YamlChaosFile

def pytest_collect_file(path, parent):
    if path.basename.startswith("chaos_"):
        if path.ext == ".toml":
            if hasattr(TomlChaosFile, "from_parent"):
                return TomlChaosFile.from_parent(parent, fspath=path)
            else:
                return TomlChaosFile(path, parent)
        elif path.ext in [".yaml", ".yml"]:
            if hasattr(TomlChaosFile, "from_parent"):
                return YamlChaosFile.from_parent(parent, fspath=path)
            else:
                return YamlChaosFile(path, parent)
    return None


def pytest_collection_modifyitems(session, config, items):
    pass

# def pytest_configure(config):
#     config.addinivalue_line("markers", "cool_marker: this one is for cool tests.")
#     config.addinivalue_line(
#         "markers", "mark_with(arg, arg2): this marker takes arguments."
#     )
