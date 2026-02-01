import { HistoryDetailClient } from "./client-page"

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params
    // Note: In a real app we might fetch this data. 
    // For now, we'll just use the ID in the title for performance/simplicity.
    return {
        title: `Analysis ${id.substring(0, 8)} - CX Coach`,
        description: `Review analysis details for request ${id}`,
    }
}

export default async function HistoryDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params
    return <HistoryDetailClient id={id} />
}
