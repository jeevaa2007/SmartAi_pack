import type { Metadata } from 'next';
import { ConfigProvider } from 'antd';
import AntdRegistry from '@/components/AntdRegistry';
import { AuthProvider } from '@/contexts/AuthContext';
import { themeConfig } from '@/styles/theme';
import '@/app/globals.css';

export const metadata: Metadata = {
  title: 'SmartPack AI - Packing Quality Verification',
  description: 'AI-Powered Packing Quality Verification Platform for Dark Store Operations',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AntdRegistry>
          <ConfigProvider theme={themeConfig}>
            <AuthProvider>
              {children}
            </AuthProvider>
          </ConfigProvider>
        </AntdRegistry>
      </body>
    </html>
  );
}
