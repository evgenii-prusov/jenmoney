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
import type { Transfer } from '../types/transfer';

interface DeleteTransferDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  transfer: Transfer | null;
  getAccountName: (accountId: number) => string;
}

export const DeleteTransferDialog: React.FC<DeleteTransferDialogProps> = ({
  open,
  onClose,
  onConfirm,
  transfer,
  getAccountName,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const handleConfirm = async () => {
    setIsDeleting(true);
    setDeleteError(null);

    try {
      await onConfirm();
      onClose();
    } catch (error) {
      console.error('Failed to delete transfer:', error);
      setDeleteError(error instanceof Error ? error.message : 'Failed to delete transfer');
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

  if (!transfer) return null;

  const formatCurrency = (amount: number, currency: string): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <WarningIcon color="error" />
        Delete Transfer
      </DialogTitle>
      
      <DialogContent>
        {deleteError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {deleteError}
          </Alert>
        )}

        <Box sx={{ mb: 2 }}>
          <Typography variant="body1" gutterBottom>
            Are you sure you want to delete this transfer? This action cannot be undone.
          </Typography>
        </Box>

        {/* Transfer Details */}
        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1, mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Transfer Details:
          </Typography>
          
          <Stack spacing={1}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Date:
              </Typography>
              <Typography variant="body2">
                {formatDate(transfer.created_at)}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                From:
              </Typography>
              <Chip
                label={getAccountName(transfer.from_account_id)}
                variant="outlined"
                size="small"
                color="error"
              />
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                To:
              </Typography>
              <Chip
                label={getAccountName(transfer.to_account_id)}
                variant="outlined"
                size="small"
                color="success"
              />
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Amount:
              </Typography>
              <Stack spacing={0.5} alignItems="flex-end">
                <Typography variant="body2" color="error.main">
                  -{formatCurrency(transfer.from_amount, transfer.from_currency)}
                </Typography>
                <Typography variant="body2" color="success.main">
                  +{formatCurrency(transfer.to_amount, transfer.to_currency)}
                </Typography>
              </Stack>
            </Box>

            {transfer.description && (
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Description:
                </Typography>
                <Typography variant="body2" sx={{ maxWidth: '60%', textAlign: 'right' }}>
                  {transfer.description}
                </Typography>
              </Box>
            )}
          </Stack>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={isDeleting}>
          Cancel
        </Button>
        <Button
          onClick={handleConfirm}
          variant="contained"
          color="error"
          startIcon={<DeleteIcon />}
          disabled={isDeleting}
        >
          {isDeleting ? 'Deleting...' : 'Delete Transfer'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteTransferDialog;