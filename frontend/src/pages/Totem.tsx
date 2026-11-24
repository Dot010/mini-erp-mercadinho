import { useAuth } from "../auth/contexto";

export function Totem() {
  const { sair } = useAuth();

  return (
    <main className="totem">
      <h1>Totem</h1>
      <p>Passe seus produtos.</p>
      <button type="button" className="link" onClick={sair}>
        Encerrar totem
      </button>
    </main>
  );
}