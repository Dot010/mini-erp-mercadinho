import { useEffect, useState, type ReactNode } from "react";
import { api, guardarToken, lerToken } from "../api";
import type { Usuario } from "../tipos";
import { AuthContexto } from "./contexto";

export function ProvedorAuth({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(() => lerToken() !== null);

  // Abriu a página com um token guardado? Pergunta à API de quem ele é.
  useEffect(() => {
    if (!lerToken()) return;
    api<Usuario>("/eu/")
      .then(setUsuario)
      .catch(() => guardarToken(null))
      .finally(() => setCarregando(false));
  }, []);

  async function entrar(email: string, senha: string) {
    const resposta = await api<{ token: string; usuario: Usuario }>("/login/", {
      metodo: "POST",
      corpo: { email, password: senha },
    });
    guardarToken(resposta.token);
    setUsuario(resposta.usuario);
    return resposta.usuario;
  }

  function sair() {
    guardarToken(null);
    setUsuario(null);
  }

  return (
    <AuthContexto.Provider value={{ usuario, carregando, entrar, sair }}>
      {children}
    </AuthContexto.Provider>
  );
}