# Travel Exam Planner

Plugin local para ChatGPT/Codex que planeja viagens porta a porta para provas presenciais e concursos. Ele combina restrições de calendário, fatos oficiais da prova, transporte de longa distância, hospedagem, deslocamentos locais, sono, impacto no trabalho, custo total e risco operacional.

O objetivo é apoiar uma decisão verificável — não comprar passagens ou reservar hospedagem automaticamente. O planejador pode priorizar `best_value` (melhor relação entre custo e inconveniência) ou `lowest_total_cost` (menor custo total entre as opções viáveis).

## O que o plugin faz

- confirma data, cidade, local, horário e duração da prova a partir de fontes oficiais quando disponíveis;
- começa pelo ponto de origem real e calcula o percurso completo até o retorno para casa;
- pesquisa datas flexíveis antes de escolher um itinerário específico;
- compara voos, ônibus e outros modos plausíveis pelo custo completo, tempo fora de casa, sono, trabalho e margem de segurança;
- separa custo financeiro de inconveniência e risco, sem transformar tudo em uma pontuação monetária oculta;
- elimina alternativas dominadas e identifica a fronteira de opções não dominadas;
- informa o impacto financeiro relativo à opção viável mais barata;
- entrega cenários decision-ready e, quando a capacidade de planilhas está disponível, um workbook `.xlsx` com resumo, pesquisa, custos, roteiro, fontes e links de reserva.

O repositório não inclui um servidor MCP próprio. O comparador é local e determinístico; dados atuais vêm de conectores disponíveis ou de fontes web verificáveis.

## Arquitetura

```text
.
├── .app.json                              # conectores declarados pelo plugin
├── .codex-plugin/plugin.json              # manifesto e metadados
├── examples/options.sample.json           # entrada sintética do comparador
├── skills/travel-exam-planner/
│   ├── SKILL.md                            # workflow e regras da skill
│   ├── agents/openai.yaml                  # interface do agente
│   ├── config/profile.example.json         # campos do perfil privado
│   ├── references/                         # modelo, busca, fontes, scoring e workbook
│   └── scripts/score_options.py            # validação, normalização e scoring
├── tests/test_score_options.py             # testes unitários
├── PRIVACY.md                              # revisão de privacidade e checklist
└── README.md
```

## Requisitos

- Python 3.10 ou posterior para executar o comparador e os testes;
- ChatGPT/Codex com suporte a plugins para usar a skill;
- conectores autenticados somente quando o planejamento precisar de calendário, e-mail, voos ou hospedagem atuais;
- fontes web oficiais ou verificáveis para fatos da prova e detalhes que os conectores não cubram.

A ausência de um conector não impede o planejamento: a skill deve declarar a indisponibilidade e usar uma fonte pública adequada como fallback. Ela nunca deve inventar disponibilidade, tarifa, regra de bagagem, calendário ou conteúdo de e-mail.

## Instalação

Se o plugin estiver publicado no marketplace pessoal, instale-o pelo identificador:

```bash
codex plugin add travel-exam-planner@personal
```

Durante o desenvolvimento, mantenha o repositório no diretório local escolhido para plugins e use o fluxo de instalação local suportado pela sua versão do Codex. Depois de instalar ou atualizar, abra uma nova tarefa para carregar a versão atual da skill e dos conectores.

## Primeiro uso

Uma solicitação típica pode ser:

```text
Planeje minha viagem para a prova de [evento], em [cidade], no dia [data].
Compare voo e ônibus, considere meu calendário e priorize melhor custo-benefício.
```

Para uma análise responsável, informe — na própria solicitação ou no perfil privado — a cidade de origem, data e local da prova, horário de início, duração prevista, margem mínima de chegada, restrições de trabalho, preferência de bagagem e objetivo de otimização. Quando uma informação material estiver faltando, a skill deve criar cenários explícitos ou pedir o dado; ela não deve preenchê-lo por suposição.

## Perfil privado

O perfil é opcional e não deve ser commitado. Para criar uma cópia local:

```bash
mkdir -p ~/.config/travel-exam-planner
cp skills/travel-exam-planner/config/profile.example.json \
  ~/.config/travel-exam-planner/profile.json
```

Os campos principais são:

- `home_base`: cidade, estado e país de onde começa o cálculo porta a porta;
- `work`: origem das restrições de agenda e se folgas parciais ou integrais podem ser negociadas;
- `sleep.low_sleep_threshold_hours`: limite para identificar uma noite materialmente curta;
- `optimization.objective`: `best_value` ou `lowest_total_cost`;
- `preferences`: moeda, hospedagem, bagagem e tolerância a pernoite em aeroporto.

Para usar outro arquivo, defina `TRAVEL_EXAM_PLANNER_PROFILE`. Nunca coloque endereço exato, agenda completa, documentos, credenciais ou dados de terceiros no perfil sem necessidade. O perfil deve permanecer fora do pacote do plugin e fora de qualquer planilha compartilhada.

Consulte [PRIVACY.md](PRIVACY.md) antes de publicar alterações ou compartilhar resultados.

## Fluxo de decisão

O processo recomendado é deliberadamente sequencial:

1. Confirmar fatos oficiais da prova: data, cidade, local, horário, duração e regras relevantes.
2. Separar restrições absolutas, restrições negociáveis e preferências.
3. Definir uma janela de busca e pesquisar datas flexíveis antes de fixar o itinerário.
4. Pesquisar voos, ônibus, hospedagem e transporte local; incluir taxas, bagagem, refeições e acessos inevitáveis.
5. Normalizar cada opção no modelo de dados e registrar fonte, horário de verificação e incertezas.
6. Eliminar opções que violam restrições absolutas e executar o comparador determinístico.
7. Escolher cenários da fronteira de Pareto e justificar o que o custo adicional compra — tempo, sono, continuidade do trabalho ou margem de contingência.
8. Informar o próximo passo e seu prazo sem executar compra, reserva, mensagem ou alteração de calendário.

A pesquisa flexível deve distinguir três referências: menor tarifa de transporte encontrada na janela declarada, menor custo completo e menor ausência viável. A menor passagem não é automaticamente a melhor viagem.

## Modelo de dados e scoring

O comparador recebe um JSON com `options`, e opcionalmente `objective` e `weights`. Cada opção precisa ter pelo menos:

- identificador e rótulo;
- `cost_brl` e uma lista não vazia de `cost_items`;
- `hours_away`, `avoidable_hours` e as contagens de pernoite, sono, conexões, aeroportos e dias de trabalho afetados;
- `risk_items` com motivo e pontos;
- `hard_constraints` com nome, status de atendimento e detalhe.

O script valida que:

- todos os números são finitos e não negativos;
- cada item de custo reconcilia `quantity × unit_cost_brl`;
- `cost_brl` é igual à soma dos itens, com tolerância de um centavo;
- URLs de compra e fonte são HTTPS ou `null`;
- status de preço é `quote`, `estimate` ou `confirmed`;
- a qualidade do sono é `poor`, `limited` ou `adequate`;
- identificadores de opção são únicos.

O score de inconveniência padrão mantém as dimensões transparentes:

| Dimensão | Peso padrão |
| --- | ---: |
| Hora evitável de viagem, espera ou tempo morto | 0,5 ponto |
| Noite em aeroporto | 8 pontos |
| Evento de sono abaixo do limite | 5 pontos |
| Conexão aérea adicional | 3 pontos |
| Troca de aeroporto | 5 pontos |
| Dia de trabalho parcialmente afetado | 4 pontos |
| Dia de trabalho integralmente afetado | 12 pontos |
| Risco específico verificado | pontos declarados no item |

Com `best_value`, a recomendação é um julgamento entre opções na fronteira de Pareto. Com `lowest_total_cost`, a seleção automática é a opção viável mais barata. Em ambos os casos, uma restrição absoluta ou margem mínima de prova continua obrigatória.

Para executar apenas a parte determinística:

```bash
python3 skills/travel-exam-planner/scripts/score_options.py \
  examples/options.sample.json --pretty
```

Leia [data-model.md](skills/travel-exam-planner/references/data-model.md) para o schema completo e [scoring.md](skills/travel-exam-planner/references/scoring.md) para as regras de decisão.

## Fontes e conectores

O manifesto declara conectores para:

- Google Calendar, para restrições de agenda quando o usuário pedir essa consulta;
- Gmail, somente para avisos de prova, passagens ou reservas solicitados;
- Decolar e Skyscanner, para descoberta e comparação de voos;
- Booking.com, para descoberta de hospedagem.

Para detalhes críticos, prefira a página real da companhia, operadora, hotel, aeroporto, transporte urbano ou organização da prova. Um snippet, preço indicativo ou página genérica não prova que uma tarifa está disponível nem que será mantida.

As regras detalhadas estão em:

- [SKILL.md](skills/travel-exam-planner/SKILL.md): limites, roteamento de ferramentas e saída obrigatória;
- [date-search.md](skills/travel-exam-planner/references/date-search.md): descoberta flexível de datas e limitações de inventário;
- [source-policy.md](skills/travel-exam-planner/references/source-policy.md): verificação, hospedagem e fallbacks;
- [data-model.md](skills/travel-exam-planner/references/data-model.md): campos e invariantes do JSON;
- [scoring.md](skills/travel-exam-planner/references/scoring.md): dominância e escolha;
- [spreadsheet-output.md](skills/travel-exam-planner/references/spreadsheet-output.md): estrutura e validação do workbook.

## Saída esperada

O resultado deve conter até três opções decision-ready, salvo quando ramificações realmente distintas exigirem mais. Para cada opção, apresentar:

- linha do tempo porta a porta;
- custo total e itens discriminados;
- diferença em relação à opção viável mais barata;
- noites, sono, trabalho, riscos e margem de contingência;
- score de inconveniência com justificativa;
- data/hora de verificação e condições de tarifa, bagagem, cancelamento e check-in;
- links de compra ou reserva, identificando se são oferta exata, handoff de reserva ou página de busca;
- próxima decisão e prazo.

O workbook deve conter, quando possível:

1. `Resumo`, com objetivo, recomendação, totais, diferenças e justificativa;
2. `Pesquisa de datas`, com combinações pesquisadas e cobertura da janela;
3. `Custos`, com todos os itens reconciliados;
4. `Roteiro`, com os eventos cronológicos de cada cenário.

Não use um link para afirmar que uma compra ou reserva foi realizada. Links são handoffs para uma decisão posterior e podem perder preço, inventário ou validade.

## Privacidade e autorização

O comparador local não faz chamadas de rede. Conectores e pesquisa web só devem ser usados dentro do escopo pedido pelo usuário. Planejar e pesquisar não autoriza comprar, reservar, enviar mensagens, alterar calendário, gravar no Drive ou criar monitoramento recorrente.

Arquivos pessoais e resultados gerados são tratados como dados sensíveis de contexto. Antes de um commit, revise `git diff`, procure tokens, chaves, cookies, e-mails, endereços, documentos, parâmetros pessoais em URLs e perfis reais. Veja o checklist completo em [PRIVACY.md](PRIVACY.md).

## Desenvolvimento e testes

Execute os testes unitários a partir da raiz:

```bash
python3 -m unittest discover -s tests -v
```

Valide também o exemplo do comparador:

```bash
python3 skills/travel-exam-planner/scripts/score_options.py \
  examples/options.sample.json --pretty
```

O manifesto do plugin deve ser validado com o validador de plugins fornecido pela instalação do Codex usada no ambiente. O caminho desse utilitário pode variar entre instalações; não inclua um caminho absoluto de máquina no repositório.

Ao alterar o schema, o scoring ou as regras de decisão:

1. atualize os documentos de referência correspondentes;
2. adicione ou ajuste testes para entradas válidas, inválidas e casos de fronteira;
3. mantenha exemplos sintéticos;
4. execute testes, validação do manifesto e revisão de privacidade antes do commit.

## Limitações conhecidas

- preços, horários, inventário, políticas e links de terceiros mudam; resultados têm timestamp e precisam ser rechecados antes da compra;
- cobertura de datas depende dos conectores, do mercado, da abertura do inventário e da janela pesquisada;
- uma estimativa não é uma cotação confirmada;
- a avaliação de sono depende de assento, duração sem interrupção, transferências e perfil do viajante;
- o comparador não substitui confirmação oficial da prova nem julgamento sobre segurança e tolerância a risco;
- a geração e a renderização do `.xlsx` dependem da capacidade de planilhas disponível no ambiente de execução.

## Contribuição

Contribuições devem preservar as fronteiras de privacidade e autorização do plugin. Não envie perfis reais, itinerários pessoais, credenciais ou dados de terceiros. Para mudanças de comportamento, explique a regra, atualize a referência técnica e inclua testes reproduzíveis.

Este repositório ainda não declara uma licença de uso. Até que uma licença seja adicionada, a publicação do código não deve ser interpretada como concessão de direitos de redistribuição ou modificação.
