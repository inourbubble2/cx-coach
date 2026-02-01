"use client"

import { AnalysisResult, Conversation } from "@/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { CheckCircle2, AlertTriangle, MessageSquare } from "lucide-react"

interface AnalysisResultViewProps {
    result: AnalysisResult
    conversation?: Conversation
}

export function AnalysisResultView({ result, conversation }: AnalysisResultViewProps) {

    const scoreData = [
        { name: 'Info', score: result.clarification_score },
        { name: 'Empathy', score: result.empathy_tone_score },
        { name: 'Solution', score: result.solution_accuracy_score },
        { name: 'Action', score: result.actionability_score },
        { name: 'Close', score: result.confirmation_closure_score },
        { name: 'Compliance', score: result.compliance_safety_score },
    ]

    const getScoreColor = (score: number) => {
        if (score >= 9) return "#22c55e" // green-500
        if (score >= 7) return "#3b82f6" // blue-500
        if (score >= 5) return "#eab308" // yellow-500
        return "#ef4444" // red-500
    }

    return (
        <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-primary/20 bg-primary/5">
                    <CardHeader>
                        <CardTitle className="text-2xl text-primary">Total Score</CardTitle>
                        <CardDescription>Overall performance rating</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-end space-x-2">
                            <span className="text-6xl font-bold tracking-tighter">
                                {result.total_score}
                            </span>
                            <span className="text-xl text-muted-foreground mb-2">/100</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>Score Breakdown</CardTitle>
                        <CardDescription>Detailed metrics by category</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {scoreData.map((item) => (
                                <div key={item.name} className="space-y-1">
                                    <div className="flex justify-between text-sm">
                                        <span className="font-medium">{item.name}</span>
                                        <span className="text-muted-foreground">{item.score}/10</span>
                                    </div>
                                    <Progress
                                        value={item.score * 10}
                                        className="h-2"
                                        indicatorColor={getScoreColor(item.score)}
                                    />
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Tabs defaultValue="feedback" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="feedback">Feedback & Coaching</TabsTrigger>
                    <TabsTrigger value="transcript">Transcript Analysis</TabsTrigger>
                </TabsList>

                <TabsContent value="feedback" className="space-y-4 mt-4">
                    {/* Strengths */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center text-green-600">
                                <CheckCircle2 className="mr-2 h-5 w-5" /> Strengths
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="list-disc pl-5 space-y-1">
                                {result.strengths.map((str, i) => (
                                    <li key={i}>{str}</li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>

                    {/* Improvements */}
                    <div className="grid gap-4">
                        {result.improvements.map((imp, i) => (
                            <Card key={i} className="border-l-4 border-l-orange-400">
                                <CardHeader className="pb-2">
                                    <div className="flex justify-between items-start">
                                        <CardTitle className="text-base font-semibold">{imp.issue}</CardTitle>
                                        <Badge variant={imp.priority === 'critical' ? 'destructive' : 'secondary'}>
                                            {imp.priority}
                                        </Badge>
                                    </div>
                                </CardHeader>
                                <CardContent className="grid gap-4 sm:grid-cols-2 text-sm">
                                    <div className="bg-muted p-3 rounded-md">
                                        <span className="font-semibold text-muted-foreground block mb-1">Original</span>
                                        &quot;{imp.original}&quot;
                                    </div>
                                    <div className="bg-primary/10 p-3 rounded-md text-foreground">
                                        <span className="font-semibold text-primary block mb-1">Better Approach</span>
                                        &quot;{imp.suggested}&quot;
                                    </div>
                                    <div className="col-span-2 text-muted-foreground italic">
                                        💡 {imp.reason}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>

                    <Card className="bg-muted/50">
                        <CardHeader>
                            <CardTitle className="flex items-center text-blue-600">
                                <MessageSquare className="mr-2 h-5 w-5" /> Overall Feedback
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="leading-relaxed">{result.overall_feedback}</p>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="transcript">
                    <Card>
                        <CardContent className="p-0">
                            <ScrollArea className="h-[600px] w-full p-4">
                                <div className="space-y-4">
                                    {conversation?.messages.map((msg, i) => (
                                        <div key={i} className={cn(
                                            "flex flex-col max-w-[80%] rounded-lg p-3",
                                            msg.role === 'agent'
                                                ? "ml-auto bg-primary text-primary-foreground"
                                                : "bg-muted mr-auto"
                                        )}>
                                            <span className="text-xs font-bold mb-1 opacity-70 uppercase">
                                                {msg.role}
                                            </span>
                                            <p className="text-sm">{msg.content}</p>
                                        </div>
                                    ))}
                                    {!conversation && (
                                        <div className="text-center text-muted-foreground py-10">
                                            No transcript available.
                                        </div>
                                    )}
                                </div>
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}

function cn(...classes: (string | undefined | null | boolean)[]) {
    return classes.filter(Boolean).join(' ')
}
