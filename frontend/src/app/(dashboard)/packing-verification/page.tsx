'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  Row,
  Col,
  Card,
  Select,
  Button,
  Upload,
  Tag,
  Typography,
  Space,
  Alert,
  Progress,
  List,
  Divider,
  Result,
  Spin,
  message,
  Image,
} from 'antd';
import {
  SafetyCertificateOutlined,
  UploadOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  AlertOutlined,
  ExperimentOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import apiClient from '@/services/api';
import { APIResponse, Order, PackagingMaterial, PackingVerificationResult } from '@/types';

const { Title, Text, Paragraph } = Typography;

export default function PackingVerificationPage() {
  const searchParams = useSearchParams();
  const initialOrderId = searchParams.get('order_id');

  const [orders, setOrders] = useState<Order[]>([]);
  const [materials, setMaterials] = useState<PackagingMaterial[]>([]);
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(initialOrderId);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [selectedMaterialIds, setSelectedMaterialIds] = useState<string[]>([]);
  const [imagePath, setImagePath] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<PackingVerificationResult | null>(null);
  const [loadingOrders, setLoadingOrders] = useState(true);

  useEffect(() => {
    fetchOrdersAndMaterials();
  }, []);

  useEffect(() => {
    if (selectedOrderId && orders.length > 0) {
      const order = orders.find((o) => o.id === selectedOrderId);
      if (order) {
        setSelectedOrder(order);
        fetchExistingVerification(order.id);
      }
    }
  }, [selectedOrderId, orders]);

  const fetchOrdersAndMaterials = async () => {
    setLoadingOrders(true);
    try {
      const [ordersRes, matRes] = await Promise.all([
        apiClient.get('/orders', { params: { limit: 100 } }) as unknown as APIResponse<Order[]>,
        apiClient.get('/packaging/materials') as unknown as APIResponse<PackagingMaterial[]>,
      ]);

      if (ordersRes.success && ordersRes.data) {
        setOrders(ordersRes.data);
        if (initialOrderId) {
          const found = ordersRes.data.find((o) => o.id === initialOrderId);
          if (found) setSelectedOrder(found);
        }
      }

      if (matRes.success && matRes.data) {
        setMaterials(matRes.data);
      }
    } catch (err) {
      console.error('Failed to fetch initial data:', err);
    } finally {
      setLoadingOrders(false);
    }
  };

  const fetchExistingVerification = async (orderId: string) => {
    try {
      const res = (await apiClient.get(`/packing-verification/order/${orderId}`)) as unknown as APIResponse<PackingVerificationResult | null>;
      if (res.success && res.data) {
        setVerificationResult(res.data);
        if (res.data.image_path) setImagePath(res.data.image_path);
      } else {
        setVerificationResult(null);
      }
    } catch (err) {
      setVerificationResult(null);
    }
  };

  const handleCustomUpload = async (options: any) => {
    const { file, onSuccess, onError } = options;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post('/packing-verification/upload-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }) as any;

      if (response.success && response.data) {
        setImagePath(response.data.saved_path);
        message.success('Packing image uploaded successfully');
        onSuccess(response.data);
      } else {
        message.error('Failed to upload image');
        onError(new Error('Upload failed'));
      }
    } catch (err: any) {
      message.error(err?.error?.message || 'Error uploading file');
      onError(err);
    } finally {
      setUploading(false);
    }
  };

  const handleRunVerification = async () => {
    if (!selectedOrderId) {
      message.warning('Please select an order to verify');
      return;
    }
    if (selectedMaterialIds.length === 0) {
      message.warning('Please select at least one packaging material used');
      return;
    }

    setVerifying(true);
    try {
      const response = (await apiClient.post('/packing-verification/verify', {
        order_id: selectedOrderId,
        packaging_material_ids: selectedMaterialIds,
        image_path: imagePath,
      })) as unknown as APIResponse<PackingVerificationResult>;

      if (response.success && response.data) {
        setVerificationResult(response.data);
        message.success(`Packing verification complete: ${response.data.status}`);
      } else {
        message.error(response.error?.message || 'Verification failed');
      }
    } catch (err: any) {
      message.error(err?.error?.message || 'Verification failed');
    } finally {
      setVerifying(false);
    }
  };

  if (loadingOrders) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Initializing Packing Quality Verification Engine..." />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={3} style={{ margin: 0 }}>
            Rule-Based Packing Quality Verification
          </Title>
          <Text type="secondary">
            AI & Rule Verification Engine evaluating item sensitivities, cold-chain isolation, and protective materials
          </Text>
        </div>
        <Tag color="purple" icon={<ThunderboltOutlined />} style={{ padding: '4px 12px', fontSize: 13 }}>
          DETERMINISTIC VERIFICATION ENGINE
        </Tag>
      </div>

      <Row gutter={[24, 24]}>
        {/* Left Column: Order Selection & Configuration */}
        <Col xs={24} lg={12}>
          <Card title="1. Select Order & Input Packaging" bordered={false}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text strong block style={{ marginBottom: 8 }}>Select Dark Store Order:</Text>
                <Select
                  showSearch
                  placeholder="Search and select order..."
                  style={{ width: '100%' }}
                  value={selectedOrderId}
                  onChange={(val) => {
                    setSelectedOrderId(val);
                    setVerificationResult(null);
                  }}
                  filterOption={(input, option) =>
                    (option?.label ?? '').toString().toLowerCase().includes(input.toLowerCase())
                  }
                  options={orders.map((o) => ({
                    value: o.id,
                    label: `${o.order_number} (${o.store_name || 'Store'}) - [${o.verification_status}]`,
                  }))}
                />
              </div>

              {selectedOrder && (
                <div>
                  <Title level={5}>Order Line Items ({selectedOrder.items?.length || 0})</Title>
                  <List
                    size="small"
                    bordered
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
                          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                            <div>
                              <Text strong>{item.product?.name || snapshot.name || 'Item'}</Text>
                              <Text type="secondary" block style={{ fontSize: 12 }}>
                                SKU: {item.product?.sku || snapshot.sku} | Qty: {item.quantity}
                              </Text>
                            </div>
                            <Space wrap>
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
                                <Tag color="orange">CRUSH</Tag>
                              )}
                            </Space>
                          </Space>
                        </List.Item>
                      );
                    }}
                  />
                </div>
              )}

              <Divider />

              <div>
                <Text strong block style={{ marginBottom: 8 }}>2. Select Declared Packaging Materials Used:</Text>
                <Select
                  mode="multiple"
                  placeholder="Select packaging materials used for this order..."
                  style={{ width: '100%' }}
                  value={selectedMaterialIds}
                  onChange={(vals) => setSelectedMaterialIds(vals)}
                  options={materials.map((m) => ({
                    value: m.id,
                    label: `${m.name} (${m.material_type}) - [${m.protection_level} Prot]`,
                  }))}
                />
              </div>

              <div>
                <Text strong block style={{ marginBottom: 8 }}>3. Controlled Packing Image Proof:</Text>
                <Upload customRequest={handleCustomUpload} showUploadList={false}>
                  <Button icon={<UploadOutlined />} loading={uploading}>
                    Upload Packing Photograph
                  </Button>
                </Upload>
                {imagePath && (
                  <div style={{ marginTop: 12 }}>
                    <Text type="success" block style={{ marginBottom: 6 }}>✓ Image attached: {imagePath}</Text>
                    <Image src={`http://localhost:8000/api/v1/${imagePath}`} alt="Packing Proof" width={160} style={{ borderRadius: 6 }} />
                  </div>
                )}
              </div>

              <Button
                type="primary"
                size="large"
                icon={<SafetyCertificateOutlined />}
                block
                loading={verifying}
                onClick={handleRunVerification}
                style={{ height: 48, fontSize: 16 }}
              >
                Execute Quality Verification Engine
              </Button>
            </Space>
          </Card>
        </Col>

        {/* Right Column: Verification Results Display */}
        <Col xs={24} lg={12}>
          <Card title="Packing Verification Outcome & Score" bordered={false}>
            {verificationResult ? (
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                {/* Status Banner */}
                <Alert
                  message={
                    <Space>
                      {verificationResult.status === 'PASS' && <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />}
                      {verificationResult.status === 'WARNING' && <WarningOutlined style={{ fontSize: 24, color: '#faad14' }} />}
                      {verificationResult.status === 'FAIL' && <CloseCircleOutlined style={{ fontSize: 24, color: '#f5222d' }} />}
                      <Title level={4} style={{ margin: 0, color: verificationResult.status === 'PASS' ? '#52c41a' : verificationResult.status === 'WARNING' ? '#faad14' : '#f5222d' }}>
                        VERIFICATION STATUS: {verificationResult.status}
                      </Title>
                    </Space>
                  }
                  description={
                    verificationResult.status === 'PASS'
                      ? 'Package meets all dark store quality standards. Ready for dispatch.'
                      : verificationResult.status === 'WARNING'
                      ? 'Quality warnings detected. Action recommended before dispatch.'
                      : 'PACKING QUALITY FAILURE. DISPATCH BLOCKED. Repacking required.'
                  }
                  type={verificationResult.status === 'PASS' ? 'success' : verificationResult.status === 'WARNING' ? 'warning' : 'error'}
                  showIcon={false}
                />

                {/* Score Meter */}
                <div style={{ textAlign: 'center', padding: '16px 0', background: '#fafafa', borderRadius: 8 }}>
                  <Progress
                    type="dashboard"
                    percent={verificationResult.packing_score}
                    strokeColor={
                      verificationResult.packing_score >= 80
                        ? '#52c41a'
                        : verificationResult.packing_score >= 60
                        ? '#faad14'
                        : '#f5222d'
                    }
                  />
                  <Title level={4} style={{ margin: '8px 0 0' }}>
                    Packing Score: {verificationResult.packing_score} / 100
                  </Title>
                  <Text type="secondary">Deterministic Rule Score</Text>
                </div>

                {/* Violations List */}
                <div>
                  <Title level={5}>Detected Rule Violations ({verificationResult.violations.length})</Title>
                  {verificationResult.violations.length === 0 ? (
                    <Text type="success">No rule violations detected.</Text>
                  ) : (
                    <List
                      dataSource={verificationResult.violations}
                      renderItem={(v) => (
                        <List.Item>
                          <List.Item.Meta
                            title={
                              <Space>
                                <Tag color={v.severity === 'CRITICAL' ? 'red' : v.severity === 'HIGH' ? 'orange' : 'gold'}>
                                  {v.severity} (-{v.deduction} pts)
                                </Tag>
                                <Text strong>{v.rule_name}</Text>
                              </Space>
                            }
                            description={
                              <div>
                                <Paragraph style={{ margin: '4px 0 0', color: '#595959' }}>{v.description}</Paragraph>
                                {v.detected_value && (
                                  <Text type="secondary" style={{ fontSize: 12 }} block>
                                    Detected: {v.detected_value} | Expected: {v.expected_value}
                                  </Text>
                                )}
                              </div>
                            }
                          />
                        </List.Item>
                      )}
                    />
                  )}
                </div>

                {/* Recommendations List */}
                <div>
                  <Title level={5}>Actionable Quality Recommendations</Title>
                  <List
                    bordered
                    dataSource={verificationResult.recommendations}
                    renderItem={(rec) => (
                      <List.Item>
                        <Text strong style={{ color: '#1677ff' }}>• {rec}</Text>
                      </List.Item>
                    )}
                  />
                </div>
              </Space>
            ) : (
              <div style={{ textAlign: 'center', padding: '60px 20px' }}>
                <SafetyCertificateOutlined style={{ fontSize: 64, color: '#bfbfbf', marginBottom: 16 }} />
                <Title level={4} type="secondary">
                  Ready for Quality Verification
                </Title>
                <Text type="secondary">
                  Select an order on the left, declare packaging materials used, and click "Execute Quality Verification Engine".
                </Text>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
