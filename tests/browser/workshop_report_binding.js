// Browser-only response fixtures. No physical evidence is written or asserted.
// Run with playwright-cli run-code --filename tests/browser/workshop_report_binding.js.
async (page) => {
  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button',{name:'My bushing v01 · Parametric Physical fit unconfirmed',exact:true}).click();
  let submitted;
  await page.route('**/api/actions',async route=>{
    submitted=route.request().postDataJSON();
    await route.fulfill({json:{job_id:'browser-fixture'}});
  });
  let polls=0;
  await page.route('**/api/jobs/browser-fixture',async route=>{
    polls++;
    await route.fulfill({json:polls<2?{status:'running'}:{status:'complete',result:{status:{physical_fit_claim_allowed:true,fixture_only:true}}}});
  });
  await page.getByText('Retained evidence hashes for inspection',{exact:true}).click();
  await page.getByLabel('Physical evidence SHA-256',{exact:true}).fill('a'.repeat(64));
  await page.getByRole('button',{name:'Inspect status',exact:true}).click();
  if(!(await page.getByRole('button',{name:'My bushing v01 · Parametric Physical fit unconfirmed',exact:true}).isDisabled())) throw Error('Project navigation remained active during job');
  await page.getByRole('status').filter({hasText:'Complete.'}).waitFor();
  if(submitted.payload.expected_physical_evidence_sha256!=='a'.repeat(64)) throw Error('Retained anchor was not submitted');
  if(!(await page.locator('.pill').innerText()).startsWith('Saved synthetic_browser_bushing v01: physical fit confirmed')) throw Error('Missing saved-version binding');
  await page.getByLabel('Material',{exact:true}).fill('PLA');
  if(!(await page.locator('.pill').innerText()).startsWith('Saved synthetic_browser_bushing v01:')) throw Error('Draft edit ambiguously relabelled the saved result');
  await page.getByLabel('Version',{exact:true}).fill('v02');
  if((await page.locator('.pill').innerText())!=='Physical fit unconfirmed') throw Error('Confirmation leaked to draft v02');
  await page.route('**/api/specs',route=>route.fulfill({json:{spec_path:'owner-validation/local/workshop/synthetic_browser_bushing/v02/spec.json',changes:[]}}));
  await page.getByRole('button',{name:'Save new version',exact:true}).click();
  await page.getByRole('status').filter({hasText:'Saved immutable version.'}).waitFor();
  if((await page.locator('.pill').innerText())!=='Physical fit unconfirmed') throw Error('Confirmation leaked to saved v02');
  await page.getByRole('button',{name:'My bushing v01 · Parametric Physical fit unconfirmed',exact:true}).click();
  if((await page.locator('.pill').innerText())!=='Physical fit unconfirmed') throw Error('Late/stale report survived selection');
  await page.unroute('**/api/actions'); await page.unroute('**/api/jobs/browser-fixture'); await page.unroute('**/api/specs');
  await page.evaluate(()=>localStorage.removeItem('workshop-evidence-anchors'));
  await page.goto('http://127.0.0.1:8765');
  console.log('Mocked UI evidence anchor, active navigation guard, saved/draft binding and save/selection regressions passed. No physical record created.');
}
