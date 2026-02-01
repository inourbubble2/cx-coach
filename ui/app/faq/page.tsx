"use client"

import useSWR, { mutate } from 'swr'
import { API, fetcher } from '@/lib/api'
import { FAQDocument } from '@/types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Loader2, Trash2, FileText, Globe } from 'lucide-react'
import { toast } from "sonner"
import { FaqUploadDialog } from '@/components/analysis/faq-upload-dialog'

// Define response type locally or import if available
interface FAQListResponse {
    items: FAQDocument[]
    count: number
}

export default function FAQPage() {
    const { data: faqData, error, isLoading, mutate } = useSWR<FAQListResponse>('/faq/list', fetcher)
    const faqs = faqData?.items

    const handleToggle = async (id: string, currentStatus: boolean) => {
        if (!faqs || !faqData) return

        // Optimistic update
        const updatedFaqs = faqs.map(f => f.id === id ? { ...f, is_active: !currentStatus } : f)
        const optimisticData = { ...faqData, items: updatedFaqs }

        try {
            // Update local state immediately
            // Note: Since we use bound mutate, we update the data for the current key
            await mutate(optimisticData, false)

            // API call
            await API.toggleFAQActive(id, !currentStatus)
            toast.success("Status Updated", { description: "FAQ visibility changed." })

            // Revalidate to sync with server
            await mutate()
        } catch (err) {
            toast.error("Error", { description: "Failed to update status." })
            await mutate() // Revert on error
        }
    }

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to delete this FAQ?")) return

        try {
            await API.deleteFAQ(id)
            toast.success("Deleted", { description: "FAQ document removed." })
            await mutate()
        } catch (err) {
            toast.error("Error", { description: "Failed to delete FAQ." })
        }
    }

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
                Error loading FAQs.
            </div>
        )
    }

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">FAQ Knowledge Base</h1>
                    <p className="text-muted-foreground">Manage documents used for AI context generation.</p>
                </div>
                <FaqUploadDialog />
            </div>

            <div className="grid gap-4">
                {faqs?.map((faq) => (
                    <Card key={faq.id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 gap-4">
                        <div className="flex items-start space-x-4">
                            <div className="mt-1">
                                {faq.file_type === 'url' ? <Globe className="h-5 w-5 text-blue-500" /> : <FileText className="h-5 w-5 text-orange-500" />}
                            </div>
                            <div>
                                <CardTitle className="text-base font-medium leading-none mb-1">
                                    {faq.filename || "Untitled Document"}
                                </CardTitle>
                                <p className="text-sm text-muted-foreground line-clamp-1 max-w-md">
                                    {faq.content_preview || "No content preview"}
                                </p>
                                <div className="flex items-center gap-2 mt-2">
                                    <Badge variant="outline" className="text-xs uppercase">{faq.file_type}</Badge>
                                    <span className="text-xs text-muted-foreground">
                                        {faq.created_at ? new Date(faq.created_at).toLocaleDateString() : 'Date unknown'}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4 self-end sm:self-center">
                            <div className="flex items-center space-x-2">
                                <Switch
                                    checked={faq.is_active}
                                    onCheckedChange={() => handleToggle(faq.id, faq.is_active)}
                                />
                                <span className="text-sm w-12">{faq.is_active ? "Active" : "Off"}</span>
                            </div>
                            <Button variant="ghost" size="icon" onClick={() => handleDelete(faq.id)} className="text-muted-foreground hover:text-destructive">
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    </Card>
                ))}
                {faqs?.length === 0 && (
                    <div className="text-center py-20 text-muted-foreground border rounded-lg border-dashed">
                        No FAQs found. Add some documents to improve AI accuracy.
                    </div>
                )}
            </div>
        </div>
    )
}
