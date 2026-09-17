# Travel Exam Planner

Plugin local para ChatGPT/Codex que planeja viagens porta a porta para provas e concursos. Ele compara custo total, tempo fora de casa, sono, impacto no trabalho e risco operacional, sem misturar reais com pontos de inconveniência.

## Arquitetura

- `skills/travel-exam-planner/`: workflow, políticas, modelo de dados e comparador determinístico.
- `.app.json`: conectores de Google Calendar, Gmail, Decolar, Skyscanner e Booking.com.
- `.codex-plugin/plugin.json`: manifesto e apresentação do plugin.
- `tests/`: testes unitários do comparador.

O plugin não inclui um servidor MCP próprio. O cálculo é local e determinístico; inventário e contexto vêm dos apps conectados ou de fontes web verificáveis. Reservas, compras, mensagens e alterações de calendário exigem autorização explícita.

## Configuração local opcional

Copie `skills/travel-exam-planner/config/profile.example.json` para `~/.config/travel-exam-planner/profile.json` e preencha apenas os dados que deseja usar. Para outro caminho, defina `TRAVEL_EXAM_PLANNER_PROFILE`. O perfil fica fora do pacote para não entrar no cache nem em um compartilhamento do plugin.

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
