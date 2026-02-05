"use client";

import { useState, useCallback, DragEvent, ChangeEvent } from "react";
import { Spinner } from "./ui/Spinner";
import { uploadCSV } from "../lib/api";

interface UploadModalProps {
  userEmail: string;
  isOpen: boolean;
  onClose: () => void;
}

export function UploadModal({ userEmail, isOpen, onClose }: UploadModalProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [uploadDone, setUploadDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetState = () => {
    setFile(null);
    setIsParsing(false);
    setUploadDone(false);
    setError(null);
    setIsDragging(false);
  };

  const handleClose = () => {
    resetState();
    onClose();
  };

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile && droppedFile.name.endsWith(".csv")) {
        processFile(droppedFile);
      }
    },
    [userEmail]
  );

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

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="bg-neutral-900 border border-neutral-800 rounded-2xl w-full max-w-lg shadow-xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-neutral-800">
            <h2 className="text-lg font-semibold text-white">
              Update Workout Data
            </h2>
            <button
              onClick={handleClose}
              className="p-1.5 text-neutral-400 hover:text-white transition-colors rounded-lg hover:bg-neutral-800"
            >
              <svg
                className="w-5 h-5"
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
            </button>
          </div>

          {/* Content */}
          <div className="p-4">
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
                relative p-8 border-2 border-dashed rounded-xl transition-all duration-200
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
                  <p className="text-white font-medium">
                    Uploading & analyzing...
                  </p>
                  <p className="text-neutral-400 text-sm mt-1">
                    Updating your training profile
                  </p>
                </div>
              ) : uploadDone ? (
                <div className="text-center">
                  <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <svg
                      className="w-7 h-7 text-emerald-500"
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
                    Profile updated successfully
                  </p>
                </div>
              ) : error ? (
                <div className="text-center">
                  <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                    <svg
                      className="w-7 h-7 text-red-500"
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
                  <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-neutral-800 flex items-center justify-center">
                    <svg
                      className="w-7 h-7 text-neutral-400"
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
                    id="modal-file-upload"
                  />
                  <label
                    htmlFor="modal-file-upload"
                    className="inline-flex items-center justify-center px-3 py-1.5 text-sm font-semibold rounded-xl bg-transparent border border-neutral-700 hover:border-neutral-500 text-neutral-300 hover:text-white cursor-pointer transition-all active:scale-[0.98]"
                  >
                    Browse files
                  </label>
                </div>
              )}
            </div>

            <p className="text-center text-neutral-500 text-xs mt-4">
              Export your data from Hevy: Settings &rarr; Export Data &rarr;
              Download CSV
            </p>
          </div>

          {/* Footer */}
          {uploadDone && (
            <div className="p-4 border-t border-neutral-800">
              <button
                onClick={handleClose}
                className="w-full px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-white font-medium transition-all active:scale-[0.98]"
              >
                Done
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
