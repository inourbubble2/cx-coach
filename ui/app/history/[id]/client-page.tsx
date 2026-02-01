"use client"

import useSWR from 'swr'
import { fetcher } from '@/lib/api'
import { AnalysisResultView } from "@/components/analysis/analysis-result-view"
import { KPIInput } from "@/components/analysis/kpi-input"
import { Button } from "@/components/ui/button"
import { ChevronLeft, Loader2 } from "lucide-react"
import Link from "next/link"
import { AnalysisResult, Conversation } from '@/types'

// Response type combining Analysis and Conversation
interface HistoryDetailResponse extends AnalysisResult {
    conversation_data?: Conversation
}

interface HistoryDetailClientProps {
    id: string
}

export function HistoryDetailClient({ id }: HistoryDetailClientProps) {
    console.log('HistoryDetailClient ID:', id);
    const { data: result, error, isLoading } = useSWR<HistoryDetailResponse>(`/history/${id}`, fetcher)

    if (isLoading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    if (error || !result) {
        return (
            <div className="container py-20 text-center">
                <h2 className="text-xl font-semibold text-destructive mb-4">Error loading analysis</h2>
                <Link href="/history">
                    <Button>Back to History</Button>
                </Link>
            </div>
        )
    }

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex justify-between items-center">
                <div className="flex items-center space-x-4">
                    <Link href="/history">
                        <Button variant="ghost" size="icon">
                            <ChevronLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">Analysis Details</h1>
                    </div>
                </div>
                <div className="text-sm text-muted-foreground">
                    {result.analyzed_at && new Date(result.analyzed_at).toLocaleString()}
                </div>
            </div>

            {/* 2-Column Layout */}
            <div className="grid gap-6 lg:grid-cols-3">
                {/* Main Content (2/3) */}
                <div className="lg:col-span-2">
                    <AnalysisResultView result={result} conversation={result.conversation_data} />
                </div>

                {/* Sidebar (1/3) */}
                <div className="space-y-6">
                    <KPIInput
                        requestId={result.request_id!}
                        initialResolved={result.is_resolved}
                        initialCsat={result.csat_score}
                    />
                </div>
            </div>
        </div>
    )
}
