"""Exact hypothetical power for a two-sided conditional McNemar test.

Enumerates independent paired binary outcomes, not study results. Marginal rates
alone do not determine power: specify P(both succeed) as well. No model calls.
"""
import argparse
import math

from analyze import mcnemar_p


def paired_power(pairs, solo, treatment, both, alpha=0.05):
    """Unconditional rejection probability, summing the paired multinomial table.

    Assumes independent, identically distributed pairs, complete outcomes and a
    fixed two-sided exact test. Suitable for small design calculations; not a
    guarantee of power under task heterogeneity or treatment-dependent failures.
    """
    if not isinstance(pairs, int) or pairs < 1:
        raise ValueError("pairs must be a positive integer")
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in (solo, treatment, both)):
        raise ValueError("outcome probabilities must be finite and between zero and one")
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be finite and strictly between zero and one")
    eps = 1e-12  # tolerate float rounding at the Frechet bounds (e.g. 0.7 + 0.4 - 1 > 0.1)
    if not max(0, solo + treatment - 1) - eps <= both <= min(solo, treatment) + eps:
        raise ValueError("P(both succeed) is incompatible with the marginal probabilities")
    pb, pc = max(0.0, treatment - both), max(0.0, solo - both)
    concordant = max(0.0, 1 - pb - pc)
    terms = []
    for b in range(pairs + 1):
        for c in range(pairs - b + 1):
            if mcnemar_p(b, c) <= alpha:
                terms.append(math.comb(pairs, b) * math.comb(pairs - b, c)
                             * pb**b * pc**c * concordant**(pairs - b - c))
    return min(1.0, max(0.0, math.fsum(terms)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", type=int, nargs="+", default=[20, 60])
    ap.add_argument("--solo", type=float, default=0.10)
    ap.add_argument("--treatment", type=float, default=0.40)
    ap.add_argument("--both", type=float, nargs="+", default=[0.0, 0.10])
    ap.add_argument("--alpha", type=float, default=0.05)
    args = ap.parse_args(argv)
    results = []
    try:
        for n in args.pairs:
            for joint in args.both:
                results.append((n, joint, paired_power(n, args.solo, args.treatment, joint, args.alpha)))
    except ValueError as e:
        ap.error(str(e))
    print("Hypothetical power only: independent complete pairs; exact two-sided McNemar test.")
    print(f"P(solo)={args.solo:g}, P(treatment)={args.treatment:g}, alpha={args.alpha:g}")
    print("| pairs | P(both succeed) | rejection probability |")
    print("|---:|---:|---:|")
    for n, joint, power in results:
        print(f"| {n} | {joint:g} | {power:.6%} |")


if __name__ == "__main__":
    main()
