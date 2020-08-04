from chaos_test import TomlChaosFile
import tempfile
import pytest
import toml
from werkzeug.utils import ImportStringError

def get_temp_file(content):
    f = tempfile.NamedTemporaryFile()
    f.write(content)
    f.seek(0)
    return f

def test_no_entry_point(_pytest):
    f = get_temp_file("""
    entry-point1="factory"
    """)    
    plugin = TomlChaosFile(f.name, _pytest.request.node)

    with pytest.raises(AssertionError, message="Define entry point to run chaos testing."):
        plugin.collect()
    f.close()

def test_entry_point_detected(_pytest):
    f = get_temp_file("""
    entry-point="factory"
    """)
    plugin = TomlChaosFile(f.name, _pytest.request.node)

    with pytest.raises(ImportStringError):
        plugin.collect()
    f.close()

def test_scenario_collection(_pytest):
    data = """
    [[act]]
    test="a"
    [[act]]
    test="b"
    """
    f = get_temp_file(data)
    assert len(TomlChaosFile.extract_acts(toml.loads(data))) == 2
    f.close()
