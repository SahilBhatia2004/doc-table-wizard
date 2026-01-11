const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ExtractionResult {
  document_id: number;
  filename: string;
  is_scanned: boolean;
  tables_extracted: number;
  tables: ExtractedTable[];
}

export interface ExtractedTable {
  id: number;
  name: string;
  headers: string[];
  row_count: number;
  preview_rows: Record<string, string>[];
}

export interface Document {
  id: number;
  filename: string;
  is_scanned: boolean;
  table_count: number;
  created_at: string;
}

export interface HealthCheck {
  status: string;
  database: string;
}

export async function checkHealth(): Promise<HealthCheck> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("API is not available");
  }
  return response.json();
}

export async function extractTables(file: File): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/extract`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || "Failed to extract tables");
  }

  return response.json();
}

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${API_BASE_URL}/documents`);
  if (!response.ok) {
    throw new Error("Failed to fetch documents");
  }
  return response.json();
}

export async function getTableRows(tableId: number): Promise<Record<string, any>[]> {
  const response = await fetch(`${API_BASE_URL}/tables/${tableId}/rows`);
  if (!response.ok) {
    throw new Error("Failed to fetch table rows");
  }
  return response.json();
}
