import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth/contexto";
import { FormEntrada } from "../components/FormEntrada";
import { FormProduto } from "../components/FormProduto";
import { paraCentavos, reais } from "../dinheiro";
import type { Produto } from "../tipos";

export const POUCO = 5;

const FILTROS = {
  todos: { texto: "Todos", passa: (p: Produto) => p.ativo },
  acabando: { texto: "Acabando", passa: (p: Produto) => p.ativo && p.estoque > 0 && p.estoque <= POUCO },
  sem: { texto: "Sem estoque", passa: (p: Produto) => p.ativo && p.estoque === 0 },
  inativos: { texto: "Inativos", passa: (p: Produto) => !p.ativo },
};
type Filtro = keyof typeof FILTROS;

export function Estoque() {
  const { usuario } = useAuth();
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [filtro, setFiltro] = useState<Filtro>("todos");
  const [busca, setBusca] = useState("");
  const [aberto, setAberto] = useState<"entrada" | "produto" | null>(null);
  const [erro, setErro] = useState("");

  function carregar() {
    api<Produto[]>("/produtos/")
      .then(setProdutos)
      .catch((e: Error) => setErro(e.message));
  }

  useEffect(carregar, []);

  async function alternarAtivo(produto: Produto) {
    try {
      await api(`/produtos/${produto.id}/`, { metodo: "PATCH", corpo: { ativo: !produto.ativo } });
      carregar();
    } catch (e) {
      setErro((e as Error).message);
    }
  }

  function pronto() {
    setAberto(null);
    carregar();
  }

  const termo = busca.toLowerCase();
  const visiveis = produtos
    .filter(FILTROS[filtro].passa)
    .filter((p) => p.nome.toLowerCase().includes(termo) || p.codigo_barras.includes(termo));
  const ehDono = usuario?.papel === "dono";

  return (
    <main className="pagina">
      <div className="pagina-topo">
        <h1>Estoque</h1>
        <div className="acoes">
          <button type="button" className="botao claro" onClick={() => setAberto("entrada")}>
            Lançar entrada
          </button>
          <button type="button" className="botao" onClick={() => setAberto("produto")}>
            + Produto
          </button>
        </div>
      </div>

      {aberto === "entrada" && (
        <FormEntrada produtos={produtos} aoTerminar={pronto} aoCancelar={() => setAberto(null)} />
      )}
      {aberto === "produto" && <FormProduto aoTerminar={pronto} aoCancelar={() => setAberto(null)} />}
      {erro && <p role="alert" className="alerta">{erro}</p>}

      <div className="filtros">
        <div role="group" aria-label="Filtro">
          {(Object.keys(FILTROS) as Filtro[]).map((chave) => (
            <button
              key={chave}
              type="button"
              aria-pressed={filtro === chave}
              onClick={() => setFiltro(chave)}
            >
              {FILTROS[chave].texto}{" "}
              <span className="mono">{produtos.filter(FILTROS[chave].passa).length}</span>
            </button>
          ))}
        </div>
        <label>
          Buscar
          <input
            type="search"
            placeholder="nome ou código"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
          />
        </label>
      </div>

      <div className="rolagem">
        <table className="tabela">
          <thead>
            <tr>
              <th>Produto</th>
              <th>Código</th>
              <th className="num">Preço</th>
              <th className="num">Em estoque</th>
              {ehDono && <th>À venda</th>}
            </tr>
          </thead>
          <tbody>
            {visiveis.map((p) => (
              <tr key={p.id} className={p.estoque === 0 && p.ativo ? "linha-zerada" : undefined}>
                <td className="forte">
                  {p.nome}
                  {p.estoque === 0 && p.ativo && <span className="selo">sem estoque</span>}
                </td>
                <td className="mono fraco">{p.codigo_barras}</td>
                <td className="num">{reais(paraCentavos(p.preco))}</td>
                <td className={`num mono forte ${p.estoque <= POUCO ? "vermelho" : ""}`}>
                  {p.estoque} un
                </td>
                {ehDono && (
                  <td>
                    <label className="alternar">
                      <input type="checkbox" checked={p.ativo} onChange={() => alternarAtivo(p)} />
                      <span className="so-leitor">{p.nome} à venda</span>
                    </label>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        {visiveis.length === 0 && <p className="fraco vazio">Nenhum produto aqui.</p>}
      </div>
      <p className="fraco pequeno">
        Em vermelho: {POUCO} unidades ou menos. O estoque não se edita aqui; só muda por entrada,
        saída ou venda.
      </p>
    </main>
  );
}