'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Table, Card, Button, Input, Select, Tag, Space, Modal, Typography, Progress, Badge, List, Divider, Row, Col } from 'antd';
import {
  SearchOutlined,
  SafetyCertificateOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  AlertOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import apiClient from '@/services/api';
import { APIResponse, Order } from '@/types';

const { Title, Text } = Typography;

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const router = useRouter();

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const params: any = { limit: 200 };
      if (search) params.search = search;
      if (statusFilter) params.verification_status = statusFilter;

      const res = (await apiClient.get('/orders', { params })) as unknown as APIResponse<Order[]>;
      if (res.success && res.data) {
        setOrders(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [search, statusFilter]);

  const handleViewOrder = (order: Order) => {
    setSelectedOrder(order);
    setModalVisible(true);
  };

  const handleStartVerification = (orderId: string) => {
    router.push(`/packing-verification?order_id=${orderId}`);
  };

  const columns = [
    {
      title: 'Order Number',
      dataIndex: 'order_number',
      key: 'order_number',
      render: (num: string) => <Tag color="blue" style={{ fontWeight: 600 }}>{num}</Tag>,
    },
    {
      title: 'Dark Store',
      dataIndex: 'store_name',
      key: 'store_name',
      render: (name: string) => name || 'Central Store',
    },
    {
      title: 'Assigned Operator',
      dataIndex: 'operator_name',
      key: 'operator_name',
      render: (name: string) => name || 'Unassigned',
    },
    {
      title: 'Verification Status',
      dataIndex: 'verification_status',
      key: 'verification_status',
      render: (verStatus: string) => {
        let color = 'default';
        let icon = null;
        if (verStatus === 'PASS') {
          color = 'green';
          icon = <CheckCircleOutlined />;
        } else if (verStatus === 'WARNING') {
          color = 'gold';
          icon = <WarningOutlined />;
        } else if (verStatus === 'FAIL') {
          color = 'red';
          icon = <CloseCircleOutlined />;
        }
        return (
          <Tag color={color} icon={icon} style={{ fontWeight: 600 }}>
            {verStatus}
          </Tag>
        );
      },
    },
    {
      title: 'Packing Score',
      dataIndex: 'packing_score',
      key: 'packing_score',
      render: (score: number | null) => (
        score !== null && score !== undefined ? (
          <Space>
            <Progress
              type="circle"
              percent={score}
              width={28}
              strokeColor={score >= 80 ? '#52c41a' : score >= 60 ? '#faad14' : '#f5222d'}
            />
            <Text strong>{score} / 100</Text>
          </Space>
        ) : (
          <Text type="secondary">—</Text>
        )
      ),
    },
    {
      title: 'Order Date',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (dateStr: string) => new Date(dateStr).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Order) => (
        <Space>
          <Button icon={<EyeOutlined />} size="small" onClick={() => handleViewOrder(record)}>
            Details
          </Button>
          <Button
            type="primary"
            icon={<SafetyCertificateOutlined />}
            size="small"
            onClick={() => handleStartVerification(record.id)}
          >
            Verify
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>
          Dark Store Packing Orders
        </Title>
        <Text type="secondary">
          Track customer orders, line item sensitivity requirements, and verification results
        </Text>
      </div>

      <Card bordered={false}>
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="Search by order number..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 300 }}
            allowClear
          />

          <Select
            placeholder="Filter Verification Status"
            style={{ width: 220 }}
            allowClear
            onChange={(val) => setStatusFilter(val)}
            options={[
              { label: 'PASS Orders', value: 'PASS' },
              { label: 'WARNING Orders', value: 'WARNING' },
              { label: 'FAIL Orders', value: 'FAIL' },
              { label: 'UNVERIFIED Orders', value: 'UNVERIFIED' },
            ]}
          />
        </Space>

        <Table
          columns={columns}
          dataSource={orders}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={`Order Details: ${selectedOrder?.order_number || ''}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setModalVisible(false)}>
            Close
          </Button>,
          <Button
            key="verify"
            type="primary"
            icon={<SafetyCertificateOutlined />}
            onClick={() => {
              setModalVisible(false);
              if (selectedOrder) handleStartVerification(selectedOrder.id);
            }}
          >
            Start Packing Verification
          </Button>,
        ]}
        width={650}
      >
        {selectedOrder && (
          <div>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Row gutter={16}>
                <Col span={12}>
                  <Text type="secondary" block>Dark Store:</Text>
                  <Text strong>{selectedOrder.store_name || 'Central Store'}</Text>
                </Col>
                <Col span={12}>
                  <Text type="secondary" block>Verification Status:</Text>
                  <Tag color={selectedOrder.verification_status === 'PASS' ? 'green' : selectedOrder.verification_status === 'FAIL' ? 'red' : 'gold'}>
                    {selectedOrder.verification_status}
                  </Tag>
                </Col>
              </Row>

              <Divider style={{ margin: '12px 0' }} />

              <Title level={5}>Order Items & Quality Requirements ({selectedOrder.items?.length || 0})</Title>
              <List
                itemLayout="horizontal"
                dataSource={selectedOrder.items || []}
                renderItem={(item) => {
                  let snapshot: any = {};
                  try {
                    snapshot = typeof item.item_attributes_snapshot === 'string'
                      ? JSON.parse(item.item_attributes_snapshot)
                      : item.item_attributes_snapshot || {};
                  } catch (e) {}

                  return (
                    <List.Item>
                      <List.Item.Meta
                        title={
                          <Space>
                            <Text strong>{item.product?.name || snapshot.name || 'Product Item'}</Text>
                            <Tag color="geekblue">{item.product?.sku || snapshot.sku}</Tag>
                            <Badge count={`Qty: ${item.quantity}`} style={{ backgroundColor: '#52c41a' }} />
                          </Space>
                        }
                        description={
                          <Space wrap style={{ marginTop: 4 }}>
                            {(item.product?.is_fragile || snapshot.is_fragile) && (
                              <Tag color="magenta" icon={<AlertOutlined />}>FRAGILE</Tag>
                            )}
                            {(item.product?.is_liquid || snapshot.is_liquid) && (
                              <Tag color="cyan" icon={<ExperimentOutlined />}>LIQUID</Tag>
                            )}
                            {(item.product?.temperature_req === 'FROZEN' || snapshot.temperature_req === 'FROZEN') && (
                              <Tag color="purple">FROZEN</Tag>
                            )}
                            {(item.product?.temperature_req === 'COLD' || snapshot.temperature_req === 'COLD') && (
                              <Tag color="blue">COLD</Tag>
                            )}
                            {(item.product?.is_crush_sensitive || snapshot.is_crush_sensitive) && (
                              <Tag color="orange">CRUSH SENSITIVE</Tag>
                            )}
                          </Space>
                        }
                      />
                    </List.Item>
                  );
                }}
              />
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
}
