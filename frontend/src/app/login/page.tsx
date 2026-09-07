'use client';

import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Alert, Space } from 'antd';
import { UserOutlined, LockOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import apiClient from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { APIResponse, LoginResponseData } from '@/types';

const { Title, Text } = Typography;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const { login } = useAuth();

  const onFinish = async (values: any) => {
    setLoading(true);
    setErrorMessage(null);

    try {
      const response = (await apiClient.post('/auth/login', {
        email: values.email,
        password: values.password,
      })) as unknown as APIResponse<LoginResponseData>;

      if (response.success && response.data) {
        login(response.data.access_token, response.data.user);
      } else {
        setErrorMessage(response.error?.message || 'Authentication failed.');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setErrorMessage(
        err?.error?.message || err?.message || 'Invalid email or password. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #001529 0%, #002140 50%, #003a70 100%)',
        padding: '20px',
      }}
    >
      <Card
        style={{
          width: '100%',
          maxWidth: 440,
          borderRadius: 12,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <Space direction="vertical" align="center">
            <div
              style={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                background: 'rgba(24, 144, 255, 0.1)',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              <SafetyCertificateOutlined style={{ fontSize: 36, color: '#1890ff' }} />
            </div>
            <Title level={3} style={{ margin: 0 }}>
              SmartPack AI
            </Title>
            <Text type="secondary">
              Dark Store Packing Quality Verification Platform
            </Text>
          </Space>
        </div>

        {errorMessage && (
          <Alert
            message={errorMessage}
            type="error"
            showIcon
            closable
            onClose={() => setErrorMessage(null)}
            style={{ marginBottom: 20 }}
          />
        )}

        <Form name="login_form" layout="vertical" onFinish={onFinish} requiredMark={false} size="large">
          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Please enter your operational email' },
              { type: 'email', message: 'Please enter a valid email address' },
            ]}
          >
            <Input prefix={<UserOutlined style={{ color: '#bfbfbf' }} />} placeholder="Email address" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please enter your password' }]}
          >
            <Input.Password prefix={<LockOutlined style={{ color: '#bfbfbf' }} />} placeholder="Password" />
          </Form.Item>

          <Form.Item style={{ marginTop: 24 }}>
            <Button type="primary" htmlType="submit" block loading={loading}>
              Sign In to Control Center
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            Demo Admin: <code>admin@smartpack.ai</code> | <code>SmartPackAdmin123!</code>
          </Text>
        </div>
      </Card>
    </div>
  );
}
