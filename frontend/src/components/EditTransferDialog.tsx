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
  Grid,
  Chip,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import type { Transfer, TransferUpdate } from '../types/transfer';
import type { Account } from '../types/account';

interface EditTransferDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: TransferUpdate) => Promise<void>;
  transfer: Transfer | null;
  accounts: Account[];
}

export const EditTransferDialog: React.FC<EditTransferDialogProps> = ({
  open,
  onClose,
  onSubmit,
  transfer,
  accounts,
}) => {
  const [description, setDescription] = useState('');
  const [fromAmount, setFromAmount] = useState<number | ''>('');
  const [toAmount, setToAmount] = useState<number | ''>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Get account information
  const fromAccount = accounts.find(acc => acc.id === transfer?.from_account_id);
  const toAccount = accounts.find(acc => acc.id === transfer?.to_account_id);
  const isSameCurrency = fromAccount?.currency === toAccount?.currency;

  useEffect(() => {
    if (open && transfer) {
      setDescription(transfer.description || '');
      setFromAmount(transfer.from_amount);
      setToAmount(transfer.to_amount);
      setSubmitError(null);
    }
  }, [open, transfer]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!transfer) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const updateData: TransferUpdate = {
        description: description.trim() || null,
      };

      // Only include amounts if they were changed
      if (fromAmount !== transfer.from_amount && fromAmount !== '') {
        updateData.from_amount = Number(fromAmount);
      }
      
      if (!isSameCurrency && toAmount !== transfer.to_amount && toAmount !== '') {
        updateData.to_amount = Number(toAmount);
      }

      await onSubmit(updateData);
      onClose();
    } catch (error) {
      console.error('Failed to update transfer:', error);
      setSubmitError(error instanceof Error ? error.message : 'Failed to update transfer');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  // Auto-calculate to_amount for same currency transfers
  useEffect(() => {
    if (isSameCurrency && fromAmount !== '') {
      setToAmount(fromAmount);
    }
  }, [fromAmount, isSameCurrency]);

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <EditIcon />
        Edit Transfer
      </DialogTitle>
      
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {submitError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {submitError}
            </Alert>
          )}

          {transfer && fromAccount && toAccount && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Transfer Details
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Chip label={fromAccount.name} color="primary" variant="outlined" />
                <Typography>→</Typography>
                <Chip label={toAccount.name} color="secondary" variant="outlined" />
              </Box>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip label={fromAccount.currency} size="small" />
                {!isSameCurrency && <Chip label={toAccount.currency} size="small" />}
              </Box>
            </Box>
          )}

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={isSameCurrency ? 12 : 6}>
                <TextField
                  label={`From Amount (${fromAccount?.currency || ''})`}
                  type="number"
                  value={fromAmount}
                  onChange={(e) => setFromAmount(e.target.value === '' ? '' : Number(e.target.value))}
                  fullWidth
                  inputProps={{ 
                    min: 0.01, 
                    step: 0.01,
                  }}
                  helperText="Amount to transfer from source account"
                />
              </Grid>
              
              {!isSameCurrency && (
                <Grid item xs={6}>
                  <TextField
                    label={`To Amount (${toAccount?.currency || ''})`}
                    type="number"
                    value={toAmount}
                    onChange={(e) => setToAmount(e.target.value === '' ? '' : Number(e.target.value))}
                    fullWidth
                    inputProps={{ 
                      min: 0.01, 
                      step: 0.01,
                    }}
                    helperText="Amount to receive in destination account"
                  />
                </Grid>
              )}
            </Grid>

            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              multiline
              rows={3}
              fullWidth
              placeholder="Optional description for this transfer"
            />

            {isSameCurrency && (
              <Typography variant="body2" color="text.secondary">
                Since both accounts use the same currency, the destination amount will match the source amount.
              </Typography>
            )}
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
            {isSubmitting ? 'Updating...' : 'Update Transfer'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default EditTransferDialog;