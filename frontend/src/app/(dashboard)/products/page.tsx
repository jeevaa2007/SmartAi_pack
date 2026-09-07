'use client';

import React, { useEffect, useState } from 'react';
import { Table, Card, Button, Input, Select, Tag, Space, Drawer, Form, Switch, InputNumber, Typography, message, Row, Col } from 'antd';
import { PlusOutlined, SearchOutlined, EditOutlined, FireOutlined, ExperimentOutlined, AlertOutlined } from '@ant-design/icons';
import apiClient from '@/services/api';
import { APIResponse, Product } from '@/types';

const { Title, Text } = Typography;

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>(undefined);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [form] = Form.useForm();

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params: any = { search, limit: 100 };
      if (categoryFilter) params.category = categoryFilter;

      const res = (await apiClient.get('/products', { params })) as unknown as APIResponse<Product[]>;
      if (res.success && res.data) {
        setProducts(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch products:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [search, categoryFilter]);

  const handleOpenDrawer = (product?: Product) => {
    if (product) {
      setEditingProduct(product);
      form.setFieldsValue(product);
    } else {
      setEditingProduct(null);
      form.resetFields();
      form.setFieldsValue({
        is_active: true,
        temperature_req: 'AMBIENT',
        is_fragile: false,
        is_liquid: false,
        is_crush_sensitive: false,
        weight: 0.5,
      });
    }
    setDrawerVisible(true);
  };

  const handleFormSubmit = async (values: any) => {
    try {
      if (editingProduct) {
        await apiClient.put(`/products/${editingProduct.id}`, values);
        message.success('Product updated successfully');
      } else {
        await apiClient.post('/products', values);
        message.success('Product created successfully');
      }
      setDrawerVisible(false);
      fetchProducts();
    } catch (err: any) {
      message.error(err?.error?.message || 'Failed to save product');
    }
  };

  const columns = [
    {
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
      render: (sku: string) => <Tag color="geekblue" style={{ fontWeight: 600 }}>{sku}</Tag>,
    },
    {
      title: 'Product Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      render: (cat: string) => <Tag color="blue">{cat}</Tag>,
    },
    {
      title: 'Weight',
      dataIndex: 'weight',
      key: 'weight',
      render: (w: number) => `${w} kg`,
    },
    {
      title: 'Sensitivity Flags',
      key: 'sensitivity',
      render: (_: any, r: Product) => (
        <Space wrap>
          {r.is_fragile && <Tag color="magenta" icon={<AlertOutlined />}>FRAGILE</Tag>}
          {r.is_liquid && <Tag color="cyan" icon={<ExperimentOutlined />}>LIQUID</Tag>}
          {r.temperature_req === 'COLD' && <Tag color="blue">COLD</Tag>}
          {r.temperature_req === 'FROZEN' && <Tag color="purple">FROZEN</Tag>}
          {r.is_crush_sensitive && <Tag color="orange">CRUSH</Tag>}
        </Space>
      ),
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
      render: (_: any, record: Product) => (
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
            Catalog Products Master Data
          </Title>
          <Text type="secondary">
            Manage product physical attributes and quality sensitivity flags
          </Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => handleOpenDrawer()}>
          Add Product SKU
        </Button>
      </div>

      <Card bordered={false}>
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="Search by SKU or product name..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 300 }}
            allowClear
          />

          <Select
            placeholder="Filter by Category"
            style={{ width: 220 }}
            allowClear
            onChange={(val) => setCategoryFilter(val)}
            options={[
              { label: 'Beverages & Liquids', value: 'Beverages & Liquids' },
              { label: 'Dairy & Cold Goods', value: 'Dairy & Cold Goods' },
              { label: 'Frozen Foods', value: 'Frozen Foods' },
              { label: 'Bakery & Confectionery', value: 'Bakery & Confectionery' },
              { label: 'Glass Bottled Preserves', value: 'Glass Bottled Preserves' },
              { label: 'Fresh Produce & Fruits', value: 'Fresh Produce & Fruits' },
            ]}
          />
        </Space>

        <Table
          columns={columns}
          dataSource={products}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title={editingProduct ? 'Edit Product SKU' : 'Add New Product SKU'}
        width={480}
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleFormSubmit}>
          <Form.Item
            name="sku"
            label="Product SKU"
            rules={[{ required: true, message: 'SKU is required' }]}
          >
            <Input placeholder="e.g. SKU-PRD-1001" disabled={!!editingProduct} />
          </Form.Item>

          <Form.Item
            name="name"
            label="Product Name"
            rules={[{ required: true, message: 'Product name is required' }]}
          >
            <Input placeholder="e.g. Organic Whole Milk 1L" />
          </Form.Item>

          <Form.Item
            name="category"
            label="Category"
            rules={[{ required: true, message: 'Category is required' }]}
          >
            <Input placeholder="e.g. Dairy & Cold Goods" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="weight" label="Weight (kg)" rules={[{ required: true }]}>
                <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="dimensions" label="Dimensions">
                <Input placeholder="e.g. 10x10x25 cm" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="temperature_req" label="Temperature Requirement">
            <Select
              options={[
                { label: 'AMBIENT (Room Temp)', value: 'AMBIENT' },
                { label: 'COLD (Refrigerated)', value: 'COLD' },
                { label: 'FROZEN (Sub-Zero)', value: 'FROZEN' },
              ]}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="is_fragile" label="Fragile Item" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="is_liquid" label="Liquid Item" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="is_crush_sensitive" label="Crush Sensitive" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="is_active" label="Active Status" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item style={{ marginTop: 24 }}>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingProduct ? 'Save Changes' : 'Create Product'}
              </Button>
              <Button onClick={() => setDrawerVisible(false)}>Cancel</Button>
            </Space>
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  );
}
