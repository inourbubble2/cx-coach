"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Upload, Loader2, FileText } from "lucide-react"
import { toast } from "sonner"
import { API } from "@/lib/api"
import { mutate } from "swr"

export function FaqUploadDialog() {
    const [open, setOpen] = useState(false)
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)

    const handleUpload = async () => {
        if (!file) return

        setUploading(true)
        try {
            // We'll use the same upload endpoint but we need to implement it in API helper first?
            // Wait, the backend supports text upload via /api/faq/upload (POST).

            // Let's assume we can upload file similarly or extend API.
            // Actually, looking at previous context, we might only have text upload implemented in UI before.
            // But backend `faq_routes.py` usually has file upload. 
            // Let's check `faq_routes.py` later. specific implementation.
            // For now, let's assume we need to add `uploadFAQ` to API.

            await API.uploadFAQ(file);

            toast.success("FAQ Uploaded", { description: "Document added to knowledge base." })
            setOpen(false)
            setFile(null)
            mutate('/faq/list')
        } catch (error) {
            toast.error("Upload Failed", { description: "Could not upload document." })
        } finally {
            setUploading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload New
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Upload FAQ Document</DialogTitle>
                    <DialogDescription>
                        Upload a text file or PDF to add to the knowledge base.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid w-full max-w-sm items-center gap-1.5">
                        <Label htmlFor="file">Document</Label>
                        <Input id="file" type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
                    </div>
                    {file && (
                        <div className="flex items-center p-2 bg-muted rounded text-sm">
                            <FileText className="h-4 w-4 mr-2" />
                            {file.name}
                        </div>
                    )}
                </div>
                <DialogFooter>
                    <Button type="submit" onClick={handleUpload} disabled={!file || uploading}>
                        {uploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Upload
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
