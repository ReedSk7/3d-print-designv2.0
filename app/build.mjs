// Build only from local, locked dependencies. Runtime never calls this script.
import { createHash } from 'node:crypto';
import { lstat, readdir, readFile, writeFile, unlink, rename } from 'node:fs/promises';
import { dirname, join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'vite';

const root = dirname(fileURLToPath(import.meta.url));
const dist = join(root, 'dist');
const record = join(dist, 'workshop-build.json');

async function plainPath(path) {
  const stat = await lstat(path);
  if (stat.isSymbolicLink()) throw new Error('App source/output cannot contain symlinks or junctions.');
  return stat;
}

async function snapshot(directory, excluded) {
  await plainPath(directory);
  const files = {};
  async function visit(folder) {
    for (const name of (await readdir(folder)).sort()) {
      const path = join(folder, name);
      const key = relative(directory, path).split(sep).join('/');
      if (excluded.has(key)) continue;
      if (key.includes('\\') || key.includes(':') || key.split('/').some(part => !part || part === '.' || part === '..')) {
        throw new Error('App files must use safe relative paths.');
      }
      const stat = await plainPath(path);
      if (stat.isDirectory()) await visit(path);
      else if (stat.isFile()) files[key] = createHash('sha256').update(await readFile(path)).digest('hex');
      else throw new Error('App source/output must contain only regular files.');
    }
  }
  await visit(directory);
  return files;
}

// A failed or interrupted build must not leave a previously valid readiness stamp.
await plainPath(root);
try { await plainPath(dist); } catch (error) { if (error.code !== 'ENOENT') throw error; }
try { await unlink(record); } catch (error) { if (error.code !== 'ENOENT') throw error; }
const inputs = await snapshot(root, new Set(['node_modules', 'dist']));
await build({ root, build: { outDir: dist, emptyOutDir: true, manifest: true } });
if (JSON.stringify(inputs) !== JSON.stringify(await snapshot(root, new Set(['node_modules', 'dist'])))) {
  throw new Error('App inputs changed during the build. Run the build again.');
}
const assets = await snapshot(dist, new Set(['workshop-build.json']));
if (!assets['index.html'] || !assets['.vite/manifest.json']) throw new Error('Vite did not emit a complete app.');
const temporary = join(dist, 'workshop-build.json.tmp');
await writeFile(temporary, JSON.stringify({ schema_version: 1, inputs, assets }, null, 2) + '\n', { flag: 'wx' });
await rename(temporary, record);
console.log(`Recorded ${Object.keys(inputs).length} source inputs and ${Object.keys(assets).length} emitted assets.`);
