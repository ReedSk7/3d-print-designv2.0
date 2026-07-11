export type TaskMode =
  | "original_product_design"
  | "reference_based_reconstruction"
  | "mesh_cleanup_and_remodel";

export type ProjectStatus =
  | "intake"
  | "measuring"
  | "modeling"
  | "review"
  | "exported"
  | "printed"
  | "delivered"
  | "archived";

export type Dimensions = {
  width: string;
  depth: string;
  height: string;
};

export type ProjectFileStatus = {
  projectDir: string;
  version: string;
  expectedFolders: string[];
  files: {
    source: string[];
    stl: string[];
    notes: string[];
    manifests: string[];
    reviewReports: string[];
    printabilityReviews: string[];
    releaseNotes: string[];
    previews: string[];
  };
  hasScad: boolean;
  hasStl: boolean;
  hasPreviews: boolean;
  hasNotes: boolean;
  hasManifest: boolean;
  hasReviewReport: boolean;
  verificationStatus: "VERIFIED" | "NOT VERIFIED";
};

export type Quote = {
  designComplexity: string;
  estimatedPrintHours: string;
  estimatedMaterialGrams: string;
  materialCostEstimate: string;
  designFeeEstimate: string;
  printFeeEstimate: string;
  totalEstimate: string;
  customerNotes: string;
};

export type Project = {
  id: string;
  projectName: string;
  projectStem: string;
  customer: string;
  description: string;
  taskMode: TaskMode;
  printer: string;
  material: string;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
  supportFreePreferred: boolean;
  functionalPart: boolean;
  replacementPart: boolean;
  needsExactFit: boolean;
  measurementsNotes: string;
  referenceNotes: string;
  protectedInterfaces: string;
  lowConfidenceZones: string;
  customerDeadline: string;
  privateNotes: string;
  dimensions: Dimensions;
  printabilityChecklist: Record<string, boolean>;
  quote: Quote;
  commandHistory: CommandResult[];
  fileStatus: ProjectFileStatus;
};

export type CommandResult = {
  command: string;
  stdout: string;
  stderr: string;
  exitCode: number;
  ok: boolean;
  durationMs?: number;
  expectedFile?: string | null;
  expectedExists?: boolean;
  message?: string;
  action?: string;
  at?: string;
};

export type Settings = {
  statuses: ProjectStatus[];
  taskModes: TaskMode[];
  checklistKeys: string[];
  printers: Record<string, [number, number, number]>;
  materials: string[];
  nsfwModels: string[];
};
