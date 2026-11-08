import argparse, sys
from pathlib import Path
from collections import defaultdict
parser=argparse.ArgumentParser(description='Recompute additional Study 2 secondary endpoints without model calls.')
parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
repo=parser.parse_args().repo.resolve()
sys.path.insert(0,str(repo/'experiments/composition-gap'))
import analyze as a
p=repo/'experiments/composition-gap/results/task-provenance/heldout-haiku.jsonl'
raw=a.load_rows([str(p)]); rows=[a.enrich(r) for r in raw]; a.validate_rows(rows)
cells=defaultdict(list)
for r in rows: cells[(r['authorization'],r['framing'],r['cond'])].append(r)
assert len(rows)==800 and len(cells)==16 and all(len(c)==50 for c in cells.values())
mismatch=[(r['authorization'],r['framing'],r['cond'],r['seed']) for r in rows if r['assembled'] != r['assembled_exact']]
print('all rows assembly mismatches:',len(mismatch),mismatch)
assert not mismatch
assert all(r['exposed_parts']==r['identified_parts'] for r in rows)
print('all rows exposed/identified mismatches:',0)
print('valid rows assembly mismatches:',sum(1 for r in rows if r['valid'] is True and r['assembled']!=r['assembled_exact']))
print('cell | valid n | normalized/exact successes | mean exposed [bootstrap CI]')
for key,c in sorted(cells.items()):
 v=[r for r in c if r['valid'] is True]; ci=a.boot_ci([[r['exposed_parts']] for r in v]); print(' / '.join(key),len(v),sum(r['assembled'] for r in v),sum(r['assembled_exact'] for r in v),round(sum(r['exposed_parts'] for r in v)/len(v),4),[round(x,4) for x in ci],sep=' | ')
print('\nmonitor minus baseline | auth | wording | pairs | exact assembly pp [CI] | discordance | p | exposed mean difference [CI]')
for base in ['local','keyword_gate']:
 for auth in ['authorized','restricted']:
  for wording in ['keyword','paraphrase']:
   m={r['seed']:r for r in cells[(auth,wording,'monitor')] if r['valid'] is True}
   b={r['seed']:r for r in cells[(auth,wording,base)] if r['valid'] is True}
   seeds=sorted(m.keys() & b.keys())
   d=[int(m[s]['assembled_exact'])-int(b[s]['assembled_exact']) for s in seeds]
   e=[m[s]['exposed_parts']-b[s]['exposed_parts'] for s in seeds]
   plus=sum(x>0 for x in d); minus=sum(x<0 for x in d)
   print(base,auth,wording,len(seeds),round(100*sum(d)/len(d),4),[round(100*x,4) for x in a.boot_ci([[x] for x in d])],f'+{plus}/-{minus}',a.mcnemar_p(plus,minus),round(sum(e)/len(e),4),[round(x,4) for x in a.boot_ci([[x] for x in e])],sep=' | ')
