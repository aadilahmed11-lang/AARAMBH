import { api } from './api';
import { addQueue, getCache, putCache, getQueue, removeQueue } from './offlineDb';

export const isOnline = () => navigator.onLine;

export async function cacheSnapshot(userId) {
  if (!isOnline()) return getCache('snapshot');
  const r = await api.get(`/v1/features/offline-data/${userId}`);
  const snapshot = { ...r.data, cached_at: new Date().toISOString() };
  await putCache('snapshot', snapshot);
  await putCache('schemes', snapshot.cached_schemes || []);
  await putCache('partners', snapshot.cached_partners || []);
  await putCache('profile', snapshot.user_profile || {});
  await putCache('applications', snapshot.applications || []);
  await putCache('sync_status', snapshot.sync_status || {});
  return snapshot;
}

export async function getOfflineSnapshot() {
  return getCache('snapshot');
}

export async function queueApplication(payload) {
  return addQueue({ type: 'application', payload });
}

export async function syncPending() {
  if (!isOnline()) return { synced: 0, pending: (await getQueue()).length };
  const queue = await getQueue();
  let synced = 0;
  const errors = [];
  for (const item of queue) {
    try {
      if (item.type === 'application') {
        const r = await api.post('/offline/sync', item.payload);
        await putCache(`queued-result-${item.id}`, r.data);
        await removeQueue(item.id);
        synced += 1;
      }
    } catch (e) {
      errors.push(e.response?.data?.detail || e.message || 'Sync failed');
    }
  }
  return { synced, pending: (await getQueue()).length, errors };
}

export async function offlineRecommend(profile, schemeType = 'business') {
  const schemes = ((await getCache('schemes')) || []).filter((s) => s.scheme_type === schemeType && s.active !== false);
  const category = String(profile.category || '').toLowerCase();
  const aliases = {'scheduled caste (sc)':'sc','sc':'sc','scheduled tribe (st)':'st','st':'st','backward class (bc)':'bc','bc':'bc','other backward class (obc)':'obc','obc':'obc','backward class muslim (bcm)':'bcm','bcm':'bcm','economically weaker section (ews)':'ews','ews':'ews','general / other':'general','general':'general'};
  const cat = aliases[category] || category;
  const income = Number(profile.annual_income || 0);
  const amount = Number(profile.loan_amount || profile.course_fee || 0);
  return schemes.map((s) => {
    let score = 20; const matching_factors=[]; const gaps=[];
    const targets = String(s.target_categories || '').split(',').map(x=>aliases[x.trim().toLowerCase()] || x.trim().toLowerCase()).filter(Boolean);
    if (targets.length && !targets.includes('all')) { if (targets.includes(cat)) {score+=25;matching_factors.push('Category matches the scheme target.')} else {score-=25;gaps.push('Category is not listed in the scheme target.')} }
    if (income && s.target_income_max) { if (income <= Number(s.target_income_max)) {score+=15;matching_factors.push('Family income is within the configured limit.')} else {score-=20;gaps.push('Family income is above the configured limit.')} }
    if (amount && (s.min_loan || s.max_loan)) { if ((!s.min_loan || amount>=Number(s.min_loan)) && (!s.max_loan || amount<=Number(s.max_loan))) {score+=15;matching_factors.push('Requested amount fits the configured range.')} else {score-=15;gaps.push('Requested amount is outside the configured range.')} }
    if (String(profile.disability_status||'').toLowerCase()==='yes' && String(s.target_disability||'').toLowerCase()==='yes') {score+=12;matching_factors.push('Disability profile matches the scheme targeting.');}
    const text=[profile.occupation,profile.business_type,profile.business_stage,profile.course_type,profile.education_level,profile.employment_status,profile.state].join(' ').toLowerCase();
    const keywords=String(s.target_keywords||'').split(',').map(x=>x.trim().toLowerCase()).filter(Boolean); const hits=keywords.filter(k=>text.includes(k));
    if(hits.length){score+=Math.min(10,hits.length*3);matching_factors.push('Profile keywords match: '+hits.slice(0,4).join(', ')+'.');}
    if(schemeType==='education' && profile.education_level) {score+=5;matching_factors.push('Education profile is available for matching.');}
    score=Math.max(0,Math.min(100,score));
    return {scheme:s,score,eligible:score>=60,rank:0,reason:(matching_factors.slice(0,4).join(' ')||'Review scheme-specific rules.')+(gaps.length?' Review: '+gaps.slice(0,2).join(' '):''),matching_factors,gaps};
  }).sort((a,b)=>b.score-a.score).slice(0,5).map((x,i)=>({...x,rank:i+1}));
}
