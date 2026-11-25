import { useEffect, useState } from "react";
import { api } from "../api";
import { paraCentavos, reais } from "../dinheiro";
import { NOME_PAGAMENTO, type Resumo } from "../tipos";

const A_CADA_30_SEGUNDOS = 30000;

export function Painel() {
  const [dados, setDados] = useState<Resumo | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    function buscar() {
      api<Resumo>("/painel/")
        .then((novos) => {
          setDados(novos);
          setErro("");
        })
        .catch((e: Error) => setErro(e.message));
    }
    buscar();
    const relogio = setInterval(buscar, A_CADA_30_SEGUNDOS);
    return () => clearInterval(relogio);
  }, []);

  if (!dados) {
    return (
      <main className="pagina">
        {erro ? <p role="alert" className="alerta">{erro}</p> : <p className="fraco">Carregando…</p>}
      </main>
    );
  }

  return (
    <main className="pagina painel">
      <div className="pagina-topo">
        <h1>Painel de hoje</h1>
        {erro && <p role="alert" className="alerta">Sem conexão. Mostrando os últimos números.</p>}
      </div>

      <div className="painel-cartoes">
        <section className="etiqueta">
          <div className="etiqueta-topo"><span>VENDIDO HOJE</span></div>
          <div className="etiqueta-valor mono">R$ {reais(paraCentavos(dados.total))}</div>
        </section>
        <section className="etiqueta">
          <div className="etiqueta-topo"><span>VENDAS</span></div>
          <div className="etiqueta-valor mono">{dados.vendas}</div>
        </section>
        <section className="etiqueta">
          <div className="etiqueta-topo"><span>TICKET MÉDIO</span></div>
          <div className="etiqueta-valor mono">R$ {reais(paraCentavos(dados.ticket_medio))}</div>
        </section>
      </div>

    
      <h2>Mais vendidos</h2>
      {dados.mais_vendidos.length === 0 ? (
        <p className="vazio">Nenhuma venda ainda hoje.</p>
      ) : (
        <table className="tabela">
          <thead>
           <tr><th>Produto</th><th className="num">Unidades</th></tr>
          </thead>
          <tbody>
            {dados.mais_vendidos.map((item) => (
              <tr key={item.nome}>
                <td>{item.nome}</td>
                <td className="num mono">{item.quantidade}</td>
          
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2>Por pagamento</h2>
      <ul className="painel-lista">
        {dados.por_pagamento.map((linha) => (
          <li key={linha.pagamento}>
            <span>{NOME_PAGAMENTO[linha.pagamento]} ({linha.vendas})</span>
            <span className="mono">R$ {reais(paraCentavos(linha.total))}</span>
          </li>
        ))}
      </ul>
    </main>
  );
}