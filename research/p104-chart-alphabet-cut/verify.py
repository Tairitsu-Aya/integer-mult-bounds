#!/usr/bin/env python3
"""Exact directed-chart cut, independent of P104 event chronology.

Tairitsu-Aya with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor Python or native compiler is imported.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import copy
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WITNESS = 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
FIXTURE = 'research/p104-native-channel/inputs/P104-FIXTURE.json'


class Rejected(ValueError):
    pass


def require(value, message):
    if not value:
        raise Rejected(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def authenticate(data, pin):
    require(digest(data) == pin['sha256'], 'source SHA256: ' + pin['path'])
    git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    require(git_blob == pin['git_blob'], 'source Git blob: ' + pin['path'])
    return data


def read_inputs():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    require(manifest['base_commit'] == '0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2',
            'scientific base')
    pins = {p['path']: p for p in manifest['files'] if p['usage'] == 'input'}
    require(set(pins) == {WITNESS, FIXTURE}, 'exact runtime input set')
    raw = {name: authenticate((ROOT / name).read_bytes(), pins[name]) for name in pins}
    return json.loads(raw[WITNESS]), json.loads(raw[FIXTURE]), raw, pins


def basis(vectors):
    """Reduced binary basis, independent of supplied basis order."""
    require(isinstance(vectors, list), 'frame vector list')
    rows = {}
    for original in vectors:
        require(type(original) is int and 0 < original < 512, 'nine-bit nonzero vector')
        value = original
        for pivot in sorted(rows, reverse=True):
            if value & (1 << pivot):
                value ^= rows[pivot]
        require(value != 0, 'independent frame vectors')
        pivot = value.bit_length() - 1
        for old_pivot in tuple(rows):
            if rows[old_pivot] & (1 << pivot):
                rows[old_pivot] ^= value
        rows[pivot] = value
    return tuple(rows[p] for p in sorted(rows, reverse=True))


def contained(small, large):
    for value in small:
        for row in large:
            if value & (1 << (row.bit_length() - 1)):
                value ^= row
        if value:
            return False
    return True


def coefficient(value):
    require(type(value) in (int, str), 'exact rational coefficient')
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise Rejected('finite rational coefficient') from exc


def atlas(witness):
    require(set(witness) == {'initial_frames', 'final_frames', 'program'}, 'witness schema')
    expected_names = {f'{p}{i}' for p, count in (('X', 104), ('Y', 104), ('Q', 8), ('G', 32), ('D', 32))
                      for i in range(count)}
    require(set(witness['initial_frames']) == set(witness['final_frames']) == expected_names,
            '280 persistent register names')
    active = {r: basis(f) for r, f in witness['initial_frames'].items()}
    require(all(len(active[f'X{i}']) == 1 and not active[f'Y{i}'] for i in range(104)),
            'source singleton and target zero entries')
    require(all(not f for r, f in active.items() if not r.startswith(('X', 'Y'))),
            'independent dirty helpers start at zero chart')
    all_frames = set(active.values())
    occurrences = defaultdict(list)
    profile = Counter()
    operations = Counter()
    for index, event in enumerate(witness['program']):
        require(isinstance(event, list) and len(event) >= 2, 'event list')
        op, reg = event[:2]
        operations[op] += 1
        if op == 'transport':
            require(len(event) == 5 and reg in active, 'transport schema')
            old, new, rank = basis(event[2]), basis(event[3]), event[4]
            require(active[reg] == old, 'transport old frame')
            require(contained(old, new) or contained(new, old), 'nested transport')
            require(type(rank) is int and rank == abs(len(new) - len(old)) > 0,
                    'actual positive transport rank')
            active[reg] = new
            all_frames.add(new)
            occurrences[old, new].append(index)
            profile[rank] += 1
        elif op == 'zero':
            require(len(event) == 3 and reg == 'C' and reg not in active, 'owned private allocation')
            active[reg] = basis(event[2])
            all_frames.add(active[reg])
        elif op == 'erase':
            require(len(event) == 3 and reg == 'C' and reg in active, 'owned private disposal')
            require(active[reg] == basis(event[2]), 'private disposal frame')
            del active[reg]
        elif op in ('copy', 'add'):
            require(len(event) == (4 if op == 'copy' else 5), 'scalar schema')
            src = event[2]
            require(reg in active and src in active and reg != src, 'two distinct live registers')
            require(active[reg] == active[src] == basis(event[-1]), 'common scalar chart')
            if op == 'copy':
                require(reg == 'C', 'owned private copy target')
            else:
                coefficient(event[3])
        else:
            raise Rejected('unknown event operation')
    require(active == {r: basis(f) for r, f in witness['final_frames'].items()}, 'all final frames')
    ordered = sorted(all_frames)
    indices = {f: i for i, f in enumerate(ordered)}
    edges = {(indices[a], indices[b]): tuple(uses) for (a, b), uses in occurrences.items()}
    sources = [indices[basis(witness['initial_frames'][f'X{i}'])] for i in range(104)]
    targets = [indices[basis(witness['final_frames'][f'Y{i}'])] for i in range(104)]
    require(len(set(sources)) == len(set(targets)) == 104, 'distinct source and target charts')
    require(all(len(ordered[i]) == 8 for i in targets), 'target hyperplane endpoints')
    cuts = {edge for edge in edges if len(ordered[edge[0]]) > len(ordered[edge[1]])}
    require(len(cuts) == 8 and all(len(edges[e]) == 1 for e in cuts), 'eight single-use downward types')
    require(all((len(ordered[a]), len(ordered[b])) == (8, 1) for a, b in cuts), 'eight rank-seven drops')
    require(all(witness['program'][edges[e][0]][1] == 'C' for e in cuts), 'actual private drop events')
    return dict(frames=ordered, edges=edges, sources=sources, targets=targets, cuts=cuts,
                profile=dict(sorted(profile.items())), operations=dict(sorted(operations.items())))


def reached(graph, starts, removed=()):
    blocked = set(removed)
    adjacency = defaultdict(list)
    for a, b in graph:
        if (a, b) not in blocked:
            adjacency[a].append(b)
    seen = set(starts)
    queue = deque(starts)
    while queue:
        a = queue.popleft()
        for b in adjacency[a]:
            if b not in seen:
                seen.add(b)
                queue.append(b)
    return seen


def separator(data, edges=None, cuts=None):
    edges = data['edges'] if edges is None else edges
    cuts = data['cuts'] if cuts is None else cuts
    reachable = reached(edges, data['sources'], cuts)
    require(not set(data['targets']) & reachable, 'source-target separator')
    boundary = {e for e in edges if e[0] in reachable and e[1] not in reachable}
    require(boundary == set(cuts), 'exact directed cut boundary')
    require(set(data['targets']) <= reached(edges, data['sources']), 'all targets reachable in intact atlas')
    return reachable


def root_ports(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for tail in product((-1, 1), repeat=7):
        if sum(x == -1 for x in tail) % 2 == 0:
            roots.add((1, *tail))
    chosen = fixture['section4_explicit_P104']
    removed = {tuple(r) for r in chosen['F0'] + chosen['C']}
    require(len(roots) == 120 and len(removed) == 16 and removed <= roots, 'P104 root fixture')
    ports = sorted(roots - removed)
    require(all(sum(row[i] * row[j] for row in ports) == 104 * (i == j)
                for i in range(8) for j in range(8)), 'doubled-coordinate tight frame')
    gram = [[Fraction(sum(x * y for x, y in zip(a, b)), 4) for b in ports] for a in ports]
    require(all(g.denominator == 1 for row in gram for g in row), 'integral ordinary Gram')
    return ports, gram


def endpoint(witness, fixture):
    _, gram = root_ports(fixture)
    names = list(witness['initial_frames'])
    state = {r: {r: Fraction(1)} for r in names}
    for event in witness['program']:
        op, reg = event[:2]
        if op == 'zero':
            require(reg not in state, 'private row absent before allocation')
            state[reg] = {}
        elif op == 'erase':
            require(reg == 'C', 'only owned row disposal')
            del state[reg]
        elif op == 'copy':
            require(state[reg] == {}, 'owned copy starts zero')
            state[reg] = dict(state[event[2]])
        elif op == 'add':
            scale = coefficient(event[3])
            for name, value in state[event[2]].items():
                updated = state[reg].get(name, 0) + scale * value
                if updated:
                    state[reg][name] = updated
                else:
                    state[reg].pop(name, None)
    require(set(state) == set(names), 'all private lifetimes closed')
    for name in names:
        expected = {name: Fraction(1)}
        if name.startswith('Y'):
            row = gram[int(name[1:])]
            expected.update({f'X{i}': value / 2 for i, value in enumerate(row) if value})
        require(state[name] == expected, 'arbitrary-input endpoint: ' + name)
    return dict(formal_inputs=len(names), restored_sources=104, restored_dirty_helpers=72,
                target_rows=104, source_to_target_rank=8,
                rank_reason='R^t R = 26 I_8 for ordinary roots, hence rank(G/2)=8',
                nonzero_transfer_coefficients=sum(bool(g) for row in gram for g in row))


def rejects(action, message):
    try:
        action()
    except Rejected as error:
        require(message in str(error), 'unexpected rejection: ' + str(error))
        return True
    raise Rejected('control was not rejected: ' + message)


def controls(witness, fixture, data, raw, pins):
    counts = []
    for edge in sorted(data['cuts']):
        remaining = data['cuts'] - {edge}
        rejects(lambda: separator(data, cuts=remaining), 'source-target separator')
        counts.append(len(set(data['targets']) & reached(data['edges'], data['sources'], remaining)))
    full = next(i for i, f in enumerate(data['frames']) if len(f) == 9)
    augmented = dict(data['edges'])
    augmented[full, data['targets'][0]] = (-1,)
    rejects(lambda: separator(data, edges=augmented), 'source-target separator')
    rejects(lambda: authenticate(raw[WITNESS] + b' ', pins[WITNESS]), 'source SHA256')
    for event_index in (0, len(witness['program']) - 1):
        mutant = copy.deepcopy(witness)
        require(mutant['program'][event_index][0] == 'add', 'actual dirty compensation event')
        mutant['program'][event_index][3] = 0
        require(atlas(mutant)['edges'] == data['edges'], 'unchanged graph in scalar control')
        rejects(lambda: endpoint(mutant, fixture), 'arbitrary-input endpoint')
    mutant = copy.deepcopy(witness)
    first_transport = next(e for e in mutant['program'] if e[0] == 'transport')
    first_transport[4] += 1
    rejects(lambda: atlas(mutant), 'actual positive transport rank')
    reordered = copy.deepcopy(witness)
    for key in ('initial_frames', 'final_frames'):
        for vectors in reordered[key].values():
            vectors.reverse()
    for e in reordered['program']:
        if e[0] == 'transport':
            e[2].reverse()
            e[3].reverse()
        else:
            e[-1].reverse()
    require(atlas(reordered) == data, 'basis-order invariance')
    return dict(single_drop_restorations_reopen_targets=counts,
                new_reversed_target_edge_reopens_cut=True,
                source_corruption_rejected=True, initial_dirty_compensation_rejected=True,
                final_query_cleanup_rejected=True, false_paid_rank_rejected=True,
                basis_order_invariance=True)


def result():
    witness, fixture, raw, pins = read_inputs()
    data = atlas(witness)
    reachable = separator(data)
    frames, edges = data['frames'], data['edges']
    edge_rows = [[a, b, list(uses)] for (a, b), uses in sorted(edges.items())]
    require(len(frames) == 444 and len(edges) == 740 and len(reachable) == 222,
            'source-bound atlas dimensions')
    return dict(status='PASS_P104_CHART_ALPHABET_CUT',
                scope='Directed transport alphabet, arbitrary retiming/common-chart linear mixing; not universal P104',
                source_sha256={p: digest(v) for p, v in sorted(raw.items())},
                atlas=dict(frame_count=len(frames), directed_type_count=len(edges),
                           occurrence_count=sum(map(len, edges.values())),
                           frames_sha256=digest(canonical_bytes(frames)),
                           edge_occurrences_sha256=digest(canonical_bytes(edge_rows)),
                           source_frame_ids=data['sources'], target_frame_ids=data['targets']),
                cut=dict(reachable_frame_ids=sorted(reachable),
                         reachable_dimensions=dict(sorted(Counter(len(frames[i]) for i in reachable).items())),
                         crossing_types=[dict(source_frame_id=a, target_frame_id=b,
                                              old=list(frames[a]), new=list(frames[b]),
                                              event_indices=list(edges[a, b]), paid_rank=7,
                                              array_capacity=1) for a, b in sorted(data['cuts'])],
                         total_array_capacity=8, identity_required_array_rank=104,
                         positive_rank_sum=56, simultaneous_cut_not_required=True),
                unchanged_invoice=dict(profile=data['profile'], operations=data['operations'],
                                       rank_mass=sum(r * n for r, n in data['profile'].items())),
                original_endpoint=endpoint(witness, fixture),
                controls=controls(witness, fixture, data, raw, pins))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path, help='Create a receipt, refusing overwrite')
    args = parser.parse_args()
    observed = result()
    if args.write_result:
        with args.write_result.open('x', encoding='utf-8') as handle:
            json.dump(observed, handle, indent=2, sort_keys=True)
            handle.write('\n')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_bytes())
        require(canonical_bytes(observed) == canonical_bytes(expected), 'canonical RESULT mismatch')
    print(observed['status'], 'frames=444 types=740 cut=8 capacity=8 identity=104 no_new_kappa')


if __name__ == '__main__':
    main()
