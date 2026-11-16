import { useState, type FormEvent } from "react";
import { api } from "../api";

type Props = { aoTerminar: () => void; aoCancelar: () => void };

export function FormProduto({ aoTerminar, aoCancelar }: Props) {
  const [nome, setNome] = useState("");
  const [codigo, setCodigo] = useState("");
  const [preco, setPreco] = useState("");
  const [erro, setErro] = useState("");

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    try {
      await api("/produtos/", {
        metodo: "POST",
        // Quem digita "8,49" quer dizer 8.49: a API só entende o ponto.
        corpo: { nome, codigo_barras: codigo, preco: preco.replace(",", ".") },
      });
      aoTerminar();
    } catch (e) {
      setErro((e as Error).message);
    }
  }

  return (
    <form className="painel-form" onSubmit={enviar} aria-label="Novo produto">
      <h2>Novo produto</h2>
      <label>
        Nome
        <input required maxLength={120} value={nome} onChange={(e) => setNome(e.target.value)} />
      </label>
      <label>
        Código de barras
        <input
          required
          inputMode="numeric"
          maxLength={14}
          value={codigo}
          onChange={(e) => setCodigo(e.target.value.trim())}
        />
      </label>
      <label>
        Preço (R$)
        <input
          required
          inputMode="decimal"
          placeholder="8,49"
          value={preco}
          onChange={(e) => setPreco(e.target.value)}
        />
      </label>
      <p className="fraco pequeno">O produto nasce com estoque 0. Depois, lance uma entrada.</p>
      {erro && <p role="alert" className="alerta">{erro}</p>}
      <div className="acoes">
        <button type="submit" className="botao">
          Cadastrar
        </button>
        <button type="button" className="link" onClick={aoCancelar}>
          Cancelar
        </button>
      </div>
    </form>
  );
}