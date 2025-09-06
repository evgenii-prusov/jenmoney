import React from 'react';
import {
  Box,
  Grid,
  Typography,
} from '@mui/material';
import { TotalBalance } from '../../components/TotalBalance';
import { RecentTransactions } from './components/RecentTransactions';
import { QuickStats } from './components/QuickStats';
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
        {/* Header row with Total Balance in top right */}
        <Grid item xs={12} md={8}>
          {/* Empty space for visual balance */}
        </Grid>
        <Grid item xs={12} md={4}>
          <TotalBalance data={totalBalanceData} loading={totalBalanceLoading} />
        </Grid>

        {/* Main content row */}
        <Grid item xs={12} md={8}>
          <RecentTransactions />
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={4}>
          <QuickStats />
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;