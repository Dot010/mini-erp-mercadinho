import type { ReactNode } from "react";
import { Navigate } from "react-router";
import type { Papel } from "../tipos";
import { INICIO, useAuth } from "./contexto";

export function Protegida({ papeis, children }: { papeis: Papel[]; children: ReactNode }) {
  const { usuario, carregando } = useAuth();

  if (carregando) return <p className="aviso-carregando">Carregando…</p>;
  if (!usuario) return <Navigate to="/login" replace />;
  if (!papeis.includes(usuario.papel)) return <Navigate to={INICIO[usuario.papel]} replace />;
  return children;
}