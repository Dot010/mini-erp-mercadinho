import { useState, type FormEvent } from "react";
import { api } from "../api";
import type { Produto } from "../tipos";

type Props = { produtos: Produto[]; aoTerminar: () => void; aoCancelar: () => void };

export function FormEntrada({ produtos, aoTerminar, aoCancelar }: Props) {
  const [produto, setProduto] = useState("");
  const [quantidade, setQuantidade] = useState(1);
  const [motivo, setMotivo] = useState("Fornecedor");
  const [erro, setErro] = useState("");

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    try {
      await api("/movimentacoes/", {
        metodo: "POST",
        corpo: { produto: Number(produto), tipo: "entrada", quantidade, motivo },
      });
      aoTerminar();
    } catch (e) {
      setErro((e as Error).message);
    }
  }

  return (
    <form className="painel-form" onSubmit={enviar} aria-label="Lançar entrada">
      <h2>Lançar entrada</h2>
      <label>
        Produto
        <select required value={produto} onChange={(e) => setProduto(e.target.value)}>
          <option value="">Escolha…</option>
          {produtos
            .filter((p) => p.ativo)
            .map((p) => (
              <option key={p.id} value={p.id}>
                {p.nome} ({p.estoque} un)
              </option>
            ))}
        </select>
      </label>
      <label>
        Quantidade
        <input
          type="number"
          min={1}
          required
          value={quantidade}
          onChange={(e) => setQuantidade(Number(e.target.value))}
        />
      </label>
      <label>
        Motivo
        <input value={motivo} maxLength={200} onChange={(e) => setMotivo(e.target.value)} />
      </label>
      {erro && <p role="alert" className="alerta">{erro}</p>}
      <div className="acoes">
        <button type="submit" className="botao">
          Guardar entrada
        </button>
        <button type="button" className="link" onClick={aoCancelar}>
          Cancelar
        </button>
      </div>
    </form>
  );
}