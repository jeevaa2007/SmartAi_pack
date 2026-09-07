'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Layout, Menu, Typography, Avatar, Dropdown, Space, Tag, Button } from 'antd';
import {
  DashboardOutlined,
  ShopOutlined,
  ShoppingOutlined,
  TeamOutlined,
  ContainerOutlined,
  SafetyCertificateOutlined,
  BarChartOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';

const { Header, Sider, Content } = Layout;
const { Text, Title } = Typography;

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: <Link href="/dashboard">Dashboard</Link>,
    },
    {
      key: '/stores',
      icon: <ShopOutlined />,
      label: <Link href="/stores">Stores</Link>,
    },
    {
      key: '/products',
      icon: <ShoppingOutlined />,
      label: <Link href="/products">Products</Link>,
    },
    {
      key: '/operators',
      icon: <TeamOutlined />,
      label: <Link href="/operators">Operators</Link>,
    },
    {
      key: '/orders',
      icon: <ContainerOutlined />,
      label: <Link href="/orders">Orders</Link>,
    },
    {
      key: '/packing-verification',
      icon: <SafetyCertificateOutlined />,
      label: <Link href="/packing-verification">Packing Verification</Link>,
    },
    {
      key: '/reports',
      icon: <BarChartOutlined />,
      label: (
        <Space>
          <Link href="/reports">Reports</Link>
          <Tag color="orange" style={{ fontSize: 10 }}>Demo</Tag>
        </Space>
      ),
    },
  ];

  const userMenuItems = [
    {
      key: 'user_info',
      label: (
        <div style={{ padding: '4px 8px' }}>
          <Text strong block>{user?.full_name}</Text>
          <Text type="secondary" style={{ fontSize: 12 }} block>{user?.email}</Text>
          <Tag color="blue" style={{ marginTop: 4 }}>{user?.role_name || 'OPERATOR'}</Tag>
        </div>
      ),
    },
    { type: 'divider' as const },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Sign Out',
      onClick: logout,
    },
  ];

  return (
    <ProtectedRoute>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          theme="dark"
          width={240}
          style={{
            overflow: 'auto',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
            zIndex: 100,
          }}
        >
          <div
            style={{
              height: 64,
              display: 'flex',
              alignItems: 'center',
              justifyContent: collapsed ? 'center' : 'flex-start',
              paddingLeft: collapsed ? 0 : 20,
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <SafetyCertificateOutlined style={{ fontSize: 24, color: '#1890ff', marginRight: collapsed ? 0 : 12 }} />
            {!collapsed && (
              <Title level={4} style={{ color: '#ffffff', margin: 0, fontSize: 16 }}>
                SmartPack AI
              </Title>
            )}
          </div>

          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[pathname]}
            items={menuItems}
            style={{ borderRight: 0, marginTop: 12 }}
          />
        </Sider>

        <Layout style={{ marginLeft: collapsed ? 80 : 240, transition: 'all 0.2s' }}>
          <Header
            style={{
              padding: '0 24px',
              background: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              boxShadow: '0 1px 4px rgba(0, 0, 0, 0.08)',
              position: 'sticky',
              top: 0,
              zIndex: 99,
            }}
          >
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ fontSize: '16px', width: 40, height: 40 }}
            />

            <Space size="large">
              <Dropdown menu={{ items: userMenuItems }} placement="bottomRight" arrow>
                <Space style={{ cursor: 'pointer' }}>
                  <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
                  <Text strong style={{ display: 'inline-block' }}>
                    {user?.full_name || 'Operator'}
                  </Text>
                  <Tag color="blue">{user?.role_name || 'OPERATOR'}</Tag>
                </Space>
              </Dropdown>
            </Space>
          </Header>

          <Content
            style={{
              margin: '24px 24px 0',
              padding: 24,
              background: '#ffffff',
              minHeight: 280,
              borderRadius: 8,
            }}
          >
            {children}
          </Content>
        </Layout>
      </Layout>
    </ProtectedRoute>
  );
};
