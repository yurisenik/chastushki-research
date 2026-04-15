export type GeneratePackRequest = {
  occasion: string;
  target: string;
  facts: string[];
  tone: string;
  boldness: number;
  safe_mode: boolean;
  count: number;
};

export type Candidate = {
  id: string;
  text: string;
  score: number;
  safe: boolean;
};

export type Pack = {
  pack_id: string;
  source_pack_id?: string | null;
  candidates: Candidate[];
  created_at: string;
};

export type HistoryResponse = {
  items: Pack[];
};
