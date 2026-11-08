"""Expand CDWRITE DBLOCK/FBLOCK records to documented D/F commands for External Model.

Nodes and elements remain in blocked CDB form. Input/result files are never modified.
All constraint and force literals, including their zero imaginary entries, are retained.
"""
import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path


def expand(source, target):
    source, target = Path(source), Path(target)
    report = target.with_suffix('.conversion.json')
    for first, second in combinations([source, target, report], 2):
        same = first.resolve() == second.resolve()
        if not same and first.exists() and second.exists():
            same = first.samefile(second)
        if same:
            raise ValueError('Source, target and conversion report must refer to different files')
    original = source.read_bytes()
    lines = original.decode('utf-8').splitlines()
    converted, records = [], {'D': [], 'F': []}
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(('DBLOCK,', 'FBLOCK,')):
            command = line[0]
            expected = int(line.split(',')[1])
            if lines[index+1].strip() != '(i9,a6,2(pg16.9))':
                raise ValueError('Unexpected load-block format; do not guess field widths')
            index += 2
            current = []
            while lines[index].strip() != '-1':
                record = lines[index]
                fields = [record[:9].strip(), record[9:15].strip(), record[15:31].strip(), record[31:47].strip()]
                int(fields[0]); float(fields[2]); float(fields[3])
                if float(fields[3]) != 0:
                    raise ValueError('Only the present real-valued static model is supported')
                converted.append(','.join([command]+fields))
                current.append(fields)
                index += 1
            if len(current) != expected:
                raise ValueError('Load-block record count mismatch')
            records[command].extend(current)
        else:
            converted.append(line)
        index += 1
    if not records['D'] or not records['F']:
        raise ValueError('Expected both existing constraint and force records')
    target.write_text('\n'.join(converted)+'\n', encoding='utf-8')
    result = {'source': str(source), 'target': str(target),
              'source_sha256': hashlib.sha256(original).hexdigest(),
              'target_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
              'constraint_records': len(records['D']), 'force_records': len(records['F']),
              'total_FX_N': sum(float(r[2]) for r in records['F'] if r[1]=='FX'),
              'nodes_elements_contacts_materials_unchanged': True}
    report.write_text(json.dumps(result, indent=2)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path); parser.add_argument('target', type=Path)
    args = parser.parse_args()
    print(json.dumps(expand(args.source, args.target), indent=2))
