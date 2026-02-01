import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
    return (
        <div className="flex h-[60vh] w-full flex-col items-center justify-center space-y-4 text-center">
            <h2 className="text-4xl font-extrabold tracking-tight lg:text-5xl">404</h2>
            <p className="text-xl text-muted-foreground">Page not found.</p>
            <Link href="/">
                <Button variant="default" size="lg">
                    Return Home
                </Button>
            </Link>
        </div>
    );
}
