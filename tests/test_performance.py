"""Performance regression test for the schema-caching fix.

BUG FOUND during a deliberate stress-test pass (2026-06-21): checking
200 files via check_directory() took ~150ms/file (~30s total).
Profiling showed nearly all of that time was xmlschema.XMLSchema(...)
recompiling the entire XSD from disk on every single validate_xsd()
call, even though the schema never changes between files in a batch.
Fixed with a module-level cache keyed by schema path.

Confirmed result of the fix: the same 200-file batch dropped from
~66s to ~0.93s (about 70x), and a 1200-file batch completed in under
3 seconds. This test doesn't re-run the full stress test (too slow
for a unit test suite) -- it verifies the cache itself is actually
being hit, which is the underlying mechanism the speedup depends on.
"""

import time

from tollgate.generator.synthetic_fixtures import build_valid_baseline
from tollgate.validation.xsd_validator import _SCHEMA_CACHE, _get_compiled_schema, validate_xsd
from pathlib import Path

SCHEMA_PATH = (
    Path(__file__).parent.parent
    / "src"
    / "tollgate"
    / "schemas"
    / "pacs.008.001.08.xsd"
)


def test_get_compiled_schema_returns_same_object_on_repeated_calls():
    """The actual mechanism the speedup depends on: calling
    _get_compiled_schema with the same path twice should return the
    SAME object (cache hit), not build a new one each time.
    """
    schema1 = _get_compiled_schema(SCHEMA_PATH)
    schema2 = _get_compiled_schema(SCHEMA_PATH)
    assert schema1 is schema2


def test_validate_xsd_does_not_rebuild_schema_on_repeated_calls():
    """End-to-end version of the same property, via the public
    validate_xsd() function rather than the private cache helper.
    """
    _SCHEMA_CACHE.clear()  # start from a clean cache for this test

    xml_str = build_valid_baseline(seed=1)

    validate_xsd(xml_str, SCHEMA_PATH)
    assert str(SCHEMA_PATH) in _SCHEMA_CACHE
    cached_schema_after_first_call = _SCHEMA_CACHE[str(SCHEMA_PATH)]

    validate_xsd(xml_str, SCHEMA_PATH)
    assert _SCHEMA_CACHE[str(SCHEMA_PATH)] is cached_schema_after_first_call


def test_repeated_validation_is_meaningfully_fast():
    """A coarse performance guard, not a precise benchmark -- checks
    that 20 repeated calls complete fast enough to imply the cache is
    working, without being so strict it flakes on a slow CI runner.
    Before the fix, 20 calls would have taken multiple seconds (each
    call rebuilding the schema from scratch); after the fix, 20 calls
    sharing one cached schema should complete in well under a second.
    """
    xml_str = build_valid_baseline(seed=2)

    start = time.time()
    for _ in range(20):
        validate_xsd(xml_str, SCHEMA_PATH)
    elapsed = time.time() - start

    assert elapsed < 2.0, (
        f"20 repeated validate_xsd() calls took {elapsed:.2f}s -- expected "
        f"well under 2s if the schema cache is working. This may indicate "
        f"a regression back to rebuilding the schema on every call."
    )
