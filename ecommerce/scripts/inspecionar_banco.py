"""Lista tabelas, colunas e quantidade de registros do banco local."""

from pathlib import Path
import sqlite3

BANCO = Path(__file__).resolve().parents[1] / "data" / "raw" / "ecommerce.db"


def main():
    if not BANCO.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {BANCO}")
    with sqlite3.connect(BANCO) as conn:
        tabelas = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )]
        for tabela in tabelas:
            # Os nomes vêm exclusivamente do catálogo SQLite, não de entrada do usuário.
            colunas = [row[1] for row in conn.execute(f'PRAGMA table_info("{tabela}")')]
            quantidade = conn.execute(f'SELECT COUNT(*) FROM "{tabela}"').fetchone()[0]
            print(f"{tabela}: {quantidade} registros")
            print("  " + ", ".join(colunas))


if __name__ == "__main__":
    main()
