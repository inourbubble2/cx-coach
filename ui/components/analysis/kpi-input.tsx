"use client"

import { useState } from "react"
import { Check, Star, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { API } from "@/lib/api"
import { toast } from "sonner"

interface KPIInputProps {
    requestId: string
    initialResolved?: boolean
    initialCsat?: number
}

export function KPIInput({ requestId, initialResolved, initialCsat }: KPIInputProps) {
    const [resolved, setResolved] = useState(initialResolved || false)
    const [csat, setCsat] = useState<string>(initialCsat?.toString() || "")
    const [loading, setLoading] = useState(false)

    const handleSave = async () => {
        setLoading(true)
        try {
            await API.updateFeedback(requestId, {
                is_resolved: resolved,
                csat_score: csat ? parseInt(csat) : undefined
            })
            toast.success("KPI Updated", {
                description: "Perfomance metrics saved successfully.",
            })
        } catch (error) {
            toast.error("Error", {
                description: "Failed to save metrics.",
            })
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex flex-col space-y-4 p-4 border rounded-lg bg-card">
            <h3 className="font-semibold flex items-center">
                Performance Metrics
            </h3>

            <div className="grid gap-4 sm:grid-cols-2 items-end">
                <div className="space-y-2">
                    <Label className="flex items-center space-x-2">
                        <Check className="w-4 h-4" />
                        <span>Issue Resolved?</span>
                    </Label>
                    <div className="flex items-center space-x-2 h-10">
                        <Switch
                            checked={resolved}
                            onCheckedChange={setResolved}
                        />
                        <span className="text-sm text-muted-foreground">
                            {resolved ? "Yes, Resolved" : "Not Resolved"}
                        </span>
                    </div>
                </div>

                <div className="space-y-2">
                    <Label className="flex items-center space-x-2">
                        <Star className="w-4 h-4" />
                        <span>CSAT Score</span>
                    </Label>
                    <Select value={csat} onValueChange={setCsat}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select score" />
                        </SelectTrigger>
                        <SelectContent>
                            {[5, 4, 3, 2, 1].map((score) => (
                                <SelectItem key={score} value={score.toString()}>
                                    {score} Stars {score === 5 && "(Excellent)"}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <Button onClick={handleSave} disabled={loading} className="w-full sm:w-auto self-end">
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Save Metrics
            </Button>
        </div>
    )
}
