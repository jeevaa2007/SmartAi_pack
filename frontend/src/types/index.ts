export interface User {
  id: string;
  full_name: string;
  email: string;
  role_name: string;
  store_id?: string | null;
  is_active: boolean;
  is_verified: boolean;
  last_login_at?: string | null;
  created_at: string;
}

export interface APIErrorDetail {
  code: string;
  message: string;
  details?: any;
}

export interface APIResponse<T = any> {
  success: boolean;
  data: T;
  error?: APIErrorDetail | null;
  meta?: Record<string, any> | null;
}

export interface LoginResponseData {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Store {
  id: string;
  store_code: string;
  store_name: string;
  location: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  sku: string;
  name: string;
  category: string;
  weight: number;
  dimensions?: string | null;
  is_fragile: boolean;
  temperature_req: 'AMBIENT' | 'COLD' | 'FROZEN';
  is_liquid: boolean;
  is_crush_sensitive: boolean;
  preferred_packaging_type?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OperatorPerformance {
  id: string;
  full_name: string;
  email: string;
  role_name: string;
  store_name?: string | null;
  is_active: boolean;
  is_verified: boolean;
  last_login_at?: string | null;
  total_verifications: number;
  avg_packing_score: number;
}

export interface PackagingMaterial {
  id: string;
  name: string;
  code: string;
  material_type: string;
  capacity_size: string;
  protection_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'MAXIMUM';
  temperature_suitability: 'ALL' | 'AMBIENT' | 'COLD_CHAIN';
  is_active: boolean;
  created_at: string;
}

export interface PackagingRule {
  id: string;
  rule_code: string;
  name: string;
  description: string;
  rule_type: string;
  condition_json?: any;
  required_material_type?: string | null;
  min_protection_level?: string | null;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  deduction_points: number;
  is_active: boolean;
  created_at: string;
}

export interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  product_name: string;
  sku: string;
  quantity: number;
  item_attributes_snapshot?: {
    is_fragile?: boolean;
    is_liquid?: boolean;
    temperature_req?: string;
    is_crush_sensitive?: boolean;
    category?: string;
  };
}

export interface Order {
  id: string;
  order_number: string;
  store_id: string;
  store_code?: string;
  store_name?: string;
  operator_id?: string | null;
  operator_name?: string | null;
  status: 'CREATED' | 'PACKING' | 'READY_FOR_VERIFICATION' | 'VERIFIED' | 'DISPATCHED' | 'CANCELLED';
  verification_status: 'UNVERIFIED' | 'PASS' | 'WARNING' | 'FAIL';
  packing_score?: number | null;
  items?: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface RuleViolationDetail {
  rule_code?: string;
  rule_name: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  description: string;
  detected_value?: string;
  expected_value?: string;
  deduction: number;
}

export interface PackingVerificationResult {
  id: string;
  order_id: string;
  order_number?: string;
  operator_id?: string | null;
  operator_name?: string | null;
  image_path?: string | null;
  packing_score: number;
  status: 'PASS' | 'WARNING' | 'FAIL';
  violations: RuleViolationDetail[];
  recommendations: string[];
  verified_at: string;
}

export interface DashboardStats {
  total_orders: number;
  verified_orders: number;
  pass_rate: number;
  warning_count: number;
  failure_count: number;
  avg_packing_score: number;
  recent_orders: Order[];
  recent_verifications: PackingVerificationResult[];
  outcome_breakdown: {
    pass: number;
    warning: number;
    fail: number;
  };
}
