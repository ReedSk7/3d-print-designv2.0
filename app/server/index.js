import express from "express";
import fs from "node:fs/promises";
import fsSync from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const appRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(appRoot, "..");
const dataDir = path.join(appRoot, "data");
const projectsJsonPath = path.join(dataDir, "projects.json");
const settingsJsonPath = path.join(dataDir, "settings.json");
const repoProjectsDir = path.join(repoRoot, "projects");

const app = express();
const port = Number(process.env.DASHBOARD_API_PORT || 4177);

// FIX #5: Caching for file detection to prevent race conditions
const fileStatusCache = new Map();
const CACHE_TTL_MS = 500;

const statuses = [
  "intake",
  "measuring",
  "modeling",
  "review",
  "exported",
  "printed",
  "delivered",
  "archived"
];

const taskModes = [
  "original_product_design",
  "reference_based_reconstruction",
  "mesh_cleanup_and_remodel"
];

const checklistKeys = [
  "fitsBuildVolume",
  "materialSelected",
  "orientationConsidered",
  "supportPlanNoted",
  "wallThicknessAcceptable",
  "holesHaveClearance",
  "snapsReviewed",
  "stressAreasReinforced",
  "sharpCornersSoftened",
  "overhangsReviewed",
  "bedContactAcceptable",
  "criticalInterfacesProtected",
  "measurementsRecorded",
  "lowConfidenceDocumented",
  "stlExported",
  "previewRendered",
  "manifestCreated",
  "reviewReportCreated"
];

app.use(express.json({ limit: "1mb" }));

async function ensureDataFiles() {
  await fs.mkdir(dataDir, { recursive: true });
  if (!fsSync.existsSync(projectsJsonPath)) {
    await fs.writeFile(projectsJsonPath, "[]\n", "utf8");
  }
  if (!fsSync.existsSync(settingsJsonPath)) {
    await fs.writeFile(
      settingsJsonPath,
      JSON.stringify(
        {
          statuses,
          taskModes,
          printers: {
            "Bambu Lab P2S": [256, 256, 256],
            "Qidi XPlus 3": [280, 280, 270],
            "Qidi XPlus 3 Pro": [280, 280, 270],
            "Ender 3 Pro": [220, 220, 250]
          },
          nsfwModels: [
            "sd-v1.5-inpainting safetensors [sha256:0ec8f8585b]",
            "sd-v1.5 safetensors",
            "sd-v2.1 safetensors",
            "sd-xl safetensors"
          ]
        },
        null,
        2
      ),
      "utf8"
    );
  }
}

async function readJson(filePath, fallback) {
  try {
    const raw = await fs.readFile(filePath, "utf8");
    return JSON.parse(raw);
  } catch (error) {
    if (error.code === "ENOENT") {
      return fallback;
    }
    throw error;
  }
}

async function writeJson(filePath, value) {
  const tempPath = `${filePath}.tmp`;
  await fs.writeFile(tempPath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  await fs.rename(tempPath, filePath);
}

function nowIso() {
  return new Date().toISOString();
}

function normalizeProjectStem(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "");
}

// FIX #9: Improved titleFromStem to handle empty stems
function titleFromStem(stem) {
  if (!stem) return "Unnamed Project";
  const title = stem
    .split("_")
    .filter(Boolean)
    .map((part) => part[0]?.toUpperCase() + part.slice(1))
    .join(" ");
  return title || "Unnamed Project";
}

function repoRelative(absPath) {
  return path.relative(repoRoot, absPath).replaceAll(path.sep, "/");
}

async function pathExists(absPath) {
  try {
    await fs.access(absPath);
    return true;
  } catch {
    return false;
  }
}

async function listMatchingFiles(dirPath, matcher) {
  if (!(await pathExists(dirPath))) {
    return [];
  }
  const entries = await fs.readdir(dirPath, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isFile() && matcher(entry.name))
    .map((entry) => path.join(dirPath, entry.name))
    .sort((a, b) => a.localeCompare(b));
}

// FIX #2: Version regex now matches single-digit versions
function extractVersion(fileName) {
  const match = fileName.match(/_v(\d+)(?:_[a-z0-9_]+)?\.[a-z0-9]+$/i);
  return match ? `v${Number(match[1]).toString().padStart(2, "0")}` : "v01";
}

function newestVersionFromFiles(files) {
  const versions = files
    .map((file) => extractVersion(path.basename(file)))
    .map((version) => Number(version.slice(1)))
    .filter((value) => Number.isFinite(value));
  if (!versions.length) {
    return "v01";
  }
  return `v${Math.max(...versions).toString().padStart(2, "0")}`;
}

async function detectProjectFiles(project) {
  const stem = project.projectStem;
  const projectDir = path.join(repoProjectsDir, stem);
  const sourceDir = path.join(projectDir, "source");
  const exportsDir = path.join(projectDir, "exports");
  const notesDir = path.join(projectDir, "notes");
  const previewsDir = path.join(projectDir, "previews");

  const sourceFiles = await listMatchingFiles(sourceDir, (name) => name.endsWith(".scad"));
  const stlFiles = await listMatchingFiles(exportsDir, (name) => name.endsWith(".stl"));
  const notesFiles = await listMatchingFiles(notesDir, (name) => name.endsWith("_notes.md"));
  const manifestFiles = await listMatchingFiles(notesDir, (name) => name.endsWith("_manifest.md"));
  const reviewReportFiles = await listMatchingFiles(notesDir, (name) => name.endsWith("_review_report.md"));
  const printabilityFiles = await listMatchingFiles(notesDir, (name) => name.endsWith("_printability_review.md"));
  const releaseFiles = await listMatchingFiles(notesDir, (name) => name.endsWith("_release_notes.md"));
  const previewFiles = await listMatchingFiles(previewsDir, (name) => name.endsWith(".png"));
  const version = newestVersionFromFiles(sourceFiles);

  const hasScad = sourceFiles.length > 0;
  const hasStl = stlFiles.length > 0;
  const hasPreviews = previewFiles.length > 0;
  const hasNotes = notesFiles.length > 0;
  const hasManifest = manifestFiles.length > 0;
  const hasReviewReport = reviewReportFiles.length > 0;

  const originalDesignComplete =
    project.taskMode === "original_product_design" &&
    hasScad &&
    hasStl &&
    hasPreviews &&
    hasNotes &&
    hasManifest &&
    hasReviewReport;
  const reconstructionComplete =
    project.taskMode !== "original_product_design" &&
    hasScad &&
    hasStl &&
    hasPreviews &&
    hasNotes &&
    hasManifest &&
    hasReviewReport;

  const expectedFolders = [
    `projects/${stem}/source`,
    `projects/${stem}/exports`,
    `projects/${stem}/notes`,
    `projects/${stem}/previews`,
    `projects/${stem}/references/measured`,
    `projects/${stem}/references/public`,
    `projects/${stem}/references/paid`
  ];

  return {
    projectDir: repoRelative(projectDir),
    version,
    expectedFolders,
    files: {
      source: sourceFiles.map(repoRelative),
      stl: stlFiles.map(repoRelative),
      notes: notesFiles.map(repoRelative),
      manifests: manifestFiles.map(repoRelative),
      reviewReports: reviewReportFiles.map(repoRelative),
      printabilityReviews: printabilityFiles.map(repoRelative),
      releaseNotes: releaseFiles.map(repoRelative),
      previews: previewFiles.map(repoRelative)
    },
    hasScad,
    hasStl,
    hasPreviews,
    hasNotes,
    hasManifest,
    hasReviewReport,
    verificationStatus: originalDesignComplete || reconstructionComplete ? "VERIFIED" : "NOT VERIFIED"
  };
}

// FIX #5: Wrapper with caching to prevent race conditions
async function detectProjectFilesWithCache(project) {
  const cacheKey = project.projectStem;
  const cached = fileStatusCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
    return cached.data;
  }
  const data = await detectProjectFiles(project);
  fileStatusCache.set(cacheKey, { data, timestamp: Date.now() });
  return data;
}

function defaultChecklist() {
  return Object.fromEntries(checklistKeys.map((key) => [key, false]));
}

function defaultQuote() {
  return {
    designComplexity: "simple",
    estimatedPrintHours: "",
    estimatedMaterialGrams: "",
    materialCostEstimate: "",
    designFeeEstimate: "",
    printFeeEstimate: "",
    totalEstimate: "",
    customerNotes: ""
  };
}

function normalizeRecord(raw) {
  return {
    id: raw.id,
    projectName: raw.projectName,
    projectStem: raw.projectStem,
    customer: raw.customer || "",
    description: raw.description || "",
    taskMode: raw.taskMode || "original_product_design",
    printer: raw.printer || "Bambu Lab P2S",
    material: raw.material || "PETG",
    status: raw.status || "intake",
    createdAt: raw.createdAt || nowIso(),
    updatedAt: raw.updatedAt || nowIso(),
    supportFreePreferred: Boolean(raw.supportFreePreferred),
    functionalPart: Boolean(raw.functionalPart),
    replacementPart: Boolean(raw.replacementPart),
    needsExactFit: Boolean(raw.needsExactFit),
    measurementsNotes: raw.measurementsNotes || "",
    referenceNotes: raw.referenceNotes || "",
    protectedInterfaces: raw.protectedInterfaces || "",
    lowConfidenceZones: raw.lowConfidenceZones || "",
    customerDeadline: raw.customerDeadline || "",
    privateNotes: raw.privateNotes || "",
    dimensions: raw.dimensions || { width: "", depth: "", height: "" },
    printabilityChecklist: { ...defaultChecklist(), ...(raw.printabilityChecklist || {}) },
    quote: { ...defaultQuote(), ...(raw.quote || {}) },
    commandHistory: raw.commandHistory || []
  };
}

async function readProjectRecords() {
  await ensureDataFiles();
  const records = await readJson(projectsJsonPath, []);
  return records.map(normalizeRecord);
}

async function writeProjectRecords(records) {
  await writeJson(projectsJsonPath, records.map(normalizeRecord));
}

async function projectRecordsWithDetectedFolders() {
  const records = await readProjectRecords();
  const byStem = new Map(records.map((record) => [record.projectStem, record]));
  const allProjects = [...records];

  if (await pathExists(repoProjectsDir)) {
    const entries = await fs.readdir(repoProjectsDir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory() || entry.name === "_template" || byStem.has(entry.name)) {
        continue;
      }
      const folderPath = path.join(repoProjectsDir, entry.name);
      const stats = await fs.stat(folderPath);
      allProjects.push(
        normalizeRecord({
          id: `folder:${entry.name}`,
          projectName: titleFromStem(entry.name),
          projectStem: entry.name,
          customer: "",
          taskMode: "original_product_design",
          printer: "",
          material: "",
          status: "review",
          createdAt: stats.birthtime.toISOString(),
          updatedAt: stats.mtime.toISOString()
        })
      );
    }
  }

  const enriched = [];
  for (const project of allProjects) {
    enriched.push({ ...project, fileStatus: await detectProjectFilesWithCache(project) });
  }
  return enriched.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

async function findProject(projectId) {
  const projects = await projectRecordsWithDetectedFolders();
  return projects.find((project) => project.id === projectId || project.projectStem === projectId);
}

async function updateProjectRecord(projectId, patch) {
  const records = await readProjectRecords();
  const index = records.findIndex((record) => record.id === projectId || record.projectStem === projectId);
  if (index < 0) {
    return null;
  }
  records[index] = normalizeRecord({ ...records[index], ...patch, updatedAt: nowIso() });
  await writeProjectRecords(records);
  return records[index];
}

// FIX #8: Improved quote escaping in formatCommand
function formatCommand(args) {
  return args
    .map((part) => {
      if (/\s/.test(part)) {
        // Escape internal quotes
        const escaped = part.replace(/"/g, '\\"');
        return `"${escaped}"`;
      }
      return part;
    })
    .join(" ");
}

function runCommand(args, cwd = repoRoot) {
  return new Promise((resolve) => {
    const startedAt = Date.now();
    const child = spawn(args[0], args.slice(1), {
      cwd,
      shell: false,
      windowsHide: true
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", (error) => {
      resolve({
        command: formatCommand(args),
        stdout,
        stderr: `${stderr}${error.message}`,
        exitCode: -1,
        durationMs: Date.now() - startedAt,
        ok: false
      });
    });
    child.on("close", (exitCode) => {
      resolve({
        command: formatCommand(args),
        stdout,
        stderr,
        exitCode: exitCode ?? -1,
        durationMs: Date.now() - startedAt,
        ok: exitCode === 0
      });
    });
  });
}

function relativeToAbsolute(relativePath) {
  return path.join(repoRoot, relativePath.replaceAll("/", path.sep));
}

function latestScadPath(project) {
  const files = project.fileStatus?.files?.source || [];
  if (!files.length) {
    return null;
  }
  return files[files.length - 1];
}

function versionedPaths(project, version = project.fileStatus?.version || "v01") {
  const stem = project.projectStem;
  return {
    projectDir: `projects/${stem}`,
    scad: `projects/${stem}/source/${stem}_${version}.scad`,
    stl: `projects/${stem}/exports/${stem}_${version}.stl`,
    iso: `projects/${stem}/previews/${stem}_${version}_iso.png`,
    front: `projects/${stem}/previews/${stem}_${version}_front.png`,
    side: `projects/${stem}/previews/${stem}_${version}_side.png`
  };
}

async function createProjectReferences(stem) {
  for (const folder of ["measured", "public", "paid"]) {
    await fs.mkdir(path.join(repoProjectsDir, stem, "references", folder), { recursive: true });
  }
}

function badRequest(response, message, details = {}) {
  response.status(400).json({ ok: false, message, ...details });
}

// FIX #7: Input sanitization for project names
function validateProjectName(projectName) {
  // Allow alphanumeric, spaces, hyphens, underscores, parentheses, ampersand, periods, commas
  const sanitizationRegex = /^[a-zA-Z0-9\s\-_()&.,]+$/;
  return sanitizationRegex.test(projectName);
}

app.get("/api/health", async (_request, response) => {
  response.json({ ok: true, appRoot, repoRoot });
});

app.get("/api/settings", async (_request, response) => {
  await ensureDataFiles();
  const settings = await readJson(settingsJsonPath, {});
  response.json({ statuses, taskModes, checklistKeys, ...settings });
});

app.get("/api/projects", async (_request, response) => {
  response.json(await projectRecordsWithDetectedFolders());
});

app.post("/api/projects", async (request, response) => {
  const body = request.body || {};
  const projectName = String(body.projectName || "").trim();
  const projectStem = normalizeProjectStem(projectName);
  if (!projectName || !projectStem) {
    return badRequest(response, "Project name is required.");
  }
  // FIX #7: Validate project name for security
  if (!validateProjectName(projectName)) {
    return badRequest(response, "Project name contains invalid characters. Use alphanumeric, spaces, hyphens, underscores, parentheses, ampersand, periods, or commas.");
  }
  if (!taskModes.includes(body.taskMode)) {
    return badRequest(response, "A valid task mode is required.");
  }
  const records = await readProjectRecords();
  if (records.some((record) => record.projectStem === projectStem)) {
    return response.status(409).json({ ok: false, message: `Project record already exists for ${projectStem}.` });
  }
  if (await pathExists(path.join(repoProjectsDir, projectStem))) {
    return response.status(409).json({
      ok: false,
      message: `Project folder already exists for ${projectStem}. Existing folders are not overwritten.`
    });
  }

  const timestamp = nowIso();
  const record = normalizeRecord({
    id: `${projectStem}-${Date.now()}`,
    projectName,
    projectStem,
    customer: body.customer,
    description: body.description,
    taskMode: body.taskMode,
    printer: body.printer,
    material: body.material,
    supportFreePreferred: body.supportFreePreferred,
    functionalPart: body.functionalPart,
    replacementPart: body.replacementPart,
    needsExactFit: body.needsExactFit,
    measurementsNotes: body.measurementsNotes,
    referenceNotes: body.referenceNotes,
    protectedInterfaces: body.protectedInterfaces,
    lowConfidenceZones: body.lowConfidenceZones,
    customerDeadline: body.customerDeadline,
    privateNotes: body.privateNotes,
    dimensions: body.dimensions,
    status: "intake",
    createdAt: timestamp,
    updatedAt: timestamp
  });
  records.push(record);
  await writeProjectRecords(records);
  response.status(201).json({ ...record, fileStatus: await detectProjectFilesWithCache(record) });
});

app.get("/api/projects/:id", async (request, response) => {
  const project = await findProject(request.params.id);
  if (!project) {
    return response.status(404).json({ ok: false, message: "Project not found." });
  }
  response.json(project);
});

app.patch("/api/projects/:id", async (request, response) => {
  const updated = await updateProjectRecord(request.params.id, request.body || {});
  if (!updated) {
    return response.status(404).json({ ok: false, message: "Only projects in app/data/projects.json can be edited." });
  }
  response.json({ ...updated, fileStatus: await detectProjectFilesWithCache(updated) });
});

app.post("/api/projects/:id/bootstrap", async (request, response) => {
  const project = await findProject(request.params.id);
  if (!project) {
    return response.status(404).json({ ok: false, message: "Project not found." });
  }
  if (project.id.startsWith("folder:")) {
    return badRequest(response, "Detected project folders cannot be bootstrapped from app data.");
  }
  const scriptPath = path.join("scripts", "new_project.py");
  const args = [
    "py",
    "-3",
    scriptPath,
    "--name",
    project.projectName,
    "--task-mode",
    project.taskMode,
    "--printer",
    project.printer,
    "--material",
    project.material
  ];
  const result = await runCommand(args);
  if (result.ok) {
    await createProjectReferences(project.projectStem);
    // FIX #3: Limit command history to prevent memory bloat
    const MAX_HISTORY = 50;
    const newHistory = [...(project.commandHistory || []), { action: "bootstrap", at: nowIso(), ...result }];
    const trimmedHistory = newHistory.slice(-MAX_HISTORY);
    await updateProjectRecord(project.id, {
      status: "measuring",
      commandHistory: trimmedHistory
    });
  }
  const refreshed = await findProject(project.id);
  response.json({
    ok: result.ok,
    message: result.ok ? "Project bootstrapped." : "Bootstrap failed. No success was assumed.",
    result,
    project: refreshed
  });
});

// FIX #4: Map actions to status updates
const STATUS_MAP = {
  validateScad: (ok) => ok ? "measuring" : null,
  exportStl: (ok) => ok ? "exported" : null,
  previewIso: (ok) => ok ? "modeling" : null,
  previewFront: (ok) => ok ? "modeling" : null,
  previewSide: (ok) => ok ? "modeling" : null,
  checkOutputs: (ok) => ok ? "review" : null,
  nextVersion: (ok) => ok ? "modeling" : null
};

app.post("/api/projects/:id/actions/:action", async (request, response) => {
  const project = await findProject(request.params.id);
  if (!project) {
    return response.status(404).json({ ok: false, message: "Project not found." });
  }

  const action = request.params.action;
  const refreshed = await findProject(project.id);
  const scadFile = latestScadPath(refreshed);
  const version = refreshed.fileStatus?.version || "v01";
  const paths = versionedPaths(refreshed, version);
  let args = null;
  let expectedFile = null;
  let nextVersionFile = null;

  if (action === "validateScad") {
    if (!scadFile) {
      return badRequest(response, "No SCAD file found to validate.");
    }
    args = ["py", "-3", path.join("scripts", "validate_scad.py"), scadFile];
  } else if (action === "exportStl") {
    if (!scadFile) {
      return badRequest(response, "No SCAD file found to export.");
    }
    args = ["py", "-3", path.join("scripts", "export_stl.py"), "--input", scadFile, "--output", paths.stl];
    expectedFile = paths.stl;
  } else if (["previewIso", "previewFront", "previewSide"].includes(action)) {
    if (!scadFile) {
      return badRequest(response, "No SCAD file found to render.");
    }
    const view = action.replace("preview", "").toLowerCase();
    const output = view === "iso" ? paths.iso : view === "front" ? paths.front : paths.side;
    args = [
      "py",
      "-3",
      path.join("scripts", "export_preview.py"),
      "--input",
      scadFile,
      "--output",
      output,
      "--view",
      view
    ];
    expectedFile = output;
  } else if (action === "checkOutputs") {
    args = [
      "py",
      "-3",
      path.join("scripts", "check_project_outputs.py"),
      "--project",
      paths.projectDir,
      "--task-mode",
      refreshed.taskMode,
      "--version",
      version
    ];
  } else if (action === "nextVersion") {
    const nextNumber = Number(version.slice(1)) + 1;
    const nextVersion = `v${nextNumber.toString().padStart(2, "0")}`;
    nextVersionFile = `projects/${refreshed.projectStem}/source/${refreshed.projectStem}_${nextVersion}.scad`;
    args = ["py", "-3", path.join("scripts", "next_version.py"), "--project", paths.projectDir, "--copy-scad"];
    expectedFile = nextVersionFile;
  } else {
    return badRequest(response, "Unknown action.");
  }

  const result = await runCommand(args);
  let expectedExists = true;
  if (expectedFile) {
    expectedExists = await pathExists(relativeToAbsolute(expectedFile));
  }
  const ok = result.ok && expectedExists;
  const finalResult = {
    ...result,
    ok,
    expectedFile,
    expectedExists,
    message: ok
      ? "Command completed and expected output was verified."
      : expectedFile
        ? "Command failed or expected output was not found. Output is NOT VERIFIED."
        : "Command failed. Output is NOT VERIFIED."
  };

  if (!refreshed.id.startsWith("folder:")) {
    // FIX #3: Limit command history to 50 entries
    const MAX_HISTORY = 50;
    const newHistory = [...(refreshed.commandHistory || []), { action, at: nowIso(), ...finalResult }];
    const trimmedHistory = newHistory.slice(-MAX_HISTORY);

    // FIX #4: Update status based on action result using STATUS_MAP
    const statusUpdater = STATUS_MAP[action];
    const newStatus = statusUpdater ? statusUpdater(ok) : null;
    const finalStatus = newStatus !== null ? newStatus : refreshed.status;

    await updateProjectRecord(refreshed.id, {
      status: finalStatus,
      commandHistory: trimmedHistory
    });
  }

  response.json({ ok, result: finalResult, project: await findProject(refreshed.id) });
});

app.post("/api/system/open-path", async (request, response) => {
  const target = request.body?.target || "projects";
  const allowed = {
    projects: path.join(repoRoot, "projects"),
    workflow: path.join(repoRoot, "docs"),
    printability: path.join(repoRoot, "standards", "FDM_PRINTABILITY_CHECKS.md")
  };
  const targetPath = allowed[target];
  if (!targetPath) {
    return badRequest(response, "Unknown path target.");
  }
  const command =
    os.platform() === "win32"
      ? ["explorer.exe", targetPath]
      : os.platform() === "darwin"
        ? ["open", targetPath]
        : ["xdg-open", targetPath];
  const child = spawn(command[0], command.slice(1), {
    detached: true,
    stdio: "ignore",
    windowsHide: true
  });
  child.unref();
  response.json({ ok: true, command: formatCommand(command), path: targetPath });
});

app.use(express.static(path.join(appRoot, "dist")));

await ensureDataFiles();
app.listen(port, "127.0.0.1", () => {
  console.log(`3D Print Design Studio Dashboard API running at http://127.0.0.1:${port}`);
  console.log(`Repo root: ${repoRoot}`);
});
