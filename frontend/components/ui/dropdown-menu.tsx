import * as React from "react"
import { cn } from "@/lib/utils"

export function DropdownMenu({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = React.useState(false)
  
  return (
    <div className="relative inline-block text-left" onBlur={() => setTimeout(() => setOpen(false), 200)}>
      {React.Children.map(children, child => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, { open, setOpen })
        }
        return child
      })}
    </div>
  )
}

export function DropdownMenuTrigger({ children, open, setOpen, asChild }: any) {
  return (
    <div onClick={() => setOpen(!open)} className="inline-flex cursor-pointer">
      {children}
    </div>
  )
}

export function DropdownMenuContent({ children, className, open, align = "left" }: any) {
  if (!open) return null;
  return (
    <div 
      className={cn(
        "absolute z-50 mt-2 min-w-[8rem] rounded-md border bg-popover p-1 text-popover-foreground shadow-md animate-in fade-in-80",
        align === "right" ? "right-0" : "left-0",
        className
      )}
    >
      {children}
    </div>
  )
}

export function DropdownMenuItem({ children, className, onClick }: any) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
        className
      )}
    >
      {children}
    </div>
  )
}

export function DropdownMenuLabel({ children, className }: any) {
  return (
    <div className={cn("px-2 py-1.5 text-sm font-semibold", className)}>
      {children}
    </div>
  )
}

export function DropdownMenuSeparator({ className }: any) {
  return (
    <div className={cn("-mx-1 my-1 h-px bg-muted", className)} />
  )
}
