# Privacidade e segurança

Este repositório foi preparado para ser público. A revisão de publicação cobre os arquivos versionados e o histórico alcançável do Git.

## O que fica fora do repositório

- O perfil pessoal é lido de `TRAVEL_EXAM_PLANNER_PROFILE` ou de `~/.config/travel-exam-planner/profile.json`.
- O perfil pode conter cidade de origem, rotina de trabalho, preferências de sono, bagagem e hospedagem; nunca o publique sem revisar e autorizar cada campo.
- Planilhas geradas (`.xlsx`) e arquivos em `outputs/` podem conter itinerários, custos e horários pessoais. Eles são ignorados pelo Git.
- Variáveis de ambiente, arquivos `.env`, chaves e arquivos `profile.json` são ignorados como proteção contra inclusão acidental.

O `.gitignore` reduz o risco de commit acidental, mas não substitui a revisão do diff nem a rotação de uma credencial que tenha sido exposta.

## O que pode ser público

- `.app.json` contém identificadores de conectores necessários para declarar as integrações do plugin. Esses identificadores não são tokens de autenticação nem concedem acesso por si só.
- `config/profile.example.json` contém somente valores fictícios e serve como referência de campos.
- `examples/options.sample.json` usa dados sintéticos, URLs públicas e timestamps de exemplo.

## Fluxo de dados

O comparador em `skills/travel-exam-planner/scripts/score_options.py` é local, determinístico e não faz chamadas de rede. Quando a skill é usada com conectores ou pesquisa web, os dados são tratados pelos respectivos serviços e somente dentro do escopo solicitado pelo usuário.

Planejamento, pesquisa e comparação não autorizam compra, reserva, envio de mensagens, alteração de calendário, gravação no Drive ou monitoramento recorrente. Essas ações exigem autorização explícita imediatamente antes da execução.

## Checklist antes de publicar

1. Execute `git status --short` e revise todos os arquivos novos e alterados.
2. Procure e remova tokens, chaves privadas, cookies, e-mails, endereços, números de documento e perfis reais.
3. Confirme que exemplos usam valores sintéticos e que links não contêm parâmetros pessoais ou tokens.
4. Se uma credencial aparecer no histórico, revogue-a e faça uma limpeza completa do histórico antes de tornar o repositório público.
