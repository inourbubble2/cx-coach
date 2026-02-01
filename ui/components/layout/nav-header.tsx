
import Link from "next/link"

export function NavHeader() {
    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container mx-auto flex h-14 items-center">
                <div className="mr-4 hidden md:flex">
                    <Link href="/" className="mr-6 flex items-center space-x-2">
                        <span className="hidden font-bold sm:inline-block">cx-coach</span>
                    </Link>
                    <nav className="flex items-center space-x-6 text-sm font-medium">
                        <Link href="/" className="transition-colors hover:text-foreground/80 text-foreground/60">
                            Dashboard
                        </Link>
                        <Link href="/history" className="transition-colors hover:text-foreground/80 text-foreground/60">
                            History
                        </Link>
                        <Link href="/faq" className="transition-colors hover:text-foreground/80 text-foreground/60">
                            FAQ Management
                        </Link>
                    </nav>
                </div>
            </div>
        </header>
    )
}
