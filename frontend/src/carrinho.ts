import { paraCentavos } from "./dinheiro";
import type { Produto } from "./tipos";

export type Item = { produto: Produto; quantidade: number };

export function adicionar(itens: Item[], produto: Produto, quantidade: number): Item[] {
  const jaTem = itens.find((item) => item.produto.id === produto.id);
  const total = (jaTem?.quantidade ?? 0) + quantidade;

  if (!produto.ativo) throw new Error(`${produto.nome} não está à venda.`);
  if (total > produto.estoque) {
    throw new Error(`${produto.nome} não entrou: só tem ${produto.estoque} no estoque.`);
  }

  if (jaTem) {
    return itens.map((item) =>
      item.produto.id === produto.id ? { ...item, quantidade: total } : item,
    );
  }
  return [...itens, { produto, quantidade }];
}

export function remover(itens: Item[], produtoId: number): Item[] {
  return itens.filter((item) => item.produto.id !== produtoId);
}

export function subtotal(item: Item) {
  return paraCentavos(item.produto.preco) * item.quantidade;
}

export function totalEmCentavos(itens: Item[]) {
  return itens.reduce((soma, item) => soma + subtotal(item), 0);
}

export function quantidadeDeItens(itens: Item[]) {
  return itens.reduce((soma, item) => soma + item.quantidade, 0);
}
