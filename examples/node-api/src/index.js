const express = require("express");

const app = express();
const PORT = process.env.PORT || 3000;

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.get("/produtos", (req, res) => {
  res.json([
    { id: 1, nome: "Teclado", preco: 199.9 },
    { id: 2, nome: "Mouse", preco: 89.9 },
  ]);
});

app.listen(PORT, () => {
  console.log(`API rodando na porta ${PORT}`);
});
