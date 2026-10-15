# Publicando este repositório no GitHub

## Preparação

1. Extraia `python-data-analytics-github.zip`.
2. Abra a pasta `python-data-analytics` no VS Code.
3. Faça uma revisão final dos arquivos que serão publicados e confirme que nenhuma informação pessoal foi adicionada após esta preparação.
4. Crie no GitHub um repositório **vazio** chamado `python-data-analytics`, preferencialmente **Public**, sem README ou .gitignore gerados pelo GitHub.

## Publicação pelo terminal

Execute os comandos na pasta `python-data-analytics`:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "docs: organiza projetos de analise de dados"
git remote add origin https://github.com/SEU-USUARIO/python-data-analytics.git
git push -u origin main
```

Substitua `SEU-USUARIO` pelo nome do perfil GitHub. A autenticação deverá ocorrer pela sua conta (Git Credential Manager, GitHub CLI ou token pessoal, conforme sua configuração).

**Atenção:** o `.gitignore` exclui ambientes virtuais, caches, relatórios gerados, CSVs processados e a cópia reconstruível do warehouse. As bases de entrada de demonstração e os previews permanecem versionados.

## Atualizações posteriores

```powershell
git add .
git commit -m "feat: atualiza estudos de analise de dados"
git push
```

## Checklist de revisão antes do push

- [ ] `git status` não mostra `.env`, credenciais, notebooks locais ou arquivos de clientes reais
- [ ] `README.md` abre corretamente no GitHub
- [ ] Todas as oito pastas dos projetos estão presentes
- [ ] Pré-visualizações de gráficos aparecem na página do repositório
- [ ] Testes Python mais recentes passam (`pytest` por projeto)
