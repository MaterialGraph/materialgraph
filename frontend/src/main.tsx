import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { useMaterialExplorer } from './useMaterialExplorer';
import { SourcePicker } from './SourcePicker';
import { MaterialIdentity } from './MaterialIdentity';
import { CandidateList } from './CandidateList';
import { ObjectiveInvestigation } from './objective/ObjectiveInvestigation';
import { PropertyComparisonWorkspace, WorkflowComparison, RestoredColumns } from './comparison/PropertyComparison';
import type { ComparisonLaunchContext } from './comparison/launch';
import { parseComparison, serializeComparison, type ComparisonRoute } from './comparison/routing';
import type { ObjectiveDraft } from './objective/request';
import './style.css';

export function App() {
  const explorer = useMaterialExplorer();
  const { selected } = explorer;
  const [launch, setLaunch] = useState<ComparisonLaunchContext | null>(null);
  const [parsed, setParsed] = useState(() => parseComparison(location.search));
  const [activeRoute, setActiveRoute] = useState<ComparisonRoute | null>(null);
  const [coldEntry, setColdEntry] = useState<{ workflow: ComparisonRoute['workflow']; objective: ObjectiveDraft | null; inputsAvailable: boolean; sequence: number } | null>(null);
  const [copied, setCopied] = useState('');
  const selectSource = (id: number) => { setColdEntry(null); explorer.select(id); };
  const inAppOrigin = useRef(false);
  const comparisonRoute = parsed.kind === 'validComparison' ? parsed.route : activeRoute;
  const comparisonVisible = parsed.kind === 'validComparison' && comparisonRoute !== null;
  const comparisonHeading = useRef<HTMLHeadingElement>(null);
  const discoveryHeading = useRef<HTMLDivElement>(null);
  const objectiveHeading = useRef<HTMLDivElement>(null);
  useEffect(() => { if (comparisonVisible) comparisonHeading.current?.focus(); }, [comparisonVisible]);
  useEffect(() => {
    const onPop = () => {
      const next = parseComparison(location.search);
      if (next.kind === 'validComparison' && (!activeRoute || serializeComparison(next.route) !== serializeComparison(activeRoute))) inAppOrigin.current = false;
      setParsed(next);
      setCopied('');
    };
    addEventListener('popstate', onPop);
    return () => removeEventListener('popstate', onPop);
  }, [activeRoute]);
  function beginComparison(nextLaunch: ComparisonLaunchContext, route: ComparisonRoute) {
    const url = serializeComparison(route);
    history.pushState(null, '', url);
    inAppOrigin.current = true;
    setActiveRoute(route);
    setLaunch(nextLaunch);
    setParsed({kind:'validComparison',route});
    setCopied('');
  }
  function returnToWorkflow() {
    const target = launch?.originWorkflow === 'objective' ? objectiveHeading : discoveryHeading;
    history.replaceState(null, '', `/?material=${comparisonRoute?.source ?? selected}`);
    setParsed({kind:'notComparison'});
    setLaunch(null);
    setActiveRoute(null);
    inAppOrigin.current = false;
    requestAnimationFrame(() => target.current?.focus());
  }
  function openColdWorkflow() {
    if (!comparisonRoute) return;
    const context = comparisonRoute.context;
    if (context?.kind === 'discovery') { explorer.setAvoid(context.avoid_element ?? ''); explorer.setPrefer(context.prefer_element ?? ''); }
    const objective = context?.kind === 'objective' ? context.request : null;
    const draft: ObjectiveDraft | null = objective ? {
      avoid: objective.objective.avoid_elements.join(', '), prefer: objective.objective.prefer_elements.join(', '),
      preserve: objective.objective.preserve_elements.join(', '), family: (objective.objective.target_family ?? '') as ObjectiveDraft['family'],
      hops: objective.objective.max_hops, limit: objective.limit, objectiveLimit: objective.objective.limit, mode: objective.mode,
      lowerCriticality: objective.objective.prefer_lower_criticality, requireStable: objective.objective.require_stable_materials,
    } : null;
    setColdEntry(previous => ({workflow:comparisonRoute.workflow,objective:draft,inputsAvailable:context !== null,sequence:(previous?.sequence ?? 0)+1}));
    history.pushState(null, '', `/?material=${comparisonRoute.source}`);
    explorer.restoreEntry(comparisonRoute.source);
    setParsed({kind:'notComparison'}); setLaunch(null); setActiveRoute(null); inAppOrigin.current = false;
    requestAnimationFrame(() => (comparisonRoute.workflow === 'objective' ? objectiveHeading : discoveryHeading).current?.focus());
  }
  async function copyLink() {
    if (!comparisonRoute) return;
    try { await navigator.clipboard.writeText(`${location.origin}${serializeComparison(comparisonRoute)}`); setCopied('Comparison link copied.'); }
    catch { setCopied('Could not copy comparison link.'); }
  }
  const invalid = parsed.kind === 'invalidComparison';
  return <div className="shell">
    <header><div className="brand">Material<span>Graph</span><small>Research workspace / 01</small></div><div className="headerNote">MATERIAL EXPLORER <span>·</span> READ ONLY</div></header>
    <div className="intro"><p className="eyebrow">EXPLORE THE MATERIAL LANDSCAPE</p><h1>Start with a material.<br/><em>Follow the evidence.</em></h1><p>Select a source identity, inspect available properties, then explore explainable candidates. Scores describe encoded rules, not experimental validation.</p></div>
    <main className="layout" hidden={comparisonVisible || invalid}>
      <SourcePicker {...explorer} select={selectSource}/>
      <section className="workspace">
        {!selected && <div className="panel welcome"><span className="eyebrow">A PLACE TO BEGIN</span><h2>Select a material to open its workspace.</h2><p>Each source identity stays distinct, even when two materials share a formula.</p></div>}
        <MaterialIdentity {...explorer}/>
        {coldEntry && <p role="status">No investigation results are contained in this link. Run the investigation to see current results.{!coldEntry.inputsAvailable && ' Investigation inputs unavailable in this link.'}</p>}
        <div ref={discoveryHeading} tabIndex={-1}><CandidateList key={`${explorer.detail?.id ?? 0}:${coldEntry?.sequence ?? 0}`} {...explorer} select={selectSource} onCompare={beginComparison}/></div>
        <div ref={objectiveHeading} tabIndex={-1}>{explorer.detail && <ObjectiveInvestigation key={`${explorer.detail.id}:${coldEntry?.sequence ?? 0}`} materialId={explorer.detail.id} initialInputs={coldEntry?.workflow === 'objective' ? coldEntry.objective : null} onCompare={beginComparison}/>}</div>
        <PropertyComparisonWorkspace/>
      </section>
    </main>
    {invalid && <main role="alert"><h1>Invalid comparison link. Check the link or start a new comparison.</h1><button type="button" onClick={() => { history.pushState(null,'','/'); setParsed({kind:'notComparison'}); }}>Open MaterialGraph workspace</button></main>}
    {comparisonVisible && <main className="workflowComparison" aria-label="Workflow property comparison"><h1 ref={comparisonHeading} tabIndex={-1}>Comparison from {comparisonRoute.workflow === 'objective' ? 'Objective Investigation' : 'Candidate Discovery'}</h1>
      {inAppOrigin.current && launch ? <button type="button" onClick={returnToWorkflow}>Return to {comparisonRoute.workflow === 'objective' ? 'Objective Investigation' : 'Candidate Discovery'}</button> : <button type="button" onClick={openColdWorkflow}>Open {comparisonRoute.workflow === 'objective' ? 'Objective Investigation' : 'Candidate Discovery'} with these inputs</button>}
      <button type="button" onClick={() => void copyLink()}>Copy comparison link</button><small>Restores these materials and recorded inputs; current values are fetched when the link is opened.</small>{copied && <p role="status">{copied}</p>}
      {!inAppOrigin.current && <p>This link restores material identities and recorded investigation context on this MaterialGraph instance. Property values are fetched again and may have changed.</p>}
      {!comparisonRoute.context && <p>Investigation context unavailable.</p>}
      {!inAppOrigin.current && comparisonRoute.workflow === 'objective' && <p>Recorded Objective request; previous rank and chain membership unavailable from this link.</p>}
      {!inAppOrigin.current && comparisonRoute.workflow === 'discovery' && <p>Selected for comparison with these recorded investigation inputs; current result membership has not been checked.</p>}
      {launch && inAppOrigin.current ? <WorkflowComparison launch={launch}/> : <RestoredComparison route={comparisonRoute}/>}
    </main>}
    <footer>MaterialGraph · Evidence and limits stay visible.</footer>
  </div>;
}

function RestoredComparison({route}:{route:ComparisonRoute}) {
  const ctx = route.context;
  const text = ctx?.kind === 'discovery' ? `Applied Avoid: ${ctx.avoid_element ?? 'none'}; applied Prefer: ${ctx.prefer_element ?? 'none'}; limit: ${ctx.limit}; substitution paths: no.` : ctx?.kind === 'objective' ? `Submitted Objective request: ${JSON.stringify(ctx.request)}.` : undefined;
  return <RestoredColumns route={route} context={text}/>;
}

const appRoot = document.getElementById('root');
if (appRoot) createRoot(appRoot).render(<React.StrictMode><App/></React.StrictMode>);
