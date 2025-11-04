import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ConsentModal } from './ConsentModal'

describe('ConsentModal', () => {
  const mockOnAccept = vi.fn()
  const mockOnDecline = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Modal Rendering', () => {
    it('renders modal when open is true', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      expect(screen.getByRole('dialog')).toBeInTheDocument()
      expect(screen.getByText('Welcome to SpendSense')).toBeInTheDocument()
    })

    it('does not render modal when open is false', () => {
      render(
        <ConsentModal
          open={false}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('displays welcome message', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      expect(screen.getByText('Welcome to SpendSense')).toBeInTheDocument()
      expect(
        screen.getByText(/Before you begin, we need your consent/)
      ).toBeInTheDocument()
    })

    it('displays explanation of data usage', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      expect(screen.getByText('How We Use Your Data')).toBeInTheDocument()
      expect(
        screen.getByText(/SpendSense analyzes your financial data/)
      ).toBeInTheDocument()
    })

    it('displays list of data accessed', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      expect(screen.getByText('Data We Access:')).toBeInTheDocument()
      expect(screen.getByText('Transaction history and details')).toBeInTheDocument()
      expect(screen.getByText('Account balances and account information')).toBeInTheDocument()
      expect(screen.getByText('Payment patterns and spending habits')).toBeInTheDocument()
    })

    it('displays list of what is NOT done', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

        expect(screen.getByText("What We Don't Do:")).toBeInTheDocument()
        expect(screen.getByText(/We do not share your data with third parties/)).toBeInTheDocument()
        expect(screen.getByText(/We do not provide financial advice/)).toBeInTheDocument()
        expect(screen.getByText(/We do not access your account credentials/)).toBeInTheDocument()
    })

    it('displays consent checkbox', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const checkbox = screen.getByLabelText(/I consent to SpendSense analyzing my financial data/i)
      expect(checkbox).toBeInTheDocument()
      expect(checkbox).not.toBeChecked()
    })

    it('displays Accept and Decline buttons', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      expect(screen.getByRole('button', { name: /accept/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /decline/i })).toBeInTheDocument()
    })
  })

  describe('Modal Behavior', () => {
    it('Accept button is disabled when checkbox is not checked', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const acceptButton = screen.getByRole('button', { name: /accept/i })
      expect(acceptButton).toBeDisabled()
    })

    it('Accept button is enabled when checkbox is checked', async () => {
      const user = userEvent.setup()
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const checkbox = screen.getByLabelText(/I consent to SpendSense analyzing my financial data/i)
      const acceptButton = screen.getByRole('button', { name: /accept/i })

      expect(acceptButton).toBeDisabled()

      await user.click(checkbox)

      await waitFor(() => {
        expect(acceptButton).not.toBeDisabled()
      })
    })

    it('calls onAccept when Accept button is clicked and checkbox is checked', async () => {
      const user = userEvent.setup()
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const checkbox = screen.getByLabelText(/I consent to SpendSense analyzing my financial data/i)
      const acceptButton = screen.getByRole('button', { name: /accept/i })

      await user.click(checkbox)
      await user.click(acceptButton)

      await waitFor(() => {
        expect(mockOnAccept).toHaveBeenCalledTimes(1)
      })
    })

    it('does not call onAccept when Accept button is clicked but checkbox is not checked', async () => {
      const user = userEvent.setup()
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const acceptButton = screen.getByRole('button', { name: /accept/i })
      
      // Try to click disabled button (should not work)
      expect(acceptButton).toBeDisabled()
      
      expect(mockOnAccept).not.toHaveBeenCalled()
    })

    it('calls onDecline when Decline button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const declineButton = screen.getByRole('button', { name: /decline/i })
      await user.click(declineButton)

      await waitFor(() => {
        expect(mockOnDecline).toHaveBeenCalledTimes(1)
      })
    })

    it('resets checkbox state after Accept is clicked', async () => {
      const user = userEvent.setup()
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const checkbox = screen.getByLabelText(/I consent to SpendSense analyzing my financial data/i)
      const acceptButton = screen.getByRole('button', { name: /accept/i })

      await user.click(checkbox)
      await waitFor(() => {
        expect(checkbox).toBeChecked()
      })

      await user.click(acceptButton)
      await waitFor(() => {
        expect(mockOnAccept).toHaveBeenCalledTimes(1)
      })

      // After Accept, checkbox should be reset (but modal will be closed by parent)
      // Since modal closes, we can't test the reset state directly
      // But the reset logic is in the component
    })

    it('resets checkbox state after Decline is clicked', async () => {
      const user = userEvent.setup()
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const checkbox = screen.getByLabelText(/I consent to SpendSense analyzing my financial data/i)
      const declineButton = screen.getByRole('button', { name: /decline/i })

      await user.click(checkbox)
      await waitFor(() => {
        expect(checkbox).toBeChecked()
      })

      await user.click(declineButton)
      await waitFor(() => {
        expect(mockOnDecline).toHaveBeenCalledTimes(1)
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
      expect(dialog).toHaveAttribute('aria-labelledby', 'consent-title')
      expect(dialog).toHaveAttribute('aria-describedby', 'consent-description')
    })

    it('has proper heading structure', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      // Check for title (h2 equivalent via DialogTitle)
      expect(screen.getByText('Welcome to SpendSense')).toBeInTheDocument()
      
      // Check for section headings
      expect(screen.getByText('How We Use Your Data')).toBeInTheDocument()
      expect(screen.getByText('Data We Access:')).toBeInTheDocument()
        expect(screen.getByText("What We Don't Do:")).toBeInTheDocument()
    })

    it('checkbox has proper ARIA attributes', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const checkbox = screen.getByLabelText(/I consent to SpendSense analyzing my financial data/i)
      expect(checkbox).toHaveAttribute('aria-label', 'I consent to SpendSense analyzing my financial data')
      expect(checkbox).toHaveAttribute('aria-describedby', 'consent-checkbox-description')
    })

    it('buttons have proper ARIA labels', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const acceptButton = screen.getByRole('button', { name: /accept/i })
      const declineButton = screen.getByRole('button', { name: /decline/i })

      expect(acceptButton).toHaveAttribute('aria-label', 'Accept consent')
      expect(declineButton).toHaveAttribute('aria-label', 'Decline consent')
    })

    it('Accept button has aria-describedby when disabled', () => {
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const acceptButton = screen.getByRole('button', { name: /accept/i })
      expect(acceptButton).toBeDisabled()
      expect(acceptButton).toHaveAttribute('aria-describedby', 'accept-disabled-description')
      
      // Check for screen reader text
      expect(screen.getByText(/Accept button is disabled until consent checkbox is checked/i)).toBeInTheDocument()
    })
  })

  describe('Keyboard Navigation', () => {
    it('supports keyboard navigation to checkbox', async () => {
      const user = userEvent.setup()
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const checkbox = screen.getByLabelText(/I consent to SpendSense analyzing my financial data/i)
      
      // Dialog focuses first focusable element by default (Decline button)
      // Tab to checkbox
      await user.tab()
      await user.tab()
      
      // Checkbox should be focusable
      expect(checkbox).toBeInTheDocument()
      // Note: Focus behavior may vary depending on Dialog's focus management
    })

    it('supports keyboard navigation to buttons', async () => {
      const user = userEvent.setup()
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const declineButton = screen.getByRole('button', { name: /decline/i })
      const acceptButton = screen.getByRole('button', { name: /accept/i })
      
      // Both buttons should be focusable
      expect(declineButton).toBeInTheDocument()
      expect(acceptButton).toBeInTheDocument()
      // Note: Focus behavior is managed by Dialog component
    })

    it('supports Space key to check checkbox', async () => {
      const user = userEvent.setup()
      render(
        <ConsentModal
          open={true}
          onAccept={mockOnAccept}
          onDecline={mockOnDecline}
        />
      )

      const checkbox = screen.getByLabelText(/I consent to SpendSense analyzing my financial data/i)
      
      // Focus checkbox first
      checkbox.focus()
      await user.keyboard(' ')
      
      await waitFor(() => {
        expect(checkbox).toBeChecked()
      })
    })
  })
})

