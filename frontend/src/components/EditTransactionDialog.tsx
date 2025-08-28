import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Alert,
  Typography,
  MenuItem,
  FormControlLabel,
  Switch,
  Chip,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { SubdirectoryArrowRight as SubdirectoryArrowRightIcon } from '@mui/icons-material';
import { transactionsApi } from '../api/transactions';
import type { Transaction, TransactionUpdate } from '../types/transaction';
import type { Account } from '../types/account';
import type { Category } from '../types/category';

interface EditTransactionDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  transaction: Transaction | null;
  accounts: Account[];
  categories: Category[];
}

export const EditTransactionDialog: React.FC<EditTransactionDialogProps> = ({
  open,
  onClose,
  onSuccess,
  transaction,
  accounts,
  categories,
}) => {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState<number | ''>('');
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [transactionDate, setTransactionDate] = useState('');
  const [isExpense, setIsExpense] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Get account information
  const account = accounts.find(acc => acc.id === transaction?.account_id);

  useEffect(() => {
    if (open && transaction) {
      setDescription(transaction.description || '');
      setAmount(Math.abs(transaction.amount)); // Always show positive amount
      setCategoryId(transaction.category_id || null);
      setTransactionDate(transaction.transaction_date);
      setIsExpense(transaction.amount < 0); // Set toggle based on amount sign
      setSubmitError(null);
    }
  }, [open, transaction]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!transaction || !amount) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Calculate the final amount based on income/expense toggle
      const finalAmount = isExpense ? -Math.abs(Number(amount)) : Math.abs(Number(amount));

      const updateData: TransactionUpdate = {
        amount: finalAmount,
        category_id: categoryId,
        description: description || null,
        transaction_date: transactionDate,
      };

      await transactionsApi.updateTransaction(transaction.id, updateData);
      onSuccess();
    } catch (error) {
      console.error('Error updating transaction:', error);
      setSubmitError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  if (!transaction) {
    return null;
  }

  // Helper function to render categories with hierarchy in dropdown
  const renderCategoryMenuItems = () => {
    const items: React.ReactNode[] = [];
    const categoryType = isExpense ? 'expense' : 'income';
    
    categories.forEach((category) => {
      // Add parent category if it matches type
      if (category.type === categoryType) {
        items.push(
          <MenuItem key={category.id} value={category.id}>
            {category.name}
          </MenuItem>
        );
      }
      
      // Add child categories with indentation if they match type
      category.children?.forEach((child) => {
        if (child.type === categoryType) {
          items.push(
            <MenuItem 
              key={child.id} 
              value={child.id}
              sx={{ 
                pl: 4,
                fontSize: '0.875rem',
                color: 'text.secondary',
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              <SubdirectoryArrowRightIcon 
                sx={{ 
                  fontSize: '1rem',
                  color: 'action.active',
                }} 
              />
              {child.name}
            </MenuItem>
          );
        }
      });
    });
    
    return items;
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <EditIcon />
            Edit Transaction
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            {submitError && (
              <Alert severity="error" onClose={() => setSubmitError(null)}>
                {submitError}
              </Alert>
            )}

            {/* Account info (read-only) */}
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Account
              </Typography>
              <Chip
                label={`${account?.name || 'Unknown'} (${account?.currency || 'N/A'})`}
                variant="outlined"
                size="small"
              />
            </Box>

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
              value={amount}
              onChange={(e) => setAmount(parseFloat(e.target.value) || '')}
              fullWidth
              required
              inputProps={{ 
                min: 0,
                step: 0.01 
              }}
              helperText={account ? `Currency: ${account.currency}` : ''}
            />

            <TextField
              select
              label="Category"
              value={categoryId || ''}
              onChange={(e) => setCategoryId(e.target.value ? parseInt(e.target.value) : null)}
              fullWidth
              helperText="Optional"
            >
              <MenuItem value="">No Category</MenuItem>
              {renderCategoryMenuItems()}
            </TextField>

            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              fullWidth
              multiline
              rows={2}
              helperText="Optional"
            />

            <TextField
              type="date"
              label="Transaction Date"
              value={transactionDate}
              onChange={(e) => setTransactionDate(e.target.value)}
              fullWidth
              required
              InputLabelProps={{
                shrink: true,
              }}
            />
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Updating...' : 'Update Transaction'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};