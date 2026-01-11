import { useState } from "react";
import { FileUp, Table2, Database } from "lucide-react";
import { FileUpload } from "@/components/FileUpload";
import { ExtractionResults } from "@/components/ExtractionResults";
import { ConnectionStatus } from "@/components/ConnectionStatus";
import { extractTables, type ExtractionResult } from "@/lib/api";

export default function Index() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExtractionResult | null>(null);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setResult(null);

    try {
      const extractionResult = await extractTables(file);
      setResult(extractionResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Table2 className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h1 className="font-semibold text-lg text-foreground">PDF Table Extractor</h1>
              <p className="text-xs text-muted-foreground">Powered by Docling</p>
            </div>
          </div>
          <ConnectionStatus />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        {!result ? (
          <div className="max-w-2xl mx-auto">
            {/* Hero Section */}
            <div className="text-center mb-10">
              <h2 className="text-3xl font-bold text-foreground mb-3">
                Extract Tables from PDFs
              </h2>
              <p className="text-muted-foreground max-w-md mx-auto">
                Upload a PDF document to automatically extract structured tables. 
                Supports both digital and scanned documents with OCR.
              </p>
            </div>

            {/* Upload Section */}
            <FileUpload 
              onUpload={handleUpload} 
              isUploading={isUploading} 
              error={error}
            />

            {/* Features */}
            <div className="grid grid-cols-3 gap-6 mt-12 pt-8 border-t border-border">
              <Feature 
                icon={<FileUp className="w-5 h-5" />}
                title="Auto OCR"
                description="Scanned PDFs are automatically detected and processed"
              />
              <Feature 
                icon={<Table2 className="w-5 h-5" />}
                title="Smart Extraction"
                description="Docling accurately extracts complex table structures"
              />
              <Feature 
                icon={<Database className="w-5 h-5" />}
                title="PostgreSQL Storage"
                description="Tables stored in row-column format for easy queries"
              />
            </div>
          </div>
        ) : (
          <div>
            <button
              onClick={handleReset}
              className="mb-8 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Upload another document
            </button>
            <ExtractionResults result={result} />
          </div>
        )}
      </main>
    </div>
  );
}

function Feature({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-10 h-10 mx-auto mb-3 rounded-lg bg-muted flex items-center justify-center text-muted-foreground">
        {icon}
      </div>
      <h3 className="font-medium text-sm text-foreground mb-1">{title}</h3>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  );
}
