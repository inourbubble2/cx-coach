"use client"

import useSWR from 'swr'
import { API, fetcher } from '@/lib/api'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Loader2, ArrowRight } from 'lucide-react'
import { AnalysisResult } from '@/types'

// HistoryListResponse is imported from types

import { HistoryListResponse } from '@/types'

export default function HistoryPage() {
    const { data: historyData, error, isLoading } = useSWR<HistoryListResponse>('/history?limit=50', fetcher)

    if (isLoading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex h-[50vh] items-center justify-center text-destructive">
                Error loading history. Is the API server running?
            </div>
        )
    }

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Analysis History</h1>
                <p className="text-muted-foreground">Review past consultations and track performance improvements.</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {historyData?.items?.map((item) => (
                    <Link key={item.request_id} href={`/history/${item.request_id}`} className="block h-full">
                        <Card className="h-full hover:bg-muted/50 transition-colors cursor-pointer">
                            <CardHeader className="pb-2">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <CardTitle className="text-lg">
                                            Score: <span className={
                                                item.total_score >= 90 ? "text-green-600" :
                                                    item.total_score >= 80 ? "text-blue-600" :
                                                        item.total_score >= 70 ? "text-amber-600" : "text-destructive"
                                            }>{item.total_score}</span>
                                        </CardTitle>
                                        <CardDescription className="text-xs mt-1">
                                            {item.analyzed_at ? new Date(item.analyzed_at).toLocaleString() : 'Date unknown'}
                                        </CardDescription>
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <span className="text-2xl font-bold text-muted-foreground">{item.grade}</span>
                                        <span className="text-xs text-muted-foreground">Grade</span>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="text-sm text-muted-foreground">
                                    Click for detailed analysis
                                </div>
                            </CardContent>
                        </Card>
                    </Link>
                ))}
                {historyData?.items?.length === 0 && (
                    <div className="col-span-full text-center py-20 text-muted-foreground">
                        No analysis history found. <Link href="/analysis" className="underline">Start a new analysis</Link>.
                    </div>
                )}
            </div>
        </div>
    )
}
