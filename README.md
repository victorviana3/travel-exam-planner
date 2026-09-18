# Travel Exam Planner

Planeje uma viagem para uma prova presencial considerando o que realmente importa: chegar com segurança, descansar, reduzir o impacto no trabalho e entender o custo completo — da saída de casa até o retorno.

O Travel Exam Planner é um plugin para ChatGPT/Codex voltado a concursos, vestibulares, certificações e outras provas presenciais. Ele pesquisa e compara itinerários completos, mostra os compromissos envolvidos em cada alternativa e ajuda você a escolher entre melhor custo-benefício e menor custo total.

> O plugin apoia a decisão. Ele não compra passagens, não faz reservas e não altera sua agenda automaticamente.

## Por que usar

A passagem mais barata nem sempre produz a viagem mais barata ou mais segura. Um voo pode exigir bagagem adicional, hospedagem extra, deslocamentos caros ou uma noite mal dormida. Um ônibus mais demorado pode preservar o horário de trabalho e eliminar uma diária de hotel.

O Travel Exam Planner reúne essas consequências em uma comparação única. Para cada alternativa, você consegue ver:

- o itinerário porta a porta, incluindo os deslocamentos até terminais e o retorno para casa;
- o custo completo, com transporte, hospedagem, bagagem, taxas, alimentação adicional e transporte local;
- o tempo total fora de casa;
- o impacto esperado no sono e no trabalho;
- os riscos operacionais, como conexões apertadas ou chegada próxima ao horário da prova;
- a diferença de preço em relação à opção viável mais barata;
- o que o custo adicional de uma opção oferece em troca;
- as fontes consultadas, o horário da verificação e os links disponíveis para continuar a reserva.

## Como funciona

O planejamento acontece em quatro etapas:

1. **Entendimento da prova:** confirmação de data, cidade, local, horário e regras relevantes em fontes oficiais, quando disponíveis.
2. **Pesquisa da viagem:** comparação de datas, voos, ônibus, hospedagem e transporte local a partir da sua origem real.
3. **Avaliação das alternativas:** análise de custo, duração, sono, trabalho, margem de segurança e riscos verificáveis.
4. **Recomendação:** apresentação das opções viáveis e não dominadas, com uma justificativa clara para a escolha recomendada.

O resultado normalmente contém até três opções realmente diferentes. Alternativas piores em custo, duração e inconveniência não são incluídas apenas para completar a lista.

Quando alguma informação importante ainda não foi divulgada — como o horário ou o local exato da prova — o planejador pode apresentar cenários separados e indicar o que já é seguro decidir e o que deve esperar.

## Objetivos de planejamento

Você pode escolher entre dois modos:

- **Melhor custo-benefício (`best_value`):** procura o equilíbrio mais vantajoso entre preço, tempo, descanso, trabalho e risco.
- **Menor custo total (`lowest_total_cost`):** recomenda a alternativa viável de menor custo completo, sem ignorar as margens necessárias para chegar à prova.

Custos financeiros e inconveniências permanecem separados. O produto não atribui silenciosamente um valor monetário ao seu tempo, sono ou tolerância a risco.

## Exemplo de uso

```text
Planeje minha viagem de Fortaleza para uma prova em Recife no dia 18 de outubro.
A prova começa às 13h. Compare voo e ônibus, considere meu calendário e priorize
melhor custo-benefício. Vou apenas com bagagem de mão.
```

Quanto mais contexto você fornecer, mais útil será a comparação. Os dados que mais influenciam o resultado são:

- cidade de origem;
- data, cidade e horário da prova;
- local da prova, caso já tenha sido divulgado;
- duração prevista e margem de chegada desejada;
- compromissos de trabalho;
- preferência de bagagem e hospedagem;
- tolerância a viagens noturnas ou pernoites em aeroporto;
- objetivo de planejamento.

Se um dado essencial estiver ausente, o planejador perguntará por ele ou trabalhará com cenários explicitamente identificados — sem apresentar suposições como fatos.

## O que você recebe

A resposta apresenta uma recomendação e as alternativas que representam escolhas relevantes, como economizar mais, passar menos tempo fora ou preservar melhor o sono.

Quando o ambiente permite gerar planilhas, o resultado também inclui um arquivo `.xlsx` com:

- `Resumo`: recomendação, comparação dos cenários e justificativa;
- `Pesquisa de datas`: combinações pesquisadas e cobertura da busca;
- `Custos`: valores discriminados e condições importantes;
- `Roteiro`: sequência cronológica de cada viagem.

Se a criação do arquivo `.xlsx` não estiver disponível, os mesmos dados devem ser apresentados em tabelas exportáveis para CSV.

Preços, horários e disponibilidade podem mudar. Por isso, cada resultado informa quando as fontes foram consultadas e diferencia estimativas, cotações e ofertas confirmadas. Os links fornecidos servem para continuar a decisão ou a reserva; não representam uma compra concluída nem garantem a manutenção do preço.

## Fontes e integrações

O plugin pode usar, conforme a disponibilidade e a solicitação do usuário:

- Google Calendar, para considerar compromissos de agenda;
- Gmail, para localizar avisos da prova, passagens ou reservas solicitadas;
- Decolar e Skyscanner, para pesquisar voos;
- Booking.com, para pesquisar hospedagem;
- sites oficiais de organizadoras, companhias, operadoras, aeroportos, hotéis e transporte urbano.

Quando o Google Calendar está conectado, o planejador consulta por padrão apenas os compromissos relevantes para a viagem; você pode pedir que ele não use o calendário. O Gmail só é consultado quando solicitado. Se uma integração não estiver disponível, o planejamento pode continuar com fontes públicas adequadas, deixando essa limitação visível no resultado.

## Privacidade e controle

Planejar uma viagem não autoriza o plugin a comprar, reservar, enviar mensagens, alterar o calendário, gravar arquivos no Drive ou iniciar monitoramento recorrente. Qualquer ação externa desse tipo exige uma autorização específica.

O perfil privado é opcional e permanece fora do repositório. Ele pode guardar preferências recorrentes, como cidade de origem, restrições de trabalho, limite de sono e tipo de bagagem. Evite incluir endereço exato, documentos, credenciais, agenda completa ou dados de terceiros.

Consulte [PRIVACY.md](PRIVACY.md) para conhecer o fluxo de dados e os cuidados necessários antes de publicar código ou compartilhar resultados.

## Instalação

### Pelo marketplace pessoal

Quando o plugin estiver publicado no marketplace pessoal:

```bash
codex plugin add travel-exam-planner@personal
```

### Perfil privado opcional

Crie uma cópia local do modelo:

```bash
mkdir -p ~/.config/travel-exam-planner
cp skills/travel-exam-planner/config/profile.example.json \
  ~/.config/travel-exam-planner/profile.json
```

Para usar outro local, defina a variável `TRAVEL_EXAM_PLANNER_PROFILE` com o caminho do arquivo. O perfil real não deve ser adicionado ao Git nem incluído em planilhas compartilhadas.

## Estado e limitações

- O comparador de alternativas é local e determinístico; a pesquisa de informações atuais depende dos conectores ou de acesso à web disponíveis no ambiente.
- Tarifas, inventário, horários e políticas precisam ser conferidos novamente antes da compra.
- Uma estimativa não equivale a uma cotação disponível para reserva.
- A qualidade do sono em viagens noturnas depende do veículo, assento, duração, interrupções e preferências pessoais.
- A recomendação não substitui a confirmação oficial das informações da prova.
- A geração do workbook depende da capacidade de planilhas disponível no ambiente.

## Para desenvolvimento

O repositório contém a definição da skill, referências de decisão e um comparador determinístico em Python:

```text
.
├── .app.json                              # integrações declaradas
├── .codex-plugin/plugin.json              # manifesto do plugin
├── examples/options.sample.json           # exemplo sintético de entrada
├── skills/travel-exam-planner/
│   ├── SKILL.md                            # comportamento da skill
│   ├── agents/openai.yaml                  # interface do agente
│   ├── config/profile.example.json         # modelo do perfil privado
│   ├── references/                         # regras e modelos detalhados
│   └── scripts/score_options.py            # validação e comparação
├── tests/test_score_options.py
├── PRIVACY.md
└── README.md
```

Requisitos para o comparador local:

- Python 3.10 ou posterior;
- nenhuma dependência Python externa.

Execute os testes:

```bash
python3 -m unittest discover -s tests -v
```

Execute o exemplo:

```bash
python3 skills/travel-exam-planner/scripts/score_options.py \
  examples/options.sample.json --pretty
```

A documentação operacional da LLM está em [SKILL.md](skills/travel-exam-planner/SKILL.md). Os detalhes sobre busca de datas, fontes, modelo de dados, scoring e planilha ficam em [`references/`](skills/travel-exam-planner/references/).

Ao modificar o comportamento, mantenha a implementação, os testes e as referências técnicas consistentes. Use somente exemplos sintéticos e revise [PRIVACY.md](PRIVACY.md) antes de publicar alterações.

## Licença

Este repositório ainda não possui uma licença de uso. A publicação do código, por si só, não concede permissão para redistribuí-lo ou modificá-lo.
