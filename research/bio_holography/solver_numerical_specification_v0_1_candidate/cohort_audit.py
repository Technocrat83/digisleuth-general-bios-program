"""Lineage and batch metadata audit; never grants biological admission."""
from collections import Counter,defaultdict
from math import log

PARTITIONS={'baseline_calibration','baseline_validation','holdout_validation'}
CLUSTER_KEYS=('dam_id','litter_id','harvest_event_id','culture_dish_id')
BATCH_KEYS=('collection_batch_id','acquisition_batch_id','treatment_batch_id')


def identifier(x):
    return isinstance(x,str) and bool(x.strip()) and x==x.strip()


def audit_members(members,require_unseen_batches=False):
    if not isinstance(members,list):raise ValueError('member array required')
    invalid=[];unresolved=[];seen_embryos=set();litter_dams=defaultdict(set)
    groups={k:defaultdict(set) for k in CLUSTER_KEYS}
    batches={k:defaultdict(set) for k in BATCH_KEYS}
    for idx,m in enumerate(members):
        if not isinstance(m,dict):
            invalid.append(f'member_{idx}:object_required')
            continue
        embryo=m.get('embryo_id')
        if not identifier(embryo):unresolved.append(f'member_{idx}:embryo_id_missing')
        elif embryo in seen_embryos:invalid.append(f'duplicate_embryo:{embryo}')
        else:seen_embryos.add(embryo)
        part=m.get('partition')
        if part not in PARTITIONS:invalid.append(f'member_{idx}:partition_invalid')
        if identifier(m.get('litter_id')) and identifier(m.get('dam_id')):
            litter_dams[m['litter_id']].add(m['dam_id'])
        for key in CLUSTER_KEYS:
            value=m.get(key)
            if not identifier(value):unresolved.append(f'member_{idx}:{key}_missing')
            elif part in PARTITIONS:groups[key][value].add(part)
        for key in BATCH_KEYS:
            value=m.get(key)
            if not identifier(value):unresolved.append(f'member_{idx}:{key}_missing')
            elif part in PARTITIONS:batches[key][value].add(part)
    for key,records in groups.items():
        for group,parts in records.items():
            if len(parts)>1:invalid.append(f'cross_partition_cluster:{key}:{group}')
    for litter,dams in litter_dams.items():
        if len(dams)>1:invalid.append(f'inconsistent_litter_dam_binding:{litter}')
    shared=[]
    for key,records in batches.items():
        for batch,parts in records.items():
            if len(parts)>1:shared.append({'field':key,'batch_id':batch,'partitions':sorted(parts)})
    if require_unseen_batches:
        for rec in shared:
            if 'holdout_validation' in rec['partitions']:
                invalid.append(f'unseen_batch_claim_invalid:{rec["field"]}:{rec["batch_id"]}')
    if not members:unresolved.append('cohort_membership_unmaterialized')
    cross=Counter(tuple(m.get(k) if identifier(m.get(k)) else None for k in ('dam_id','collection_batch_id','acquisition_batch_id','treatment_batch_id')) for m in members if isinstance(m,dict))
    batch_counts=Counter(m.get('acquisition_batch_id') for m in members if isinstance(m,dict) and identifier(m.get('acquisition_batch_id')))
    total=sum(batch_counts.values())
    entropy=-sum((v/total)*log(v/total) for v in batch_counts.values()) if total else None
    status='INVALID' if invalid else 'UNRESOLVED' if unresolved else 'VALID_METADATA_ONLY'
    return {
        'metadata_group_audit':status,'invalid':invalid,'unresolved':unresolved,
        'counts':{'embryos':len(seen_embryos),'dams':len(groups['dam_id']),'litters':len(groups['litter_id']),'collection_batches':len(batches['collection_batch_id']),'acquisition_batches':len(batches['acquisition_batch_id']),'treatment_batches':len(batches['treatment_batch_id'])},
        'dam_batch_cross_tab':[{'dam_id':k[0],'collection_batch_id':k[1],'acquisition_batch_id':k[2],'treatment_batch_id':k[3],'record_count':v} for k,v in sorted(cross.items(),key=lambda x:repr(x[0]))],
        'shared_batches':shared,'acquisition_batch_entropy_nats':entropy,
        'entropy_scope':'records with valid acquisition batch IDs only; diagnostic, not independence evidence',
        'biological_independence':'NOT_ESTABLISHED_BY_METADATA_AUDIT',
        'effective_biological_sample_size':None,'admission':'PENDING_ADMISSION',
        'calibration_gate':'HOLD','promotion_authority':False
    }
