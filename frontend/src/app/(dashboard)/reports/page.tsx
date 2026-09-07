'use client';

import React from 'react';
import { Card, Result, Button, Typography, Tag } from 'antd';
import { BarChartOutlined, RocketOutlined } from '@ant-design/icons';
import Link from 'next/link';

const { Title, Text } = Typography;

export default function ReportsPage() {
  return (
    <Card bordered={false}>
      <Result
        icon={<BarChartOutlined style={{ color: '#1890ff', fontSize: 64 }} />}
        title="Advanced Analytics & Compliance Reports"
        subTitle="Historical trend analysis, dark store performance leaderboard, and damage root-cause reports will be enabled in subsequent milestones."
        extra={[
          <Tag color="orange" key="tag" style={{ padding: '4px 12px', fontSize: 13, marginBottom: 16 }}>
            PLANNED FOR 50% / 75% MILESTONES
          </Tag>,
          <div key="actions" style={{ marginTop: 16 }}>
            <Link href="/dashboard">
              <Button type="primary" icon={<RocketOutlined />}>
                Return to Operational Control Center
              </Button>
            </Link>
          </div>,
        ]}
      />
    </Card>
  );
}
