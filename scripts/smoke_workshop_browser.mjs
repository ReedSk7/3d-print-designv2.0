#!/usr/bin/env node
/**
 * Real production UI + real loopback bridge; disposable synthetic data only.
 * Prerequisites (app/): npm ci; npm run build; npx playwright install chromium.
 * Run: node scripts/smoke_workshop_browser.mjs --python <project-python>
 * Offline local fallback: WORKSHOP_SMOKE_CHROMIUM=<installed-Chromium-executable>.
 * CI leaves that unset to use the browser installed by pinned Playwright.
 * No worker actions: Windows generation/cancellation have separate platform CI.
 */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtemp, readFile, rm} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {tmpdir} from 'node:os';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const repository = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
if (args.length !== 0 && (args.length !== 2 || args[0] !== '--python')) {
  throw new Error('Usage: node scripts/smoke_workshop_browser.mjs [--python <project-python>]');
}
const python = args[1] || process.env.PYTHON || 'python';
const require = createRequire(join(repository, 'app/package.json'));
const {chromium} = require('playwright');
const root = await mkdtemp(join(tmpdir(), 'print-workshop-browser-smoke-'));
let bridge;
let browser;
let bridgeOutput = '';
let cleanupPromise;

const delay = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));
async function cleanup() {
  if (cleanupPromise) return cleanupPromise;
  cleanupPromise = (async () => {
    if (browser) await Promise.race([browser.close().catch(() => {}), delay(3000)]);
    if (bridge?.pid && bridge.exitCode === null && bridge.signalCode === null) {
      bridge.stdin.end();
      await Promise.race([once(bridge, 'exit'), delay(3000)]);
      if (bridge.exitCode === null && bridge.signalCode === null) {
        bridge.kill('SIGKILL');
        await Promise.race([once(bridge, 'exit'), delay(2000)]);
      }
    }
    await rm(root, {recursive: true, force: true, maxRetries: 3, retryDelay: 100});
  })();
  return cleanupPromise;
}

// This absolute bound also covers a stalled browser launch or cleanup.
const hardDeadline = setTimeout(() => {
  bridge?.kill('SIGKILL');
  console.error('Browser smoke exceeded its 110-second absolute deadline.');
  rm(root, {recursive: true, force: true}).finally(() => process.exit(1));
}, 110_000);
for (const signal of ['SIGINT', 'SIGTERM']) {
  process.once(signal, () => cleanup().finally(() => process.exit(1)));
}

async function startBridge() {
  bridge = spawn(python, ['-B', join(repository, 'scripts/_workshop_browser_fixture.py'), root], {
    cwd: repository,
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true,
  });
  bridge.stdin.on('error', error => { bridgeOutput = (bridgeOutput + error.message).slice(-12_000); });
  const ready = new Promise((resolveReady, reject) => {
    const timer = setTimeout(() => reject(new Error('Synthetic bridge startup timed out.')), 20_000);
    const finish = (error, value) => {
      clearTimeout(timer);
      error ? reject(error) : resolveReady(value);
    };
    bridge.once('error', error => finish(error));
    bridge.once('exit', code => finish(new Error(`Synthetic bridge exited (${code}): ${bridgeOutput}`)));
    bridge.stderr.on('data', chunk => { bridgeOutput = (bridgeOutput + chunk).slice(-12_000); });
    let stdout = '';
    bridge.stdout.on('data', chunk => {
      stdout += chunk;
      const newline = stdout.indexOf('\n');
      if (newline >= 0) {
        try { finish(null, JSON.parse(stdout.slice(0, newline)).url); }
        catch (error) { finish(error); }
      }
    });
  });
  return ready;
}

async function exercise() {
  const url = await startBridge();
  assert.match(url, /^http:\/\/127\.0\.0\.1:\d+$/);
  browser = await chromium.launch({
    headless: true,
    timeout: 20_000,
    executablePath: process.env.WORKSHOP_SMOKE_CHROMIUM || undefined,
  });
  const context = await browser.newContext({viewport: {width: 1440, height: 1100}, acceptDownloads: true});
  const page = await context.newPage();
  page.setDefaultTimeout(7000);
  page.setDefaultNavigationTimeout(15_000);
  const errors = [];
  const unexpectedRequests = [];
  page.on('pageerror', error => errors.push(`pageerror: ${error.message}`));
  page.on('console', message => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`);
  });
  page.on('request', request => {
    if (!request.url().startsWith(`${url}/`) || request.url().includes('/api/actions')) {
      unexpectedRequests.push(request.url());
    }
  });
  page.on('response', response => {
    if (response.status() >= 400) errors.push(`HTTP ${response.status()}: ${response.url()}`);
  });
  await page.goto(url, {waitUntil: 'networkidle'});
  await page.getByRole('heading', {name: 'Print Workshop', exact: true}).waitFor();
  await page.getByRole('button', {name: /Synthetic browser saved design/}).waitFor();
  const cards = page.locator('.project-list > button');
  assert.equal(await cards.count(), 4, 'Valid, corrupt, and both differing legacy records must remain visible.');

  // A damaged catalog record must be actionable without becoming an editable spec.
  await cards.filter({hasText: 'synthetic browser corrupt'}).click();
  await page.getByRole('heading', {name: 'Record needs attention'}).waitFor();
  assert.match(await page.locator('main').innerText(), /synthetic_browser_corrupt\/v01\/spec\.json/);
  assert.match(await page.getByRole('alert').innerText(), /Keep the original files/);
  assert.equal(await page.getByRole('button', {name: 'Save new version', exact: true}).count(), 0);
  assert.equal(await page.getByRole('button', {name: 'Generate source + STL', exact: true}).count(), 0);

  // Same stored project ID, distinct source locations: both real downloads survive.
  for (const [location, route, size] of [
    ['projects/synthetic_browser_legacy', '/legacy/', 1],
    ['owner-validation/local/workshop/legacy/synthetic_browser_legacy', '/local-legacy/', 2],
  ]) {
    await cards.filter({hasText: location}).click();
    const source = page.locator(`a[href="${route}synthetic_browser_legacy/source/synthetic.scad"]`);
    await source.waitFor();
    assert.equal(await page.locator('.project-list > button.selected').count(), 1);
    assert.match(await page.locator('.project-list > button.selected').innerText(), new RegExp(location));
    assert.match(await page.locator('main').innerText(), /not been migrated/);
    const downloaded = page.waitForEvent('download');
    await source.click();
    const download = await downloaded;
    assert.equal(await download.failure(), null);
    assert.match(await readFile(await download.path(), 'utf8'), new RegExp(`cube\\(${size}\\)`));
  }

  await page.getByLabel('Search designs').fill('Synthetic browser saved design');
  await page.waitForFunction(() => document.querySelectorAll('.project-list > button').length === 1);
  await cards.first().click();
  await page.getByLabel('Name', {exact: true}).waitFor();
  assert.equal(await page.getByLabel('Project ID', {exact: true}).inputValue(), 'synthetic_browser_saved');
  assert.equal(await page.getByLabel('Exact part or target').inputValue(), 'Synthetic browser fixture; no physical-fit claim.');
  const originalPath = join(root, 'owner-validation/local/workshop/synthetic_browser_saved/v01/spec.json');
  const original = await readFile(originalPath);
  await page.getByLabel('Version', {exact: true}).fill('v02');
  await page.getByLabel('Exact part or target').fill('Synthetic browser revision; no physical test performed.');
  const saved = page.waitForResponse(response => response.url() === `${url}/api/specs` && response.request().method() === 'POST');
  await page.getByRole('button', {name: 'Save new version', exact: true}).click();
  assert.equal((await saved).status(), 201);
  await page.getByRole('status').filter({hasText: 'Saved immutable version.'}).waitFor();
  assert.deepEqual(await readFile(originalPath), original, 'Saving a revision changed the original synthetic specification.');
  const revision = JSON.parse(await readFile(join(root, 'owner-validation/local/workshop/synthetic_browser_saved/v02/spec.json'), 'utf8'));
  assert.equal(revision.project.version, 'v02');
  assert.equal(revision.physical_verification.status, 'not_confirmed');

  // Reload proves the real bridge persisted the selected specification and context.
  await page.reload({waitUntil: 'networkidle'});
  const revisionCard = page.getByRole('button', {name: /Synthetic browser saved design/}).filter({hasText: 'v02'});
  await revisionCard.click();
  assert.equal(await page.getByLabel('Exact part or target').inputValue(), 'Synthetic browser revision; no physical test performed.');
  await page.getByLabel('Part family').selectOption('round_adapter');
  await page.getByRole('button', {name: 'New design', exact: true}).click();
  assert.equal(await page.getByLabel('Project ID', {exact: true}).inputValue(), 'my_round_adapter');
  assert.equal(await page.getByRole('button', {name: 'Generate source + STL', exact: true}).count(), 0);
  assert.match(await page.getByRole('status').innerText(), /Example dimensions are starters/);

  const refreshedJobs = page.waitForResponse(response => response.url() === `${url}/api/jobs`);
  await page.getByRole('button', {name: 'Refresh job history'}).click();
  assert.equal((await refreshedJobs).status(), 200);
  await page.getByText('No jobs recorded.', {exact: true}).waitFor();
  assert.deepEqual(unexpectedRequests, [], 'Smoke requested external resources or a generation worker action.');
  assert.deepEqual(errors, [], 'Browser console, page, or HTTP errors occurred.');
  const bridgeExited = once(bridge, 'exit');
  const stopped = page.waitForResponse(response => response.url() === `${url}/api/stop`);
  await page.getByRole('button', {name: 'Stop workshop', exact: true}).click();
  assert.equal((await stopped).status(), 200);
  await page.getByRole('status').filter({hasText: 'Workshop stopped.'}).waitFor();
  let shutdownDeadline;
  try {
    const result = await Promise.race([
      bridgeExited,
      new Promise((_, reject) => {
        shutdownDeadline = setTimeout(() => reject(new Error('Stop workshop did not stop the bridge within 5 seconds.')), 5000);
      }),
    ]);
    assert.deepEqual(result, [0, null], 'Workshop bridge did not exit cleanly after Stop workshop.');
  } finally { clearTimeout(shutdownDeadline); }
  assert.deepEqual(errors, []);
}

let deadline;
try {
  await Promise.race([
    exercise(),
    new Promise((_, reject) => { deadline = setTimeout(() => reject(new Error('Browser smoke exceeded 90 seconds.')), 90_000); }),
  ]);
} catch (error) {
  console.error(error.stack || error);
  if (bridgeOutput) console.error(bridgeOutput);
  process.exitCode = 1;
} finally {
  clearTimeout(deadline);
  try { await cleanup(); }
  finally { clearTimeout(hardDeadline); }
}
if (process.exitCode !== 1) {
  console.log('PASS: synthetic built-UI catalog, diagnostics, source navigation, immutable save, reload, and shutdown; no browser errors. No generation or physical-fit evidence.');
}
