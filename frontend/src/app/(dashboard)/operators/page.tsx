'use client';

import React, { useEffect, useState } from 'react';
import { Table, Card, Tag, Typography, Progress, Space, Input } from 'antd';
import { SearchOutlined, UserOutlined, SafetyCertificateOutlined, CheckCircleOutlined } from '@ant-design/icons';
import apiClient from '@/services/api';
import { APIResponse, OperatorPerformance } from '@/types';

const { Title, Text } = Typography;

export default function OperatorsPage() {
  const [operators, setOperators] = useState<OperatorPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchOperators = async () => {
    setLoading(true);
    try {
      const res = (await apiClient.get('/operators')) as unknown as APIResponse<OperatorPerformance[]>;
      if (res.success && res.data) {
        setOperators(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch operators:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOperators();
  }, []);

  const filteredOperators = operators.filter(
    (op) =>
      op.full_name.toLowerCase().includes(search.toLowerCase()) ||
      op.email.toLowerCase().includes(search.toLowerCase()) ||
      (op.store_name && op.store_name.toLowerCase().includes(search.toLowerCase()))
  );

  const columns = [
    {
      title: 'Full Name',
      dataIndex: 'full_name',
      key: 'full_name',
      render: (name: string) => <Text strong>{name}</Text>,
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Role',
      dataIndex: 'role_name',
      key: 'role_name',
      render: (role: string) => {
        let color = 'blue';
        if (role === 'ADMIN') color = 'purple';
        if (role === 'SUPERVISOR') color = 'gold';
        return <Tag color={color} style={{ fontWeight: 600 }}>{role}</Tag>;
      },
    },
    {
      title: 'Assigned Dark Store',
      dataIndex: 'store_name',
      key: 'store_name',
      render: (store: string) => store ? <Tag color="cyan">{store}</Tag> : <Text type="secondary">Central Hub</Text>,
    },
    {
      title: 'Total Verifications',
      dataIndex: 'total_verifications',
      key: 'total_verifications',
      render: (count: number) => (
        <Space>
          <SafetyCertificateOutlined style={{ color: '#1890ff' }} />
          <Text strong>{count}</Text>
        </Space>
      ),
    },
    {
      title: 'Avg Quality Score',
      dataIndex: 'avg_packing_score',
      key: 'avg_packing_score',
      render: (score: number) => (
        <Space>
          <Progress
            type="circle"
            percent={score}
            width={28}
            strokeColor={score >= 80 ? '#52c41a' : score >= 60 ? '#faad14' : '#f5222d'}
          />
          <Text strong>{score} / 100</Text>
        </Space>
      ),
    },
    {
      title: 'Last Login',
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      render: (dateStr: string) => (dateStr ? new Date(dateStr).toLocaleString() : 'Never'),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>
          Operator Roster & Packing Accuracy Performance
        </Title>
        <Text type="secondary">
          Monitor operational staff performance and dark store quality verification accuracy
        </Text>
      </div>

      <Card bordered={false}>
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="Search by operator name, email, or store..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 340 }}
            allowClear
          />
        </Space>

        <Table
          columns={columns}
          dataSource={filteredOperators}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}
