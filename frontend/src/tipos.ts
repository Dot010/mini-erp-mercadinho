export type Papel = "dono" | "caixa" | "estoquista" | "totem";

export type Usuario = {
  id: number;
  email: string;
  first_name: string;
  papel: Papel;
};

export type Produto = {
  id: number;
  nome: string;
  codigo_barras: string;
  preco: string;
  estoque: number;
  ativo: boolean;
  restrito: boolean;
};

export type Pagamento = "dinheiro" | "cartao" | "pix";

export type ItemVenda = {
  produto: string;
  quantidade: number;
  preco_unitario: string;
  subtotal: string;
};

export type Venda = {
  id: number;
  operador: string;
  pagamento: Pagamento;
  status: "finalizada" | "cancelada";
  total: string;
  criada_em: string;
  itens: ItemVenda[];
};

export type Chamado = {
  id: number;
  totem: string;
  motivo: string;
  status: "aberto" | "liberado" | "usado";
  liberado_por: string | null;
  criado_em: string;
};

export type Resumo = {
  inicio: string;
  fim: string;
  total: string;
  vendas: number;
  ticket_medio: string;
  por_pagamento: { pagamento: Pagamento; vendas: number; total: string }[];
  mais_vendidos: { nome: string; quantidade: number }[];
};

export const NOME_PAGAMENTO: Record<Pagamento, string> = {
  dinheiro: "Dinheiro",
  cartao: "Cartão",
  pix: "Pix",
};


export type Relatorio = {
  id: number;
  inicio: string;
  fim: string;
  status: "pendente" | "pronto" | "erro";
  dados: Resumo | null;
  criado_em: string;
  terminado_em: string | null;
};