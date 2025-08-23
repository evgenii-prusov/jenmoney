import React from 'react';
import { Box, Typography } from '@mui/material';

export const AccountsPageDebug: React.FC = () => {
  console.log('AccountsPageDebug rendering');
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4">
        Debug: Accounts Page is Rendering
      </Typography>
      <Typography variant="body1">
        If you can see this, the basic rendering is working.
      </Typography>
    </Box>
  );
};

export default AccountsPageDebug;