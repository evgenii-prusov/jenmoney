import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
  Box,
  Chip,
  Stack,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import WarningIcon from '@mui/icons-material/Warning';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import { transactionsApi } from '../api/transactions';
import type { Transaction } from '../types/transaction';

interface DeleteTransactionDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  transaction: Transaction | null;
}

export const DeleteTransactionDialog: React.FC<DeleteTransactionDialogProps> = ({
  open,
  onClose,
  onSuccess,
  transaction,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const handleConfirm = async () => {
    if (!transaction) return;

    setIsDeleting(true);
    setDeleteError(null);

    try {
      await transactionsApi.deleteTransaction(transaction.id);
      onSuccess();
    } catch (error) {
      console.error('Failed to delete transaction:', error);
      setDeleteError(error instanceof Error ? error.message : 'Failed to delete transaction');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClose = () => {
    if (!isDeleting) {
      setDeleteError(null);
      onClose();
    }
  };

  if (!transaction) {
    return null;
  }

  const isIncome = transaction.amount >= 0;
  const formattedAmount = Math.abs(transaction.amount).toFixed(2);

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <DeleteIcon color="error" />
          Delete Transaction
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {deleteError && (
            <Alert severity="error" onClose={() => setDeleteError(null)}>
              {deleteError}
            </Alert>
          )}

          <Alert severity="warning" icon={<WarningIcon />}>
            <Typography variant="body2">
              This action cannot be undone. The transaction will be permanently deleted 
              and account balances will be adjusted accordingly.
            </Typography>
          </Alert>

          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Transaction Details:
            </Typography>
            
            <Stack spacing={1}>
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="body2" color="text.secondary">
                  Type:
                </Typography>
                <Chip
                  icon={isIncome ? <TrendingUpIcon /> : <TrendingDownIcon />}
                  label={isIncome ? 'Income' : 'Expense'}
                  color={isIncome ? 'success' : 'error'}
                  size="small"
                  variant="outlined"
                />
              </Box>

              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="body2" color="text.secondary">
                  Amount:
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {formattedAmount} {transaction.currency}
                </Typography>
              </Box>

              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="body2" color="text.secondary">
                  Date:
                </Typography>
                <Typography variant="body2">
                  {new Date(transaction.transaction_date).toISOString().split('T')[0]}
                </Typography>
              </Box>

              {transaction.description && (
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body2" color="text.secondary">
                    Description:
                  </Typography>
                  <Typography variant="body2">
                    {transaction.description}
                  </Typography>
                </Box>
              )}
            </Stack>
          </Box>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={isDeleting}>
          Cancel
        </Button>
        <Button 
          onClick={handleConfirm}
          color="error"
          variant="contained"
          disabled={isDeleting}
          startIcon={<DeleteIcon />}
        >
          {isDeleting ? 'Deleting...' : 'Delete Transaction'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};