# Bounded-noise ridge contract

The v0.5.7 ridge batteries previously required every randomly forced walk to
finish within one unit of 4.5. The JavaScript run reported 7 failed checks and
the Python run 11, but both exited zero because they allowed up to 15 failures.
Those results were not complete assertion passes.

This change replaces that unsupported one-unit requirement with a derived
finite-step tracking bound. Both ridge scripts now exit nonzero for any failed
assertion. The contraction implementation and disturbance amplitude are unchanged.

## State space and assumptions

Let the circle length be 9, its midpoint be $\mu=4.5$, and
$q(z)=z\bmod 9\in[0,9)$. The exact recurrence used by the noisy-walk section is

$$x_{n+1}=C_k(x_n+u_n),\qquad C_k(z)=\mu+k(q(z)-\mu).$$

The experiments use $k=0.55$, $|u_n|\le B=1.5$, and 50 steps. The initial state
may be any finite real number; it is canonicalized by the first step. The proof
below assumes real arithmetic, $0<k<1$, and $B<\mu(1-k)$. These gain and seam
conditions are also checked by each ridge battery.

## Why the seam stops mattering after the first step

Every canonical input is in $[0,9)$, so every output lies in

$$I=[\mu(1-k),\mu(1+k)).$$

This holds after the first step even if the initial disturbed input crosses the
seam. With the chosen parameters, $I=[2.025,6.975)$. Adding a disturbance produces
an input in $[0.525,8.475)$, strictly inside $[0,9)$. Therefore no subsequent
modulo operation wraps. More generally, the strict condition
$B<\mu(1-k)$ puts all of $I+[-B,B]$ inside $(0,9)$.

Writing $e_n=x_n-\mu$, we consequently have $|e_1|\le\mu k$ and, for $n\ge1$,

$$e_{n+1}=k e_n+k u_n.$$

## Finite-step bound

For every integer $N\ge1$, the triangle inequality and the finite geometric sum
give

$$|e_N|\le k^{N-1}|e_1|+kB\sum_{r=0}^{N-2}k^r
\le E_N:=\mu k^N+\frac{kB(1-k^{N-1})}{1-k}.$$

The sum is empty for $N=1$. The asymptotic tracking radius is
$kB/(1-k)=11/6$, approximately 1.8333, rather than one. Persistent forcing need
not converge to the midpoint.

This bound is attainable on the negative side: choose $x_0=B$ and $u_n=-B$ for
every step. Then the first canonical input is zero, $e_1=-\mu k$, and
$e_N=-E_N$. On the positive side, choose $x_0=9-B-\varepsilon$ and constant
$u_n=B$; then $e_N=E_N-k^N\varepsilon$. The latter approaches the open endpoint.
With zero disturbance and arbitrary wrapped initial state, the separate formula
is $e_N=k^N(q(x_0)-\mu)$.

## Executed regression contract

Both ridge scripts check the finite-step bound and the absence of subsequent
seam crossings for every seeded noisy-walk step. They also check deterministic
negative worst-case forcing, a near-positive worst case with a known initial
gap, and zero-noise trajectories from seven initial states including wrapped
ones. The negative worst case explicitly exceeds one unit, preserving an
executable counterexample to the old requirement.

Numerical comparisons allow an absolute $10^{-12}$ tolerance for these
50-step double-precision experiments. The real-arithmetic derivation above is
not a formal floating-point roundoff certificate or a claim about every
possible gain, noise amplitude, or physical system.

The two scripts also undergo a local fault-injection check: a temporary source
copy receives exactly one failed assertion and must exit one. Other upstream
batteries keep their existing acceptance policies; their individual assertion
counts and process outcomes are recorded separately.

Local verification on Node 24.22.1 and Python 3.12.14 passed 57 checks from
`npm test`, 23 from `test_descent.py`, 15,819 from the corrected JavaScript ridge
script, and 23,648 from the corrected Python ridge script. All 22 extra battery
scripts exited zero and reported zero failed checks, with 163,757 numerical
checks in total. These repeated and overlapping checks are not independent
scientific trials. The new hosted matrix still needs to run after publication.
