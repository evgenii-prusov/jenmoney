import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 4 }}>
          <Paper sx={{ p: 3, backgroundColor: 'error.lighter' }}>
            <Typography variant="h5" color="error" gutterBottom>
              Something went wrong
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', mt: 2 }}>
              {this.state.error?.message}
            </Typography>
            <Typography variant="caption" sx={{ display: 'block', mt: 2 }}>
              {this.state.error?.stack}
            </Typography>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;