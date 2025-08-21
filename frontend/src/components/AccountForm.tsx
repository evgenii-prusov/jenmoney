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
} from '@mui/material';
import { Currency } from '../types/account';
import type { Account, AccountCreate, AccountUpdate } from '../types/account';

interface AccountFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: AccountCreate | AccountUpdate) => Promise<void>;
  account?: Account | null;
  mode: 'create' | 'edit';
}

const currencies = [
  { value: Currency.EUR, label: 'EUR - Euro' },
  { value: Currency.USD, label: 'USD - US Dollar' },
  { value: Currency.RUB, label: 'RUB - Russian Ruble' },
  { value: Currency.JPY, label: 'JPY - Japanese Yen' },
];

export const AccountForm: React.FC<AccountFormProps> = ({
  open,
  onClose,
  onSubmit,
  account,
  mode,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    currency: Currency.EUR as Currency,
    balance: 0,
    description: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (account && mode === 'edit') {
      setFormData({
        name: account.name,
        currency: account.currency,
        balance: account.balance,
        description: account.description || '',
      });
    } else if (mode === 'create') {
      setFormData({
        name: '',
        currency: Currency.EUR,
        balance: 0,
        description: '',
      });
    }
    setErrors({});
    setSubmitError(null);
  }, [account, mode, open]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Account name is required';
    } else if (formData.name.length > 100) {
      newErrors.name = 'Account name must be less than 100 characters';
    }

    if (formData.balance < 0) {
      newErrors.balance = 'Balance cannot be negative';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const submitData = mode === 'create' 
        ? {
            name: formData.name.trim(),
            currency: formData.currency,
            balance: formData.balance,
            description: formData.description.trim() || null,
          }
        : {
            name: formData.name.trim(),
            currency: formData.currency,
            balance: formData.balance,
            description: formData.description.trim() || null,
          };

      await onSubmit(submitData);
      handleClose();
    } catch (error) {
      console.error('Form submission error:', error);
      setSubmitError(
        error instanceof Error ? error.message : 'Failed to save account'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setFormData({
        name: '',
        currency: Currency.EUR,
        balance: 0,
        description: '',
      });
      setErrors({});
      setSubmitError(null);
      onClose();
    }
  };

  const handleChange = (field: keyof typeof formData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = field === 'balance' 
      ? parseFloat(event.target.value) || 0
      : event.target.value;
    
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
    
    if (submitError) {
      setSubmitError(null);
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 },
      }}
    >
      <DialogTitle sx={{ fontWeight: 600 }}>
        {mode === 'create' ? 'Create New Account' : 'Edit Account'}
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, mt: 1 }}>
          {submitError && (
            <Alert severity="error" onClose={() => setSubmitError(null)}>
              {submitError}
            </Alert>
          )}

          <TextField
            label="Account Name"
            value={formData.name}
            onChange={handleChange('name')}
            error={!!errors.name}
            helperText={errors.name}
            fullWidth
            required
            autoFocus
            disabled={isSubmitting}
            inputProps={{ maxLength: 100 }}
          />

          <TextField
            select
            label="Currency"
            value={formData.currency}
            onChange={handleChange('currency')}
            fullWidth
            required
            disabled={isSubmitting}
          >
            {currencies.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            label="Balance"
            type="number"
            value={formData.balance}
            onChange={handleChange('balance')}
            error={!!errors.balance}
            helperText={errors.balance}
            fullWidth
            required
            disabled={isSubmitting}
            inputProps={{
              step: 0.01,
              min: 0,
            }}
          />

          <TextField
            label="Description"
            value={formData.description}
            onChange={handleChange('description')}
            fullWidth
            multiline
            rows={3}
            disabled={isSubmitting}
            placeholder="Optional account description..."
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
          {isSubmitting 
            ? (mode === 'create' ? 'Creating...' : 'Saving...') 
            : (mode === 'create' ? 'Create Account' : 'Save Changes')
          }
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AccountForm;