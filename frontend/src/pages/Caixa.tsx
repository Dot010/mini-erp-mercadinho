import { useEffect, useRef, useState, type FormEvent } from "react";
import { api } from "../api";
import {
  adicionar,
  quantidadeDeItens,
  remover,
  subtotal,
  totalEmCentavos,
  type Item,
} from "../carrinho";
import { ChamadosTotem } from "../components/ChamadosTotem";
import { paraCentavos, reais } from "../dinheiro";
import type { Pagamento, Produto, Venda } from "../tipos";

const PAGAMENTOS: { valor: Pagamento; texto: string }[] = [
  { valor: "dinheiro", texto: "Dinheiro" },
  { valor: "cartao", texto: "Cartão" },
  { valor: "pix", texto: "Pix" },
];

export function Caixa() {
  const [codigo, setCodigo] = useState("");
  const [quantidade, setQuantidade] = useState(1);
  const [itens, setItens] = useState<Item[]>([]);

  const itensAgora = useRef<Item[]>([]);
  const [pagamento, setPagamento] = useState<Pagamento>("pix");
  const [erro, setErro] = useState("");
  const [ultima, setUltima] = useState<Venda | null>(null);
  const [enviando, setEnviando] = useState(false);
  const campoCodigo = useRef<HTMLInputElement>(null);
  const finalizarRef = useRef<() => void>(() => {});

  function mudarItens(novos: Item[]) {
    itensAgora.current = novos;
    setItens(novos);
  }

  async function bipar(evento: FormEvent) {
    evento.preventDefault();
    const lido = codigo;
    setCodigo("");
    setErro("");
    try {
      const lidos = await api<Produto[]>(`/produtos/?codigo=${encodeURIComponent(lido)}`);
      if (lidos.length === 0) throw new Error(`Nenhum produto com o código ${lido}.`);
      mudarItens(adicionar(itensAgora.current, lidos[0], quantidade));
      setQuantidade(1);
    } catch (e) {
      setErro((e as Error).message);
    }
    campoCodigo.current?.focus();
  }

  async function finalizar() {
    if (itens.length === 0 || enviando) return;
    setErro("");
    setEnviando(true);
    try {
      const venda = await api<Venda>("/vendas/", {
        metodo: "POST",
        corpo: {
          pagamento,
          itens: itens.map((item) => ({
            produto: item.produto.codigo_barras,
            quantidade: item.quantidade,
          })),
        },
      });
      setUltima(venda);
      mudarItens([]);
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setEnviando(false);
      campoCodigo.current?.focus();
    }
  }

  // O atalho F9 sempre chama a versão mais nova do finalizar.
  useEffect(() => {
    finalizarRef.current = finalizar;
  });

  useEffect(() => {
    function atalho(evento: KeyboardEvent) {
      if (evento.key === "F2") {
        evento.preventDefault();
        campoCodigo.current?.focus();
      }
      if (evento.key === "F9") {
        evento.preventDefault();
        finalizarRef.current();
      }
    }
    window.addEventListener("keydown", atalho);
    return () => window.removeEventListener("keydown", atalho);
  }, []);

  const total = totalEmCentavos(itens);

  return (
    <main className="caixa">
      <section className="caixa-itens" aria-label="Itens da venda">
        <form className="bipar" onSubmit={bipar}>
          <label className="campo-codigo">
            <span>
              Código de barras <kbd>[F2]</kbd>
            </span>
            <input
              ref={campoCodigo}
              autoFocus
              required
              inputMode="numeric"
              value={codigo}
              onChange={(e) => setCodigo(e.target.value.trim())}
            />
          </label>
          <label className="campo-qtd">
            Qtd.
            <input
              type="number"
              min={1}
              value={quantidade}
              onChange={(e) => setQuantidade(Math.max(1, Number(e.target.value)))}
            />
          </label>
          <button type="submit" className="botao">
            Adicionar
          </button>
        </form>

        {erro && <p role="alert" className="alerta">{erro}</p>}

        <div className="rolagem">
          <table className="tabela">
            <thead>
              <tr>
                <th>#</th>
                <th>Produto</th>
                <th className="num">Qtd.</th>
                <th className="num">Unit.</th>
                <th className="num">Total</th>
                <th>
                  <span className="so-leitor">Remover</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {itens.map((item, i) => (
                <tr key={item.produto.id}>
                  <td className="mono fraco">{String(i + 1).padStart(3, "0")}</td>
                  <td>
                    {item.produto.nome}{" "}
                    <span className="mono fraco pequeno">{item.produto.codigo_barras}</span>
                  </td>
                  <td className="num mono">{item.quantidade}</td>
                  <td className="num mono">{reais(paraCentavos(item.produto.preco))}</td>
                  <td className="num mono forte">{reais(subtotal(item))}</td>
                  <td>
                    <button
                      type="button"
                      className="remover"
                      aria-label={`Remover ${item.produto.nome}`}
                      onClick={() => mudarItens(remover(itens, item.produto.id))}
                    >
                      ×
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {itens.length === 0 && <p className="fraco vazio">Bipe o primeiro produto.</p>}
        </div>
      </section>

      <aside className="caixa-pagamento" aria-label="Pagamento">
        <ChamadosTotem />
        <div className="etiqueta">
          <div className="etiqueta-topo">
            <span>TOTAL</span>
            <span className="mono">{quantidadeDeItens(itens)} itens</span>
          </div>
          <div className="etiqueta-valor mono">
            <span>R$</span>
            {reais(total)}
          </div>
        </div>

        <fieldset className="pagamentos">
          <legend>Pagamento</legend>
          <div>
            {PAGAMENTOS.map((opcao) => (
              <button
                key={opcao.valor}
                type="button"
                aria-pressed={pagamento === opcao.valor}
                onClick={() => setPagamento(opcao.valor)}
              >
                {opcao.texto}
              </button>
            ))}
          </div>
        </fieldset>

        <button
          type="button"
          className="botao grande"
          disabled={itens.length === 0 || enviando}
          onClick={finalizar}
        >
          Finalizar venda <kbd>[F9]</kbd>
        </button>
        <button type="button" className="link" onClick={() => mudarItens([])}>
          Limpar a venda
        </button>

        {ultima && (
          <p role="status" className="mono fraco pequeno ultima">
            última venda: #{ultima.id} · R$ {reais(paraCentavos(ultima.total))} ·{" "}
            {ultima.pagamento}
          </p>
        )}
      </aside>
    </main>
  );
}