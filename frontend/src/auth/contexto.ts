import { createContext, useContext } from "react";
import type { Papel, Usuario } from "../tipos";

type Auth = {
  usuario: Usuario | null;
  carregando: boolean;
  entrar: (email: string, senha: string) => Promise<Usuario>;
  sair: () => void;
};

export const AuthContexto = createContext<Auth | null>(null);

export function useAuth() {
  const auth = useContext(AuthContexto);
  if (!auth) throw new Error("useAuth precisa estar dentro do <ProvedorAuth>.");
  return auth;
}


export const INICIO: Record<Papel, string> = {
  dono: "/caixa",
  caixa: "/caixa",
  estoquista: "/estoque",
  totem: "/totem",
};