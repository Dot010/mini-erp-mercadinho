
export function paraCentavos(valor: string) {
  const [reais, centavos = "0"] = valor.split(".");
  return Number(reais) * 100 + Number(centavos.padEnd(2, "0"));
}

const formato = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function reais(centavos: number) {
  return formato.format(centavos / 100);
}