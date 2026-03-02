export interface Chemical {
  id: string;
  dtxsid: string | null;
  cas_number: string | null;
  preferred_name: string;
  inci_name: string | null;
  molecular_formula: string | null;
  molecular_weight: number | null;
  smiles: string | null;
  description: string | null;
  hazard_data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface RegulatoryStatus {
  id: string;
  chemical_id: string;
  list_name: string;
  list_full_name: string;
  status: string;
  classification: string | null;
  details: Record<string, unknown>;
  effective_date: string | null;
  source_url: string | null;
}
