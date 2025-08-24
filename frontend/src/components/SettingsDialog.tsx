import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Paper,
  Alert,
  Skeleton,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { Currency } from '../types/account';
import { CategoryForm } from './CategoryForm';
import { ConfirmDialog } from './ConfirmDialog';
import {
  useCategoriesWithToast,
  useCreateCategoryWithToast,
  useUpdateCategoryWithToast,
  useDeleteCategoryWithToast,
} from '../hooks/useCategoriesWithToast';
import type { Category, CategoryCreate, CategoryUpdate } from '../types/category';

// Define type locally to avoid Vite import issue
interface UserSettings {
  id: number;
  default_currency: Currency;
  created_at: string;
  updated_at: string;
}

interface SettingsDialogProps {
  open: boolean;
  onClose: () => void;
  settings: UserSettings | undefined;
  onSave: (currency: Currency) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export const SettingsDialog: React.FC<SettingsDialogProps> = ({
  open,
  onClose,
  settings,
  onSave,
}) => {
  const [defaultCurrency, setDefaultCurrency] = useState<Currency>(Currency.USD);
  const [tabValue, setTabValue] = useState(0);
  
  // Category management state
  const [categoryFormOpen, setCategoryFormOpen] = useState(false);
  const [categoryFormMode, setCategoryFormMode] = useState<'create' | 'edit'>('create');
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState<Category | null>(null);

  // Category hooks
  const { data: categoriesData, isLoading: categoriesLoading, error: categoriesError } = useCategoriesWithToast();
  const createCategoryMutation = useCreateCategoryWithToast();
  const updateCategoryMutation = useUpdateCategoryWithToast();
  const deleteCategoryMutation = useDeleteCategoryWithToast();

  useEffect(() => {
    if (settings) {
      setDefaultCurrency(settings.default_currency);
    }
  }, [settings]);

  const handleSave = () => {
    onSave(defaultCurrency);
    onClose();
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Category handlers
  const handleCreateCategory = () => {
    setSelectedCategory(null);
    setCategoryFormMode('create');
    setCategoryFormOpen(true);
  };

  const handleEditCategory = (category: Category) => {
    setSelectedCategory(category);
    setCategoryFormMode('edit');
    setCategoryFormOpen(true);
  };

  const handleDeleteClick = (category: Category) => {
    setCategoryToDelete(category);
    setDeleteDialogOpen(true);
  };

  const handleCategoryFormSubmit = async (data: CategoryCreate | CategoryUpdate) => {
    if (categoryFormMode === 'create') {
      await createCategoryMutation.mutateAsync(data as CategoryCreate);
    } else if (selectedCategory) {
      await updateCategoryMutation.mutateAsync({
        id: selectedCategory.id,
        data: data as CategoryUpdate,
      });
    }
    setCategoryFormOpen(false);
  };

  const handleDeleteConfirm = async () => {
    if (categoryToDelete) {
      await deleteCategoryMutation.mutateAsync(categoryToDelete.id);
      setDeleteDialogOpen(false);
      setCategoryToDelete(null);
    }
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>Settings</DialogTitle>
        <DialogContent>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="settings tabs">
            <Tab label="Currency" />
            <Tab label="Categories" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Choose your preferred currency for displaying total balances and conversions.
            </Typography>
            <FormControl fullWidth>
              <InputLabel>Default Currency</InputLabel>
              <Select
                value={defaultCurrency}
                label="Default Currency"
                onChange={(e) => setDefaultCurrency(e.target.value as Currency)}
              >
                <MenuItem value={Currency.USD}>USD - US Dollar</MenuItem>
                <MenuItem value={Currency.EUR}>EUR - Euro</MenuItem>
                <MenuItem value={Currency.RUB}>RUB - Russian Ruble</MenuItem>
                <MenuItem value={Currency.JPY}>JPY - Japanese Yen</MenuItem>
              </Select>
            </FormControl>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Manage your expense and income categories.
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleCreateCategory}
                size="small"
              >
                Add Category
              </Button>
            </Box>

            {categoriesError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                Failed to load categories
              </Alert>
            )}

            <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
              {categoriesLoading ? (
                <List>
                  {[1, 2, 3].map((i) => (
                    <ListItem key={i}>
                      <Skeleton width="100%" height={60} />
                    </ListItem>
                  ))}
                </List>
              ) : categoriesData && categoriesData.items.length > 0 ? (
                <List>
                  {categoriesData.items.map((category) => (
                    <ListItem key={category.id} divider>
                      <ListItemText
                        primary={category.name}
                        secondary={category.description || 'No description'}
                      />
                      <ListItemSecondaryAction>
                        <Tooltip title="Edit">
                          <IconButton
                            edge="end"
                            aria-label="edit"
                            onClick={() => handleEditCategory(category)}
                            sx={{ mr: 1 }}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => handleDeleteClick(category)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No categories yet. Click "Add Category" to create your first one.
                  </Typography>
                </Box>
              )}
            </Paper>
          </TabPanel>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
          {tabValue === 0 && (
            <Button onClick={handleSave} variant="contained">
              Save Currency Settings
            </Button>
          )}
        </DialogActions>
      </Dialog>

      <CategoryForm
        open={categoryFormOpen}
        onClose={() => setCategoryFormOpen(false)}
        onSubmit={handleCategoryFormSubmit}
        category={selectedCategory}
        mode={categoryFormMode}
      />

      <ConfirmDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        onConfirm={handleDeleteConfirm}
        title="Delete Category"
        message={`Are you sure you want to delete "${categoryToDelete?.name}"? This action cannot be undone.`}
      />
    </>
  );
};

export default SettingsDialog;