import { CheckCircle2, FileText, Table2, Eye } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ExtractionResult, ExtractedTable } from "@/lib/api";

interface ExtractionResultsProps {
  result: ExtractionResult;
}

export function ExtractionResults({ result }: ExtractionResultsProps) {
  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 animate-slide-up">
      {/* Summary Card */}
      <Card className="border-success/30 bg-success/5">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0">
              <CheckCircle2 className="w-6 h-6 text-success" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-lg text-foreground">
                Extraction Complete
              </h3>
              <div className="flex flex-wrap items-center gap-3 mt-2">
                <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  <FileText className="w-4 h-4" />
                  <span className="truncate max-w-[200px]">{result.filename}</span>
                </div>
                <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  <Table2 className="w-4 h-4" />
                  <span>{result.tables_extracted} tables found</span>
                </div>
                {result.is_scanned && (
                  <Badge variant="secondary" className="text-xs">
                    OCR Applied
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tables */}
      {result.tables.length > 0 ? (
        <div className="space-y-6">
          {result.tables.map((table) => (
            <TablePreview key={table.id} table={table} />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
              <Table2 className="w-6 h-6 text-muted-foreground" />
            </div>
            <p className="text-muted-foreground">
              No tables were found in this document
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function TablePreview({ table }: { table: ExtractedTable }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Table2 className="w-5 h-5 text-primary" />
            {table.name}
          </CardTitle>
          <Badge variant="outline" className="font-mono text-xs">
            {table.row_count} rows
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                {table.headers.map((header, idx) => (
                  <th key={idx}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.preview_rows.map((row, rowIdx) => (
                <tr key={rowIdx}>
                  {table.headers.map((header, cellIdx) => (
                    <td key={cellIdx}>{row[header] || "—"}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {table.row_count > 5 && (
          <p className="text-xs text-muted-foreground mt-3 text-center">
            Showing 5 of {table.row_count} rows • Full data saved to database
          </p>
        )}
      </CardContent>
    </Card>
  );
}
