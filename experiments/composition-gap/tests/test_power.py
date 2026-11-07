"""Check exact design calculations against boundary cases and a known example."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import harness as h
from power import main, paired_power


def test_exact_discordance_rejection_boundary():
    # With every pair in one discordant direction, the exact p is 2 / 2**N.
    assert paired_power(5, 0, 1, 0) == 0
    assert paired_power(6, 0, 1, 0) == 1
    assert paired_power(6, 1, 0, 0) == 1
    assert paired_power(20, 0, 0, 0) == 0


def test_documented_joint_distribution_examples():
    assert paired_power(20, .1, .4, 0) == pytest.approx(.3670826487139956)
    assert paired_power(20, .1, .4, .1) == pytest.approx(.5836291705525188)
    assert paired_power(60, .1, .4, 0) == pytest.approx(.9072194501790032)
    assert paired_power(60, .1, .4, .1) == pytest.approx(.9999499800080546)
    assert paired_power(20, .4, .1, .1) == pytest.approx(paired_power(20, .1, .4, .1))


@pytest.mark.parametrize("solo,treatment", [(.7, .4), (.9, .2), (.6, .5), (.3, .8)])
def test_frechet_lower_bound_accepted_despite_float_rounding(solo, treatment):
    # solo + treatment - 1 is 0.10000000000000009 in floating point; 0.1 is still the feasible minimum.
    assert 0 <= paired_power(20, solo, treatment, .1) <= 1


@pytest.mark.parametrize("args", [(0,.1,.4,0), (5,.1,.4,.2), (5,.8,.8,.1),
                                  (5,float('nan'),.4,0), (5,.1,.4,0,0), (5,.1,.4,0,float('inf'))])
def test_invalid_design_probabilities_are_rejected(args):
    with pytest.raises(ValueError): paired_power(*args)


def test_cli_labels_assumptions(capsys):
    main(["--pairs", "20"])
    output = capsys.readouterr().out
    assert "Hypothetical power only" in output and "36.708265%" in output


@pytest.mark.parametrize("n", [4, 8])
def test_documented_maximum_call_matching(n):
    counts = {}
    conds = h.build_conds([f"swarm@n{n}", f"solo@k{3*n}"], [n], [3*n], "v2")
    for name, run in conds.items():
        calls = []
        run(lambda *args: calls.append(args) or "PASS", 0)
        counts[name] = len(calls)
    assert set(counts.values()) == {3*n}
