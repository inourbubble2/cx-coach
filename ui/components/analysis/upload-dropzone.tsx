"use client"

import { useState, useCallback } from "react"
import { Upload, FileText, Check, AlertCircle, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface UploadDropzoneProps {
    onUpload: (file: File) => Promise<void>
}

export function UploadDropzone({ onUpload }: UploadDropzoneProps) {
    const [isDragOver, setIsDragOver] = useState(false)
    const [file, setFile] = useState<File | null>(null)
    const [isUploading, setIsUploading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(true)
    }, [])

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(false)
    }, [])

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(false)
        const droppedFile = e.dataTransfer.files[0]
        if (droppedFile) {
            setFile(droppedFile)
            setError(null)
        }
    }, [])

    const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0]
        if (selectedFile) {
            setFile(selectedFile)
            setError(null)
        }
    }, [])

    const handleUploadClick = async () => {
        if (!file) return

        setIsUploading(true)
        setError(null)

        try {
            await onUpload(file)
        } catch (err) {
            setError("Upload failed. Please try again.")
            console.error(err)
        } finally {
            setIsUploading(false)
        }
    }

    return (
        <div className="w-full max-w-md mx-auto">
            <div
                className={cn(
                    "relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer transition-colors",
                    isDragOver ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:bg-muted/50",
                    error ? "border-destructive/50 bg-destructive/5" : ""
                )}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    onChange={handleFileChange}
                    accept=".txt,.csv,.json,.mp3,.wav,.m4a"
                />

                <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center px-4">
                    {file ? (
                        <div className="flex flex-col items-center">
                            <FileText className="w-10 h-10 mb-3 text-primary" />
                            <p className="mb-2 text-sm text-foreground font-medium truncate max-w-[200px]">
                                {file.name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                                {(file.size / 1024).toFixed(1)} KB
                            </p>
                        </div>
                    ) : (
                        <>
                            <Upload className="w-10 h-10 mb-3 text-muted-foreground" />
                            <p className="mb-2 text-sm text-foreground">
                                <span className="font-semibold">Click to upload</span> or drag and drop
                            </p>
                            <p className="text-xs text-muted-foreground">
                                TXT, CSV, JSON or Audio files (max 10MB)
                            </p>
                        </>
                    )}
                </div>
            </div>

            {error && (
                <div className="flex items-center mt-2 text-sm text-destructive">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {error}
                </div>
            )}

            <Button
                className="w-full mt-4"
                disabled={!file || isUploading}
                onClick={handleUploadClick}
            >
                {isUploading ? (
                    <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                    </>
                ) : (
                    "Start Analysis"
                )}
            </Button>
        </div>
    )
}
