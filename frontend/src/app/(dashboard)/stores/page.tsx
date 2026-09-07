'use client';

import React, { useEffect, useState } from 'react';
import { Table, Card, Button, Input, Tag, Space, Drawer, Form, Switch, Typography, message } from 'antd';
import { PlusOutlined, SearchOutlined, ShopOutlined, EditOutlined } from '@ant-design/icons';
import apiClient from '@/services/api';
import { APIResponse, Store } from '@/types';

const { Title, Text } = Typography;

export default function StoresPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [editingStore, setEditingStore] = useState<Store | null>(null);
  const [form] = Form.useForm();

  const fetchStores = async () => {
    setLoading(true);
    try {
      const res = (await apiClient.get('/stores', { params: { search } })) as unknown as APIResponse<Store[]>;
      if (res.success && res.data) {
        setStores(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch stores:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStores();
  }, [search]);

  const handleOpenDrawer = (store?: Store) => {
    if (store) {
      setEditingStore(store);
      form.setFieldsValue(store);
    } else {
      setEditingStore(null);
      form.resetFields();
      form.setFieldsValue({ is_active: true });
    }
    setDrawerVisible(true);
  };

  const handleFormSubmit = async (values: any) => {
    try {
      if (editingStore) {
        await apiClient.put(`/stores/${editingStore.id}`, values);
        message.success('Store updated successfully');
      } else {
        await apiClient.post('/stores', values);
        message.success('Store created successfully');
      }
      setDrawerVisible(false);
      fetchStores();
    } catch (err: any) {
      message.error(err?.error?.message || 'Failed to save store');
    }
  };

  const columns = [
    {
      title: 'Store Code',
      dataIndex: 'store_code',
      key: 'store_code',
      render: (code: string) => <Tag color="blue" style={{ fontWeight: 600 }}>{code}</Tag>,
    },
    {
      title: 'Store Name',
      dataIndex: 'store_name',
      key: 'store_name',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? 'ACTIVE' : 'INACTIVE'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Store) => (
        <Button icon={<EditOutlined />} size="small" onClick={() => handleOpenDrawer(record)}>
          Edit
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={3} style={{ margin: 0 }}>
            Dark Stores Master Data
          </Title>
          <Text type="secondary">
            Manage dark store fulfillment centers and regional micro-hubs
          </Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => handleOpenDrawer()}>
          Add Dark Store
        </Button>
      </div>

      <Card bordered={false}>
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="Search by store code or name..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 320 }}
            allowClear
          />
        </Space>

        <Table
          columns={columns}
          dataSource={stores}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title={editingStore ? 'Edit Dark Store' : 'Add New Dark Store'}
        width={420}
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleFormSubmit}>
          <Form.Item
            name="store_code"
            label="Store Code"
            rules={[{ required: true, message: 'Store code is required' }]}
          >
            <Input placeholder="e.g. STR-BLR-01" disabled={!!editingStore} />
          </Form.Item>

          <Form.Item
            name="store_name"
            label="Store Name"
            rules={[{ required: true, message: 'Store name is required' }]}
          >
            <Input placeholder="e.g. Indiranagar Dark Store" />
          </Form.Item>

          <Form.Item
            name="location"
            label="Location / Region"
            rules={[{ required: true, message: 'Location is required' }]}
          >
            <Input placeholder="e.g. Bangalore, KA" />
          </Form.Item>

          <Form.Item name="is_active" label="Active Status" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item style={{ marginTop: 24 }}>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingStore ? 'Save Changes' : 'Create Store'}
              </Button>
              <Button onClick={() => setDrawerVisible(false)}>Cancel</Button>
            </Space>
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  );
}
