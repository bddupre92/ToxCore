import type { Chemical } from "./chemical";

export interface Product {
  id: string;
  barcode: string | null;
  name: string;
  brand: string | null;
  category: string | null;
  subcategory: string | null;
  image_url: string | null;
  raw_ingredients: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProductScore {
  id: string;
  product_id: string;
  overall_score: number;
  hazard_score: number;
  exposure_score: number;
  transparency_score: number;
  grade: "A" | "B" | "C" | "D" | "F";
  scoring_version: string;
  score_details: Record<string, unknown>;
  computed_at: string;
}

export interface ProductWithScore extends Product {
  score: ProductScore | null;
}

export interface ProductIngredient {
  id: string;
  product_id: string;
  chemical_id: string | null;
  raw_name: string;
  resolved_name: string | null;
  position: number;
  confidence: number;
  chemical: Chemical | null;
}

export interface SearchResult {
  id: string;
  name: string;
  brand: string | null;
  category: string | null;
  image_url: string | null;
  overall_score: number | null;
  grade: string | null;
  rank: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  page: number;
  limit: number;
}

export interface ComparisonData {
  products: ProductWithScore[];
  ingredients: Record<string, ProductIngredient[]>;
  flagged_ingredients: Record<string, ProductIngredient[]>;
}
