import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  MenuItem,
  Box,
  Alert,
  Typography,
  Divider,
  Grid,
} from '@mui/material';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import type { Account } from '../types/account';
import type { TransferCreate, TransferFormData, TransferValidationErrors } from '../types/transfer';

interface TransferFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: TransferCreate) => Promise<void>;
  accounts: Account[];
}

export const TransferForm: React.FC<TransferFormProps> = ({
  open,
  onClose,
  onSubmit,
  accounts,
}) => {
  const [formData, setFormData] = useState<TransferFormData>({
    from_account_id: 0,
    to_account_id: 0,
    from_amount: 0,
    to_amount: 0,
    description: '',
  });

  const [errors, setErrors] = useState<TransferValidationErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Get currency information for selected accounts
  const fromAccount = accounts.find(acc => acc.id === formData.from_account_id);
  const toAccount = accounts.find(acc => acc.id === formData.to_account_id);

  useEffect(() => {
    if (open) {
      // Reset form when opened
      setFormData({
        from_account_id: 0,
        to_account_id: 0,
        from_amount: 0,
        to_amount: 0,
        description: '',
      });
      setErrors({});
      setSubmitError(null);
      setIsSubmitting(false);
    }
  }, [open]);

  const validateForm = (): boolean => {
    const newErrors: TransferValidationErrors = {};

    if (!formData.from_account_id) {
      newErrors.from_account_id = 'Please select a source account';
    }

    if (!formData.to_account_id) {
      newErrors.to_account_id = 'Please select a destination account';
    }

    if (formData.from_account_id === formData.to_account_id && formData.from_account_id !== 0) {
      newErrors.general = 'Source and destination accounts must be different';
    }

    if (formData.from_amount <= 0) {
      newErrors.from_amount = 'Amount must be greater than 0';
    }

    if (formData.to_amount <= 0) {
      newErrors.to_amount = 'Amount must be greater than 0';
    }

    // Check if source account has sufficient balance
    if (fromAccount && formData.from_amount > fromAccount.balance) {
      newErrors.from_amount = `Insufficient balance. Available: ${fromAccount.balance.toFixed(2)} ${fromAccount.currency}`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (field: keyof TransferFormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = ['from_account_id', 'to_account_id'].includes(field)
      ? parseInt(event.target.value)
      : ['from_amount', 'to_amount'].includes(field)
      ? parseFloat(event.target.value) || 0
      : event.target.value;

    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));

    // Clear errors when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined,
      }));
    }
    if (errors.general) {
      setErrors(prev => ({
        ...prev,
        general: undefined,
      }));
    }
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const transferData: TransferCreate = {
        from_account_id: formData.from_account_id,
        to_account_id: formData.to_account_id,
        from_amount: formData.from_amount,
        to_amount: formData.to_amount,
        description: formData.description || null,
      };

      await onSubmit(transferData);
      onClose();
    } catch (error) {
      console.error('Transfer failed:', error);
      setSubmitError(
        error instanceof Error 
          ? error.message 
          : 'Failed to create transfer. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  // Filter accounts for dropdowns
  const fromAccountOptions = accounts.filter(acc => acc.id !== formData.to_account_id);
  const toAccountOptions = accounts.filter(acc => acc.id !== formData.from_account_id);

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 3 }
      }}
    >
      <DialogTitle sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
        <SwapHorizIcon color="primary" />
        Transfer Between Accounts
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
          {submitError && (
            <Alert severity="error" onClose={() => setSubmitError(null)}>
              {submitError}
            </Alert>
          )}

          {errors.general && (
            <Alert severity="error">
              {errors.general}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Source Account Section */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom color="primary">
                From Account
              </Typography>
              
              <TextField
                select
                label="Source Account"
                value={formData.from_account_id}
                onChange={handleChange('from_account_id')}
                error={!!errors.from_account_id}
                helperText={errors.from_account_id}
                fullWidth
                required
                disabled={isSubmitting}
              >
                <MenuItem value={0} disabled>
                  Select source account
                </MenuItem>
                {fromAccountOptions.map((account) => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.name} ({account.balance.toFixed(2)} {account.currency})
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                label={`Amount to Transfer ${fromAccount ? `(${fromAccount.currency})` : ''}`}
                type="number"
                value={formData.from_amount}
                onChange={handleChange('from_amount')}
                error={!!errors.from_amount}
                helperText={errors.from_amount || (fromAccount ? `Available: ${fromAccount.balance.toFixed(2)} ${fromAccount.currency}` : '')}
                fullWidth
                required
                disabled={isSubmitting || !fromAccount}
                sx={{ mt: 2 }}
                inputProps={{
                  step: 0.01,
                  min: 0,
                }}
              />
            </Grid>

            {/* Divider for visual separation */}
            <Grid item xs={12} md={0} sx={{ display: { xs: 'block', md: 'none' } }}>
              <Divider />
            </Grid>

            {/* Destination Account Section */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom color="secondary">
                To Account
              </Typography>
              
              <TextField
                select
                label="Destination Account"
                value={formData.to_account_id}
                onChange={handleChange('to_account_id')}
                error={!!errors.to_account_id}
                helperText={errors.to_account_id}
                fullWidth
                required
                disabled={isSubmitting}
              >
                <MenuItem value={0} disabled>
                  Select destination account
                </MenuItem>
                {toAccountOptions.map((account) => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.name} ({account.balance.toFixed(2)} {account.currency})
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                label={`Amount to Receive ${toAccount ? `(${toAccount.currency})` : ''}`}
                type="number"
                value={formData.to_amount}
                onChange={handleChange('to_amount')}
                error={!!errors.to_amount}
                helperText={errors.to_amount}
                fullWidth
                required
                disabled={isSubmitting || !toAccount}
                sx={{ mt: 2 }}
                inputProps={{
                  step: 0.01,
                  min: 0,
                }}
              />
            </Grid>
          </Grid>

          {/* Exchange Rate Information */}
          {fromAccount && toAccount && fromAccount.currency !== toAccount.currency && (
            <Alert severity="info">
              <Typography variant="body2">
                <strong>Multi-currency transfer:</strong> You are transferring from {fromAccount.currency} to {toAccount.currency}. 
                Please ensure the amounts reflect the correct exchange rate for your transaction.
              </Typography>
            </Alert>
          )}

          {/* Description */}
          <TextField
            label="Description"
            value={formData.description}
            onChange={handleChange('description')}
            fullWidth
            multiline
            rows={2}
            disabled={isSubmitting}
            placeholder="Optional transfer description..."
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button 
          onClick={handleClose} 
          disabled={isSubmitting}
          color="inherit"
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating Transfer...' : 'Create Transfer'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TransferForm;