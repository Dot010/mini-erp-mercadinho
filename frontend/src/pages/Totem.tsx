import { useEffect, useRef, useState, type FormEvent } from "react";
import { api } from "../api";
import { useAuth } from "../auth/contexto";
import {
  adicionar,
  quantidadeDeItens,
  remover,
  subtotal,
  totalEmCentavos,
  type Item,
} from "../carrinho";
import { paraCentavos, reais } from "../dinheiro";
import type { Chamado, Produto, Venda } from "../tipos";

export function Totem() {
  const { sair } = useAuth();
  const [codigo, setCodigo] = useState("");
  const [itens, setItens] = useState<Item[]>([]);
  const itensAgora = useRef<Item[]>([]);
  const [ultimo, setUltimo] = useState<Produto | null>(null);
  const [erro, setErro] = useState("");
  const campo = useRef<HTMLInputElement>(null);
  const [chamado, setChamado] = useState<Chamado | null>(null);
  const [pago, setPago] = useState<Venda | null>(null);

  async function chamarAtendente(motivo: string) {
    try {
      setChamado(
        await api<Chamado>("/chamados/", { metodo: "POST", corpo: { motivo } }),
      );
    } catch (e) {
      setErro((e as Error).message);
    }
  }
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
      const lidos = await api<Produto[]>(
        `/produtos/?codigo=${encodeURIComponent(lido)}`,
      );
      if (lidos.length === 0)
        throw new Error("Não achamos este produto. Chame um atendente.");
      const produto = lidos[0];
      mudarItens(adicionar(itensAgora.current, produto, 1));
      setUltimo(produto);
      if (produto.restrito && !chamado) await chamarAtendente(produto.nome);
    } catch (e) {
      setErro((e as Error).message);
    }
    campo.current?.focus();
  }

  function mudarQuantidade(item: Item, quanto: number) {
    setErro("");
    if (item.quantidade + quanto <= 0) {
      mudarItens(remover(itensAgora.current, item.produto.id));
      campo.current?.focus();
      return;
    }
    try {
      mudarItens(adicionar(itensAgora.current, item.produto, quanto));
    } catch (e) {
      setErro((e as Error).message);
    }
    campo.current?.focus();
  }
  useEffect(() => {
    if (chamado?.status !== "aberto") return;
    const relogio = setInterval(() => {
      api<Chamado>(`/chamados/${chamado.id}/`)
        .then(setChamado)
        .catch(() => {});
    }, 3000);
    return () => clearInterval(relogio);
  }, [chamado]);

  useEffect(() => {
    if (!pago) return;
    const espera = setTimeout(() => {
      setPago(null);
      setUltimo(null);
      setChamado(null);
      mudarItens([]);
    }, 6000);
    return () => clearTimeout(espera);
  }, [pago]);

  useEffect(() => {
    function atalho(evento: KeyboardEvent) {
      if (
        evento.ctrlKey &&
        evento.shiftKey &&
        evento.key.toLowerCase() === "e"
      ) {
        evento.preventDefault();
        sair();
      }
    }
    window.addEventListener("keydown", atalho);
    return () => window.removeEventListener("keydown", atalho);
  }, [sair]);
  const precisaConferir = itens.some((item) => item.produto.restrito);
  const liberado = chamado?.status === "liberado";
  const podePagar = itens.length > 0 && (!precisaConferir || liberado);

  async function pagar() {
    setErro("");
    try {
      const venda = await api<Venda>("/vendas/", {
        metodo: "POST",
        corpo: {
          pagamento: "pix",
          chamado: precisaConferir ? chamado?.id : null,
          itens: itens.map((item) => ({
            produto: item.produto.codigo_barras,
            quantidade: item.quantidade,
          })),
        },
      });
      setPago(venda);
    } catch (e) {
      setErro((e as Error).message);
    }
  }

  if (pago) {
    return (
      <main className="totem totem-fim" aria-live="polite">
        <p className="totem-grande">Obrigado!</p>
        <p>
          Pagamento de{" "}
          <b className="mono">R$ {reais(paraCentavos(pago.total))}</b> aprovado.
        </p>
        <p className="fraco">Pode levar suas compras. Volte sempre.</p>
      </main>
    );
  }
  return (
    <main className="totem">
      <header className="totem-topo">
        <span className="marca">
          Mercadinho <span className="fraco">. passe seus produtos</span>
        </span>
        <button
          type="button"
          className="botao claro"
          disabled={chamado?.status === "aberto"}
          onClick={() => chamarAtendente("Ajuda no totem")}
        >
          {chamado?.status === "aberto"
            ? "Atendente a caminho"
            : "Chamar atendente"}
        </button>
      </header>

      <form onSubmit={bipar} className="totem-leitor">
        <label>
          <span className="so-leitor">Código de barras</span>
          <input
            ref={campo}
            autoFocus
            required
            inputMode="numeric"
            placeholder="Passe o código de barras no leitor"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value.trim())}
          />
        </label>
      </form>

      <section
        className="totem-ultimo"
        aria-label="Último item"
        aria-live="polite"
      >
        {ultimo ? (
          <>
            <span className="fraco">
              Confira se é este o produto na sua mão:
            </span>
            <span className="totem-grande">{ultimo.nome}</span>
            <span className="mono">R$ {reais(paraCentavos(ultimo.preco))}</span>
          </>
        ) : (
          <span className="totem-grande fraco">Passe o primeiro produto</span>
        )}
      </section>

      <section className="totem-lista" aria-label="Sua compra">
        <table className="tabela">
          <caption>Sua compra</caption>
          <tbody>
            {itens.map((item) => (
              <tr key={item.produto.id}>
                <td>
                  <div className="qtd">
                    <button
                      type="button"
                      aria-label={`Um a menos de ${item.produto.nome}`}
                      onClick={() => mudarQuantidade(item, -1)}
                    >
                      −
                    </button>
                    <span className="mono">{item.quantidade}</span>
                    <button
                      type="button"
                      aria-label={`Um a mais de ${item.produto.nome}`}
                      onClick={() => mudarQuantidade(item, 1)}
                    >
                      +
                    </button>
                  </div>
                </td>
                <td>
                  {item.produto.nome}
                  {item.produto.restrito && !liberado && (
                    <span className="aviso-18">
                      precisa da conferência de um funcionário
                    </span>
                  )}
                </td>
                <td className="num mono">{reais(subtotal(item))}</td>
                <td>
                  <button
                    type="button"
                    className="remover"
                    aria-label={`Tirar ${item.produto.nome}`}
                    onClick={() => mudarItens(remover(itens, item.produto.id))}
                  >
                    ×
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="totem-rodape">
        {erro && (
          <p role="alert" className="alerta">
            {erro}
          </p>
        )}
        {precisaConferir && !liberado && (
          <p role="status" className="alerta">
            Um funcionário foi chamado para conferir. O pagamento libera em
            seguida.
          </p>
        )}
        {liberado && (
          <p role="status" className="ok">
            Liberado por {chamado?.liberado_por}. Pode pagar.
          </p>
        )}
        <div className="totem-pagar">
          <div className="etiqueta">
            <span className="forte">
              TOTAL · {quantidadeDeItens(itens)} itens
            </span>
            <span className="etiqueta-valor mono">
              <span>R$</span>
              {reais(totalEmCentavos(itens))}
            </span>
          </div>
          <button
            type="button"
            className="botao enorme"
            disabled={!podePagar}
            onClick={pagar}
          >
            Pagar com Pix
          </button>
        </div>
        <p className="fraco pequeno">
          Pix simulado: o pagamento de verdade fica para o futuro.
        </p>
      </section>
    </main>
  );
}
