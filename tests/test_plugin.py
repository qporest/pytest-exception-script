import pytest
import sys

def test_empty_chaos(testdir):
    """
    Without enry-point expect an error.
    """
    # create a temporary conftest.py file
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)
    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    # check that all 4 tests passed
    if sys.version_info.major < 3:
        result.assert_outcomes(passed=0, failed=0, error=1)
    else:
        result.assert_outcomes(passed=0, failed=0, errors=1)


def test_app_factory_incorrect_definition(testdir):
    """
    Can't import chosen entry-point. Also - do not support module imports
    """
    # create a temporary conftest.py file
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)
    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="factory"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    if sys.version_info.major < 3:
        result.assert_outcomes(error=1)
    else:    
        result.assert_outcomes(errors=1)

def test_app_factory_definition_succeeds(testdir):
    """Confirm that correct entry-point definition succeeds."""
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)
    
    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    result.assert_outcomes(passed=0)

def test_errors_collected_no_next_point_with_at_least_one_act(testdir):
    """Fail is at least a single act exists, but no next-point is defined."""
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeini("""
    [pytest]
    addopts = -v
    """)
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)

    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="OSError"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    if sys.version_info.major < 3:
        result.assert_outcomes(error=1)
    else:    
        result.assert_outcomes(errors=1)


def test_errors_multiple_acts_collected_no_next_point(testdir):
    """Make sure that our plugin works."""
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)

    testdir.makeini("""
    [pytest]
    addopts = -v
    """)

    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="OSError"
    [[act]]
    [[act."fake_app_success.process_data"]]
    exc="werkzeug.utils.ImportStringError"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    # check that all 4 tests passed
    if sys.version_info.major < 3:
        result.assert_outcomes(error=1)
    else:    
        result.assert_outcomes(errors=1)

def test_errors_not_every_act_has_next_point_first_missing(testdir):
    """
    Multiple acts are defined, but one of them does not have
    next-point defined, because they are defined per act.
    """
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)

    testdir.makeini("""
    [pytest]
    addopts = -v
    """)

    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="OSError"
    [[act]]
    "next-point"="fake_app_success.process_data"
    [[act."fake_app_success.process_data"]]
    exc="werkzeug.utils.ImportStringError"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    if sys.version_info.major < 3:
        result.assert_outcomes(error=1)
    else:    
        result.assert_outcomes(errors=1)

def test_errors_not_every_act_has_next_point_last_missing(testdir):
    """
    Multiple acts are defined, but one of them does not have
    next-point defined, because they are defined per act.
    """
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)

    testdir.makeini("""
    [pytest]
    addopts = -v
    """)

    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    [[act]]
    "next-point"="fake_app_success.process_data"
    [[act."fake_app_success.get_data"]]
    exc="OSError"
    [[act]]
    [[act."fake_app_success.process_data"]]
    exc="werkzeug.utils.ImportStringError"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    if sys.version_info.major < 3:
        result.assert_outcomes(error=1)
    else:    
        result.assert_outcomes(errors=1)

def test_fails_collected_builtin_exception_global_next(testdir):
    """
    Everything is defined correctly - test confirms that tested file 
    cannot survive given exception. Using Built-in Exception
    """
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeini("""
    [pytest]
    addopts = -v
    """)
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)

    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    next-point="fake_app_success.process_data"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="OSError"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    # check that all 4 tests passed
    result.assert_outcomes(failed=1)


def test_fails_act_collected_import_exception_local_next(testdir):
    """
    Everything is defined correctly - test confirms that tested file 
    cannot survive given exception. Using Imported exception
    """
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeini("""
    [pytest]
    # addopts = -v
    """)
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)

    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    [[act]]
    next-point="fake_app_success.process_data"
    [[act."fake_app_success.get_data"]]
    exc="werkzeug.utils.ImportStringError,test1,test2"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    # check that all 4 tests passed
    result.assert_outcomes(failed=1)


def test_succeeds_act_collected_builtin_exception_global_next(testdir):
    """Make sure that our plugin works."""
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeini("""
    [pytest]
    addopts = -v
    """)
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)

    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    next-point="fake_app_success.process_data"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="KeyError"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    # check that all 4 tests passed
    result.assert_outcomes(passed=1)


def test_succeeds_acts_collected_multiple_builtin_acts(testdir):
    """Make sure that our plugin works."""
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeini("""
    [pytest]
    addopts = -v
    """)
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)

    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    next-point="fake_app_success.process_data"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="KeyError"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="KeyError"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    # check that all 4 tests passed
    result.assert_outcomes(passed=2)


def test_succeeds_many_acts_collected_multiple_builtin_acts(testdir):
    """Make sure that our plugin works."""
    # create a temporary conftest.py file
    testdir.copy_example("tests/fake_app_success.py")
    testdir.makeini("""
    [pytest]
    addopts = -v
    """)
    testdir.makeconftest("""
    pytest_plugins = ["chaos_test"]
    """)

    # create a temporary pytest test file
    f = testdir.tmpdir.join("chaos_test").new(ext="toml")
    f.write("""entry-point="fake_app_success.factory"
    next-point="fake_app_success.process_data"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="KeyError"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="KeyError"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="KeyError"
    [[act]]
    [[act."fake_app_success.get_data"]]
    exc="KeyError"
    """)
    # run all tests with pytest
    result = testdir.runpytest()
    # check that all 4 tests passed
    result.assert_outcomes(passed=4)
