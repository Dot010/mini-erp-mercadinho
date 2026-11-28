import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import { INICIO, useAuth } from "./auth/contexto";
import { Protegida } from "./auth/Protegida";
import { ProvedorAuth } from "./auth/ProvedorAuth";
import { Topo } from "./components/Topo";
import { Caixa } from "./pages/Caixa";
import { Estoque } from "./pages/Estoque";
import { Login } from "./pages/Login";
import { Totem } from "./pages/Totem";
import { Painel } from "./pages/Painel";
import { Relatorios } from "./pages/Relatorios";

function Inicio() {
  const { usuario, carregando } = useAuth();
  if (carregando) return null;
  return <Navigate to={usuario ? INICIO[usuario.papel] : "/login"} replace />;
}

export default function App() {
  return (
    <ProvedorAuth>
      <BrowserRouter>
        <Topo />
        <Routes>
          <Route
            path="/relatorios"
            element={
              <Protegida papeis={["dono"]}>
                <Relatorios />
              </Protegida>
            }
          />
          <Route
            path="/painel"
            element={
              <Protegida papeis={["dono"]}>
                <Painel />
              </Protegida>
            }
          />
          <Route
            path="/totem"
            element={
              <Protegida papeis={["totem"]}>
                <Totem />
              </Protegida>
            }
          />
          <Route path="/login" element={<Login />} />
          <Route
            path="/caixa"
            element={
              <Protegida papeis={["dono", "caixa"]}>
                <Caixa />
              </Protegida>
            }
          />
          <Route
            path="/estoque"
            element={
              <Protegida papeis={["dono", "estoquista"]}>
                <Estoque />
              </Protegida>
            }
          />
          <Route path="*" element={<Inicio />} />
        </Routes>
      </BrowserRouter>
    </ProvedorAuth>
  );
}
