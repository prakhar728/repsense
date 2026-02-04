"use client";

import { useState, useCallback, DragEvent, ChangeEvent } from "react";
import { Button } from "./ui/Button";
import { Card, CardContent } from "./ui/Card";
import { Spinner } from "./ui/Spinner";
import { uploadCSV } from "../lib/api";
import { ParsedCSVData } from "../lib/mockData";

interface UploadScreenProps {
  userEmail: string;
  onContinue: (data: ParsedCSVData) => void;
  onBack: () => void;
}

export function UploadScreen({ userEmail, onContinue, onBack }: UploadScreenProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [uploadDone, setUploadDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith(".csv")) {
      processFile(droppedFile);
    }
  }, [userEmail]);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      processFile(selectedFile);
    }
  };

  const processFile = async (selectedFile: File) => {
    setFile(selectedFile);
    setIsParsing(true);
    setUploadDone(false);
    setError(null);

    try {
      await uploadCSV(userEmail, selectedFile);
      setUploadDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsParsing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-neutral-400 hover:text-white transition-colors mb-6 group"
          aria-label="Go back"
        >
          <svg
            className="w-5 h-5 group-hover:-translate-x-1 transition-transform"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          <span className="text-sm font-medium">Back</span>
        </button>

        <h1 className="text-3xl font-bold text-white mb-2">
          Upload your workout data
        </h1>
        <p className="text-neutral-400">
          Upload your Hevy workout export (CSV)
        </p>
      </div>

      {/* Upload Area */}
      <Card variant="elevated" padding="none" className="overflow-hidden">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            relative p-12 border-2 border-dashed rounded-2xl transition-all duration-200
            ${
              isDragging
                ? "border-emerald-500 bg-emerald-500/10"
                : "border-neutral-700 hover:border-neutral-600"
            }
            ${isParsing ? "pointer-events-none opacity-60" : ""}
          `}
        >
          {isParsing ? (
            <div className="text-center">
              <Spinner size="lg" className="mx-auto mb-4" />
              <p className="text-white font-medium">Uploading & analyzing...</p>
              <p className="text-neutral-400 text-sm mt-1">
                Generating your training profile
              </p>
            </div>
          ) : uploadDone ? (
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-emerald-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <p className="text-white font-medium mb-1">{file?.name}</p>
              <p className="text-neutral-400 text-sm">
                Profile generated successfully
              </p>
            </div>
          ) : error ? (
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-red-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <p className="text-white font-medium mb-1">Upload failed</p>
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          ) : (
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-neutral-800 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-neutral-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <p className="text-white font-medium mb-1">
                Drag & drop your CSV file here
              </p>
              <p className="text-neutral-400 text-sm mb-4">
                or click to browse files
              </p>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="inline-flex items-center justify-center px-3 py-1.5 text-sm font-semibold rounded-xl bg-transparent border border-neutral-700 hover:border-neutral-500 text-neutral-300 hover:text-white cursor-pointer transition-all active:scale-[0.98]"
              >
                Browse files
              </label>
            </div>
          )}
        </div>
      </Card>

      {/* Continue button after successful upload */}
      {uploadDone && (
        <Card variant="elevated" className="mt-6 animate-in slide-in-from-bottom-4 fade-in duration-300">
          <CardContent>
            <Button
              variant="primary"
              size="lg"
              className="w-full"
              onClick={() =>
                onContinue({
                  workoutsDetected: 0,
                  weeksCovered: 0,
                  avgSessionsPerWeek: 0,
                  topLifts: [],
                })
              }
            >
              Continue
              <svg
                className="w-5 h-5 ml-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Helper text */}
      {!file && (
        <p className="text-center text-neutral-500 text-sm mt-6">
          Export your data from Hevy: Settings &rarr; Export Data &rarr; Download CSV
        </p>
      )}
    </div>
  );
}
