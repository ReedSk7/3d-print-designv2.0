import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Box,
  CheckCircle2,
  Clipboard,
  FileCode2,
  FileText,
  FolderOpen,
  Gauge,
  Hammer,
  Home,
  Layers,
  Play,
  Plus,
  RefreshCw,
  Search,
  Settings2,
  ShieldCheck,
  TerminalSquare
} from "lucide-react";
import {
  bootstrapProject,
  createProject,
  getProjects,
  getSettings,
  openSystemPath,
  runProjectAction,
  updateProject
} from "./api";
import type { CommandResult, Project, ProjectStatus, Settings, TaskMode } from "./types";

type View = "dashboard" | "projects" | "new" | "detail" | "workflow" | "printability";

const allowedViews: View[] = ["dashboard", "projects", "new", "detail", "workflow", "printability"];

function initialRoute() {
  if (typeof window === "undefined") {
    return { view: "dashboard" as View, selectedId: "" };
  }
  const params = new URL(window.location.href).searchParams;
  const project = params.get("project");
  if (project) {
    return { view: "detail" as View, selectedId: project };
  }
  const requestedView = params.get("view") as View | null;
  return {
    view: requestedView && allowedViews.includes(requestedView) && requestedView !== "detail" ? requestedView : "dashboard",
    selectedId: ""
  };
}

const defaultSettings: Settings = {
  statuses: ["intake", "measuring", "modeling", "review", "exported", "printed", "delivered", "archived"],
  taskModes: ["original_product_design", "reference_based_reconstruction", "mesh_cleanup_and_remodel"],
  checklistKeys: [],
  printers: {
    "Bambu Lab P2S": [256, 256, 256],
    "Qidi XPlus 3": [280, 280, 270],
    "Qidi XPlus 3 Pro": [280, 280, 270],
    "Ender 3 Pro": [220, 220, 250]
  },
  materials: ["PLA", "PETG", "PETG HF", "TPU", "ABS", "ASA", "Other"],
  nsfwModels: [
    "sd-v1.5-inpainting safetensors [sha256:0ec8f8585b]",
    "sd-v1.5 safetensors",
    "sd-v2.1 safetensors",
    "sd-xl safetensors"
  ]
};

const checklistLabels: Record<string, string> = {
  fitsBuildVolume: "Fits selected printer build volume",
  materialSelected: "Correct material selected",
  orientationConsidered: "Correct orientation considered",
  supportPlanNoted: "Support-free or supports noted",
  wallThicknessAcceptable: "Wall thickness acceptable",
  holesHaveClearance: "Holes have clearance",
  snapsReviewed: "Snap/latch areas reviewed",
  stressAreasReinforced: "Stress areas reinforced",
  sharpCornersSoftened: "Sharp corners softened where useful",
  overhangsReviewed: "Overhangs reviewed",
  bedContactAcceptable: "Bed contact surface acceptable",
  criticalInterfacesProtected: "Critical interfaces protected",
  measurementsRecorded: "Measurements recorded",
  lowConfidenceDocumented: "Low-confidence areas documented",
  stlExported: "STL exported",
  previewRendered: "Preview rendered",
  manifestCreated: "Manifest created",
  reviewReportCreated: "Review report created"
};

const emptyForm = {
  projectName: "",
  customer: "",
  description: "",
  taskMode: "original_product_design" as TaskMode,
  printer: "Bambu Lab P2S",
  material: "PETG",
  supportFreePreferred: true,
  functionalPart: false,
  replacementPart: false,
  needsExactFit: false,
  measurementsNotes: "",
  referenceNotes: "",
  protectedInterfaces: "",
  lowConfidenceZones: "",
  customerDeadline: "",
  privateNotes: "",
  dimensions: { width: "", depth: "", height: "" }
};

function statusClass(status: string) {
  return `status status-${status}`;
}

function boolBadge(value: boolean, trueText = "Yes", falseText = "No") {
  return <span className={value ? "badge good" : "badge muted"}>{value ? trueText : falseText}</span>;
}

function dateShort(value: string) {
  if (!value) return "";
  return new Date(value).toLocaleDateString();
}

function projectStemPreview(name: string) {
  return name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function buildVolumeWarning(project: Pick<Project, "dimensions" | "printer">, settings: Settings) {
  const rawDims = [
    project.dimensions?.width ? Number(project.dimensions.width) : null,
    project.dimensions?.depth ? Number(project.dimensions.depth) : null,
    project.dimensions?.height ? Number(project.dimensions.height) : null
  ];
  const dims = rawDims.filter((d) => d !== null && d > 0);
  if (dims.length === 0) return null;
  const volume = settings.printers[project.printer];
  if (!volume) return null;
  const tooLarge = rawDims.some((value, index) => value !== null && value > volume[index]);
  const displayDims = rawDims.map(d => d || "?").join(" x ");
  return tooLarge
    ? `Warning: provided dimensions ${displayDims} mm exceed ${project.printer} volume ${volume.join(" x ")} mm.`
    : `Build volume check: ${displayDims} mm fits ${project.printer} (${volume.join(" x ")} mm).`;
}

function generatePrompt(project: Project) {
  const reconstructionBlock =
    project.taskMode === "original_product_design"
      ? ""
      : `
For this reconstruction/remodeling job:
- Define the exact target part.
- Define reused surrounding parts.
- Define what is not being modeled.
- Record anchor dimensions.
- Protect interfaces.
- Use compare-and-revise loops.
- Do not trust rough meshes as authoritative.
- Do not claim STL or preview success unless files exist.`;

  return `You are working inside the existing repo 3d-print-designV2.0.

Follow root AGENTS.md first. OpenSCAD is the editable source of truth. STL files are export artifacts only.

Task mode: ${project.taskMode}
Project stem: ${project.projectStem}
Project scope: ${project.projectName}
Description:
${project.description || "No description provided."}

Printer: ${project.printer || "NOT SPECIFIED"}
Material: ${project.material || "NOT SPECIFIED"}
Support-free preferred: ${project.supportFreePreferred ? "yes" : "no"}
Functional part: ${project.functionalPart ? "yes" : "no"}
Replacement part: ${project.replacementPart ? "yes" : "no"}
Needs exact fit: ${project.needsExactFit ? "yes" : "no"}

Measurements:
${project.measurementsNotes || "No measurement notes provided yet."}

Protected interfaces:
${project.protectedInterfaces || "None recorded yet."}

Reference notes:
${project.referenceNotes || "No reference notes provided yet."}

Reference hierarchy:
1. measured dimensions from the real part
2. trusted or purchased reference STL/STEP/CAD
3. official OEM drawings, service docs, or diagrams
4. official product photos
5. user photos of intact or broken part
6. AI-generated meshes or photo-to-3D outputs

Low-confidence zones:
${project.lowConfidenceZones || "None recorded yet."}

Required outputs:
- source/${project.projectStem}_vNN.scad
- exports/${project.projectStem}_vNN.stl
- notes/${project.projectStem}_vNN_notes.md
- notes/${project.projectStem}_vNN_manifest.md
- previews/${project.projectStem}_vNN_iso.png
- front/side previews for reconstruction jobs

Verification requirements:
- Run validate_scad.py.
- Export STL with export_stl.py.
- Render required previews with export_preview.py.
- Run check_project_outputs.py.
- Mark missing outputs as NOT VERIFIED.
- Do not claim STL or preview success unless files exist.${reconstructionBlock}
`;
}

function CommandPanel({ result }: { result: CommandResult | null }) {
  if (!result) return null;
  return (
    <section className={`command-panel ${result.ok ? "command-ok" : "command-fail"}`}>
      <div className="section-heading">
        <TerminalSquare size={18} />
        <h3>{result.ok ? "Command Passed" : "Command Failed"}</h3>
      </div>
      <dl className="command-meta">
        <dt>Command</dt>
        <dd>{result.command}</dd>
        <dt>Exit code</dt>
        <dd>{result.exitCode}</dd>
        {result.expectedFile && (
          <>
            <dt>Expected file</dt>
            <dd>
              {result.expectedFile} {result.expectedExists ? "(exists)" : "(NOT VERIFIED)"}
            </dd>
          </>
        )}
      </dl>
      {result.message && <p>{result.message}</p>}
      <div className="output-grid">
        <pre>{result.stdout || "stdout: (empty)"}</pre>
        <pre>{result.stderr || "stderr: (empty)"}</pre>
      </div>
    </section>
  );
}

function App() {
  const route = initialRoute();
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [projects, setProjects] = useState<Project[]>([]);
  const [view, setView] = useState<View>(route.view);
  const [selectedId, setSelectedId] = useState<string>(route.selectedId);
  const [activeTab, setActiveTab] = useState("Overview");
  const [form, setForm] = useState(emptyForm);
  const [createdProject, setCreatedProject] = useState<Project | null>(null);
  const [commandResult, setCommandResult] = useState<CommandResult | null>(null);
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);

  async function refreshProjects() {
    setLoading(true);
    try {
      const [nextSettings, nextProjects] = await Promise.all([getSettings(), getProjects()]);
      setSettings({ ...defaultSettings, ...nextSettings });
      setProjects(nextProjects);
      setNotice("");
      if (selectedId && !nextProjects.some((project) => project.id === selectedId || project.projectStem === selectedId)) {
        setSelectedId("");
      }
    } catch (error) {
      setNotice(error instanceof Error ? error.message : String(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshProjects();
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const url = new URL(window.location.href);
    url.search = "";
    if (view === "detail" && selectedId) {
      url.searchParams.set("project", selectedId);
    } else if (view !== "dashboard") {
      url.searchParams.set("view", view);
    }
    window.history.replaceState(null, "", url);
  }, [selectedId, view]);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedId || project.projectStem === selectedId) || null,
    [projects, selectedId]
  );

  const projectsByStatus = useMemo(() => {
    const counts = Object.fromEntries(settings.statuses.map((status) => [status, 0])) as Record<ProjectStatus, number>;
    for (const project of projects) {
      counts[project.status] = (counts[project.status] || 0) + 1;
    }
    return counts;
  }, [projects, settings.statuses]);

  const recentProjects = projects.slice(0, 5);

  function updateForm(field: string, value: unknown) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submitProject(event: FormEvent) {
    event.preventDefault();
    setNotice("");
    setCommandResult(null);
    const project = await createProject(form);
    setCreatedProject(project);
    setSelectedId(project.id);
    await refreshProjects();
  }

  async function runBootstrap(project: Project) {
    setNotice("");
    const payload = await bootstrapProject(project.id);
    setCommandResult(payload.result);
    if (!payload.ok) setNotice(payload.message);
    await refreshProjects();
  }

  async function runAction(project: Project, action: string) {
    setNotice("");
    const payload = await runProjectAction(project.id, action);
    setCommandResult(payload.result);
    if (!payload.ok) setNotice(payload.result.message || "Command failed.");
    await refreshProjects();
  }

  async function patchProject(project: Project, patch: Partial<Project>) {
    if (project.id.startsWith("folder:")) {
      setNotice("Detected project folders are read-only until they are added to app/data/projects.json.");
      return;
    }
    const updated = await updateProject(project.id, patch);
    setProjects((current) => current.map((item) => (item.id === updated.id ? updated : item)));
  }

  function selectProject(project: Project) {
    setSelectedId(project.id);
    setActiveTab("Overview");
    setView("detail");
    setCommandResult(null);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Box size={26} />
          <div>
            <strong>3D Print Design Studio</strong>
            <span>Local OpenSCAD dashboard</span>
          </div>
        </div>
        <nav>
          <button className={view === "dashboard" ? "active" : ""} onClick={() => setView("dashboard")}>
            <Home size={17} /> Dashboard
          </button>
          <button className={view === "projects" ? "active" : ""} onClick={() => setView("projects")}>
            <Layers size={17} /> Projects
          </button>
          <button className={view === "new" ? "active" : ""} onClick={() => setView("new")}>
            <Plus size={17} /> New Project
          </button>
          <button className={view === "workflow" ? "active" : ""} onClick={() => setView("workflow")}>
            <ShieldCheck size={17} /> Workflow
          </button>
          <button className={view === "printability" ? "active" : ""} onClick={() => setView("printability")}>
            <Gauge size={17} /> Printability
          </button>
        </nav>
        <div className="sidebar-note">
          Root <code>AGENTS.md</code> stays authoritative. The app wraps existing scripts only.
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">Local only</p>
            <h1>{view === "detail" && selectedProject ? selectedProject.projectName : "3D Print Design Studio Dashboard"}</h1>
          </div>
          <button className="ghost" onClick={() => refreshProjects()}>
            <RefreshCw size={16} /> Refresh
          </button>
        </header>

        {notice && (
          <div className="notice">
            <AlertTriangle size={17} />
            {notice}
          </div>
        )}

        {view === "dashboard" && (
          <Dashboard
            projects={projects}
            projectsByStatus={projectsByStatus}
            recentProjects={recentProjects}
            loading={loading}
            setView={setView}
            selectProject={selectProject}
            openPath={async (target) => {
              const result = await openSystemPath(target);
              setNotice(`Opened ${result.path}`);
            }}
          />
        )}

        {view === "projects" && <ProjectList projects={projects} loading={loading} selectProject={selectProject} />}

        {view === "new" && (
          <NewProject
            form={form}
            settings={settings}
            createdProject={createdProject}
            updateForm={updateForm}
            submitProject={submitProject}
            runBootstrap={runBootstrap}
          />
        )}

        {view === "detail" && selectedProject && (
          <ProjectDetail
            project={selectedProject}
            settings={settings}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            runAction={runAction}
            patchProject={patchProject}
            commandResult={commandResult}
          />
        )}

        {view === "workflow" && <WorkflowPanel />}
        {view === "printability" && <PrintabilityReference />}
      </main>
    </div>
  );
}

function Dashboard({
  projects,
  projectsByStatus,
  recentProjects,
  loading,
  setView,
  selectProject,
  openPath
}: {
  projects: Project[];
  projectsByStatus: Record<ProjectStatus, number>;
  recentProjects: Project[];
  loading: boolean;
  setView: (view: View) => void;
  selectProject: (project: Project) => void;
  openPath: (target: string) => Promise<void>;
}) {
  const verifiedCount = projects.filter((project) => project.fileStatus.verificationStatus === "VERIFIED").length;
  const reviewCount = projects.filter((project) => project.fileStatus.verificationStatus === "NOT VERIFIED").length;
  return (
    <div className="page-grid">
      <section className="metric-grid">
        <div className="metric-card">
          <span>Total Projects</span>
          <strong>{loading ? "..." : projects.length}</strong>
        </div>
        <div className="metric-card">
          <span>Verified Outputs</span>
          <strong>{loading ? "..." : verifiedCount}</strong>
          <small>Required artifacts detected</small>
        </div>
        <div className="metric-card">
          <span>Needs Review</span>
          <strong>{loading ? "..." : reviewCount}</strong>
          <small>Missing or unchecked outputs</small>
        </div>
      </section>

      <section className="card">
        <div className="section-heading">
          <Gauge size={18} />
          <h2>Projects By Status</h2>
        </div>
        <div className="status-grid">
          {Object.entries(projectsByStatus).map(([status, count]) => (
            <div key={status} className="status-count">
              <span className={statusClass(status)}>{status}</span>
              <strong>{count}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <div className="section-heading">
          <Play size={18} />
          <h2>Quick Actions</h2>
        </div>
        <div className="quick-actions">
          <button onClick={() => setView("new")}>
            <Plus size={17} /> New Project
          </button>
          <button onClick={() => openPath("projects")}>
            <FolderOpen size={17} /> Open Projects Folder
          </button>
          <button onClick={() => setView("workflow")}>
            <FileText size={17} /> View Workflow
          </button>
          <button onClick={() => setView("printability")}>
            <Clipboard size={17} /> View Printability Checklist
          </button>
        </div>
      </section>

      <section className="card span-2">
        <div className="section-heading">
          <Search size={18} />
          <h2>Recent Projects</h2>
        </div>
        <div className="compact-list">
          {loading && <p className="muted-text">Loading project records...</p>}
          {!loading && !recentProjects.length && <p className="muted-text">No project records found yet.</p>}
          {!loading &&
            recentProjects.map((project) => (
              <button key={project.id} onClick={() => selectProject(project)}>
                <span>{project.projectName}</span>
                <span className={statusClass(project.status)}>{project.status}</span>
                <span className={project.fileStatus.verificationStatus === "VERIFIED" ? "badge good" : "badge warn"}>
                  {project.fileStatus.verificationStatus}
                </span>
              </button>
            ))}
        </div>
      </section>
    </div>
  );
}

function ProjectList({
  projects,
  loading,
  selectProject
}: {
  projects: Project[];
  loading: boolean;
  selectProject: (project: Project) => void;
}) {
  return (
    <section className="card">
      <div className="section-heading">
        <Layers size={18} />
        <h2>Project List</h2>
      </div>
      {loading && <p className="muted-text">Loading project records...</p>}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Project</th>
              <th>Customer</th>
              <th>Mode</th>
              <th>Printer</th>
              <th>Material</th>
              <th>Status</th>
              <th>Created</th>
              <th>Updated</th>
              <th>SCAD</th>
              <th>STL</th>
              <th>Previews</th>
              <th>Verification</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr key={project.id} onClick={() => selectProject(project)}>
                <td>
                  <strong>{project.projectName}</strong>
                  <small>{project.projectStem}</small>
                </td>
                <td>{project.customer || "-"}</td>
                <td>{project.taskMode}</td>
                <td>{project.printer || "-"}</td>
                <td>{project.material || "-"}</td>
                <td>
                  <span className={statusClass(project.status)}>{project.status}</span>
                </td>
                <td>{dateShort(project.createdAt)}</td>
                <td>{dateShort(project.updatedAt)}</td>
                <td>{boolBadge(project.fileStatus.hasScad)}</td>
                <td>{boolBadge(project.fileStatus.hasStl)}</td>
                <td>{boolBadge(project.fileStatus.hasPreviews)}</td>
                <td>
                  <span className={project.fileStatus.verificationStatus === "VERIFIED" ? "badge good" : "badge warn"}>
                    {project.fileStatus.verificationStatus}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="project-card-list">
        {projects.map((project) => (
          <button key={project.id} className="project-card-row" onClick={() => selectProject(project)}>
            <div>
              <strong>{project.projectName}</strong>
              <small>{project.projectStem}</small>
            </div>
            <div className="project-card-meta">
              <span>{project.taskMode}</span>
              <span>{project.printer || "-"}</span>
              <span>{project.material || "-"}</span>
            </div>
            <div className="project-card-badges">
              <span className={statusClass(project.status)}>{project.status}</span>
              <span className={project.fileStatus.verificationStatus === "VERIFIED" ? "badge good" : "badge warn"}>
                {project.fileStatus.verificationStatus}
              </span>
            </div>
            <div className="project-card-artifacts">
              {boolBadge(project.fileStatus.hasScad, "SCAD", "NO SCAD")}
              {boolBadge(project.fileStatus.hasStl, "STL", "NO STL")}
              {boolBadge(project.fileStatus.hasPreviews, "PREVIEWS", "NO PREVIEWS")}
            </div>
          </button>
        ))}
      </div>
      {!loading && !projects.length && <p className="muted-text">No projects are recorded yet. Start with New Project.</p>}
    </section>
  );
}

function NewProject({
  form,
  settings,
  createdProject,
  updateForm,
  submitProject,
  runBootstrap
}: {
  form: typeof emptyForm;
  settings: Settings;
  createdProject: Project | null;
  updateForm: (field: string, value: unknown) => void;
  submitProject: (event: FormEvent) => Promise<void>;
  runBootstrap: (project: Project) => Promise<void>;
}) {
  const stem = projectStemPreview(form.projectName);
  const volumeWarning = buildVolumeWarning(form, settings);
  return (
    <div className="split-layout">
      <form className="card form" onSubmit={submitProject}>
        <div className="section-heading">
          <Plus size={18} />
          <h2>New Project</h2>
        </div>
        <p className="muted-text">
          Create the intake record first. Bootstrap only after the task mode and fit-critical notes are clear enough.
        </p>

        <div className="form-section">
          <h3>Project Basics</h3>
          <div className="form-grid">
            <label>
              Project name
              <input value={form.projectName} onChange={(event) => updateForm("projectName", event.target.value)} required />
            </label>
            <label>
              Customer/requester
              <input value={form.customer} onChange={(event) => updateForm("customer", event.target.value)} />
            </label>
            <label>
              Task mode
              <select value={form.taskMode} onChange={(event) => updateForm("taskMode", event.target.value as TaskMode)}>
                {settings.taskModes.map((mode) => (
                  <option key={mode} value={mode}>
                    {mode}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Customer deadline
              <input type="date" value={form.customerDeadline} onChange={(event) => updateForm("customerDeadline", event.target.value)} />
            </label>
          </div>

          <label>
            Description
            <textarea value={form.description} onChange={(event) => updateForm("description", event.target.value)} />
          </label>
        </div>

        <div className="form-section">
          <h3>Printer, Material, And Fit</h3>
          <div className="form-grid">
            <label>
              Printer
              <select value={form.printer} onChange={(event) => updateForm("printer", event.target.value)}>
                {[...Object.keys(settings.printers), "Other"].map((printer) => (
                  <option key={printer} value={printer}>
                    {printer}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Material
              <select value={form.material} onChange={(event) => updateForm("material", event.target.value)}>
                {settings.materials.map((material) => (
                  <option key={material} value={material}>
                    {material}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="checkbox-row">
            {[
              ["supportFreePreferred", "Support-free preferred"],
              ["functionalPart", "Functional part"],
              ["replacementPart", "Replacement part"],
              ["needsExactFit", "Needs exact fit"]
            ].map(([field, label]) => (
              <label key={field} className="check">
                <input
                  type="checkbox"
                  checked={Boolean(form[field as keyof typeof form])}
                  onChange={(event) => updateForm(field, event.target.checked)}
                />
                {label}
              </label>
            ))}
          </div>

          <div className="form-grid thirds">
            {(["width", "depth", "height"] as const).map((field) => (
              <label key={field}>
                {field} mm
                <input
                  type="number"
                  value={form.dimensions[field]}
                  onChange={(event) =>
                    updateForm("dimensions", { ...form.dimensions, [field]: event.target.value })
                  }
                />
              </label>
            ))}
          </div>
          {volumeWarning && <p className={volumeWarning.startsWith("Warning") ? "inline-warning" : "inline-ok"}>{volumeWarning}</p>}
        </div>

        <div className="form-section">
          <h3>Measurements And References</h3>
          {[
            ["measurementsNotes", "Measurement notes"],
            ["referenceNotes", "Reference notes"],
            ["protectedInterfaces", "Protected interfaces"],
            ["lowConfidenceZones", "Low-confidence zones"],
            ["privateNotes", "Private notes"]
          ].map(([field, label]) => (
            <label key={field}>
              {label}
              <textarea value={String(form[field as keyof typeof form])} onChange={(event) => updateForm(field, event.target.value)} />
            </label>
          ))}
        </div>

        <button type="submit">
          <Plus size={17} /> Create Project Record
        </button>
      </form>

      <section className="card sticky-card">
        <div className="section-heading">
          <FolderOpen size={18} />
          <h2>Expected Structure</h2>
        </div>
        <pre className="folder-preview">{`projects/${stem || "<project_stem>"}/source
projects/${stem || "<project_stem>"}/exports
projects/${stem || "<project_stem>"}/notes
projects/${stem || "<project_stem>"}/previews
projects/${stem || "<project_stem>"}/references/measured
projects/${stem || "<project_stem>"}/references/public
projects/${stem || "<project_stem>"}/references/paid`}</pre>
        {createdProject && (
          <div className="created-box">
            <h3>{createdProject.projectName}</h3>
            <p>
              Stem: <code>{createdProject.projectStem}</code>
            </p>
            <button onClick={() => runBootstrap(createdProject)}>
              <Hammer size={17} /> Bootstrap Project
            </button>
          </div>
        )}
      </section>
    </div>
  );
}

function ProjectDetail({
  project,
  settings,
  activeTab,
  setActiveTab,
  runAction,
  patchProject,
  commandResult
}: {
  project: Project;
  settings: Settings;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  runAction: (project: Project, action: string) => Promise<void>;
  patchProject: (project: Project, patch: Partial<Project>) => Promise<void>;
  commandResult: CommandResult | null;
}) {
  const tabs = [
    "Overview",
    "Measurements",
    "References",
    "Generated Codex Prompt",
    "Files",
    "Verification",
    "Print Settings",
    "Customer Quote Notes",
    "Release Checklist"
  ];
  return (
    <div className="detail-page">
      <section className="card detail-summary">
        <div>
          <p className="eyebrow">{project.projectStem}</p>
          <h2>{project.projectName}</h2>
          <p>{project.description || "No description recorded."}</p>
        </div>
        <div className="summary-badges">
          <span className={statusClass(project.status)}>{project.status}</span>
          <span className={project.fileStatus.verificationStatus === "VERIFIED" ? "badge good" : "badge warn"}>
            {project.fileStatus.verificationStatus}
          </span>
        </div>
      </section>

      <div className="tabs">
        {tabs.map((tab) => (
          <button key={tab} className={tab === activeTab ? "active" : ""} onClick={() => setActiveTab(tab)}>
            {tab}
          </button>
        ))}
      </div>

      {activeTab === "Overview" && <OverviewTab project={project} settings={settings} patchProject={patchProject} />}
      {activeTab === "Measurements" && <TextTab project={project} field="measurementsNotes" title="Measurements" patchProject={patchProject} />}
      {activeTab === "References" && <ReferencesTab project={project} patchProject={patchProject} />}
      {activeTab === "Generated Codex Prompt" && <PromptTab project={project} />}
      {activeTab === "Files" && <FilesTab project={project} />}
      {activeTab === "Verification" && (
        <VerificationTab project={project} runAction={runAction} commandResult={commandResult} />
      )}
      {activeTab === "Print Settings" && <PrintSettingsTab project={project} settings={settings} patchProject={patchProject} />}
      {activeTab === "Customer Quote Notes" && <QuoteTab project={project} patchProject={patchProject} />}
      {activeTab === "Release Checklist" && <ReleaseChecklistTab project={project} patchProject={patchProject} />}
    </div>
  );
}

function OverviewTab({
  project,
  settings,
  patchProject
}: {
  project: Project;
  settings: Settings;
  patchProject: (project: Project, patch: Partial<Project>) => Promise<void>;
}) {
  const volumeWarning = buildVolumeWarning(project, settings);
  return (
    <section className="card">
      <div className="detail-grid">
        <div>
          <h3>Project Metadata</h3>
          <p>Customer: {project.customer || "-"}</p>
          <p>Task mode: {project.taskMode}</p>
          <p>Printer: {project.printer || "-"}</p>
          <p>Material: {project.material || "-"}</p>
          <p>Created: {dateShort(project.createdAt)}</p>
          <p>Updated: {dateShort(project.updatedAt)}</p>
        </div>
        <label>
          Status
          <select value={project.status} onChange={(event) => patchProject(project, { status: event.target.value as ProjectStatus })}>
            {settings.statuses.map((status) => (
              <option key={status}>{status}</option>
            ))}
          </select>
        </label>
      </div>
      {volumeWarning && <p className={volumeWarning.startsWith("Warning") ? "inline-warning" : "inline-ok"}>{volumeWarning}</p>}
      <div className="flag-grid">
        {boolBadge(project.supportFreePreferred, "Support-free preferred", "Supports allowed")}
        {boolBadge(project.functionalPart, "Functional", "Non-functional")}
        {boolBadge(project.replacementPart, "Replacement", "Not replacement")}
        {boolBadge(project.needsExactFit, "Exact fit", "Loose fit acceptable")}
      </div>
    </section>
  );
}

function TextTab({
  project,
  field,
  title,
  patchProject
}: {
  project: Project;
  field: keyof Pick<Project, "measurementsNotes" | "referenceNotes" | "protectedInterfaces" | "lowConfidenceZones" | "privateNotes">;
  title: string;
  patchProject: (project: Project, patch: Partial<Project>) => Promise<void>;
}) {
  const [value, setValue] = useState(String(project[field] || ""));
  useEffect(() => setValue(String(project[field] || "")), [project.id, project[field]]);
  return (
    <section className="card">
      <h2>{title}</h2>
      <textarea className="large-textarea" value={value} onChange={(event) => setValue(event.target.value)} />
      <button onClick={() => patchProject(project, { [field]: value } as Partial<Project>)}>
        <CheckCircle2 size={17} /> Save
      </button>
    </section>
  );
}

function ReferencesTab({
  project,
  patchProject
}: {
  project: Project;
  patchProject: (project: Project, patch: Partial<Project>) => Promise<void>;
}) {
  return (
    <div className="split-layout">
      <TextTab project={project} field="referenceNotes" title="Reference Notes" patchProject={patchProject} />
      <section className="card">
        <h2>Reference Hierarchy</h2>
        <ol className="ordered">
          <li>measured dimensions from the real part</li>
          <li>trusted or purchased reference STL/STEP/CAD</li>
          <li>official OEM drawings, service docs, or diagrams</li>
          <li>official product photos</li>
          <li>user photos of intact or broken part</li>
          <li>AI-generated meshes or photo-to-3D outputs</li>
        </ol>
        <p className="muted-text">Paid references stay local-only unless redistribution rights are clear.</p>
      </section>
    </div>
  );
}

function PromptTab({ project }: { project: Project }) {
  const prompt = generatePrompt(project);
  return (
    <section className="card">
      <div className="section-heading">
        <FileCode2 size={18} />
        <h2>Generated Codex/OpenSCAD Prompt</h2>
      </div>
      <button onClick={() => navigator.clipboard.writeText(prompt)}>
        <Clipboard size={17} /> Copy Prompt
      </button>
      <pre className="prompt-box">{prompt}</pre>
    </section>
  );
}

function FilesTab({ project }: { project: Project }) {
  const groups = project.fileStatus.files;
  return (
    <section className="card">
      <div className="section-heading">
        <FolderOpen size={18} />
        <h2>Files</h2>
      </div>
      <div className="file-status-grid">
        {[
          ["SCAD", project.fileStatus.hasScad],
          ["STL", project.fileStatus.hasStl],
          ["Notes", project.fileStatus.hasNotes],
          ["Manifest", project.fileStatus.hasManifest],
          ["Review report", project.fileStatus.hasReviewReport],
          ["Previews", project.fileStatus.hasPreviews]
        ].map(([label, ok]) => (
          <div key={String(label)} className="file-chip">
            {ok ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
            <span>{label}</span>
            <strong>{ok ? "FOUND" : "NOT VERIFIED"}</strong>
          </div>
        ))}
      </div>
      {Object.entries(groups).map(([group, files]) => (
        <div key={group} className="file-group">
          <h3>{group}</h3>
          {files.length ? (
            <ul>
              {files.map((file) => (
                <li key={file}>
                  <code>{file}</code>
                </li>
              ))}
            </ul>
          ) : (
            <p className="badge warn">NOT VERIFIED</p>
          )}
        </div>
      ))}
    </section>
  );
}

function VerificationTab({
  project,
  runAction,
  commandResult
}: {
  project: Project;
  runAction: (project: Project, action: string) => Promise<void>;
  commandResult: CommandResult | null;
}) {
  const actions = [
    ["validateScad", "Validate SCAD"],
    ["exportStl", "Export STL"],
    ["previewIso", "Export ISO Preview"],
    ["previewFront", "Export Front Preview"],
    ["previewSide", "Export Side Preview"],
    ["checkOutputs", "Check Project Outputs"],
    ["nextVersion", "Create Next Version"]
  ];
  return (
    <section className="card">
      <div className="section-heading">
        <TerminalSquare size={18} />
        <h2>Verification Commands</h2>
      </div>
      <div className="quick-actions">
        {actions.map(([action, label]) => (
          <button key={action} onClick={() => runAction(project, action)}>
            <Play size={17} /> {label}
          </button>
        ))}
      </div>
      <CommandPanel result={commandResult} />
    </section>
  );
}

function PrintSettingsTab({
  project,
  settings,
  patchProject
}: {
  project: Project;
  settings: Settings;
  patchProject: (project: Project, patch: Partial<Project>) => Promise<void>;
}) {
  const [dimensions, setDimensions] = useState(project.dimensions);
  useEffect(() => setDimensions(project.dimensions), [project.id, project.dimensions]);
  const volumeWarning = buildVolumeWarning({ ...project, dimensions }, settings);
  return (
    <section className="card">
      <h2>Print Settings</h2>
      <div className="form-grid thirds">
        {(["width", "depth", "height"] as const).map((field) => (
          <label key={field}>
            {field} mm
            <input value={dimensions[field]} onChange={(event) => setDimensions({ ...dimensions, [field]: event.target.value })} />
          </label>
        ))}
      </div>
      {volumeWarning && <p className={volumeWarning.startsWith("Warning") ? "inline-warning" : "inline-ok"}>{volumeWarning}</p>}
      <button onClick={() => patchProject(project, { dimensions })}>
        <CheckCircle2 size={17} /> Save Dimensions
      </button>
    </section>
  );
}

function QuoteTab({
  project,
  patchProject
}: {
  project: Project;
  patchProject: (project: Project, patch: Partial<Project>) => Promise<void>;
}) {
  const [quote, setQuote] = useState(project.quote);
  useEffect(() => setQuote(project.quote), [project.id, project.quote]);
  function update(field: string, value: string) {
    setQuote((current) => ({ ...current, [field]: value }));
  }
  return (
    <section className="card form">
      <h2>Customer Quote Notes</h2>
      <div className="form-grid">
        <label>
          Design complexity
          <select value={quote.designComplexity} onChange={(event) => update("designComplexity", event.target.value)}>
            <option>simple</option>
            <option>medium</option>
            <option>complex</option>
          </select>
        </label>
        {[
          ["estimatedPrintHours", "Estimated print hours"],
          ["estimatedMaterialGrams", "Estimated material grams"],
          ["materialCostEstimate", "Material cost estimate"],
          ["designFeeEstimate", "Design fee estimate"],
          ["printFeeEstimate", "Print fee estimate"],
          ["totalEstimate", "Total estimate"]
        ].map(([field, label]) => (
          <label key={field}>
            {label}
            <input value={String(quote[field as keyof typeof quote])} onChange={(event) => update(field, event.target.value)} />
          </label>
        ))}
      </div>
      <label>
        Notes for customer
        <textarea value={quote.customerNotes} onChange={(event) => update("customerNotes", event.target.value)} />
      </label>
      <button onClick={() => patchProject(project, { quote })}>
        <CheckCircle2 size={17} /> Save Quote Notes
      </button>
    </section>
  );
}

function ReleaseChecklistTab({
  project,
  patchProject
}: {
  project: Project;
  patchProject: (project: Project, patch: Partial<Project>) => Promise<void>;
}) {
  const checklist = project.printabilityChecklist || {};
  function toggle(key: string) {
    patchProject(project, { printabilityChecklist: { ...checklist, [key]: !checklist[key] } });
  }
  return (
    <section className="card">
      <div className="section-heading">
        <Clipboard size={18} />
        <h2>Release Checklist</h2>
      </div>
      <div className="checklist-grid">
        {Object.entries(checklistLabels).map(([key, label]) => (
          <label key={key} className="checklist-item">
            <input type="checkbox" checked={Boolean(checklist[key])} onChange={() => toggle(key)} />
            {label}
          </label>
        ))}
      </div>
    </section>
  );
}

function WorkflowPanel() {
  return (
    <section className="card readable">
      <div className="section-heading">
        <ShieldCheck size={18} />
        <h2>Workflow</h2>
      </div>
      <p>
        This dashboard wraps the existing repo workflow: request, classify task mode, bootstrap project, record references,
        protect interfaces, generate clean OpenSCAD, validate, export STL, render previews, check outputs, then record notes
        and release artifacts.
      </p>
      <p>Root AGENTS.md remains authoritative. OpenSCAD is the editable source of truth. STL is an export artifact.</p>
    </section>
  );
}

function PrintabilityReference() {
  return (
    <section className="card readable">
      <div className="section-heading">
        <Gauge size={18} />
        <h2>Printability Checklist</h2>
      </div>
      <div className="checklist-grid">
        {Object.values(checklistLabels).map((label) => (
          <label key={label} className="checklist-item static">
            <input type="checkbox" readOnly />
            {label}
          </label>
        ))}
      </div>
      <p className="muted-text">Use PETG for heat, outdoor, impact, or functional parts unless the job says otherwise.</p>
    </section>
  );
}

export default App;
