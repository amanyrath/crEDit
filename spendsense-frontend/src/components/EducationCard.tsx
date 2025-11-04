import { useState } from 'react'
import {
  CreditCard,
  PiggyBank,
  TrendingUp,
  Wallet,
  DollarSign,
  type LucideIcon,
} from 'lucide-react'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { RationaleBox } from './RationaleBox'
import { cn } from '@/lib/utils'

export type EducationCategory =
  | 'credit'
  | 'savings'
  | 'budgeting'
  | 'debt'
  | 'investing'
  | 'general'

export interface EducationCardProps {
  /**
   * Unique identifier for the education card
   */
  id: string
  /**
   * Title of the education content
   */
  title: string
  /**
   * Brief description (2-3 sentences)
   */
  description: string
  /**
   * Full content to display when expanded
   */
  fullContent: string
  /**
   * Rationale explaining why this content is shown
   */
  rationale: string
  /**
   * Category determines icon and color variant
   */
  category: EducationCategory
  /**
   * Tags displayed as hashtags
   */
  tags: string[]
  /**
   * Loading state
   */
  loading?: boolean
  /**
   * Optional className for additional styling
   */
  className?: string
}

/**
 * Icon mapping for categories
 */
const categoryIcons: Record<EducationCategory, LucideIcon> = {
  credit: CreditCard,
  savings: PiggyBank,
  budgeting: TrendingUp,
  debt: Wallet,
  investing: DollarSign,
  general: DollarSign,
}

/**
 * Color variants for categories
 */
const categoryColors: Record<EducationCategory, { border: string; icon: string }> = {
  credit: {
    border: 'border-blue-500',
    icon: 'text-blue-600',
  },
  savings: {
    border: 'border-green-500',
    icon: 'text-green-600',
  },
  budgeting: {
    border: 'border-purple-500',
    icon: 'text-purple-600',
  },
  debt: {
    border: 'border-red-500',
    icon: 'text-red-600',
  },
  investing: {
    border: 'border-yellow-500',
    icon: 'text-yellow-600',
  },
  general: {
    border: 'border-gray-500',
    icon: 'text-gray-600',
  },
}

/**
 * EducationCard component
 * Displays personalized financial education content in a card format.
 * Includes icon, title, description, rationale box, tags, and expandable full content.
 *
 * Features:
 * - Category-based color coding and icons
 * - Expandable full content (modal)
 * - Loading state support
 * - Accessibility features
 * - Responsive design
 */
export function EducationCard({
  id,
  title,
  description,
  fullContent,
  rationale,
  category,
  tags,
  loading = false,
  className,
}: EducationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const Icon = categoryIcons[category]
  const colors = categoryColors[category]

  if (loading) {
    return (
      <Card className={cn('animate-pulse', className)} role="article">
        <CardHeader>
          <div className="h-6 w-3/4 bg-gray-200 rounded mb-2" />
          <div className="h-4 w-full bg-gray-200 rounded mb-1" />
          <div className="h-4 w-5/6 bg-gray-200 rounded" />
        </CardHeader>
        <CardContent>
          <div className="h-20 bg-gray-200 rounded mb-4" />
        </CardContent>
        <CardFooter>
          <div className="h-10 w-32 bg-gray-200 rounded" />
        </CardFooter>
      </Card>
    )
  }

  return (
    <>
      <Card
        className={cn('hover:shadow-md transition-shadow', className)}
        role="article"
        aria-labelledby={`education-title-${id}`}
        aria-describedby={`education-description-${id}`}
      >
        <CardHeader>
          <div className="flex items-start gap-4">
            <div className={cn('p-2 rounded-lg bg-gray-50', colors.icon)}>
              <Icon className="h-6 w-6" aria-hidden="true" />
            </div>
            <div className="flex-1">
              <CardTitle
                id={`education-title-${id}`}
                className={cn('text-xl border-l-4 pl-3', colors.border)}
              >
                {title}
              </CardTitle>
              <CardDescription id={`education-description-${id}`} className="mt-2">
                {description}
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <RationaleBox content={rationale} />

          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2" role="list" aria-label="Tags">
              {tags.map((tag, index) => (
                <span
                  key={index}
                  className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full"
                  role="listitem"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </CardContent>

        <CardFooter>
          <Button
            onClick={() => setIsExpanded(true)}
            variant="outline"
            className="w-full"
            aria-expanded={isExpanded}
            aria-controls={`education-modal-${id}`}
          >
            Learn More
          </Button>
        </CardFooter>
      </Card>

      <Dialog open={isExpanded} onOpenChange={setIsExpanded}>
        <DialogContent
          id={`education-modal-${id}`}
          className="max-w-2xl max-h-[90vh] overflow-y-auto"
          aria-labelledby={`modal-title-${id}`}
        >
          <DialogHeader>
            <div className="flex items-center gap-3">
              <div className={cn('p-2 rounded-lg bg-gray-50', colors.icon)}>
                <Icon className="h-6 w-6" aria-hidden="true" />
              </div>
              <DialogTitle id={`modal-title-${id}`}>{title}</DialogTitle>
            </div>
            <DialogDescription>{description}</DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <RationaleBox content={rationale} />

            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-gray-700">{fullContent}</div>
            </div>

            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-4 border-t">
                {tags.map((tag, index) => (
                  <span
                    key={index}
                    className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
