import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router";
import { INICIO, useAuth } from "../auth/contexto";

export function Login() {
  const { usuario, entrar } = useAuth();
  const navegar = useNavigate();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  if (usuario) return <Navigate to={INICIO[usuario.papel]} replace />;

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      const quem = await entrar(email, senha);
      navegar(INICIO[quem.papel], { replace: true });
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não deu para entrar.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="login">
      <form onSubmit={enviar}>
        <div className="login-topo">
          <span className="marca">Balcão</span>
          <span className="mono fraco">mercadinho</span>
        </div>
        <label>
          E-mail
          <input
            type="email"
            autoComplete="username"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            autoComplete="current-password"
            required
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
          />
        </label>
        {erro && <p role="alert" className="alerta">{erro}</p>}
        <button type="submit" className="botao" disabled={enviando}>
          {enviando ? "Entrando…" : "Entrar"}
        </button>
        <p className="fraco pequeno">Esqueceu a senha? Fale com o dono do mercado.</p>
      </form>
    </main>
  );
}