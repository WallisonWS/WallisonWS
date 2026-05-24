#!/usr/bin/env python3
"""
📊 Script de Sincronização do Trello
Autor: Wallison Araujo (WallisonWS)
Descrição: Conecta à API do Trello para ler cartões e estatísticas de produtividade
           e atualiza o README.md. Roda 100% na nuvem do GitHub Actions.
"""

import os
import sys
from datetime import datetime
import urllib.request
import json

def fetch_trello_data(api_key, token, board_id):
    # Se configurado, busca dados reais do Trello
    try:
        # Busca as listas do Board
        url_lists = f"https://api.trello.com/1/boards/{board_id}/lists?key={api_key}&token={token}"
        req = urllib.request.Request(url_lists, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            lists = json.loads(response.read().decode('utf-8'))
            
        done_cards = 0
        doing_cards = 0
        todo_cards = 0
        
        for lst in lists:
            list_name = lst['name'].lower()
            list_id = lst['id']
            
            # Busca cartões de cada lista
            url_cards = f"https://api.trello.com/1/lists/{list_id}/cards?key={api_key}&token={token}"
            req_c = urllib.request.Request(url_cards, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_c) as response_c:
                cards = json.loads(response_c.read().decode('utf-8'))
                count = len(cards)
                
                if "done" in list_name or "concluido" in list_name or "pronto" in list_name:
                    done_cards += count
                elif "doing" in list_name or "andamento" in list_name or "fazendo" in list_name:
                    doing_cards += count
                else:
                    todo_cards += count
                    
        return {
            "connected": True,
            "todo": todo_cards,
            "doing": doing_cards,
            "done": done_cards,
            "total": todo_cards + doing_cards + done_cards
        }
    except Exception as e:
        print(f"[TRELLO] Erro ao conectar com a API: {str(e)}")
        return None

def main():
    api_key = os.environ.get("TRELLO_API_KEY")
    token = os.environ.get("TRELLO_TOKEN")
    board_id = os.environ.get("TRELLO_BOARD_ID")
    
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        print(f"[TRELLO] Erro: Arquivo {readme_path} nao encontrado.")
        sys.exit(1)
        
    date_str = datetime.now().strftime("%d/%m/%Y as %H:%M")
    
    # Se houver chaves configuradas, faz o fetch real. Caso contrário, exibe o painel de configuração/mock.
    if api_key and token and board_id:
        data = fetch_trello_data(api_key, token, board_id)
    else:
        data = None
        
    if data and data.get("connected"):
        todo = data["todo"]
        doing = data["doing"]
        done = data["done"]
        total = data["total"]
        status_text = f"🟢 **API Conectada** | Ultima sincronizacao: {date_str} UTC"
    else:
        # Dados demonstrativos (Mock) explicando como ativar a sincronização real
        todo = 3
        doing = 2
        done = 45
        total = 50
        status_text = (
            f"💡 **Modo de Demonstracao** | Para ativar a sincronizacao real com o seu Trello, "
            f"adicione as Secrets no repositorio (`TRELLO_API_KEY`, `TRELLO_TOKEN`, `TRELLO_BOARD_ID`)."
        )
        
    # Gera a barra de progresso visual em Markdown
    if total > 0:
        percent_done = int((done / total) * 100)
    else:
        percent_done = 0
        
    bar_length = 20
    filled_length = int(bar_length * percent_done // 100)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    trello_block = f"""<!-- TRELLO_STATS_START -->
#### 📊 Trello & Kanban - Metricas de Produtividade GTD
```text
Progresso de Tarefas: [{bar}] {percent_done}%
--------------------------------------------------
📋 A Fazer (To Do):     {todo}
⚙️ Em Andamento (Doing): {doing}
✅ Concluidos (Done):    {done}
```
_{status_text}_
<!-- TRELLO_STATS_END -->"""

    print("[TRELLO] Atualizando secao do Trello no README.md...")
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    start_tag = "<!-- TRELLO_STATS_START -->"
    end_tag = "<!-- TRELLO_STATS_END -->"
    
    if start_tag in content and end_tag in content:
        before = content.split(start_tag)[0]
        after = content.split(end_tag)[1]
        new_content = before + trello_block + after
    else:
        # Se as tags não existirem, adiciona ao final do arquivo ou acima de "Estatísticas"
        print("[TRELLO] Tags nao encontradas. Inserindo no final do arquivo.")
        new_content = content + "\n\n" + trello_block
        
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print("[TRELLO] README.md atualizado com sucesso!")

if __name__ == "__main__":
    main()
