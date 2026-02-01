"use client"

import { useState } from "react"
import { UploadDropzone } from "@/components/analysis/upload-dropzone"
import { AnalysisResultView } from "@/components/analysis/analysis-result-view"
import { AnalysisResult } from "@/types"
import { API } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"
import Link from "next/link"

export default function AnalysisPage() {
    const [result, setResult] = useState<AnalysisResult | null>(null)

    const handleUpload = async (file: File) => {
        try {
            const data = await API.uploadFile(file)
            setResult(data)
        } catch (error) {
            console.error("Analysis failed", error)
            throw error // Re-throw for Dropzone to handle
        }
    }

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex items-center space-x-4">
                <Link href="/">
                    <Button variant="ghost" size="icon">
                        <ChevronLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Analysis Studio</h1>
                    <p className="text-muted-foreground">Upload a conversation to receive instant AI coaching.</p>
                </div>
            </div>

            {!result ? (
                <div className="mt-20">
                    <UploadDropzone onUpload={handleUpload} />

                    <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                        <div className="p-6 bg-muted/50 rounded-lg">
                            <h3 className="font-semibold mb-2">1. Upload</h3>
                            <p className="text-sm text-muted-foreground">Support for text, JSON, CSV logs or audio recordings.</p>
                        </div>
                        <div className="p-6 bg-muted/50 rounded-lg">
                            <h3 className="font-semibold mb-2">2. Analyze</h3>
                            <p className="text-sm text-muted-foreground">AI evaluates 6 key dimensions of consultation quality.</p>
                        </div>
                        <div className="p-6 bg-muted/50 rounded-lg">
                            <h3 className="font-semibold mb-2">3. Improve</h3>
                            <p className="text-sm text-muted-foreground">Get actionable feedback and specific coaching tips.</p>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold">Analysis Results</h2>
                        <Button variant="outline" onClick={() => setResult(null)}>Analyze Another</Button>
                    </div>
                    <AnalysisResultView result={result} />
                </div>
            )}
        </div>
    )
}
