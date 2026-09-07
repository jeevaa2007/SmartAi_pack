import type { ThemeConfig } from 'antd';

/**
 * Custom Ant Design theme tokens for SmartPack AI UI.
 * Implements a premium, dark-mode-first aesthetic with a high-contrast layout.
 */
export const themeConfig: ThemeConfig = {
  token: {
    colorPrimary: '#10b981',       // High-contrast emerald green for positive verification states
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',       // Amber warning color for warnings
    colorError: '#ef4444',         // Red warning color for critical packing failures
    colorInfo: '#3b82f6',          // Deep blue for orders info
    
    // Core Layout Styles
    borderRadius: 8,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  components: {
    Button: {
      borderRadius: 6,
      controlHeight: 40,
      fontWeight: 600,
    },
    Table: {
      borderRadius: 8,
      headerBg: '#fafafa',
    },
    Card: {
      borderRadius: 8,
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    },
  },
};
