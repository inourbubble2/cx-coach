"use client"

import Link from "next/link"
import { Upload, FileText, BarChart3, Clock, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import useSWR from 'swr'
import { fetcher } from '@/lib/api'
import { DashboardStats, HistoryListResponse } from "@/types"

export default function Home() {
  const { data: stats, error: statsError } = useSWR<DashboardStats>('/home/stats', fetcher)
  const { data: history } = useSWR<HistoryListResponse>('/history?limit=5', fetcher)

  console.log('Stats Response:', stats)
  console.log('Stats Error:', statsError)

  return (
    <div className="flex min-h-screen flex-col">


      <main className="container mx-auto flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <div className="flex items-center space-x-2">
            <Link href="/analysis">
              <Button>
                <Upload className="mr-2 h-4 w-4" />
                Upload New Analysis
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Analyzed</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_analyzed || 0}</div>
              <p className="text-xs text-muted-foreground">Lifetime analysis count</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Score</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.avg_score || 0}</div>
              <p className="text-xs text-muted-foreground">Average quality score</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Resolution Rate</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.resolution_rate || 0}%</div>
              <p className="text-xs text-muted-foreground">Issues marked resolved</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Processing Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.avg_analysis_seconds || 0}s</div>
              <p className="text-xs text-muted-foreground">Upload to Result</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Card className="col-span-4">
            <CardHeader>
              <CardTitle>Overview</CardTitle>
            </CardHeader>
            <CardContent className="pl-2">
              <div className="h-[240px] flex items-center justify-center text-muted-foreground bg-muted/20 rounded-md">
                Recent Activity Chart (Coming Soon)
              </div>
            </CardContent>
          </Card>
          <Card className="col-span-3">
            <CardHeader>
              <CardTitle>Recent Analysis</CardTitle>
              <CardDescription>
                Recent consultations processed.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-8">
                {history?.items?.map((item: any) => {
                  console.log('Dashboard Item:', item);
                  return (
                    <Link key={item.request_id} href={`/history/${item.request_id}`} className="block">
                      <div className="flex items-center p-2 rounded-md hover:bg-muted/50 transition-colors">
                        <div className="space-y-1">
                          <p className="text-sm font-medium leading-none truncate max-w-[150px]">{item.request_id.substring(0, 8)}...</p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(item.analyzed_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className={`ml-auto font-medium ${item.total_score >= 90 ? 'text-green-600' : 'text-foreground'}`}>
                          {item.total_score} pts
                        </div>
                      </div>
                    </Link>
                  )
                })}
                {!history?.items?.length && (
                  <div className="text-sm text-muted-foreground text-center">No recent history</div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
