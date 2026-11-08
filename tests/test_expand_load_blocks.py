"""Protect the actual CDB converter's input and its separate review outputs."""
import hashlib
import json
import os

import pytest

from cadloop.fea.expand_load_blocks import expand


def record(node, label, real, imaginary='0.000000000E+00'):
    return f'{node:9d}{label:<6}{real:>16}{imaginary:>16}'


SOURCE = ('/PREP7\n! Opaque node/element/contact/material payload stays unchanged\n'
          'N,101,0.000000000E+00,0.000000000E+00,0.000000000E+00\n'
          'MP,EX,1,6.890000000E+04\n'
          'DBLOCK,2\n(i9,a6,2(pg16.9))\n'
          + record(101, 'UX', '-1.234567890E-05') + '\n'
          + record(102, 'UZ', '0.000000000E+00') + '\n-1\n'
          'FBLOCK,2\n(i9,a6,2(pg16.9))\n'
          + record(201, 'FX', '2.500000000E+00', '-0.000000000E+00') + '\n'
          + record(202, 'FZ', '-3.250000000E+00') + '\n-1\nFINISH\n')


def write_source(path):
    path.write_bytes(SOURCE.encode('utf-8'))
    return path.read_bytes()


def link_or_skip(source, target):
    try:
        os.link(source, target)
    except OSError as exc:
        pytest.skip(f'Temporary filesystem does not support hard links: {exc}')


def test_distinct_outputs_preserve_source_and_numeric_literals(tmp_path):
    source, target = tmp_path/'original.cdb', tmp_path/'external.cdb'
    original = write_source(source)
    result = expand(source, target)
    text = target.read_text()
    assert source.read_bytes() == original
    assert text == ('/PREP7\n! Opaque node/element/contact/material payload stays unchanged\n'
                    'N,101,0.000000000E+00,0.000000000E+00,0.000000000E+00\n'
                    'MP,EX,1,6.890000000E+04\n'
                    'D,101,UX,-1.234567890E-05,0.000000000E+00\n'
                    'D,102,UZ,0.000000000E+00,0.000000000E+00\n'
                    'F,201,FX,2.500000000E+00,-0.000000000E+00\n'
                    'F,202,FZ,-3.250000000E+00,0.000000000E+00\nFINISH\n')
    assert result['constraint_records'] == 2
    assert result['force_records'] == 2
    assert result['total_FX_N'] == 2.5
    assert result['source_sha256'] == hashlib.sha256(original).hexdigest()
    assert result['target_sha256'] == hashlib.sha256(target.read_bytes()).hexdigest()
    assert json.loads(target.with_suffix('.conversion.json').read_text()) == result


def test_same_resolved_source_and_target_are_rejected(tmp_path):
    source = tmp_path/'model.cdb'
    original = write_source(source)
    (tmp_path/'sub').mkdir()
    with pytest.raises(ValueError, match='different files'):
        expand(source, tmp_path/'sub'/'..'/'model.cdb')
    assert source.read_bytes() == original
    assert not source.with_suffix('.conversion.json').exists()


def test_source_report_path_collision_is_rejected(tmp_path):
    target = tmp_path/'external.cdb'
    source = target.with_suffix('.conversion.json')
    original = write_source(source)
    with pytest.raises(ValueError, match='different files'):
        expand(source, target)
    assert source.read_bytes() == original
    assert not target.exists()


@pytest.mark.parametrize('alias_pair', ['source_target', 'source_report', 'target_report'])
def test_existing_hard_link_collisions_are_rejected_without_writes(tmp_path, alias_pair):
    source, target = tmp_path/'original.cdb', tmp_path/'external.cdb'
    report = target.with_suffix('.conversion.json')
    original = write_source(source)
    if alias_pair == 'source_target':
        link_or_skip(source, target)
    elif alias_pair == 'source_report':
        link_or_skip(source, report)
    else:
        target.write_bytes(b'Existing converted model must survive')
        link_or_skip(target, report)
    before = {p:p.read_bytes() for p in [source,target,report] if p.exists()}
    with pytest.raises(ValueError, match='different files'):
        expand(source, target)
    assert source.read_bytes() == original
    assert {p:p.read_bytes() for p in [source,target,report] if p.exists()} == before
