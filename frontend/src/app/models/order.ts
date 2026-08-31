export interface Order {
  id: number;
  user_id: number;
  total_amount: number;
  status: string;
  created_at?: string;
}
