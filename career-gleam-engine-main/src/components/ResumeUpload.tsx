import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import ResumeGradeGuide from "@/components/ResumeGradeGuide";
import { getResumeGradeSummary } from "@/lib/resume-grading";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: "uploading" | "success" | "error";
  score: number;
}

const ResumeUpload = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      processFiles(Array.from(e.target.files));
    }
  };

  const processFiles = (newFiles: File[]) => {
    const uploadedFiles: UploadedFile[] = newFiles.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      status: "uploading" as const,
      score: Math.min(96, Math.max(48, 58 + file.name.length * 2 + Math.round(Math.random() * 18))),
    }));

    setFiles((prev) => [...prev, ...uploadedFiles]);

    // Simulate upload
    uploadedFiles.forEach((file) => {
      setTimeout(() => {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === file.id ? { ...f, status: "success" as const } : f
          )
        );
      }, 1500 + Math.random() * 1000);
    });
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Upload Resumes
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Drag and drop your resume files or click to browse. We support PDF, DOC, and DOCX formats.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-3xl mx-auto"
        >
          {/* Upload Zone */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
              isDragging
                ? "border-accent bg-accent/5 scale-[1.02]"
                : "border-border hover:border-accent/50 hover:bg-muted/30"
            }`}
          >
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            
            <motion.div
              animate={{ scale: isDragging ? 1.1 : 1 }}
              className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-accent/10 mb-6"
            >
              <Upload className="w-10 h-10 text-accent" />
            </motion.div>

            <h3 className="text-xl font-semibold text-foreground mb-2">
              {isDragging ? "Drop files here" : "Drag & Drop Resumes"}
            </h3>
            <p className="text-muted-foreground mb-4">
              or click to browse from your computer
            </p>
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <FileText className="w-4 h-4" />
              <span>PDF, DOC, DOCX up to 10MB each</span>
            </div>
          </div>

          {/* Uploaded Files List */}
          <AnimatePresence>
            {files.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6 space-y-3"
              >
                {files.map((file) => (
                  (() => {
                    const grade = getResumeGradeSummary(file.score);
                    const GradeIcon = grade.icon;

                    return (
                      <motion.div
                        key={file.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        className={`rounded-2xl border border-border bg-card p-4 shadow-card transition-all ${file.status === "success" ? `${grade.surfaceClassName} ${grade.ringClassName}` : ""}`}
                      >
                        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                          <div className="flex items-center gap-4">
                            <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${file.status === "success" ? grade.surfaceClassName : "bg-accent/10"}`}>
                              <FileText className={`h-6 w-6 ${file.status === "success" ? grade.textClassName : "text-accent"}`} />
                            </div>
                            <div>
                              <p className="font-medium text-foreground">{file.name}</p>
                              <p className="text-sm text-muted-foreground">
                                {formatSize(file.size)}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-3">
                            {file.status === "uploading" && (
                              <Loader2 className="h-5 w-5 animate-spin text-accent" />
                            )}
                            {file.status === "success" && (
                              <>
                                <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold ${grade.badgeClassName}`}>
                                  <GradeIcon className="h-4 w-4" />
                                  <span>{grade.label}</span>
                                </div>
                                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/70">
                                  <Check className={`h-4 w-4 ${grade.textClassName}`} />
                                </div>
                              </>
                            )}
                            <button
                              onClick={() => removeFile(file.id)}
                              className="flex h-8 w-8 items-center justify-center rounded-full transition-colors hover:bg-muted"
                            >
                              <X className="h-4 w-4 text-muted-foreground" />
                            </button>
                          </div>
                        </div>

                        {file.status === "success" && (
                          <div className="mt-4">
                            <div className="mb-2 flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <GradeIcon className={`h-4 w-4 ${grade.textClassName}`} />
                                <span className={`text-sm font-semibold ${grade.textClassName}`}>
                                  {grade.band}
                                </span>
                              </div>
                              <span className="text-sm font-semibold text-foreground">{file.score}/100</span>
                            </div>
                            <div className="h-2 overflow-hidden rounded-full bg-white/70">
                              <div
                                className={`h-full rounded-full ${grade.progressClassName}`}
                                style={{ width: `${file.score}%` }}
                              />
                            </div>
                            <p className="mt-2 text-sm text-muted-foreground">{grade.description}</p>
                          </div>
                        )}
                      </motion.div>
                    );
                  })()
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Action Button */}
          {files.length > 0 && files.every((f) => f.status === "success") && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 text-center"
            >
              <Button variant="gradient" size="lg">
                Analyze & Grade {files.length} Resume{files.length > 1 ? "s" : ""}
              </Button>
            </motion.div>
          )}

          <ResumeGradeGuide />
        </motion.div>
      </div>
    </section>
  );
};

export default ResumeUpload;
