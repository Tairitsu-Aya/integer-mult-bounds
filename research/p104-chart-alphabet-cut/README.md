# Independent P104 cut check and directed-type extension

The native P104 channel's **directed transport alphabet**, not only its recorded
chronology, has an eight-array communication bottleneck. Arbitrary retiming,
different scalar coefficients, additional common-chart linear mixing and fresh
zero/copy/discard storage cannot complete the identity while retaining this
alphabet and its eight downward transport uses.

This extends the **frozen-itinerary** scope of David Arias's [PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082)
and Adam Gall's [PR2090](https://github.com/CrocSwap/integer-mult-bounds/pull/2090).
Their rank-eight result, the original `G/2` channel and its native realization
are credited predecessors. The new step removes the time and role-availability
restrictions: a separator remains in the complete directed graph of charts.
It is not a new native compilation, a universal P104 obstruction, an improved
moment or a new kappa.

**Concurrent result:** Jeremy Diviney's [PR2113](https://github.com/CrocSwap/integer-mult-bounds/pull/2113),
head `fa1a45f91c14bb4b372d19dd7d66e11fea480ef5`, was published at 19:37 UTC
and found during this branch's pre-submission overlap check. It already proves
the arbitrary-frame-path-interleaving result with two independent checkers.
This independently developed branch is published as corroborating evidence,
without a competing PR. The directed-type formulation below additionally makes
explicit that new storage alone, arbitrary role reassignment and repetition of
the existing upward types do not bypass the cut while the total crossing count
is eight. The shared retiming conclusion and cut set are not claimed as new
relative to PR2113.

## Exact model and changed hypothesis

Use the immutable PR1972 word distributed by PR1991. Its 280 persistent inputs
are 104 independent source arrays X, 104 independent target arrays Y and 72
independent arbitrary dirty helper arrays. All arrays have a common finite
vector-space dimension d over Q or C. The source and target entry/exit charts
remain those of the word; intrinsic endpoint adapters are invertible and do
not alter ranks. The native physical interpretation is inherited from PR1991.

A chart is identified by its entire binary subspace of F2^9, not by its
dimension. Collapse all occurrences of the same chart, ignoring which register
holds it or when it is visited. For every literal transport add its **directed**
old-chart to new-chart edge. This gives 444 charts and 740 directed types from
1,410 positive-rank occurrences.

The following deliberately favorable class contains every legal retiming of
the original word, including all commutations of independent original events:

1. Arbitrary finite chronological programs may use the listed directed types.
   The 732 upward types may be used any finite number of times, on any suitable
   registers. This grants more freedom than preserving the original invoice.
2. Each of the eight listed downward types is used at most once. More generally,
   the theorem below charges its total number of downward *occurrences*, q.
3. Arbitrary fixed linear mixing and copies within a common chart are allowed.
   New zero arrays and independently initialized dirty arrays may be supplied;
   common-chart copies and owned disposal are granted freely. Such a grant is
   a relaxation, not physical copy/erase admission.
4. Each counted transport carries one d-dimensional array. A batch of several
   independent arrays has their total capacity; it is not one free d-dimensional
   message. No source information is supplied initially in helpers or Y.

Time, lifetime and register constraints can only reduce this class. New chart
edges, reversing an upward edge, inserting an unlisted intermediate chart,
non-common-chart operations, larger uncharged message spaces and nonlinear or
input-dependent coding are outside it. Repetition of an upward type does not
grant its inverse. No jointly executable schedule is inferred from a graph path.

## Certificate and proof

Let R be the set of charts reachable from the 104 source entry charts after
removing all eight downward types. The independently reconstructed certificate
in [RESULT.json](RESULT.json) has these properties:

| Exact property | Value |
|---|---:|
| Charts / directed transport types | 444 / 740 |
| Charts in R / outside R | 222 / 222 |
| Source entry charts in R | 104 |
| Target exit charts in R | 0 |
| Directed edges from R to its complement | exactly the eight private drops |
| Dimensions of each crossing | 8 to 1 |
| Recorded occurrences per crossing | one |

The crossing events, with zero-based indices in the pinned word, are
`2463, 2472, 2479, 2487, 2495, 2503, 2510, 2518`. Each is a rank-seven native
transport of the owned private copy C. Removing them disconnects all sources
from all target exits. Restoring any one makes exactly 52 target exits reachable.
The complete canonical frame and edge/occurrence digests, reachable chart IDs
and explicit crossing bases are recorded, so the partition is reproducible.
PR2082 already identifies these same eight occurrences in its temporal graph;
the set of events is not new. The new certificate proves they remain a cut
after merging every visit to a chart and discarding the chronological restrictions.

**Lemma (chronology-free communication bound).** Every program in the stated
class with q crossing occurrences has source-to-target rank at most q*d.

*Proof.* Fix all nonsource inputs. Record the d-dimensional value transmitted
by each R-to-complement occurrence in its actual execution order. Let Q(X)
be this q*d-dimensional transcript. A common-chart operation cannot cross the
partition. All other allowed transports stay within a part or enter R; they
cannot introduce new source information into the complement. By induction on
the actual chronological program, every value in the complement is a fixed
linear function of its initial inputs and the transcript values already
received. Incoming feedback to R is permitted and does not change this fact.

Every final Y chart lies in the complement. Thus, on varying X with the other
inputs fixed, the X-to-Y map factors through Q(X), so its rank is at most q*d.
The sampled transmissions need not coexist at one time. Equivalently,
`ker Q` is contained in the kernel of the output block; linear factorization
gives the same rank bound. This argument depends on actual message occurrences,
not merely the number of edge types. QED.

With the retained eight occurrences, the bound is 8*d. An identity transfer
`Y <- Y+X` has rank 104*d, hence is impossible in this class. The original
channel attains rank 8*d: the exact scalar replay gives `Y <- Y+(G/2)X`, all
sources/helpers are restored, and the independently regenerated E8 root matrix
satisfies `R_root^t R_root = 26 I_8`. Consequently `G/2` has rank eight. The
rank-eight attainment and tight-frame identity are predecessor facts rechecked
here, not claimed new.

**Reusing the same drops is not free.** If all directed types are retained but
the downward-use cap is relaxed, identity requires q>=104. Each crossing type
costs seven paid ranks, so the crossing subtotal alone is at least 728, versus
56 in the original eight-use word. This is a bound within this directed
alphabet, not a 96-child lower bound for arbitrary new native operations and
not a full global moment. A redesign using new directed types is outside it.

## Relation to the temporal and interleaving results

PR2082 and PR2090 preserve chronological access and private lifetimes; both
explicitly leave retiming outside their claims. This package starts from that
handoff. The exploratory dependency-order check found 240 extra possible
same-chart phase pairs under retiming, with the obstruction unchanged. The
delivered proof does not depend on that dependency graph or those counts: it
discards **all** time and role constraints and even permits unlimited upward
type repetition. Only the source-bound directed alphabet and paid crossing
multiplicity remain. This avoids treating a phase vertex as a one-use capacity:
one register may transmit many values over time, so capacity is charged at the
actual eight downward occurrences instead.
PR2113 independently obtains the same 1,698-phase interleaving obstruction and
71,224 possible directed contacts. This branch's 853/845 phase cones and
444-chart quotient provide corroboration. Its broader directed-type statement
permits new storage and drops the per-register paths as well; the algebraic
reason is the same certified separation, rather than a different rank-eight
phenomenon.

The terminal correction and its budget floor in [PR2083](https://github.com/CrocSwap/integer-mult-bounds/pull/2083)
and [PR2089](https://github.com/CrocSwap/integer-mult-bounds/pull/2089) use new
downward edges into target hyperplanes and are outside this alphabet. Adding
one such reversed target-completion edge makes this checker reject the old
separator. Neither those constructions nor their full-cost obstructions are
claimed anew.

## Independent checking and reproduction

Both programs use only the standard library and authenticate inputs before
semantic use. They import neither predecessor Python nor each other.

- `verify.py` uses reduced binary bases and the 444-vertex directed quotient.
  It checks every original frame/scalar/lifetime transition, the exact cut and
  sparse rational rows over all 280 independent inputs. Thirteen rejecting
  controls cover every omitted crossing, a new reversed target edge, source
  corruption, initial dirty compensation, final query cleanup and a false paid
  rank. Permuting all frame bases is a positive invariance control.
- `audit.py` explicitly enumerates binary spans, constructs 1,698 register
  phases and grants communication between all same-chart phases regardless
  of time. Separate forward/reverse fixed points contain 853/845 disjoint
  phases. It checks the committed partition and whole-atlas digests, every
  single-crossing restoration, and the invalid equal-dimension relaxation.
  It independently enumerates the E8 lattice shell and executes dense integer
  columns on an exact quarter grid, rather than using the primary sparse
  Fraction interpreter.

From the repository root:

```sh
python3 -I -O -B research/p104-chart-alphabet-cut/verify.py
python3 -I -O -B research/p104-chart-alphabet-cut/audit.py
python3.12 scripts/research_package.py --package research/p104-chart-alphabet-cut
```

The checkers are read-only. `verify.py --write-result PATH` creates a new
receipt and refuses overwrite. The selected record/catalogue/native proof
text are provenance; only the exact original word and P104 fixture are runtime
inputs. The generic metadata check additionally needs the pinned Git history.

The separate unmodified PR1991 native replay also passed locally on Ubuntu
24.04 / CPython 3.12.3: 17.059 s wall time and sampled peak RSS 36,466,688 bytes,
with one CPU and a 1 GiB memory stop. It includes complete finite transport
operators, phases and the original arbitrary-input endpoint. This is additional
local corroboration of the inherited native interface; native regeneration,
all-size lifting, hosting, precision, an outer multiplication theorem, hosted
CI and a proof assistant are not established by this package.

## Open next questions

1. **Change a directed chart edge.** Can a paid transport replacement or a
   newly inserted intermediate chart cross the certified partition while
   preserving a favorable *complete* moment? First list a candidate edge's
   exact endpoints and show a source-information route through it; then check
   a jointly executable schedule, native phase and restoration. The existing
   terminal route is already priced elsewhere. The new blocker here is the
   unchanged alphabet, not execution order alone.
2. **Refine an existing monotone transport.** Factoring A->C through a new
   intermediate B preserves net rank mass when A is contained in B contained
   in C, but changes the child histogram and timing. First test simultaneous
   source/target availability and the extra moment cost. Such a new directed
   factorization is deliberately outside the proved class and is not granted
   as a free improvement.

## Provenance and credit

Scientific base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The selected result is unchanged. The selector and refined task are in
[SELECTION.json](SELECTION.json) and [TASK.json](TASK.json). The advance claim
is [PR2090 comment 6176563969](https://github.com/CrocSwap/integer-mult-bounds/pull/2090#issuecomment-6176563969).

Rohan Arun / PR1972 (`fd82d172f46933fd253c2c6de4bd5eaff5429cfd`) supplies the
complete scalar/frame word. Chafik Boukhalfa / PR1991
(`6e222517e182e98499239bc9a4009f540e1c5520`) supplies the native realization and
source distribution. Adam Gall / PR1940 supplies the delivery schedule;
Josie Elliston / PR1071 and Ali Romman / PR1125 supply the P104 fixture and
delivery bounds, with the retained PR968/717/446/595/620 lineage. David Arias /
PR2082 (`60f4e337ffba470e09727dd435b1f1be3b67d03d`) and Adam Gall / PR2090
(`dff116efc2c4ddd7236020ad8316db5c98aa693e`) supply the sharp frozen-itinerary
obstructions and explicit retiming handoff. Their identities, native recipes
and existing rank-eight conclusions are not claimed as new.
Jeremy Diviney / PR2113 supplies the concurrent arbitrary-interleaving result
and its legal retiming witness; that construction is not reproduced or claimed
by this branch. The advance claim here preceded the overlapping publication,
and the overlap was found before any PR was opened for this branch.

Prepared for Tairitsu-Aya with substantial OpenAI Codex assistance. The two
code-disjoint checks are by this same author/assistant, not independent human
review or formal-kernel verification. New work is Apache-2.0; pinned
predecessors and their notices are unchanged.
