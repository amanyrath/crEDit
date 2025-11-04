import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'

interface ConsentModalProps {
  open: boolean
  onAccept: () => void
  onDecline: () => void
}

/**
 * ConsentModal component
 * Displays a modal asking users to consent to data processing before accessing the platform
 * Modal cannot be dismissed without accepting or declining
 */
export function ConsentModal({ open, onAccept, onDecline }: ConsentModalProps) {
  const [consentChecked, setConsentChecked] = useState(false)

  const handleAccept = () => {
    if (consentChecked) {
      onAccept()
      setConsentChecked(false) // Reset for next time
    }
  }

  const handleDecline = () => {
    onDecline()
    setConsentChecked(false) // Reset for next time
  }

  return (
    <Dialog
      open={open}
      onOpenChange={() => {
        // Prevent closing modal by clicking overlay or pressing Escape
        // Modal can only be closed by Accept or Decline buttons
      }}
    >
      <DialogContent
        className="sm:max-w-[600px]"
        onEscapeKeyDown={e => e.preventDefault()}
        onInteractOutside={e => e.preventDefault()}
        aria-describedby="consent-description"
        role="dialog"
        aria-modal="true"
        aria-labelledby="consent-title"
      >
        <DialogHeader>
          <DialogTitle id="consent-title" className="text-2xl font-bold">
            Welcome to SpendSense
          </DialogTitle>
          <DialogDescription id="consent-description" className="text-base mt-2">
            Before you begin, we need your consent to process your financial data.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Welcome Message */}
          <div className="space-y-2">
            <h2 className="text-lg font-semibold">How We Use Your Data</h2>
            <p className="text-sm text-muted-foreground">
              SpendSense analyzes your financial data to provide personalized recommendations and
              insights to help you make better financial decisions.
            </p>
          </div>

          {/* Data Accessed List */}
          <div className="space-y-2">
            <h3 className="text-base font-medium">Data We Access:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground ml-2">
              <li>Transaction history and details</li>
              <li>Account balances and account information</li>
              <li>Payment patterns and spending habits</li>
            </ul>
          </div>

          {/* What We Don't Do List */}
          <div className="space-y-2">
            <h3 className="text-base font-medium">What We Don't Do:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground ml-2">
              <li>We do not share your data with third parties</li>
              <li>We do not provide financial advice or recommendations</li>
              <li>We do not access your account credentials or passwords</li>
            </ul>
          </div>

          {/* Consent Checkbox */}
          <div className="flex items-start space-x-3 pt-2">
            <Checkbox
              id="consent-checkbox"
              checked={consentChecked}
              onCheckedChange={checked => setConsentChecked(checked === true)}
              aria-label="I consent to SpendSense analyzing my financial data"
              aria-describedby="consent-checkbox-description"
              className="mt-1"
            />
            <label
              htmlFor="consent-checkbox"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
              id="consent-checkbox-description"
            >
              I consent to SpendSense analyzing my financial data
            </label>
          </div>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2 sm:gap-0">
          <Button
            type="button"
            variant="outline"
            onClick={handleDecline}
            className="w-full sm:w-auto"
            aria-label="Decline consent"
          >
            Decline
          </Button>
          <Button
            type="button"
            onClick={handleAccept}
            disabled={!consentChecked}
            className="w-full sm:w-auto"
            aria-label="Accept consent"
            aria-describedby={!consentChecked ? 'accept-disabled-description' : undefined}
          >
            Accept
          </Button>
          {!consentChecked && (
            <span id="accept-disabled-description" className="sr-only">
              Accept button is disabled until consent checkbox is checked
            </span>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
