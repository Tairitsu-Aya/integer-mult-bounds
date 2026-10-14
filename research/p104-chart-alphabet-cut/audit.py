#!/usr/bin/env python3
"""Independent literal-span/phase-graph and integer-column replay.

Imports neither verify.py nor any predecessor program. The chronology-free
phase graph deliberately overapproximates all jointly executable schedules.
Tairitsu-Aya with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
W = 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
F = 'research/p104-native-channel/inputs/P104-FIXTURE.json'


def ensure(ok, reason):
    if not ok:
        raise ValueError(reason)


def closed(vectors):
    values = {0}
    for x in vectors:
        ensure(type(x) is int and 0 < x < 512, 'nine-bit vector')
        values.update(y ^ x for y in tuple(values))
    ensure(len(values) == 2 ** len(vectors), 'independent input basis')
    return frozenset(values)


def representative(space):
    # Greedily choose the numerically smallest new coset representatives from
    # the *entire* subspace. This independently obtains reduced binary rows.
    generated, rows = {0}, []
    for value in sorted(space):
        if value not in generated:
            rows.append(value)
            generated.update(x ^ value for x in tuple(generated))
    ensure(generated == set(space), 'complete literal span')
    return tuple(reversed(rows))


def read():
    pins = json.loads((P / 'SOURCES.json').read_bytes())
    data = {}
    for item in pins['files']:
        if item['usage'] != 'input':
            continue
        raw = (ROOT / item['path']).read_bytes()
        ensure(hashlib.sha256(raw).hexdigest() == item['sha256'], 'SHA256 input pin')
        header = ('blob %d\0' % len(raw)).encode()
        ensure(hashlib.sha1(header + raw).hexdigest() == item['git_blob'], 'Git blob input pin')
        data[item['path']] = json.loads(raw)
    ensure(set(data) == {W, F}, 'runtime input inventory')
    return data[W], data[F]


def phases(witness):
    nodes, active, links, drops = [], {}, [], set()

    def create(reg, vectors):
        node = len(nodes)
        nodes.append(closed(vectors))
        active[reg] = node
        return node

    for reg, vectors in witness['initial_frames'].items():
        create(reg, vectors)
    start = [active['X%d' % i] for i in range(104)]
    histogram = Counter()
    for index, event in enumerate(witness['program']):
        op, reg = event[:2]
        if op == 'zero':
            ensure(reg == 'C' and reg not in active, 'private lifetime opening')
            create(reg, event[2])
        elif op == 'erase':
            ensure(reg == 'C' and nodes[active[reg]] == closed(event[2]), 'private lifetime closing')
            del active[reg]
        elif op == 'transport':
            previous = active[reg]
            before, after = closed(event[2]), closed(event[3])
            ensure(nodes[previous] == before, 'literal source chart')
            ensure(before <= after or after <= before, 'nested literal subspaces')
            rank = abs(len(before).bit_length() - len(after).bit_length())
            ensure(rank == event[4] and rank > 0, 'literal rank')
            current = create(reg, event[3])
            links.append((previous, current, index))
            histogram[rank] += 1
            if len(before) > len(after):
                ensure(reg == 'C' and rank == 7, 'all downward uses are private rank seven')
                drops.add(index)
        else:
            ensure(op in ('copy', 'add'), 'known scalar event')
            ensure(nodes[active[reg]] == nodes[active[event[2]]] == closed(event[-1]),
                   'common literal scalar subspace')
    ensure(set(active) == set(witness['final_frames']), 'final persistent inventory')
    for reg, vectors in witness['final_frames'].items():
        ensure(nodes[active[reg]] == closed(vectors), 'literal final frame')
    finish = [active['Y%d' % i] for i in range(104)]
    return nodes, links, drops, start, finish, histogram


def closure(nodes, links, initial, deleted, dimension_only=False, reverse=False):
    # All visits to the same chart may communicate, with *no* temporal or
    # lifetime compatibility test. Such extra routes make exclusion stronger.
    groups = defaultdict(set)
    for index, space in enumerate(nodes):
        groups[len(space) if dimension_only else space].add(index)
    known = set(initial)
    while True:
        old = len(known)
        for members in groups.values():
            if known.intersection(members):
                known.update(members)
        for a, b, event in links:
            if reverse:
                a, b = b, a
            if event not in deleted and a in known:
                known.add(b)
        if len(known) == old:
            return known


def integer_endpoint(witness, fixture):
    names = list(witness['initial_frames'])
    count = len(names)
    column = {name: i for i, name in enumerate(names)}
    state = {name: [4 * (i == j) for j in range(count)] for i, name in enumerate(names)}
    for e in witness['program']:
        op, target = e[:2]
        if op == 'zero':
            state[target] = [0] * count
        elif op == 'copy':
            ensure(not any(state[target]), 'private copy zero row')
            state[target] = list(state[e[2]])
        elif op == 'erase':
            del state[target]
        elif op == 'add':
            scale = Fraction(e[3])
            for j, value in enumerate(state[e[2]]):
                numerator = value * scale.numerator
                ensure(numerator % scale.denominator == 0, 'exact quarter-grid arithmetic')
                state[target][j] += numerator // scale.denominator
    roots = set()
    # Separate lattice-shell enumeration, not the primary checker's root-pair
    # constructor. Doubled E8 roots have uniform coordinate parity.
    for alphabet in ((-2, 0, 2), (-1, 1)):
        for vector in product(alphabet, repeat=8):
            if sum(x * x for x in vector) != 8 or sum(vector) % 4:
                continue
            if next(x for x in vector if x) > 0:
                roots.add(vector)
    f = fixture['section4_explicit_P104']
    omitted = {tuple(r) for r in f['F0'] + f['C']}
    ensure(len(roots) == 120 and len(omitted) == 16 and omitted <= roots, 'lattice-shell roots')
    ports = sorted(roots - omitted)
    for i in range(8):
        for j in range(8):
            ensure(sum(r[i] * r[j] for r in ports) == (104 if i == j else 0), 'rank-eight tight frame')
    for name, observed in state.items():
        expected = [0] * count
        expected[column[name]] = 4
        if name.startswith('Y'):
            target = ports[int(name[1:])]
            for i, source in enumerate(ports):
                dot = sum(x * y for x, y in zip(target, source))
                ensure(dot % 2 == 0, 'integer twice-Gram entry')
                expected[column['X%d' % i]] = dot // 2
        ensure(observed == expected, 'integer arbitrary-input endpoint: ' + name)
    return count


def main():
    witness, fixture = read()
    nodes, links, drops, starts, finishes, histogram = phases(witness)
    ensure(len(drops) == 8, 'eight distinct recorded transport occurrences')
    forward = closure(nodes, links, starts, drops)
    backward = closure(nodes, links, finishes, drops, reverse=True)
    ensure(not set(finishes) & forward, 'independent no source-target route')
    ensure(not forward & backward, 'disjoint directional phase cones')
    ensure(set(finishes) <= closure(nodes, links, starts, set()), 'intact graph positive control')
    for event in drops:
        ensure(set(finishes) & closure(nodes, links, starts, drops - {event}),
               'every restored drop opens a source-target route')
    ensure(set(finishes) <= closure(nodes, links, starts, drops, dimension_only=True),
           'equal dimension is not a valid common-chart replacement')
    raw_result = json.loads((P / 'RESULT.json').read_bytes())
    canonical = sorted({representative(space) for space in nodes})
    ids = {b: i for i, b in enumerate(canonical)}
    edge_events = defaultdict(list)
    for a, b, event in links:
        edge_events[ids[representative(nodes[a])], ids[representative(nodes[b])]].append(event)
    rows = [[a, b, uses] for (a, b), uses in sorted(edge_events.items())]
    encode = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
    ensure(hashlib.sha256(encode(canonical)).hexdigest() == raw_result['atlas']['frames_sha256'],
           'independent complete-frame digest')
    ensure(hashlib.sha256(encode(rows)).hexdigest() == raw_result['atlas']['edge_occurrences_sha256'],
           'independent complete-edge digest')
    reached_ids = sorted({ids[representative(nodes[n])] for n in forward})
    ensure(reached_ids == raw_result['cut']['reachable_frame_ids'], 'independent separator certificate')
    ensure(sorted(drops) == sorted(i for e in raw_result['cut']['crossing_types'] for i in e['event_indices']),
           'cut occurrence binding')
    ensure({str(k): v for k, v in histogram.items()} == raw_result['unchanged_invoice']['profile'],
           'independent full paid histogram')
    count = integer_endpoint(witness, fixture)
    print('PASS_INDEPENDENT_P104_ALPHABET_AUDIT',
          f'phases={len(nodes)} frames={len(canonical)} cut={len(drops)} formal_columns={count}',
          f'forward_phases={len(forward)} backward_phases={len(backward)}')


if __name__ == '__main__':
    main()
