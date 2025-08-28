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
  FormControlLabel,
  Switch,
} from '@mui/material';
import { transactionsApi } from '../api/transactions';
import type { Account } from '../types/account';
import type { Category } from '../types/category';
import type { TransactionCreate, TransactionFormData, TransactionValidationErrors } from '../types/transaction';

interface TransactionFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  accounts: Account[];
  categories: Category[];
}

export const TransactionForm: React.FC<TransactionFormProps> = ({
  open,
  onClose,
  onSuccess,
  accounts,
  categories,
}) => {
  const [formData, setFormData] = useState<TransactionFormData>({
    account_id: 0,
    amount: 0,
    category_id: null,
    description: '',
    transaction_date: new Date().toISOString().split('T')[0], // Today's date
  });

  const [isExpense, setIsExpense] = useState(true); // Toggle for income/expense
  const [errors, setErrors] = useState<TransactionValidationErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Get currency information for selected account
  const selectedAccount = accounts.find(acc => acc.id === formData.account_id);

  useEffect(() => {
    if (open) {
      // Reset form when dialog opens
      setFormData({
        account_id: 0,
        amount: 0,
        category_id: null,
        description: '',
        transaction_date: new Date().toISOString().split('T')[0],
      });
      setIsExpense(true);
      setErrors({});
      setSubmitError(null);
      setIsSubmitting(false);
    }
  }, [open]);

  const validateForm = (): boolean => {
    const newErrors: TransactionValidationErrors = {};

    if (!formData.account_id) {
      newErrors.account_id = 'Account is required';
    }

    if (!formData.amount || formData.amount === 0) {
      newErrors.amount = 'Amount is required and must not be zero';
    }

    if (!formData.transaction_date) {
      newErrors.transaction_date = 'Transaction date is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Calculate the final amount based on income/expense toggle
      const finalAmount = isExpense ? -Math.abs(formData.amount) : Math.abs(formData.amount);

      const transactionData: TransactionCreate = {
        account_id: formData.account_id,
        amount: finalAmount,
        category_id: formData.category_id || null,
        description: formData.description || null,
        transaction_date: formData.transaction_date,
      };

      await transactionsApi.createTransaction(transactionData);
      onSuccess();
    } catch (error) {
      console.error('Error creating transaction:', error);
      setSubmitError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFieldChange = (field: keyof TransactionFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  // Filter categories by type (income/expense)
  const filteredCategories = categories.filter(cat => 
    isExpense ? cat.type === 'expense' : cat.type === 'income'
  );

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
    >
      <form onSubmit={handleSubmit}>
        <DialogTitle>Add New Transaction</DialogTitle>
        
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            {submitError && (
              <Alert severity="error" onClose={() => setSubmitError(null)}>
                {submitError}
              </Alert>
            )}

            <TextField
              select
              label="Account"
              value={formData.account_id}
              onChange={(e) => handleFieldChange('account_id', parseInt(e.target.value))}
              error={!!errors.account_id}
              helperText={errors.account_id}
              fullWidth
              required
            >
              <MenuItem value={0}>Select an account</MenuItem>
              {accounts.map((account) => (
                <MenuItem key={account.id} value={account.id}>
                  {account.name} ({account.currency})
                </MenuItem>
              ))}
            </TextField>

            <FormControlLabel
              control={
                <Switch
                  checked={isExpense}
                  onChange={(e) => setIsExpense(e.target.checked)}
                  color="error"
                />
              }
              label={
                <Typography variant="body2">
                  {isExpense ? 'Expense' : 'Income'}
                </Typography>
              }
            />

            <TextField
              type="number"
              label="Amount"
              value={formData.amount || ''}
              onChange={(e) => handleFieldChange('amount', parseFloat(e.target.value) || 0)}
              error={!!errors.amount}
              helperText={errors.amount || (selectedAccount ? `Currency: ${selectedAccount.currency}` : '')}
              fullWidth
              required
              inputProps={{ 
                min: 0,
                step: 0.01 
              }}
            />

            <TextField
              select
              label="Category"
              value={formData.category_id || ''}
              onChange={(e) => handleFieldChange('category_id', e.target.value ? parseInt(e.target.value) : null)}
              error={!!errors.category_id}
              helperText={errors.category_id || 'Optional'}
              fullWidth
            >
              <MenuItem value="">No Category</MenuItem>
              {filteredCategories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {category.name}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              label="Description"
              value={formData.description}
              onChange={(e) => handleFieldChange('description', e.target.value)}
              error={!!errors.description}
              helperText={errors.description || 'Optional'}
              fullWidth
              multiline
              rows={2}
            />

            <TextField
              type="date"
              label="Transaction Date"
              value={formData.transaction_date}
              onChange={(e) => handleFieldChange('transaction_date', e.target.value)}
              error={!!errors.transaction_date}
              helperText={errors.transaction_date}
              fullWidth
              required
              InputLabelProps={{
                shrink: true,
              }}
            />
          </Box>
        </DialogContent>

        <DialogActions>
          <Button 
            onClick={handleClose} 
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating...' : 'Create Transaction'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};