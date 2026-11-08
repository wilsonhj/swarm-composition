"""Exploratory follow-up analysis (run_v2_followup.sh, run id 13824e02): framing levels and Sonnet relay over 20 seeds.
Run from experiments/composition-gap: uv run --no-project python analyze_followup.py"""
import json,glob,os,sys,collections
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from scoring import score_row
from analyze import validate_rows
def check(rows, model, framings):
    """Fail loudly on duplicate trials or metadata outside what this group intends (served models may be mixed)."""
    validate_rows(rows)
    seen=set()
    for r in rows:
        k=(r.get('policy'),r.get('framing'),r.get('cond'),r.get('seed'))
        if k in seen: raise ValueError(f'duplicate trial across runs: policy/framing/cond/seed={k}; select one run')
        seen.add(k)
    for field,ok in (('model',{model}),('design',{'v2'}),('backend',{'claude-code'}),
                     ('policy',{'none','strict'}),('framing',set(framings))):
        bad={r.get(field) for r in rows}-ok
        if bad: raise ValueError(f'unexpected {field} {sorted(map(str,bad))} (expected {sorted(ok)}) in {model} group')
def load(pats, excl=(), model=None, framings=()):
    rows=[]
    for p in pats:
        fs=[f for f in glob.glob(str(BASE/p)) if not any(e in os.path.basename(f) for e in excl)]
        if not fs: raise FileNotFoundError(f'no result files match {p} (relative to {BASE})')
        for f in fs:
            for l in open(f):
                r=json.loads(l); r['_f']=f; rows.append(r)
    if model: check(rows, model, framings)
    return rows
def sonnet5(r):
    for t in r.get('turns',[]):
        m=t.get('model'); m=m if isinstance(m,list) else [m]
        if 'claude-sonnet-5' in m: return True
    return False
# --- analysis (runs on import) ---
CONDS=['solo','solo@k5','solo@k12','pipeline','swarm@n4','swarm_noobj@n4','relay_informed','relay_uninformed']
for model,seedmax in (('claude-haiku-5-5',1019),('claude-sonnet-5-5',1009)):
    rows=load([f'results/v2/*{model}_v2_*.jsonl', f'results/v2_followup/*{model}_v2_*hinted*.jsonl'], excl=('rerun',), model=model, framings=('neutral','hinted','explicit'))
    rows=[r for r in rows if r['seed']<=seedmax and r.get('failed_calls')==0]
    for excl5 in ((False,True) if 'sonnet' in model else (False,)):
        print(f'\n## {model} assembled/recoverable by framing' + (' (rows with any claude-sonnet-5 turn excluded)' if excl5 else ''))
        for pol in ('none','strict'):
            print(f'{pol:6} {"cond":17}' + ''.join(f'{fr:>14}' for fr in ('neutral','hinted','explicit')))
            for c in CONDS:
                cells=[]
                for fr in ('neutral','hinted','explicit'):
                    rs=[r for r in rows if r['policy']==pol and r['framing']==fr and r['cond']==c and not (excl5 and sonnet5(r))]
                    s=[score_row(r) for r in rs]
                    cells.append(f'{sum(x["assembled"] for x in s)}/{sum(x["recoverable"] for x in s)}/{len(s)}')
                print(f'{"":6} {c:17}' + ''.join(f'{x:>14}' for x in cells))

from math import comb
def binom_p(b,c):
    n=b+c
    if n==0: return 1.0
    k=min(b,c); return min(1.0, 2*sum(comb(n,i) for i in range(k+1))/2**n)
rows=load(['results/v2/*claude-sonnet-5-5_v2_*.jsonl','results/v2_followup/*sonnet*seeds1010.jsonl'], excl=('rerun',),
          model='claude-sonnet-5-5', framings=('neutral','explicit'))
rows=[r for r in rows if r['cond'] in ('solo','solo@k5','relay_informed','relay_uninformed') and r.get('failed_calls')==0]
S={}
for r in rows: S[(r['policy'],r['framing'],r['cond'],r['seed'])]=(score_row(r),r)
seeds=range(1000,1020)
print("Sonnet 5.5, seeds 1000-1019 (frozen 1000-1009 + follow-up 1010-1019); neutral+explicit cells")
for pol in ('none','strict'):
    for c in ('relay_informed','relay_uninformed'):
        xs=[S[(pol,fr,c,s)] for fr in ('neutral','explicit') for s in seeds if (pol,fr,c,s) in S]
        a=[r['seed'] for x,r in xs if x['assembled']]; rc=sum(x['recoverable'] for x,_ in xs)
        req=sum(bool(x.get('requested')) for x,_ in xs)
        print(f"  {pol:6} {c:17} assembled {len(a)}/{len(xs)} (distinct seeds {len(set(a))}: {sorted(set(a))}), recoverable {rc}/{len(xs)}, requested {req}/{len(xs)}")
        if c=='relay_uninformed' and pol=='strict':
            for half,rng in (('1000-1009',range(1000,1010)),('1010-1019',range(1010,1020))):
                h=[x for x,r in xs if r['seed'] in rng]; print(f"      seeds {half}: assembled {sum(x['assembled'] for x in h)}/{len(h)}, recoverable {sum(x['recoverable'] for x in h)}/{len(h)}")
    for fr in ('neutral','explicit'):
        for c in ('solo','solo@k5'):
            xs=[S[(pol,fr,c,s)][0] for s in seeds if (pol,fr,c,s) in S]
            print(f"  {pol:6} {fr:8} {c:8} assembled {sum(x['assembled'] for x in xs)}/{len(xs)}")
print("\nPaired by seed, strict: relay_uninformed vs solo, same framing cell (b = relay only, c = solo only)")
for fr in ('neutral','explicit'):
    for m in ('assembled','recoverable'):
        b=c=0; n=0
        for s in seeds:
            k1,k2=('strict',fr,'relay_uninformed',s),('strict',fr,'solo',s)
            if k1 in S and k2 in S:
                n+=1; x,y=S[k1][0][m],S[k2][0][m]; b+=x and not y; c+=y and not x
        print(f"  {fr:8} {m:11} n={n} relay-only={b} solo-only={c} diff={(b-c)/n*100:+.0f}pp exact McNemar p={binom_p(b,c):.3f}")
mixed=[(r['framing'],r['seed']) for (x,r) in S.values() if r['cond']=='relay_uninformed' and r['policy']=='strict' and sonnet5(r)]
print("\nstrict relay_uninformed rows with a claude-sonnet-5 turn:", mixed, "(frozen 1000-1009 strict/explicit rows have no per-turn model log)")
print("\nSensitivity: seeds 1010-1019 only (all per-turn logged), rows with any claude-sonnet-5 turn dropped from the pair")
for fr in ('neutral','explicit'):
    for m in ('assembled','recoverable'):
        b=c=n=0
        for s in range(1010,1020):
            k1,k2=('strict',fr,'relay_uninformed',s),('strict',fr,'solo',s)
            if k1 in S and k2 in S and not sonnet5(S[k1][1]) and not sonnet5(S[k2][1]):
                n+=1; x,y=S[k1][0][m],S[k2][0][m]; b+=x and not y; c+=y and not x
        print(f"  {fr:8} {m:11} n={n} relay-only={b} solo-only={c} exact McNemar p={binom_p(b,c):.3f}")
xs=[S[('strict',fr,'relay_uninformed',s)] for fr in ('neutral','explicit') for s in range(1010,1020)]
xs=[(x,r) for x,r in xs if not sonnet5(r)]
print(f"  strict relay_uninformed, seeds 1010-1019, clean rows: assembled {sum(x['assembled'] for x,_ in xs)}/{len(xs)} distinct seeds {sorted({r['seed'] for x,r in xs if x['assembled']})}")
