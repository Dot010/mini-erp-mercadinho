import { NavLink } from "react-router";
import { useAuth } from "../auth/contexto";
import type { Papel } from "../tipos";

const LINKS: { para: string; texto: string; papeis: Papel[] }[] = [
  { para: "/painel", texto: "Painel", papeis: ["dono"] },
  { para: "/relatorios", texto: "Relatórios", papeis: ["dono"] },
  { para: "/estoque", texto: "Estoque", papeis: ["dono", "estoquista"] },
  { para: "/caixa", texto: "Caixa", papeis: ["dono", "caixa"] },
];

export function Topo() {
  const { usuario, sair } = useAuth();
  if (!usuario || usuario.papel === "totem") return null;

  const meus = LINKS.filter((link) => link.papeis.includes(usuario.papel));

  return (
    <header className="topo">
      <div className="topo-esquerda">
        <span className="marca">Balcão</span>
        <nav aria-label="Navegação">
          {meus.map((link) => (
            <NavLink key={link.para} to={link.para}>
              {link.texto}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="topo-direita">
        <span>
          {usuario.first_name} <span className="fraco">({usuario.papel})</span>
        </span>
        <button type="button" className="link" onClick={sair}>
          Sair
        </button>
      </div>
    </header>
  );
}
