const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";
const CHAVE_TOKEN = "balcao:token";

export function lerToken() {
  return localStorage.getItem(CHAVE_TOKEN);
}

export function guardarToken(token: string | null) {
  if (token) localStorage.setItem(CHAVE_TOKEN, token);
  else localStorage.removeItem(CHAVE_TOKEN);
}

export class ErroApi extends Error {
  status: number;

  constructor(status: number, mensagem: string) {
    super(mensagem);
    this.status = status;
  }
}

function mensagemDoErro(status: number, corpo: unknown) {
  if (corpo && typeof corpo === "object") {
    if ("detail" in corpo) return String(corpo.detail);
    const primeiro = Object.values(corpo)[0];
    if (Array.isArray(primeiro)) return String(primeiro[0]);
  }
  if (status === 403) return "Seu papel não permite esta ação.";
  return "Algo deu errado. Tente de novo.";
}

export async function api<T>(
  caminho: string,
  opcoes: { metodo?: string; corpo?: unknown } = {},
): Promise<T> {
  const cabecalhos: Record<string, string> = { "Content-Type": "application/json" };
  const token = lerToken();
  if (token) cabecalhos.Authorization = `Token ${token}`;

  const resposta = await fetch(BASE + caminho, {
    method: opcoes.metodo ?? "GET",
    headers: cabecalhos,
    body: opcoes.corpo === undefined ? undefined : JSON.stringify(opcoes.corpo),
  });

  const corpo = resposta.status === 204 ? null : await resposta.json().catch(() => null);
  if (!resposta.ok) throw new ErroApi(resposta.status, mensagemDoErro(resposta.status, corpo));
  return corpo as T;
}

export async function baixarArquivo(caminho: string, nome: string) {
  const token = lerToken();
  const resposta = await fetch(BASE + caminho, {
    headers: token ? { Authorization: `Token ${token}` } : {},
  });
  if (!resposta.ok) throw new ErroApi(resposta.status, "Não foi possível baixar o arquivo.");

  const arquivo = await resposta.blob();
  const link = document.createElement("a");
  link.href = URL.createObjectURL(arquivo);
  link.download = nome;
  link.click();
  URL.revokeObjectURL(link.href);
}