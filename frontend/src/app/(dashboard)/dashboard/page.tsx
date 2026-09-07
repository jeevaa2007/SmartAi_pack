'use client';

import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Table, Tag, Typography, Progress, Space, Alert, Spin } from 'antd';
import {
  ContainerOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';
import apiClient from '@/services/api';
import { APIResponse, DashboardStats } from '@/types';

const { Title, Text } = Typography;

const COLORS = {
  PASS: '#52c41a',
  WARNING: '#faad14',
  FAIL: '#f5222d',
};

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboardStats = async () => {
    setLoading(true);
    try {
      const res = (await apiClient.get('/dashboard/stats')) as unknown as APIResponse<DashboardStats>;
      if (res.success && res.data) {
        setStats(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch dashboard metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Loading Dark Store Control Center Analytics..." />
      </div>
    );
  }

  const pieData = stats
    ? [
        { name: 'PASS', value: stats.outcome_breakdown.pass_count },
        { name: 'WARNING', value: stats.outcome_breakdown.warning_count },
        { name: 'FAIL', value: stats.outcome_breakdown.fail_count },
      ]
    : [];

  const verificationColumns = [
    {
      title: 'Order Number',
      dataIndex: 'order_number',
      key: 'order_number',
      render: (text: string) => <Text strong>{text || 'ORD-UNKNOWN'}</Text>,
    },
    {
      title: 'Operator',
      dataIndex: 'operator_name',
      key: 'operator_name',
      render: (text: string) => text || 'System Operator',
    },
    {
      title: 'Packing Score',
      dataIndex: 'packing_score',
      key: 'packing_score',
      render: (score: number) => (
        <Space>
          <Progress
            type="circle"
            percent={score}
            width={32}
            strokeColor={score >= 80 ? '#52c41a' : score >= 60 ? '#faad14' : '#f5222d'}
          />
          <Text strong>{score} / 100</Text>
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        let color = 'green';
        let icon = <CheckCircleOutlined />;
        if (status === 'WARNING') {
          color = 'gold';
          icon = <WarningOutlined />;
        } else if (status === 'FAIL') {
          color = 'red';
          icon = <CloseCircleOutlined />;
        }
        return (
          <Tag color={color} icon={icon} style={{ fontWeight: 600, padding: '2px 8px' }}>
            {status}
          </Tag>
        );
      },
    },
    {
      title: 'Verified At',
      dataIndex: 'verified_at',
      key: 'verified_at',
      render: (dateStr: string) => new Date(dateStr).toLocaleString(),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={3} style={{ margin: 0 }}>
            Operational Quality Control Center
          </Title>
          <Text type="secondary">
            AI & Rule-Powered Packing Quality Verification for Dark Store Dispatch
          </Text>
        </div>
        <Tag color="blue" icon={<ThunderboltOutlined />} style={{ padding: '4px 12px', fontSize: 13 }}>
          LIVE POSTGRESQL METRICS
        </Tag>
      </div>

      <Alert
        message="Quality Assurance Directive"
        description="Detect packaging quality issues, missing cold-chain isolation, and fragile cushioning violations before dispatch."
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} style={{ background: '#f6ffed', borderColor: '#b7eb8f' }}>
            <Statistic
              title="Total Orders"
              value={stats?.total_orders || 0}
              prefix={<ContainerOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} style={{ background: '#e6f7ff', borderColor: '#91caff' }}>
            <Statistic
              title="Verified Orders"
              value={stats?.verified_orders || 0}
              prefix={<SafetyCertificateOutlined style={{ color: '#1677ff' }} />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} style={{ background: '#f6ffed', borderColor: '#b7eb8f' }}>
            <Statistic
              title="Packing Pass Rate"
              value={stats?.pass_rate || 0}
              suffix="%"
              precision={1}
              valueStyle={{ color: '#3f8600' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} style={{ background: '#fff2f0', borderColor: '#ffccc7' }}>
            <Statistic
              title="Avg Packing Score"
              value={stats?.avg_packing_score || 0}
              suffix="/ 100"
              precision={1}
              valueStyle={{ color: stats && stats.avg_packing_score >= 80 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts & Breakdown */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Verification Outcomes Breakdown" bordered={false}>
            <div style={{ height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    <Cell key="cell-pass" fill={COLORS.PASS} />
                    <Cell key="cell-warning" fill={COLORS.WARNING} />
                    <Cell key="cell-fail" fill={COLORS.FAIL} />
                  </Pie>
                  <RechartsTooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Packing Quality Status Totals" bordered={false}>
            <Row gutter={[16, 16]} style={{ padding: '20px 0' }}>
              <Col span={8} style={{ textAlign: 'center' }}>
                <CheckCircleOutlined style={{ fontSize: 36, color: '#52c41a' }} />
                <Title level={4} style={{ color: '#52c41a', margin: '8px 0 0' }}>
                  {stats?.outcome_breakdown.pass_count || 0}
                </Title>
                <Text type="secondary">PASS Orders</Text>
              </Col>
              <Col span={8} style={{ textAlign: 'center' }}>
                <WarningOutlined style={{ fontSize: 36, color: '#faad14' }} />
                <Title level={4} style={{ color: '#faad14', margin: '8px 0 0' }}>
                  {stats?.warning_count || 0}
                </Title>
                <Text type="secondary">WARNING Orders</Text>
              </Col>
              <Col span={8} style={{ textAlign: 'center' }}>
                <CloseCircleOutlined style={{ fontSize: 36, color: '#f5222d' }} />
                <Title level={4} style={{ color: '#f5222d', margin: '8px 0 0' }}>
                  {stats?.failure_count || 0}
                </Title>
                <Text type="secondary">FAIL Orders</Text>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Recent Verifications Table */}
      <Card title="Recent Packing Verifications Activity" bordered={false}>
        <Table
          columns={verificationColumns}
          dataSource={stats?.recent_verifications || []}
          rowKey="id"
          pagination={false}
          size="middle"
        />
      </Card>
    </div>
  );
}
