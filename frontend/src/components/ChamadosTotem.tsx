import { useEffect, useState } from "react";
import { api } from "../api";
import type { Chamado } from "../tipos";

const A_CADA_5_SEGUNDOS = 5000;

export function ChamadosTotem() {
  const [chamados, setChamados] = useState<Chamado[]>([]);

  function buscar() {
    api<Chamado[]>("/chamados/")
      .then(setChamados)
      .catch(() => {});
  }

  useEffect(() => {
    buscar();
    const relogio = setInterval(buscar, A_CADA_5_SEGUNDOS);
    return () => clearInterval(relogio);
  }, []);

  async function liberar(id: number) {
    await api(`/chamados/${id}/liberar/`, { metodo: "POST" }).catch(() => {});
    buscar();
  }

  if (chamados.length === 0) return null;

  return (
    <section
      className="chamados"
      aria-label="Chamados do totem"
      aria-live="polite"
    >
      <h2>Totem chamando</h2>
      <ul>
        {chamados.map((chamado) => (
          <li key={chamado.id}>
            <span>
              <b>{chamado.totem}</b> . {chamado.motivo}
            </span>
            <button
              type="button"
              className="botao"
              onClick={() => liberar(chamado.id)}
            >
              Conferi, liberar
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
