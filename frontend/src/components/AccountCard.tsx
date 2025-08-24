import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  IconButton,
  Chip,
  Box,
  Tooltip,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { Currency } from '../types/account';
import type { Account } from '../types/account';

interface AccountCardProps {
  account: Account;
  onEdit: (account: Account) => void;
  onDelete: (account: Account) => void;
}

const currencySymbols: Record<Currency, string> = {
  [Currency.EUR]: '€',
  [Currency.USD]: '$',
  [Currency.RUB]: '₽',
  [Currency.JPY]: '¥',
};

const formatBalance = (balance: number, currency: Currency): string => {
  const symbol = currencySymbols[currency];
  const formattedNumber = balance.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  
  if (currency === Currency.EUR) {
    return `${formattedNumber} ${symbol}`;
  }
  return `${symbol}${formattedNumber}`;
};

export const AccountCard: React.FC<AccountCardProps> = ({
  account,
  onEdit,
  onDelete,
}) => {
  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        cursor: 'pointer',
        '&:hover': {
          '& .MuiCardActions-root': {
            opacity: 1,
          },
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography
            variant="h6"
            component="h2"
            sx={{
              fontWeight: 600,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              maxWidth: '50%',
            }}
          >
            {account.name}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={account.currency}
              size="small"
              color="primary"
              variant="outlined"
              sx={{ fontWeight: 600 }}
            />
            <Chip
              label={`${(account.percentage_of_total * 100).toFixed(0)}%`}
              size="small"
              color="default"
              variant="outlined"
              sx={{ fontWeight: 600 }}
            />
          </Box>
        </Box>

        <Typography
          variant="h4"
          component="p"
          color="primary"
          sx={{
            fontWeight: 700,
            mb: account.balance_in_default_currency ? 1 : 2,
            letterSpacing: '-0.5px',
          }}
        >
          {formatBalance(account.balance, account.currency)}
        </Typography>

        {account.balance_in_default_currency && account.default_currency && (
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{
              mb: 2,
              fontSize: '0.95rem',
            }}
          >
            ≈ {formatBalance(account.balance_in_default_currency, account.default_currency)}
            {account.exchange_rate_used && (
              <Tooltip title={`Exchange rate: 1 ${account.currency} = ${account.exchange_rate_used.toFixed(4)} ${account.default_currency}`}>
                <Typography
                  component="span"
                  variant="caption"
                  sx={{ ml: 1, color: 'text.disabled' }}
                >
                  @ {account.exchange_rate_used.toFixed(4)}
                </Typography>
              </Tooltip>
            )}
          </Typography>
        )}

        {account.description && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              lineHeight: 1.5,
            }}
          >
            {account.description}
          </Typography>
        )}
      </CardContent>

      <CardActions
        sx={{
          justifyContent: 'flex-end',
          px: 2,
          py: 1,
          opacity: 0.7,
          transition: 'opacity 0.2s ease-in-out',
        }}
      >
        <Tooltip title="Edit account">
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(account);
            }}
            sx={{
              color: 'primary.main',
              '&:hover': {
                backgroundColor: 'primary.main',
                color: 'primary.contrastText',
              },
            }}
          >
            <EditIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete account">
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(account);
            }}
            sx={{
              color: 'error.main',
              '&:hover': {
                backgroundColor: 'error.main',
                color: 'error.contrastText',
              },
            }}
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </CardActions>
    </Card>
  );
};

export default AccountCard;