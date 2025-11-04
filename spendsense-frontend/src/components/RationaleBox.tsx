import { cn } from '@/lib/utils'

export interface RationaleBoxProps {
  /**
   * The specific data point or rationale explaining why content is shown
   * Example: "Your Visa ending in 4523 is at 65% utilization ($3,400 of $5,000 limit)"
   */
  content: string
  /**
   * Optional className for additional styling
   */
  className?: string
}

/**
 * RationaleBox component
 * Displays a highlighted box explaining why specific content is shown to the user.
 * Used in education cards and offers to provide transparency about recommendations.
 * 
 * Visual styling:
 * - Light blue background (#eff6ff)
 * - Left border accent (#1e40af)
 * - Subtle shadow
 * - Clear typography
 */
export function RationaleBox({ content, className }: RationaleBoxProps) {
  return (
    <div
      className={cn(
        'rounded-md p-4 border-l-4 shadow-sm',
        'bg-[#eff6ff] border-[#1e40af]',
        'text-sm text-gray-700',
        className
      )}
      role="region"
      aria-label="Why we're showing this"
      aria-describedby="rationale-content"
    >
      <div className="font-semibold text-gray-900 mb-2">
        Why we're showing this
      </div>
      <div id="rationale-content" className="text-gray-700">
        {content}
      </div>
    </div>
  )
}

