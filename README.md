# Travel Exam Planner

Plugin local para ChatGPT/Codex que planeja viagens porta a porta para provas e concursos. Ele usa busca flexível para descobrir as datas aéreas mais baratas que comportam a prova, compara modos de transporte pelo itinerário completo — incluindo sono útil em deslocamentos noturnos — e elimina alternativas dominadas. O objetivo pode priorizar melhor custo-benefício ou menor custo total.

## Arquitetura

- `skills/travel-exam-planner/`: workflow, políticas, modelo de dados e comparador determinístico.
- `.app.json`: conectores de Google Calendar, Gmail, Decolar, Skyscanner e Booking.com.
- `.codex-plugin/plugin.json`: manifesto e apresentação do plugin.
- `tests/`: testes unitários do comparador.

Cada planejamento termina com uma planilha `.xlsx` contendo o resumo dos cenários, custos discriminados, roteiro e links disponíveis para compra ou reserva.

O plugin não inclui um servidor MCP próprio. O cálculo é local e determinístico; inventário e contexto vêm dos apps conectados ou de fontes web verificáveis. Reservas, compras, mensagens e alterações de calendário exigem autorização explícita.

## Configuração local opcional

Copie `skills/travel-exam-planner/config/profile.example.json` para `~/.config/travel-exam-planner/profile.json` e preencha apenas os dados que deseja usar. Em `optimization.objective`, escolha `best_value` ou `lowest_total_cost`. Para outro caminho, defina `TRAVEL_EXAM_PLANNER_PROFILE`. O perfil fica fora do pacote para não entrar no cache nem em um compartilhamento do plugin.

## Testes

```bash
python3 -m unittest discover -s tests -v
python3 skills/travel-exam-planner/scripts/score_options.py examples/options.sample.json --pretty
python3 /home/victor/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

## Instalação local

Este projeto é publicado no marketplace pessoal como `travel-exam-planner@personal`. O caminho esperado pelo marketplace é `~/plugins/travel-exam-planner`; durante o desenvolvimento ele pode ser um link simbólico para este repositório.

```bash
codex plugin add travel-exam-planner@personal
```

Depois da instalação ou de uma atualização, abra uma nova tarefa para carregar a versão atual da skill e dos conectores.
