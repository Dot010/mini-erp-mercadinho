import { useEffect, useState, type FormEvent } from "react";
import { api, baixarArquivo } from "../api";
import { paraCentavos, reais } from "../dinheiro";
import type { Relatorio } from "../tipos";

const NOME_STATUS: Record<Relatorio["status"], string> = {
  pendente: "Gerando…",
  pronto: "Pronto",
  erro: "Erro",
};

function hojeISO() {
  return new Date().toLocaleDateString("en-CA");
}

function inicioDoMesISO() {
  return hojeISO().slice(0, 8) + "01";
}

function dataBR(iso: string) {
  const [ano, mes, dia] = iso.split("-");
  return `${dia}/${mes}/${ano}`;
}

export function Relatorios() {
  const [lista, setLista] = useState<Relatorio[]>([]);
  const [inicio, setInicio] = useState(inicioDoMesISO);
  const [fim, setFim] = useState(hojeISO);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  function carregar() {
    api<Relatorio[]>("/relatorios/")
      .then(setLista)
      .catch((e: Error) => setErro(e.message));
  }

  useEffect(carregar, []);

  const temPendente = lista.some((r) => r.status === "pendente");

  useEffect(() => {
    if (!temPendente) return;
    const relogio = setInterval(carregar, 2000);
    return () => clearInterval(relogio);
  }, [temPendente]);

  async function pedir(evento: FormEvent) {
    evento.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      await api("/relatorios/", { metodo: "POST", corpo: { inicio, fim } });
      carregar();
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  async function baixar(relatorio: Relatorio) {
    try {
      await baixarArquivo(
        `/relatorios/${relatorio.id}/csv/`,
        `relatorio_${relatorio.inicio}_${relatorio.fim}.csv`,
      );
    } catch (e) {
      setErro((e as Error).message);
    }
  }

  return (
    <main className="pagina">
      <div className="pagina-topo">
        <h1>Relatórios</h1>
      </div>

      <form className="relatorio-form" onSubmit={pedir}>
        <label>
          De
          <input
            type="date"
            value={inicio}
            onChange={(e) => setInicio(e.target.value)}
            required
          />
        </label>
        <label>
          Até
          <input
            type="date"
            value={fim}
            onChange={(e) => setFim(e.target.value)}
            required
          />
        </label>
        <button type="submit" className="botao" disabled={enviando}>
          {enviando ? "Pedindo…" : "Gerar relatório"}
        </button>
      </form>

      {erro && (
        <p role="alert" className="alerta">
          {erro}
        </p>
      )}

      {lista.length === 0 ? (
        <p className="vazio fraco">Nenhum relatório pedido ainda.</p>
      ) : (
        <div className="rolagem">
          <table className="tabela">
            <thead>
              <tr>
                <th>Período</th>
                <th>Status</th>
                <th className="num">Total</th>
                <th className="num">Vendas</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {lista.map((relatorio) => (
                <tr key={relatorio.id}>
                  <td>
                    {dataBR(relatorio.inicio)} a {dataBR(relatorio.fim)}
                  </td>
                  <td>{NOME_STATUS[relatorio.status]}</td>
                  <td className="num mono">
                    {relatorio.dados
                      ? `R$ ${reais(paraCentavos(relatorio.dados.total))}`
                      : "—"}
                  </td>
                  <td className="num mono">
                    {relatorio.dados ? relatorio.dados.vendas : "—"}
                  </td>
                  <td className="num">
                    {relatorio.status === "pronto" && (
                      <button
                        type="button"
                        className="botao claro"
                        onClick={() => baixar(relatorio)}
                      >
                        Baixar CSV
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
