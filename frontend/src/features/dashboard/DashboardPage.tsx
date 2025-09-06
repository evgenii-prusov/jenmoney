import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
} from '@mui/material';
import { TotalBalance } from '../../components/TotalBalance';
import { RecentTransactions } from './components/RecentTransactions';
import { useTotalBalance } from '../../hooks/useSettings';

export const DashboardPage: React.FC = () => {
  const { data: totalBalanceData, isLoading: totalBalanceLoading } = useTotalBalance();

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Overview of your financial status
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Total Balance */}
        <Grid item xs={12}>
          <TotalBalance data={totalBalanceData} loading={totalBalanceLoading} />
        </Grid>

        {/* Recent Transactions */}
        <Grid item xs={12} md={8}>
          <RecentTransactions />
        </Grid>

        {/* Quick Stats - Placeholder for future features */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Quick Stats
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Monthly analytics coming soon...
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;