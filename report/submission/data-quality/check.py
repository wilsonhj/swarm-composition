import sys,json,hashlib,itertools,collections,argparse
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3]);R=ap.parse_args().repo.resolve();E=R/'experiments/composition-gap';sys.path.insert(0,str(E))
import analyze as a, harness as h
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
vcontract=json.loads((R/'docs/handoffs/v2-inputs.json').read_text()); pcontract=json.loads((R/'docs/handoffs/provenance-inputs.json').read_text())
cond={'solo','solo@k5','solo@k12','pipeline','swarm@n4','swarm_noobj@n4','relay_informed','relay_uninformed'}
out={'sources':{},'v2':{},'provenance':{}}
for x in vcontract['files']:
 if x['kind'] not in ('raw','manifest'): continue
 p=R/x['path']; actual=sha(p); assert actual==x['sha256']; out['sources'][x['path']]=actual
 if x['kind']!='raw': continue
 rows=a.load_rows([str(p)]); assert len(rows)==x['rows']
 seeds=set(range(1000,1020 if x['group']=='haiku' else 1010))
 keys=[(r['cond'],r['seed']) for r in rows]; expected=set(itertools.product(cond,seeds))
 assert len(set(keys))==len(keys) and set(keys)==expected
 er=[a.enrich(r) for r in rows]; a.validate_rows(er); assert all(r['valid'] is True for r in er)
 turns=[t for r in rows for t in r['turns']]; group=out['v2'].setdefault(x['group'],{'rows':0,'valid':0,'failed':0,'turns':0,'missing_model_turns':0,'files':[],'strict_neutral_cells':{}})
 group['rows']+=len(rows);group['valid']+=sum(r['valid'] is True for r in er);group['turns']+=len(turns);group['missing_model_turns']+=sum(not t.get('model') for t in turns)
 group['files'].append({'file':x['path'],'grid':len(expected),'unique_keys':len(set(keys)),'logical_calls':len(turns),'sha256':actual})
 if rows[0]['policy']=='strict' and rows[0]['framing']=='neutral':
  for c in ['solo','pipeline','swarm@n4']:
   rr=[r for r in er if r['cond']==c and r['valid'] is True]
   group['strict_neutral_cells'][c]={'n':len(rr),'assembled':sum(r['assembled'] for r in rr),'recoverable':sum(r['recoverable'] for r in rr)}
for x in pcontract['files']:
 if x['kind'] not in ('raw','manifest','protocol'): continue
 p=R/x['path']; assert sha(p)==x['sha256']; out['sources'][x['path']]=sha(p)
p=E/'results/task-provenance/heldout-haiku.jsonl'; raw=a.load_rows([str(p)]); rows=[a.enrich(r) for r in raw]; a.validate_rows(rows)
keys=[(r['cond'],r['authorization'],r['framing'],r['seed']) for r in rows]
expected=set(itertools.product(['local','provenance','monitor','keyword_gate'],['authorized','restricted'],['keyword','paraphrase'],range(3000,3050)))
assert len(keys)==len(set(keys))==len(expected)==800 and set(keys)==expected
turns=[t for r in raw for t in r['turns']]; fails=[{k:r[k] for k in ['cond','authorization','framing','seed','failed_calls']} for r in raw if r['failed_calls']]
pr=out['provenance'];pr.update(rows=len(rows),unique_keys=len(set(keys)),expected_grid=len(expected),valid=sum(r['valid'] is True for r in rows),failed=fails,turns=len(turns),missing_model_turns=sum(not t.get('model') for t in turns),missing_model_success_turns=sum(not t.get('model') and not t.get('failed') for t in turns))
pr['cells']={}
for auth,metric in [('restricted','recoverable'),('authorized','assembled')]:
 for cond_name in ['local','provenance']:
  rs=[r for r in rows if r['authorization']==auth and r['framing']=='paraphrase' and r['cond']==cond_name and r['valid'] is True]; k=sum(r[metric] for r in rs); pr['cells'][f'{auth}|paraphrase|{cond_name}|{metric}']={'events':k,'n':len(rs),'wilson95':a.wilson(k,len(rs))}
contr=a.paired_contrasts(rows,'local');pr['paired']={}
for x in contr:
 g=dict(zip(a.IDENTITY,x['group']))
 if x['cond']=='provenance' and g['framing']=='paraphrase':
  metric='recoverable' if g['authorization']=='restricted' else 'assembled'
  pr['paired'][g['authorization']]={'metric':metric,'pairs':x['n_pairs'],'difference':x[metric][0],'paired_bootstrap95':x[metric][1],'discordant_and_exact_p':x[metric+'_disc']}
lists,words,secret=h.make_task(3000)
pr['seed3000']={'lists':[{'items':ls,'position_1_indexed':i+1,'selected':ls[i]} for ls,i in lists],'target':secret,'conditions':{}}
for c in ['local','provenance']:
 r=next(r for r in raw if r['seed']==3000 and r['cond']==c and r['authorization']=='restricted' and r['framing']=='paraphrase')
 pr['seed3000']['conditions'][c]={'board':r['board'],'raw_responses':[t['raw'] for t in r['turns'] if t['role']!='monitor'],'assembled':a.enrich(r)['assembled'],'recoverable':a.enrich(r)['recoverable']}
out['assessment']={'intended_use':'Illustrative diagrams and reported model-specific descriptive cells, with explicit run and failure limitations', 'verdict':'Suitable for these scoped uses, conditional on recorded limitations; not external or prospective validation', 'findings':[{'severity':'medium','confidence':'high','issue':'One provenance worker call failed; authorized provenance paraphrase valid n is 49, with unknown counterfactual outcome','remediation':'Show valid denominator, failure and bounds; do not impute outcome.'},{'severity':'medium','confidence':'high','issue':'Original v2 runs lack per-turn served-model IDs; Sonnet strict explicit manifest includes two served models','remediation':'Label requested model and mixed original cell; keep verified-model rerun separate on the same seeds.'},{'severity':'medium','confidence':'high','issue':'Rerun uses same task seeds as original, while all Study 2 successful turns have recorded served model','remediation':'Do not count rerun as independent task seeds.'}], 'temporal_scope':'Frozen historic sprint records; later freshness or model drift is outside this scope.'}
out['caveats']=['Run-specific trial keys retain metadata: study/design/backend/model/authorization/policy/framing/run_id/prompt_hash/protocol_hash/condition/seed; study 1 files carry separate run identifiers.', 'Sonnet rerun shares seeds with original strict explicit cell; do not pool as independent seeds. Original manifest lists mixed served models; old turns lack per-call served model metadata.', 'Study 2 one failed worker turn is excluded; retries within logical calls were not recorded. No fresh inference; trusted metadata, one model and fixed synthetic task; future provider behavior and prospective noninspection cannot be independently verified.']
print(json.dumps(out,indent=2))
