# NOTA METODOLÓGICA: A EVOLUÇÃO DOS MÉTODOS DE ANÁLISE *SHIFT-SHARE* (SSA)

**Resumo** — Este documento descreve, formaliza e ilustra numericamente a evolução metodológica da análise *shift-share* (SSA), da decomposição clássica de Dunn (1960) às reformulações homotéticas (Esteban-Marquillas, 1972; Arcelus, 1984), à forma dinâmica (Barff-Knight, 1988), às formalizações inferenciais (Berzeg, 1978, 1984) e à extensão espacial (Nazara-Hewings, 2004). Cada etapa é apresentada segundo o ciclo justificar–formalizar–interpretar e ilustrada com um exemplo numérico único, construído com dados sintéticos para cinco regiões e três setores, de modo que o leitor acompanhe como cada fórmula se deriva da anterior e o que cada nova camada de decomposição corrige. O documento não relata resultados de uma aplicação empírica real — define e sustenta teoricamente as escolhas de método.
**Palavras-chave:** *Shift-share analysis*. Decomposição de crescimento regional. Efeito competitivo. Efeito alocação. *Shift-share* espacial.

## 1 INTRODUÇÃO

A análise *shift-share* (SSA) é, desde sua formulação original, uma identidade contábil que reparte a variação do emprego regional em componentes atribuíveis ao crescimento nacional, à composição setorial da região e a um resíduo dito "competitivo". Como observam Loveridge e Selting (1998), "SSA é apenas uma identidade contábil praticável: nunca pretendeu ser uma teoria" — afirmação que orienta toda a leitura deste documento. Se a SSA não é um modelo causal, o valor de cada variante está em quão bem ela isola, do resíduo, os efeitos que não deveriam nele estar: a estrutura setorial da região, o viés de ponderação temporal, a ausência de significância estatística e, mais recentemente, a dependência espacial entre regiões vizinhas.

Este documento cobre a fundamentação teórica de cada camada de reformulação, a formalização matemática associada e a tradução de cada fórmula para um exemplo numérico único e recorrente. Ele não cobre a implementação computacional das rotinas (tratada em código separado), nem pretende ser uma revisão exaustiva da literatura — para isso, ver o levantamento bibliográfico que fundamenta esta nota. O objetivo aqui é estritamente pedagógico-metodológico: mostrar, com números, *por que* cada variante surgiu e *o que* ela corrige na anterior.

## 2 FUNDAMENTAÇÃO TEÓRICA

### 2.1 A identidade contábil e seu defeito central

A forma canônica da SSA foi sistematizada por Perloff, Dunn, Lampard e Muth (1960) e, em sua formulação de referência, por Dunn (1960), com popularização por Fuchs (1959, 1962). A decomposição clássica reparte a variação de emprego de uma região *r* no setor *i* em três parcelas aditivas: o efeito de crescimento nacional, o efeito de composição setorial (*industry mix*) e o efeito competitivo ou diferencial regional. O defeito central, identificado já por Rosenfeld (1959) e Houston (1967) e formalizado por Esteban-Marquillas (1972), é que o efeito competitivo clássico é ponderado pelo nível de emprego observado da região no setor — de modo que duas regiões com taxas de crescimento idênticas, mas estruturas setoriais distintas, recebem efeitos competitivos diferentes. O componente que deveria medir "vantagem competitiva pura" está, portanto, contaminado por estrutura produtiva. Essa contaminação motiva diretamente a Seção 6 (Esteban-Marquillas) e a Seção 7 (Arcelus) adiante.

### 2.2 As três ondas de reformulação

A literatura pós-1960 pode ser lida em três ondas, cada uma corrigindo uma falha diferente da identidade clássica. A primeira onda é homotética/alocativa (Esteban-Marquillas, 1972; Herzog e Olsen, 1977; Arcelus, 1984; Haynes e Machunda, 1987) e ataca a contaminação estrutural do efeito competitivo. A segunda onda é temporal/dinâmica (Fuchs, 1959; Stilwell, 1969; Barff e Knight, 1988) e ataca o viés de escolha do ano de ponderação e a distorção de crescimento composto em decomposições estáticas de ponto a ponto. A terceira onda é inferencial (Berzeg, 1978, 1984; Patterson, 1991; Knudsen, 2000) e ataca a impossibilidade de testar estatisticamente uma identidade determinística. A extensão espacial de Nazara e Hewings (2004), tratada na Seção 11, é posterior às três e ataca um pressuposto implícito em todas elas: o de que regiões vizinhas não interagem. Entre a onda inferencial e a espacial, a Seção 10 aprofunda a própria onda inferencial: Knudsen (2000) mostra que a formalização estatística da SSA não precisa se limitar ao modelo linear de Berzeg, podendo ser derivada da teoria da informação pelo princípio de mínima informação discriminante, o que leva a um modelo log-linear estimado por máxima verossimilhança como um modelo linear generalizado de Poisson. As seções 4 a 11 seguem exatamente essa ordem histórica e lógica.

## 3 BASE DE DADOS DO EXEMPLO ILUSTRATIVO

Para tornar cada fórmula tangível, este documento usa **um único conjunto de dados sintéticos**, reaproveitado em todas as seções seguintes, com *R* = 5 regiões (unidades federativas do Nordeste brasileiro, escolhidas por terem fronteiras terrestres reais entre si — relevante para a Seção 11) e *N* = 3 setores agregados. As regiões são Piauí (PI), Ceará (CE), Maranhão (MA), Bahia (BA) e Pernambuco (PE); os setores são Agropecuária (AGR), Indústria (IND) e Serviços (SER). Os valores de emprego são **inteiramente hipotéticos** — não correspondem a estatísticas oficiais — e foram construídos para exibir, de forma didática, um caso de vantagem competitiva concentrada em serviços (PI), um caso de forte crescimento industrial idiossincrático (CE), um caso de desvantagem competitiva generalizada (MA), um caso "neutro" próximo à média nacional em todas as taxas (BA) e um caso de especialização mal alocada (PE).

Seja $E_{0,ri}$ o emprego da região *r* no setor *i* no ano-base $t_0$ e $E_{1,ri}$ o emprego no ano-terminal $t_1$. A Tabela 1 apresenta os dados-base e a Tabela 2, o ano terminal.

**Tabela 1 — Emprego por região e setor, ano-base ($E_{0,ri}$)**

| Região | AGR | IND | SER | Total |
|:---|---:|---:|---:|---:|
| PI | 180 | 90 | 230 | 500 |
| CE | 150 | 220 | 430 | 800 |
| MA | 200 | 70 | 180 | 450 |
| BA | 260 | 310 | 560 | 1.130 |
| PE | 140 | 280 | 520 | 940 |
| **Nacional** | **930** | **970** | **1.920** | **3.820** |

Fonte: dados sintéticos ilustrativos, elaboração própria.

**Tabela 2 — Emprego por região e setor, ano-terminal ($E_{1,ri}$)**

| Região | AGR | IND | SER | Total |
|:---|---:|---:|---:|---:|
| PI | 189 | 103 | 322 | 614 |
| CE | 158 | 279 | 559 | 996 |
| MA | 200 | 77 | 225 | 502 |
| BA | 273 | 356 | 728 | 1.357 |
| PE | 158 | 322 | 650 | 1.130 |
| **Nacional** | **978** | **1.137** | **2.484** | **4.599** |

Fonte: dados sintéticos ilustrativos, elaboração própria.

Dessas duas tabelas derivam-se as três taxas de crescimento que alimentam toda a análise subsequente: a taxa regional-setorial $g_{ri} = (E_{1,ri}-E_{0,ri})/E_{0,ri}$, a taxa nacional do setor $g_{ni} = (\sum_r E_{1,ri} - \sum_r E_{0,ri})/\sum_r E_{0,ri}$ e a taxa nacional agregada $g_n = (\sum_{r,i} E_{1,ri} - \sum_{r,i} E_{0,ri})/\sum_{r,i} E_{0,ri}$. Neste exemplo, $g_n = 20{,}39\%$, e as taxas nacionais setoriais são $g_{n,\text{AGR}} = 5{,}16\%$, $g_{n,\text{IND}} = 17{,}22\%$ e $g_{n,\text{SER}} = 29{,}38\%$ — um padrão de terciarização nacional que será a "ponta" contra a qual cada região é comparada.

**Tabela 3 — Taxa de crescimento regional-setorial $g_{ri}$ (%)**

| Região | AGR | IND | SER |
|:---|---:|---:|---:|
| PI | 5,00 | 14,44 | 40,00 |
| CE | 5,33 | 26,82 | 30,00 |
| MA | 0,00 | 10,00 | 25,00 |
| BA | 5,00 | 14,84 | 30,00 |
| PE | 12,86 | 15,00 | 25,00 |

Fonte: elaboração própria a partir das Tabelas 1 e 2.

## 4 DECOMPOSIÇÃO CLÁSSICA (DUNN, 1960)

A forma canônica, sistematizada por Perloff, Dunn, Lampard e Muth (1960) a partir de precursores como o Barlow Report de 1940 e Creamer (1943), reparte a variação absoluta de emprego $\Delta E_{ri} = E_{1,ri} - E_{0,ri}$ em três parcelas aditivas, todas ponderadas pelo emprego-base $E_{0,ri}$:

$$ \Delta E_{ri} = \underbrace{E_{0,ri}\,g_n}_{NE_{ri}} + \underbrace{E_{0,ri}\,(g_{ni}-g_n)}_{IM_{ri}} + \underbrace{E_{0,ri}\,(g_{ri}-g_{ni})}_{CE_{ri}} \tag{1} $$

em que $NE_{ri}$ é o **efeito de crescimento nacional** (o quanto a região teria crescido se cada setor acompanhasse exatamente a taxa agregada do país), $IM_{ri}$ é o **efeito de composição setorial** (crescimento extra ou perdido por a região estar voltada a setores nacionalmente mais ou menos dinâmicos que a média) e $CE_{ri}$ é o **efeito competitivo ou diferencial regional** (o resíduo: quanto a região cresceu acima ou abaixo do que seu próprio setor cresceu no país). A soma $NE_{ri}+IM_{ri}$ é o crescimento "esperado" da região; $CE_{ri}$ é o desvio ("*shift*") dessa expectativa — o que dá nome ao método (SELTING; LOVERIDGE, 1992).

A Tabela 4 aplica a Equação 1 aos dados das Tabelas 1–3. Note que a soma das três colunas, célula a célula, reproduz exatamente $\Delta E_{ri}$ — a identidade é algébrica, não estatística, e vale à precisão de máquina.

**Tabela 4 — Decomposição clássica de Dunn (1960): totais regionais**

| Região | $\Delta E_r$ | $NE_r$ | $IM_r$ | $CE_r$ |
|:---|---:|---:|---:|---:|
| PI | 114 | 101,96 | −9,62 | 21,65 |
| CE | 196 | 163,14 | 8,79 | 24,07 |
| MA | 52 | 91,77 | −16,52 | −23,25 |
| BA | 227 | 230,44 | 0,85 | −4,29 |
| PE | 190 | 191,69 | 16,49 | −18,18 |

Fonte: elaboração própria, Equação 1 aplicada às Tabelas 1–3.

A leitura já revela o problema que motivou toda a literatura subsequente. Piauí e Ceará têm efeitos competitivos positivos e de magnitude parecida (21,65 e 24,07), mas por razões distintas: o Ceará deve seu resultado principalmente à indústria (crescimento setorial de 26,82% contra 17,22% nacional), enquanto o Piauí deve o seu quase inteiramente a serviços (40% contra 29,38% nacional). O componente $CE_r$, por si só, não distingue essas duas histórias — nem informa se o desempenho vem de um setor em que a região é fortemente especializada ou de um setor marginal em sua estrutura. Essa é exatamente a lacuna que Esteban-Marquillas (1972) endereça na Seção 6.

## 5 A CONTROVÉRSIA DOS PESOS: BASE, TERMINAL E MÉDIA

Fuchs (1959) mostrou que o efeito competitivo é relativamente pouco sensível à escolha do ano de ponderação, mas o efeito de composição setorial é sensível — e propôs a **média entre pesos-base e pesos-terminais** como correção. Stilwell (1969) propôs o extremo oposto, uma "composição reversa" com pesos exclusivamente terminais, para sinalizar regiões em declínio; Ashby (1970) criticou essa escolha como excessiva, defendendo uma convenção intermediária "cinquenta-cinquenta". A escolha do ano de ponderação, portanto, não é uma decisão neutra — é uma escolha teórica sobre qual estrutura produtiva (a de partida ou a de chegada) deve servir de referência para julgar o desempenho da região.

Para reponderar pelo ano terminal preservando a identidade aditiva, define-se a taxa "reversa" $g'_{ri} = (E_{0,ri}-E_{1,ri})/E_{1,ri}$ — o crescimento de $t_1$ para $t_0$ — e repete-se a Equação 1 usando $E_{1,ri}$ como peso e $g'$ no lugar de $g$:

$$ E_{0,ri}-E_{1,ri} = E_{1,ri}\,g'_n + E_{1,ri}\,(g'_{ni}-g'_n) + E_{1,ri}\,(g'_{ri}-g'_{ni}) \tag{2} $$

Como o lado esquerdo da Equação 2 é $-\Delta E_{ri}$, basta inverter o sinal de cada componente para obter a decomposição terminal na mesma unidade da Equação 1. A Tabela 5 compara o efeito competitivo sob pesos-base (Equação 1) e sob pesos-terminais (Equação 2, sinal invertido).

**Tabela 5 — Sensibilidade do efeito competitivo à escolha do ano de ponderação**

| Região | $CE_r$ (peso-base) | $CE_r$ (peso-terminal) | Diferença |
|:---|---:|---:|---:|
| PI | 21,65 | 16,48 | −5,17 |
| CE | 24,07 | 20,34 | −3,73 |
| MA | −23,25 | −20,21 | 3,04 |
| BA | −4,29 | −3,98 | 0,31 |
| PE | −18,18 | −12,63 | 5,55 |

Fonte: elaboração própria, Equações 1 e 2.

O efeito competitivo muda de magnitude, mas não de sinal, em todas as cinco regiões deste exemplo — confirmando, nesta escala reduzida, o achado de Fuchs (1959) de relativa estabilidade de sinal do componente competitivo clássico. O mesmo não ocorrerá com o efeito de alocação de Esteban-Marquillas, como mostra a Seção 6.3 adiante — e é justamente essa diferença de comportamento sob reponderação que torna a crítica de Herzog e Olsen (1977) empiricamente relevante.

## 6 A REFORMULAÇÃO HOMOTÉTICA: ESTEBAN-MARQUILLAS (1972)

### 6.1 Justificativa

Esteban-Marquillas (1972) demonstrou formalmente o problema já apontado por Rosenfeld (1959): como $CE_{ri}$ na Equação 1 é ponderado pelo emprego efetivamente observado $E_{0,ri}$, duas regiões com a mesma taxa diferencial $(g_{ri}-g_{ni})$ recebem efeitos competitivos absolutos diferentes apenas porque uma delas tem mais peso naquele setor — o componente mistura, portanto, "quanto a região é competitiva" com "quanto emprego ela tem para multiplicar essa competitividade". A solução proposta foi substituir o peso observado por um peso contrafactual: o emprego que a região *teria* no setor se sua estrutura produtiva reproduzisse exatamente as participações setoriais nacionais.

### 6.2 Formalização

Define-se o **emprego homotético**:

$$ E^{*}_{ri} = E_{0,r\bullet}\left(\frac{E_{0,\bullet i}}{E_{0,\bullet\bullet}}\right) \tag{3} $$

em que $E_{0,r\bullet}=\sum_i E_{0,ri}$ é o total regional, $E_{0,\bullet i}=\sum_r E_{0,ri}$ é o total nacional do setor *i* e $E_{0,\bullet\bullet}$ é o total nacional. $E^{*}_{ri}$ é, portanto, o total de emprego da região distribuído segundo as participações setoriais do país — a estrutura que a região teria se fosse uma miniatura fiel da economia nacional. O efeito competitivo clássico da Equação 1 é então reescrito como a soma de dois termos:

$$ CE_{ri} = \underbrace{E^{*}_{ri}\,(g_{ri}-g_{ni})}_{CE^{*}_{ri}\ \text{(competitivo puro)}} + \underbrace{(E_{0,ri}-E^{*}_{ri})\,(g_{ri}-g_{ni})}_{AE_{ri}\ \text{(efeito alocação)}} \tag{4} $$

$CE^{*}_{ri}$ é o efeito competitivo **livre de estrutura** — mede apenas a diferença de taxa, ponderada pelo emprego "neutro" $E^{*}$. $AE_{ri}$, o **efeito alocação**, é o produto entre o grau de especialização da região no setor ($E_{0,ri}-E^{*}_{ri}$, positivo se a região é mais especializada que a média nacional naquele setor) e a vantagem competitiva nesse mesmo setor ($g_{ri}-g_{ni}$). $AE_{ri}$ é positivo quando a região se especializa exatamente nos setores em que também é competitiva (alocação "correta") e negativo quando ela se especializa em setores nos quais tem desvantagem, ou deixa de se especializar em setores nos quais tem vantagem (alocação "incorreta" ou subotimizada).

### 6.3 Aplicação e interpretação

A Tabela 6 traz o emprego homotético (Equação 3); a Tabela 7, a decomposição de Esteban-Marquillas (Equação 4) em totais regionais, ao lado da decomposição clássica para comparação.

**Tabela 6 — Emprego homotético $E^{*}_{ri}$**

| Região | AGR | IND | SER |
|:---|---:|---:|---:|
| PI | 121,73 | 126,96 | 251,31 |
| CE | 194,76 | 203,14 | 402,09 |
| MA | 109,55 | 114,27 | 226,18 |
| BA | 275,10 | 286,94 | 567,96 |
| PE | 228,85 | 238,69 | 472,46 |

Fonte: elaboração própria, Equação 3.

**Tabela 7 — Decomposição de Esteban-Marquillas (1972): totais regionais**

| Região | $NE_r$ | $IM_r$ | $CE_r$ (clássico) | $CE^{*}_r$ (puro) | $AE_r$ (alocação) |
|:---|---:|---:|---:|---:|---:|
| PI | 101,96 | −9,62 | 21,65 | 22,99 | −1,33 |
| CE | 163,14 | 8,79 | 24,07 | 22,35 | 1,72 |
| MA | 91,77 | −16,52 | −23,25 | −23,80 | 0,55 |
| BA | 230,44 | 0,85 | −4,29 | −3,72 | −0,57 |
| PE | 191,69 | 16,49 | −18,18 | −8,35 | −9,83 |

Fonte: elaboração própria, Equação 4. Note que $CE^{*}_r + AE_r = CE_r$ (clássico) em cada linha, confirmando a Equação 4.

O caso de Pernambuco ilustra exatamente o que a reformulação foi desenhada para revelar. Na decomposição clássica (Tabela 4), PE tinha um efeito competitivo de −18,18 — número que, isoladamente, sugere fraco desempenho competitivo generalizado. A Tabela 7 mostra que isso é impreciso: o efeito competitivo *puro* de PE é de apenas −8,35 (metade do valor clássico), e o restante, −9,83, é efeito de **má alocação**: PE tem vantagem competitiva forte em Agropecuária ($g_{ri}-g_{ni}=+7,70$ pontos percentuais) mas está *sub*-especializado nesse setor ($E_{0,ri}-E^{*}_{ri}=-88,85$, ou seja, emprega menos em Agropecuária do que sua estrutura homotética previria) — a região não está capturando um ganho que sua própria vantagem comparativa permitiria. Já Piauí e Ceará mostram exatamente o padrão oposto: seus efeitos de alocação são pequenos (−1,33 e +1,72), o que indica que a maior parte do desempenho observado nessas duas regiões é competitividade genuína, não um acidente de composição setorial.

## 7 A EXTENSÃO DE ARCELUS (1984) E SEUS LIMITES ALGÉBRICOS

### 7.1 Justificativa

Arcelus (1984) argumentou que Esteban-Marquillas não "explorou suficientemente" a propriedade do emprego homotético, restringindo-a ao efeito competitivo. Sua proposta foi aplicar a mesma lógica de decomposição — separar um termo "esperado" (ponderado por $E^{*}$) de um termo "diferencial" (ponderado por $E_{0,ri}-E^{*}_{ri}$) — também ao efeito de crescimento nacional e ao efeito de composição setorial, produzindo quatro subcomponentes em vez de dois.

### 7.2 Formalização

Aplicando a mesma partição da Equação 4 aos dois primeiros termos da Equação 1:

$$ NE_{ri} = \underbrace{E^{*}_{ri}\,g_n}_{EN_{ri}} + \underbrace{(E_{0,ri}-E^{*}_{ri})\,g_n}_{DN_{ri}} \qquad IM_{ri} = \underbrace{E^{*}_{ri}\,(g_{ni}-g_n)}_{EM_{ri}} + \underbrace{(E_{0,ri}-E^{*}_{ri})\,(g_{ni}-g_n)}_{DM_{ri}} \tag{5} $$

### 7.3 Uma propriedade algébrica que qualifica a extensão

Somando a Equação 5 sobre os setores *i* de uma mesma região *r*, duas propriedades emergem diretamente da definição de $E^{*}$ na Equação 3: primeiro, $\sum_i (E_{0,ri}-E^{*}_{ri}) \equiv 0$ para qualquer região, porque o emprego homotético é construído para preservar exatamente o total regional ($\sum_i E^{*}_{ri}=E_{0,r\bullet}$); segundo, $\sum_i E^{*}_{ri}(g_{ni}-g_n) \equiv 0$ para qualquer região, porque os pesos $E^{*}_{ri}/E_{0,r\bullet}$ reproduzem exatamente as participações setoriais nacionais, e a média nacional ponderada por essas participações é, por definição, $g_n$. Segue que, somados por região, $DN_r \equiv 0$ e $EM_r \equiv 0$ **identicamente**, para qualquer conjunto de dados — não é um resultado deste exemplo específico, mas uma propriedade algébrica da construção. A Tabela 8 confirma isso numericamente.

**Tabela 8 — Extensão de Arcelus (1984): totais regionais**

| Região | $EN_r$ | $DN_r$ | $EM_r$ | $DM_r$ | $CE^{*}_r$ | $AE_r$ |
|:---|---:|---:|---:|---:|---:|---:|
| PI | 101,96 | 0,00 | 0,00 | −9,62 | 22,99 | −1,33 |
| CE | 163,14 | 0,00 | 0,00 | 8,79 | 22,35 | 1,72 |
| MA | 91,77 | 0,00 | 0,00 | −16,52 | −23,80 | 0,55 |
| BA | 230,44 | 0,00 | 0,00 | 0,85 | −3,72 | −0,57 |
| PE | 191,69 | 0,00 | 0,00 | 16,49 | −8,35 | −9,83 |

Fonte: elaboração própria, Equação 5.

Em outras palavras: ao nível regional agregado (a soma sobre setores), a homotetização de $NE$ e $IM$ não produz informação nova — $EN_r$ reproduz $NE_r$ e $DM_r$ reproduz $IM_r$ da Tabela 4, célula a célula. O ganho analítico da homotetização, como Esteban-Marquillas já havia percebido, está concentrado no efeito competitivo, onde $(g_{ri}-g_{ni})$ varia célula a célula e não se anula ao somar. Esse resultado algébrico é consistente com — e ajuda a explicar — o achado empírico de Keil (1992), que, usando dados de Indiana (1977–1986), concluiu que as extensões homotéticas de Esteban-Marquillas e Arcelus "lançam pouca luz sobre o crescimento regional total" mesmo quando esclarecem taxas de indústrias individuais: o próprio arcabouço algébrico garante que dois dos quatro novos subcomponentes de Arcelus sejam nulos quando agregados por região. Arcelus (1984) propôs ainda um segundo modelo (Arcelus II), com um efeito de crescimento regional endógeno e um efeito de composição regional, que usa a taxa de crescimento *da própria região* como referência em vez da taxa nacional; por não termos acesso à formulação algébrica original da fonte primária, essa extensão é tratada aqui apenas conceitualmente, sem exemplo numérico — ver a ressalva na Seção 14.

## 8 SHIFT-SHARE DINÂMICO: BARFF-KNIGHT (1988)

### 8.1 Justificativa

Todas as decomposições até aqui são "estáticas comparativas": comparam apenas os pontos $t_0$ e $t_1$, ignorando a trajetória entre eles. Barff e Knight (1988), retomando uma sugestão de Thirlwall (1967) de particionar o período em subperíodos, argumentaram que essa comparação de extremos é distorcida por crescimento composto e por mudanças na composição setorial *durante* o intervalo — um setor pode crescer rapidamente no início do período e desacelerar no fim (ou vice-versa) sem que a taxa ponta a ponta capture essa dinâmica.

### 8.2 Formalização

Particiona-se o intervalo $[t_0,t_1]$ em $K$ subperíodos. Para cada subperíodo $k$, calcula-se a decomposição clássica (Equação 1) usando o emprego do início do subperíodo como peso-base; o efeito competitivo dinâmico é a soma dos efeitos competitivos de cada subperíodo:

$$ CE^{\text{din}}_{ri} = \sum_{k=1}^{K} E_{k-1,ri}\left(g^{(k)}_{ri}-g^{(k)}_{ni}\right) \tag{6} $$

em que $g^{(k)}_{ri}$ e $g^{(k)}_{ni}$ são as taxas regional-setorial e nacional-setorial calculadas apenas dentro do subperíodo $k$, com peso-base $E_{k-1,ri}$ (o emprego no início daquele subperíodo, não o do início do período total). Compara-se $CE^{\text{din}}_{ri}$ ao efeito competitivo estático $CE^{\text{est}}_{ri}$ (Equação 1, aplicada diretamente a $t_0$ e $t_1$) para medir a magnitude da distorção de trajetória.

### 8.3 Aplicação

Para ilustrar, o intervalo $[t_0,t_1]$ foi dividido em dois subperíodos ($K=2$) com uma trajetória setorial deliberadamente desigual — crescimento industrial concentrado no primeiro subperíodo e crescimento de serviços concentrado no segundo, um padrão plausível de transição estrutural. A Tabela 9 compara o efeito competitivo dinâmico (soma dos dois subperíodos, Equação 6) ao estático (Equação 1).

**Tabela 9 — Efeito competitivo: decomposição dinâmica versus estática, totais regionais**

| Região | $CE^{\text{din}}_r$ (soma de 2 subperíodos) | $CE^{\text{est}}_r$ | Diferença |
|:---|---:|---:|---:|
| PI | 23,55 | 25,65 | −2,10 |
| CE | 25,08 | 25,93 | −0,84 |
| MA | −23,96 | −24,97 | 1,01 |
| BA | −4,96 | −4,86 | −0,09 |
| PE | −19,71 | −21,75 | 2,04 |

Fonte: elaboração própria, Equações 1 e 6, com trajetória hipotética de dois subperíodos.

A diferença entre as duas formas não é uniforme entre regiões — nem em magnitude, nem em sinal. Para Piauí e Ceará, a forma estática superestima o efeito competitivo em relação à forma dinâmica (diferenças negativas); para Maranhão e Pernambuco, ocorre o oposto: a forma estática *subestima* o desempenho competitivo real ao concentrar toda a comparação nos dois pontos extremos. Isso confirma, neste exemplo reduzido, a advertência de Barff e Knight (1988): a decomposição ponto a ponto pode inverter o sinal relativo da vantagem competitiva entre regiões dependendo de como a mudança estrutural se distribuiu dentro do intervalo, sobretudo quando o período é longo ou volátil.

## 9 FORMALIZAÇÃO INFERENCIAL: A ANOVA DE BERZEG (1978, 1984)

### 9.1 Justificativa

Como observam Selting e Loveridge (1992), por ser uma identidade determinística, nenhum componente da SSA clássica pode ser testado estatisticamente — não há erro-padrão, não há teste de hipótese, não há forma de dizer se um efeito competitivo de −4,29 (Bahia, Tabela 4) é "significativamente" diferente de zero ou apenas ruído amostral. Berzeg (1978, 1984) forneceu a fundamentação estatística definitiva ao recastar a identidade como um modelo linear de análise de variância (ANOVA), no qual o crescimento nacional é o intercepto, a composição setorial é um coeficiente estimado e o efeito competitivo é o **termo de erro** de uma regressão — passível, sob normalidade dos erros, de teste *t*.

### 9.2 Formalização

Considere a regressão da taxa de crescimento regional-setorial em variáveis binárias (*dummies*) de setor, sem intercepto separado (conjunto completo de *dummies*):

$$ g_{ri} = \sum_{i=1}^{N} \beta_i D_i + u_{ri} \tag{7} $$

em que $D_i$ é uma *dummy* igual a 1 se a observação pertence ao setor $i$ e $\beta_i$, estimado por mínimos quadrados ordinários, é a média amostral de $g_{ri}$ no setor $i$ — o análogo, nesta formulação, do parâmetro de composição setorial $g_{ni}$. O resíduo $u_{ri} = g_{ri}-\hat\beta_i$ é a **taxa competitiva estimada**: sob a hipótese de erros normais e homocedásticos, a razão entre a média de $u_{ri}$ em uma região e seu erro-padrão segue distribuição *t* de Student,

$$ t_r = \frac{\bar{u}_r}{s/\sqrt{n_r}} \tag{8} $$

com $s$ o desvio-padrão residual do modelo (Equação 7) e $n_r$ o número de observações setoriais na região $r$ — permitindo testar $H_0: \bar u_r = 0$, isto é, se a região tem, em média, desempenho competitivo estatisticamente distinguível de zero.

### 9.3 Aplicação

A Tabela 10 mostra a decomposição célula a célula da Equação 7 aplicada ao painel de 15 observações (5 regiões × 3 setores) das Tabelas 1–2. A Tabela 11 aplica o teste da Equação 8 por região.

**Tabela 10 — Regressão de Berzeg: taxa observada, componente de composição estimado e resíduo competitivo**

| Região | Setor | $g_{ri}$ | $\hat\beta_i$ (mix estimado) | $u_{ri}$ (competitivo) |
|:---|:---|---:|---:|---:|
| PI | AGR | 0,0500 | 0,0564 | −0,0064 |
| PI | IND | 0,1444 | 0,1622 | −0,0178 |
| PI | SER | 0,4000 | 0,3000 | 0,1000 |
| CE | AGR | 0,0533 | 0,0564 | −0,0030 |
| CE | IND | 0,2682 | 0,1622 | 0,1060 |
| CE | SER | 0,3000 | 0,3000 | 0,0000 |
| MA | AGR | 0,0000 | 0,0564 | −0,0564 |
| MA | IND | 0,1000 | 0,1622 | −0,0622 |
| MA | SER | 0,2500 | 0,3000 | −0,0500 |
| BA | AGR | 0,0500 | 0,0564 | −0,0064 |
| BA | IND | 0,1484 | 0,1622 | −0,0138 |
| BA | SER | 0,3000 | 0,3000 | 0,0000 |
| PE | AGR | 0,1286 | 0,0564 | 0,0722 |
| PE | IND | 0,1500 | 0,1622 | −0,0122 |
| PE | SER | 0,2500 | 0,3000 | −0,0500 |

Fonte: elaboração própria, Equação 7, mínimos quadrados ordinários com 15 observações.

**Tabela 11 — Teste *t* do desempenho competitivo médio por região ($H_0: \bar u_r=0$; graus de liberdade = 12)**

| Região | $\bar u_r$ | $t_r$ | valor-*p* |
|:---|---:|---:|---:|
| PI | 0,0253 | 0,7659 | 0,4585 |
| CE | 0,0343 | 1,0393 | 0,3192 |
| MA | −0,0562 | −1,7022 | 0,1145 |
| BA | −0,0067 | −0,2039 | 0,8418 |
| PE | 0,0033 | 0,1008 | 0,9213 |

Fonte: elaboração própria, Equação 8.

Nenhuma região atinge significância convencional de 5% neste exemplo — o mais próximo é o Maranhão, com $t=-1,70$ e valor-*p*=0,11, sugerindo desvantagem competitiva sistemática, mas não conclusiva na amostra. Esse resultado ilustra, mais do que qualquer conclusão substantiva sobre as regiões fictícias, a própria lição metodológica da Seção 9.1: a decomposição clássica (Tabela 4) mostraria o efeito competitivo do Maranhão como um número aparentemente grande e "real" (−23,25), mas a formalização de Berzeg revela que, com apenas três observações setoriais por região, esse número não é estatisticamente distinguível de zero ao nível de 5% — exatamente o tipo de afirmação que a SSA clássica é incapaz de fazer e que o limiar de significância listado no Quadro de Parâmetros Consolidados (Seção 13) torna operacional.

## 10 KNUDSEN (2000): AS DUAS FORMAS PROBABILÍSTICAS, ANOVA E TEORIA DA INFORMAÇÃO

### 10.1 Justificativa

Knudsen (2000) classifica os métodos de SSA em três famílias: os modelos contábeis tradicionais, os modelos de análise de variância (ANOVA) e os modelos de teoria da informação. As duas últimas são as "duas formas probabilísticas" que o artigo apresenta. A primeira é a ANOVA de Berzeg (1978, 1984), que o autor reescreve nas versões simples, com a extensão de Arcelus e dinâmica (equações 4 a 6 do artigo). A segunda é o *shift-share* de teoria da informação, derivado do princípio de mínima informação discriminante (MDI) (equações 7 a 19), ao qual o artigo acrescenta um modelo misto, com variável exógena contínua, para mostrar a flexibilidade da abordagem (equações 20 a 24). A ideia de fundo é ler o problema da SSA como a partição da variação de uma tabela de contingência com três dimensões (setor, região e ano). Assim lida, a SSA é um caso particular da classe de modelos para dados tabulares agregados usada em planejamento, geografia e ciência regional, e passa a admitir testes de hipótese sobre a variação do emprego por região ou setor.

O artigo também qualifica a equivalência entre a identidade contábil (Equação 1) e a forma ANOVA (Equação 7). As duas são matematicamente equivalentes, mas a regressão estimada não reproduz os componentes contábeis, por duas razões: ela é medida em taxas, e não em empregos, de modo que os termos diferem pelo fator $E_{0,ri}$; e seus erros são heterocedásticos. Segundo Knudsen (2000), Berzeg (1978, 1984) mostra que as estimativas coincidem quando se supõe $E[e_{ri}^2] = \sigma^2/w_{ri}$, com $w_{ri} = E_{0,ri}/\sum_{r,i}E_{0,ri}$, e se estima por mínimos quadrados ponderados. A regressão da Seção 9, estimada por mínimos quadrados ordinários sem ponderação, não tem essa propriedade: nela, a taxa $g_{ri}$ de uma célula de emprego-base pequeno, cuja variância tende a ser maior, pesa tanto quanto a de uma célula grande.

Na comparação empírica do artigo (emprego do Bureau of Labor Statistics agregado nas divisões setoriais do BLS e nas nove divisões censitárias dos Estados Unidos, anos de 1970 e 1980), a forma informacional teve ajuste superior e discriminou melhor os parâmetros nos modelos simples e com a extensão de Arcelus: a porcentagem da *deviance* do modelo nulo explicada (PNMD, uma medida do tipo $R^2$) foi de 0,5163 e 0,6601, contra $R^2$ de 0,1836 e 0,2284 da ANOVA correspondente. Na forma dinâmica, o ajuste foi fraco nos dois casos (0,0258 contra 0,0111). O autor conclui com cautela. Os modelos informacionais exigem pouca manipulação prévia dos dados, permitem incorporar a informação disponível sob a forma de restrições, colocam a SSA no campo da análise estatística de dados tabulares nominais e parecem úteis em dados com poucos valores extremos grandes; em contrapartida, seus parâmetros são mais difíceis de interpretar e nem sempre ajustam melhor que a ANOVA.

### 10.2 Formalização

**Forma I (ANOVA).** É a regressão da Equação 7 (Seção 9.2). Knudsen (2000) a escreve com intercepto, $g_{ri} = a + B_i + e_{ri}$ (sua equação 4), em que $a$ estima $g_n$, $B_i$ estima $g_{ni}-g_n$ e o erro $e_{ri}$ estima o termo competitivo $g_{ri}-g_{ni}$; a Equação 7 usa o conjunto completo de *dummies* de setor no lugar do intercepto, o que é apenas outra parametrização. A extensão de Arcelus acrescenta um efeito de região, $g_{ri} = a + B_i + G_r + e_{ri}$ (equação 5), e a forma dinâmica acrescenta ainda um efeito de período $V_k$ (equação 6). Sob normalidade dos erros, a razão entre cada parâmetro e seu erro-padrão segue a distribuição *t* de Student.

**Forma II (teoria da informação).** Sejam $q_{ri} = E_{0,ri}/\sum_{r,i}E_{0,ri}$ a distribuição *a priori* (participações no ano-base) e $p_{ri} = E_{1,ri}/\sum_{r,i}E_{1,ri}$ a distribuição *a posteriori* (participações no ano terminal). O ganho de informação de Kullback e Leibler (1951), equação 7 do artigo, mede a informação obtida ao observar $P$ dado $Q$:

$$ I(P:Q) = \sum_{r,i} p_{ri}\,\ln\frac{p_{ri}}{q_{ri}} \tag{12} $$

O modelo de mínima informação discriminante escolhe $P$ minimizando $I(P:Q)$ sujeito a restrições lineares que representam o que se sabe sobre a distribuição final, além de $\sum_{r,i}p_{ri}=1$ e $p_{ri}\ge 0$ (equação 8). O problema pode ser resolvido pelo dual, um programa geométrico sem restrições (equação 9), mas, com restrições de igualdade lineares, o método de Lagrange leva diretamente a um modelo log-linear em $p_{ri}$ (equação 10), e as quantidades resultantes são estimadores assintóticos de máxima verossimilhança. Na forma básica, a restrição fixa os totais setoriais, $\sum_r p_{ri} = o_i$ (equação 11), e a solução é $p_{ri} = q_{ri}\exp(a + o_i + f_{ri})$ (equação 12 do artigo). Na extensão de Arcelus, acrescenta-se a restrição dos totais regionais, $\sum_i p_{ri} = d_r$ (equação 15), e a solução passa a ser $p_{ri} = q_{ri}\exp(a + o_i + d_r + f_{ri})$ (equação 16). Reescrita em níveis de emprego (equação 17) e linearizada, ela dá a **forma estática** (equação 18 do artigo):

$$ \ln\frac{E_{1,ri}}{E_{0,ri}} = A + O_i + D_r + \ln F_{ri} \tag{13} $$

em que $A$ é o intercepto (crescimento comum), $O_i$ é o efeito do setor (análogo, em escala logarítmica, do componente de composição setorial), $D_r$ é o efeito da região (análogo, em escala logarítmica, do efeito competitivo regional) e $\ln F_{ri}$ é o termo de erro. A **forma dinâmica** pode ser obtida de duas maneiras: aplicando a Equação 13 a períodos sucessivos e somando ou tirando a média dos resultados, como em Barff e Knight (1988), ou acrescentando à tabela uma dimensão de tempo, com um efeito $T_k$ para cada par de anos adjacentes $k = 1,\dots,T$ (equação 19 do artigo):

$$ \ln\frac{E_{k,ri}}{E_{k-1,ri}} = A + O_i + D_r + T_k + \ln F_{rik} \tag{14} $$

Nas duas formas, os parâmetros só são determinados a menos de uma constante aditiva: um nível de cada dimensão não pode ser estimado (o artigo os chama de *aliased*) e os demais são lidos em relação a ele.

**Estimação.** Como as soluções MDI são estimadores de máxima verossimilhança, Knudsen (2000) calibra esses modelos com métodos de modelos lineares generalizados (GLM), remetendo à literatura de regressão de Poisson para dados de contagem agregados (FLOWERDEW; LOVETT, 1989; LOVETT; FLOWERDEW, 1989; MCCULLAGH; NELDER, 1983) e à inclusão de informação *a priori* por meio de *offsets* (KNUDSEN, 1992). Na forma estática usada nesta nota e na implementação de referência, o modelo estimado é um GLM de Poisson com ligação log, em que $\ln E_{0,ri}$ entra como *offset* (regressor com coeficiente fixado em 1):

$$ E_{1,ri} \sim \text{Poisson}(\mu_{ri}), \qquad \ln\mu_{ri} = \ln E_{0,ri} + A + O_i + D_r \tag{15} $$

Os parâmetros são assintoticamente normais, de modo que a razão entre o coeficiente e seu erro-padrão dá o teste de Wald, $z_r = \hat D_r/\text{ep}(\hat D_r)$, sob $H_0: D_r = 0$. O ajuste é medido pela *deviance*, assintoticamente distribuída como qui-quadrado, e resumido pela PNMD, $1 - \mathcal{D}_{\text{modelo}}/\mathcal{D}_{\text{nulo}}$, que se lê como um $R^2$. Knudsen (2000) observa ainda que a ANOVA simples (sua equação 4) e a forma informacional simples (equação 14 do artigo, sem o efeito de região) deveriam produzir resultados idênticos se esta fosse calibrada com pesos $w_{ri}^{-1}$ e erros $\ln F_{ri}$ normais (BERZEG, 1984; KNUDSEN; BARFF, 1991), e que os parâmetros das duas formas deveriam guardar uma relação exponencial. No texto do artigo essa relação aparece impressa como $B_i = \exp(O_i - 1)$; a leitura coerente com $g_{ri} = E_{1,ri}/E_{0,ri} - 1$ é $B_i = e^{O_i} - 1$. Na comparação empírica, porém, o autor não encontra uma relação precisa entre os parâmetros e atribui a discrepância à inversa generalizada usada para contornar a singularidade de $X^{\top}X$ na calibração.

**Adaptações da implementação de referência.** A implementação do projeto (`ssa_models.knudsen_mdi` e seção 9 do caderno `evolucao_shift_share.ipynb`) segue as Equações 13 a 15 e acrescenta três elementos que não estão no artigo. Primeiro, os erros-padrão são, por padrão, quase-Poisson: a matriz de covariância de máxima verossimilhança é multiplicada pela dispersão estimada $\hat\phi = \chi^2_{\text{Pearson}}/(n-p)$. Emprego não é uma contagem de Poisson, e os erros de máxima verossimilhança pura, que supõem variância igual à média, dependem da unidade de medida: a mesma série medida em empregos ou em milhares de empregos leva a conclusões de significância diferentes. Os erros quase-Poisson não têm esse problema e deixam as estimativas pontuais inalteradas; os erros de máxima verossimilhança pura do artigo continuam disponíveis como opção. Segundo, os efeitos regionais são recentrados para média ponderada nula, $\tilde D_r = D_r - \sum_s \omega_s D_s$, com $\omega_s = W_s/\sum_{s'}W_{s'}$ e $W_r$ o emprego-base da região somado nos períodos usados (um na forma estática, $T$ na dinâmica); o erro-padrão de $\tilde D_r$ é calculado para esse contraste a partir da matriz de covariância completa. Terceiro, o efeito regional é convertido em taxa competitiva por período, $e^{\tilde D_r} - 1$, e em empregos, $CE_r = (e^{\tilde D_r} - 1)\,W_r$, na mesma escala dos componentes das Seções 4 a 8. Quando $\hat\phi$ fica muito acima de 1, a correção quase-Poisson amplia os erros-padrão pelo fator $\hat\phi^{1/2}$; o modelo binomial negativo (FLOWERDEW; LOVETT, 1989) é a alternativa que modela a sobredispersão de forma explícita.

**Modelo misto.** Para ilustrar a flexibilidade da Forma II, Knudsen (2000) trata o caso em que interessa uma sub-região (seu exemplo é um condado de Maryland avaliado frente à economia dos Estados Unidos). Nos modelos tabulares, a significância dos parâmetros depende da variação em torno da média da própria tabela, o que obrigaria a incluir na análise todas as unidades da economia de referência. A solução proposta é tomar a informação nacional das margens da tabela maior e introduzi-la como variável contínua exógena: com $N_i$ o emprego nacional no setor $i$, o modelo calibrado é $\ln(E_{1,ri}/E_{0,ri}) = \ln N_i + A + O_i + \ln F_{ri}$ (equação 23), e seu análogo ANOVA é $g_{ri} = a + n_i + B_i + e_{ri}$ (equação 24). Esse modelo não é implementado no projeto nem ilustrado nesta nota.

### 10.3 Aplicação

A Tabela 15 estima a forma estática (Equações 13 e 15) sobre o mesmo painel de 15 observações das Tabelas 1 e 2, com Bahia (a região "neutra" do exemplo) e Agropecuária como categorias de referência, isto é, como os níveis *aliased* de cada dimensão. Para manter a comparação com o artigo, os erros-padrão da tabela são os de máxima verossimilhança pura, com dispersão fixada em 1.

**Tabela 15 — Forma informacional estática de Knudsen (Equações 13 e 15): coeficientes, erro-padrão e teste de Wald**

| Termo | Coeficiente ($\hat D_r$ ou $\hat O_i$) | Erro-padrão | $z$ | valor-*p* |
|:---|---:|---:|---:|---:|
| Intercepto ($A$, referência BA×AGR) | 0,0490 | 0,040 | 1,22 | 0,222 |
| Região: PI (rel. a BA) | 0,0388 | 0,049 | 0,79 | 0,427 |
| Região: CE (rel. a BA) | 0,0277 | 0,042 | 0,66 | 0,507 |
| Região: MA (rel. a BA) | −0,0426 | 0,053 | −0,81 | 0,420 |
| Região: PE (rel. a BA) | −0,0126 | 0,040 | −0,31 | 0,754 |
| Setor: IND (rel. a AGR) | 0,1065 | 0,045 | 2,39 | 0,017 |
| Setor: SER (rel. a AGR) | 0,2048 | 0,038 | 5,32 | 0,000 |

Fonte: elaboração própria, Equações 13 e 15, GLM Poisson com *offset* $\ln E_{0,ri}$ e erros-padrão de máxima verossimilhança pura, 15 observações, 8 graus de liberdade residuais. *Deviance*/g.l. = 0,49; PNMD = 0,90.

A razão *deviance*/g.l. de 0,49, e a dispersão de Pearson de valor semelhante ($\hat\phi \approx 0{,}50$), não indicam sobredispersão neste painel. Com os erros quase-Poisson que a implementação usa por padrão, os erros-padrão da Tabela 15 seriam multiplicados por $\hat\phi^{1/2} \approx 0{,}70$, e nenhuma conclusão mudaria: os efeitos regionais continuam não significativos a 5%, e os dois efeitos setoriais continuam significativos.

O primeiro resultado notável não está nos efeitos de região, mas nos de setor. Na Seção 9, os coeficientes setoriais da Forma I foram usados apenas como médias amostrais, sem teste; a Forma II testa formalmente a composição setorial e a rejeita como nula com folga (Indústria: $p=0,017$; Serviços: $p<0,001$). O componente de composição setorial deste exemplo não é apenas numericamente grande: é estatisticamente bem determinado, ao contrário do componente competitivo, discutido a seguir. O padrão lembra o resultado empírico de Knudsen (2000), em que a forma informacional discriminou melhor os parâmetros setoriais do que a ANOVA.

Os efeitos de região reproduzem a conclusão substantiva da Seção 9: nenhuma região diverge de forma estatisticamente significativa da região de referência ao nível de 5%, e o Maranhão tem o coeficiente mais negativo do conjunto ($-0,0426$), embora com $p=0,420$, distante do limiar. A recentragem ponderada da implementação (Seção 10.2) mudaria o nível desses efeitos, porque subtrai a mesma constante de todos os $\hat D_r$, mas não as diferenças entre regiões nem sua ordenação. A Tabela 16 compara diretamente as duas formas.

**Tabela 16 — Comparação Forma I (ANOVA) versus Forma II (teoria da informação): efeito regional e significância**

| Região | Forma I: $\bar u_r$ (Tabela 11) | Forma I: valor-*p* | Forma II: $\hat D_r$ (rel. a BA) | Forma II: valor-*p* |
|:---|---:|---:|---:|---:|
| PI | 0,0253 | 0,459 | 0,0388 | 0,427 |
| CE | 0,0343 | 0,319 | 0,0277 | 0,507 |
| MA | −0,0562 | 0,115 | −0,0426 | 0,420 |
| BA | −0,0067 | 0,842 | (referência) | — |
| PE | 0,0033 | 0,921 | −0,0126 | 0,754 |

Fonte: elaboração própria, Tabela 11 e Tabela 15.

As duas formas não são diretamente comparáveis célula a célula. A Forma I deixa a região no termo de erro e reporta o desvio médio de cada região em relação às médias setoriais não ponderadas, em unidades de taxa; a Forma II reporta um coeficiente log-multiplicativo relativo à Bahia. A comparação que o próprio Knudsen (2000) faz entre parâmetros regionais usa a ANOVA com efeito de região explícito (sua equação 5) frente à equação 18. Ainda assim, as duas formas concordam no essencial: Piauí e Ceará ficam acima da Bahia, o Maranhão é sempre o mais negativo, e nenhuma região é estatisticamente distinguível de zero, ou da referência, a 5%. Elas divergem nas posições intermediárias: o Ceará supera o Piauí na Forma I e fica atrás dele na Forma II, e Pernambuco fica acima da Bahia na Forma I e abaixo dela na Forma II.

Essa concordância parcial não deve ser generalizada. Na Poisson, a variância cresce com a média, de modo que as células com mais emprego pesam mais sem que seja preciso escolher pesos, ponderação que na Forma I precisa ser imposta por mínimos quadrados ponderados. Por isso, as duas formas tendem a divergir mais em painéis com heterogeneidade de escala pronunciada entre células região-setor (células de emprego-base muito pequeno ao lado de células muito grandes), situação em que a Forma I sem ponderação pode subestimar a incerteza nas células pequenas e superestimá-la nas grandes. Em painéis reais, a dispersão $\hat\phi$ deve ser verificada antes de reportar os testes da Forma II.

## 11 SHIFT-SHARE ESPACIAL: NAZARA-HEWINGS (2004)

### 11.1 Justificativa

Todas as reformulações anteriores tratam cada região como uma unidade isolada. Nazara e Hewings (2004) argumentaram que essa suposição é implausível quando regiões vizinhas compartilham mercados de trabalho, cadeias de fornecimento ou efeitos de transbordamento (*spillover*) — o desempenho competitivo de uma região pode estar sistematicamente correlacionado com o de suas vizinhas, positiva ou negativamente. A proposta foi incorporar uma matriz de pesos espaciais à decomposição, criando uma taxonomia de vinte estruturas de decomposição possíveis conforme o componente considerado "local" ou "vizinho".

### 11.2 Formalização

Seja $w_{rs}$ o elemento da matriz de pesos espaciais $W$ — aqui, contiguidade de fronteira terrestre entre as unidades federativas, padronizada em linha ($\sum_s w_{rs}=1$ para toda região $r$ com ao menos um vizinho). Define-se a **taxa competitiva** regional (para distinguir do efeito competitivo em nível, $CE_r$, que depende da escala de emprego da região):

$$ c_r = \frac{CE_r}{E_{0,r\bullet}} \tag{9} $$

O componente espacial central da abordagem de Nazara-Hewings é a **defasagem espacial** da taxa competitiva — a média (ponderada pela contiguidade) da taxa competitiva das regiões vizinhas:

$$ (Wc)_r = \sum_{s} w_{rs}\,c_s \tag{10} $$

A diferença $c_r - (Wc)_r$ indica se a região tem desempenho competitivo destoante de sua vizinhança imediata (positiva: melhor que os vizinhos; negativa: pior). Para testar se essa dependência espacial é sistemática — e não um artefato de amostra pequena —, calcula-se o **I de Moran global** sobre as taxas competitivas (nunca sobre o emprego em nível, cuja heterogeneidade de escala entre regiões mascara inteiramente o padrão espacial):

$$ I = \frac{n}{S_0}\cdot\frac{z'Wz}{z'z}, \qquad z_r = c_r - \bar c, \qquad S_0=\sum_r\sum_s w_{rs} \tag{11} $$

com valor esperado sob a hipótese nula de aleatoriedade espacial $E[I]=-1/(n-1)$. Valores de $I$ acima de $E[I]$ indicam autocorrelação espacial positiva (regiões vizinhas com taxas competitivas parecidas); valores abaixo indicam autocorrelação negativa (vizinhos dissimilares).

### 11.3 Aplicação

A malha de contiguidade das cinco regiões deste exemplo segue as fronteiras terrestres reais entre as unidades federativas: Piauí faz fronteira com as quatro demais (Ceará, Maranhão, Bahia e Pernambuco), Ceará e Pernambuco fazem fronteira entre si, e Bahia e Pernambuco também. Maranhão e Bahia, apesar de ambos vizinhos do Piauí, não fazem fronteira uma com a outra. A Tabela 12 apresenta a matriz padronizada em linha.

**Tabela 12 — Matriz de pesos espaciais $W$ (contiguidade de fronteira, padronizada em linha)**

| | PI | CE | MA | BA | PE |
|:---|---:|---:|---:|---:|---:|
| PI | 0,000 | 0,250 | 0,250 | 0,250 | 0,250 |
| CE | 0,500 | 0,000 | 0,000 | 0,000 | 0,500 |
| MA | 1,000 | 0,000 | 0,000 | 0,000 | 0,000 |
| BA | 0,500 | 0,000 | 0,000 | 0,000 | 0,500 |
| PE | 0,333 | 0,333 | 0,000 | 0,333 | 0,000 |

Fonte: elaboração própria a partir de fronteiras terrestres reais entre as cinco unidades federativas (subconjunto ilustrativo; ver Seção 14).

**Tabela 13 — Taxa competitiva local, defasagem espacial e hiato (Equações 9–10)**

| Região | $c_r$ (taxa competitiva local) | $(Wc)_r$ (média dos vizinhos) | Hiato $c_r-(Wc)_r$ |
|:---|---:|---:|---:|
| PI | 4,33% | −1,12% | 5,45 p.p. |
| CE | 3,01% | 1,20% | 1,81 p.p. |
| MA | −5,17% | 4,33% | −9,50 p.p. |
| BA | −0,38% | 1,20% | −1,58 p.p. |
| PE | −1,93% | 2,32% | −4,25 p.p. |

Fonte: elaboração própria, Equações 9 e 10.

O caso do Maranhão é o mais informativo: sua taxa competitiva local é a mais negativa do conjunto (−5,17%), mas seu único vizinho na malha, o Piauí, tem a taxa mais positiva (4,33%) — um hiato de −9,5 pontos percentuais em relação à própria vizinhança. Isso é o oposto do padrão que a hipótese de *spillover* positivo prediria (vizinhos com desempenho parecido) e resulta, para este pequeno conjunto de cinco regiões, em um I de Moran global de $I=-0{,}4852$, abaixo do valor esperado sob aleatoriedade $E[I]=-0{,}25$ — um sinal de dissimilaridade, e não de agrupamento espacial positivo, entre vizinhos. Como discutido na Seção 14, um I de Moran com apenas cinco unidades tem poder estatístico praticamente nulo; o valor é reportado aqui unicamente para ilustrar o cálculo da Equação 11, não como evidência substantiva de dependência espacial.

## 12 SÍNTESE: A LÓGICA DA EVOLUÇÃO METODOLÓGICA

O Quadro 1 resume, para cada variante tratada, qual falha da variante anterior ela ataca e o que permanece em aberto depois dela — a mesma lógica de "problema → correção → novo limite" que estruturou as Seções 4 a 11.

**Quadro 1 — Evolução dos componentes da SSA: problema atacado e limite remanescente**

| Variante | Problema que ataca | Mudança estrutural | Limite remanescente |
|:---|:---|:---|:---|
| Dunn (1960) — clássico | (linha de base) | Identidade aditiva de 3 componentes | Efeito competitivo contaminado por estrutura; sem inferência |
| Fuchs (1959) / pesos terminais | Viés do ano de ponderação | Média ou reversão de pesos | Sensibilidade permanece no efeito de alocação (Seção 6) |
| Esteban-Marquillas (1972) | Contaminação estrutural do efeito competitivo | Emprego homotético; efeito de alocação | Sinal de $AE$ sensível à escolha de pesos (Herzog-Olsen, 1977) |
| Arcelus (1984) | Homotetização restrita ao efeito competitivo | Extensão a todos os componentes | Dois dos quatro novos subcomponentes são nulos por construção ao nível regional (Seção 7.3) |
| Barff-Knight (1988) | Viés de ponto-a-ponto e crescimento composto | Soma de decomposições anuais/subperiódicas | Ainda determinístico; exige dados de alta frequência |
| Berzeg (1978, 1984) | Impossibilidade de teste estatístico | Identidade recastada como ANOVA/regressão | Pressupõe normalidade; erro absorve toda variação não sistemática |
| Knudsen (2000) | ANOVA heterocedástica, que depende de pesos impostos para reproduzir a identidade | *Shift-share* de mínima informação discriminante: modelo log-linear estimado por máxima verossimilhança (GLM de Poisson com *offset* pelo emprego-base) | Parâmetros em escala log, de interpretação mais difícil; erros de máxima verossimilhança pura exigem correção de dispersão (quase-Poisson) |
| Nazara-Hewings (2004) | Regiões tratadas como independentes | Matriz de pesos espaciais; defasagem espacial | Sensível à especificação da matriz; exige N grande para inferência confiável |

Fonte: elaboração própria, síntese das Seções 4 a 11.

## 13 QUADRO DE PARÂMETROS CONSOLIDADOS

| Parâmetro | Valor adotado |
|:---|:---|
| Número de regiões no exemplo (*R*) | 5 (PI, CE, MA, BA, PE) |
| Número de setores no exemplo (*N*) | 3 (Agropecuária, Indústria, Serviços) |
| Natureza dos dados de emprego | Sintéticos/hipotéticos, não correspondem a estatísticas oficiais |
| Ano-base / ano-terminal | $t_0$ / $t_1$ genéricos (rótulos hipotéticos, sem correspondência calendárica) |
| Número de subperíodos na decomposição dinâmica (Seção 8) | 2, com trajetória setorial hipotética e deliberadamente desigual entre subperíodos |
| Especificação da regressão de Berzeg (Seção 9) | Mínimos quadrados ordinários, conjunto completo de *dummies* de setor, sem ponderação por emprego |
| Nível de significância de referência (Seção 9) | 5% |
| Graus de liberdade da regressão de Berzeg | $n-k = 15-3 = 12$ |
| Especificação do modelo de Knudsen (Seção 10) | Forma estática (equação 18 de Knudsen, 2000): GLM Poisson, ligação log, *offset* $\ln E_{0,ri}$, categorias de referência BA (região) e AGR (setor) |
| Erros-padrão do modelo de Knudsen (Seção 10) | Máxima verossimilhança pura na Tabela 15; quase-Poisson ($\hat\phi$ = qui-quadrado de Pearson/g.l.) por padrão na implementação |
| Diagnóstico de dispersão (Seção 10) | $\hat\phi \gg 1$ indica sobredispersão; modelo binomial negativo como alternativa |
| Critério de vizinhança espacial (Seção 11) | Contiguidade de fronteira terrestre real entre as 5 unidades federativas, padronizada em linha |
| Base de cálculo do I de Moran (Seção 11) | Taxa competitiva $c_r=CE_r/E_{0,r\bullet}$, nunca o emprego em nível |

## 14 LIMITAÇÕES

**Escala do exemplo numérico.** Cinco regiões e três setores foram escolhidos exclusivamente por clareza expositiva — o quadro é pequeno demais para qualquer inferência estatística com poder adequado. Os testes *t* e de Wald das Seções 9 e 10, e o I de Moran da Seção 11, devem ser lidos como demonstrações do cálculo, não como evidência substantiva; com $n=5$, o I de Moran em particular tem variância amostral elevada e não deve ser interpretado como teste confiável de dependência espacial.

**Dados inteiramente sintéticos.** Nenhum valor de emprego neste documento corresponde a estatística oficial de Piauí, Ceará, Maranhão, Bahia ou Pernambuco — os nomes das unidades federativas foram usados apenas para ancorar a matriz de contiguidade espacial (Seção 11) em fronteiras reais, não para descrever essas economias.

**Trajetória do exemplo dinâmico é arbitrária.** A divisão em dois subperíodos e a distribuição de crescimento setorial entre eles (Seção 8) foram escolhidas para exibir divergência entre a forma dinâmica e a estática, não estimadas a partir de nenhum processo real; a magnitude da divergência em uma aplicação empírica dependerá inteiramente da volatilidade e do comprimento do período analisado, como já advertiam Barff e Knight (1988).

**Extensão de Arcelus II não formalizada numericamente.** O segundo modelo de Arcelus (1984), com efeitos de crescimento e composição regionais endógenos, é descrito apenas conceitualmente na Seção 7.3: a fonte primária do artigo original não foi consultada diretamente para esta nota, e uma reconstrução algébrica não verificada correria o risco de atribuir a Arcelus uma formulação que não é exatamente a sua. Recomenda-se, antes de qualquer uso formal dessa extensão, a consulta direta a Arcelus (1984), *Growth and Change* 15(1), pp. 3–8.

**Adaptações ao modelo de Knudsen (2000).** A Seção 10 foi conferida com o texto integral do artigo, e as equações que ela cita (4 a 6, 7 a 19 e 20 a 24) seguem a numeração do original. Três elementos não vêm do artigo, mas da implementação de referência do projeto: os erros-padrão quase-Poisson usados por padrão, a recentragem de $D_r$ para média ponderada nula e a conversão $(e^{D_r}-1)\,W_r$ em empregos. O artigo também não discute sobredispersão; a menção ao modelo binomial negativo vem de Flowerdew e Lovett (1989). A relação entre os parâmetros das Formas I e II segue a leitura $B_i = e^{O_i} - 1$, que difere da forma impressa no artigo, e o próprio autor não a encontrou com precisão nos dados (Seção 10.2). Por fim, o modelo misto com variável exógena contínua (equações 20 a 24) é apenas descrito, sem implementação nem exemplo numérico, e a forma dinâmica (equação 19) é formalizada mas não aplicada ao exemplo, cujas trajetórias de subperíodo da Seção 8 são hipotéticas.

**Matriz de contiguidade reduzida.** A malha espacial da Seção 11 usa apenas cinco das 26 unidades federativas mais o Distrito Federal — um subconjunto ilustrativo, não a matriz de contiguidade completa da federação brasileira (que integra o código computacional do projeto mais amplo do qual esta nota deriva). Padrões de dependência espacial identificados em um subconjunto de cinco regiões não são generalizáveis à matriz completa.

**Sensibilidade a escolha não neutra de pesos.** Como demonstrado na Seção 5 e na Seção 6.3, tanto o efeito competitivo clássico quanto — de forma mais acentuada, e inclusive com inversão de sinal — o efeito de alocação de Esteban-Marquillas são sensíveis à escolha do ano de ponderação. Essa sensibilidade é uma propriedade do método, não um artefato deste exemplo específico, e já havia sido documentada empiricamente por Herzog e Olsen (1977) em dados reais das regiões do U.S. Bureau of Economic Analysis.

## REFERÊNCIAS

ARCELUS, Francisco J. An extension of shift-share analysis. **Growth and Change**, v. 15, n. 1, p. 3-8, 1984.

BARFF, Richard A.; KNIGHT, Prentice L. Dynamic shift-share analysis. **Growth and Change**, v. 19, n. 2, p. 1-10, 1988.

BERZEG, Korkut. The empirical content of shift-share analysis. **Journal of Regional Science**, v. 18, n. 3, p. 463-469, 1978.

BERZEG, Korkut. A note on statistical approaches to shift-share analysis. **Journal of Regional Science**, v. 24, n. 2, p. 277-285, 1984.

DUNN, Edgar S. A statistical and analytical technique for regional analysis. **Papers of the Regional Science Association**, v. 6, p. 97-112, 1960.

ESTEBAN-MARQUILLAS, Joan M. A reinterpretation of shift-share analysis. **Regional and Urban Economics**, v. 2, n. 3, p. 249-255, 1972.

FLOWERDEW, Robin; LOVETT, Andrew. Compound and generalized Poisson models for interurban migration. In: CONGDON, Peter; BATEY, Peter (org.). **Advances in Regional Demography**. London: Belhaven Press, 1989. p. 246-256.

FUCHS, Victor R. Changes in the location of US manufacturing since 1929. **Journal of Regional Science**, v. 1, n. 2, p. 1-17, 1959.

HAYNES, Kingsley E.; MACHUNDA, Z. B. Considerations in extending shift-share analysis: note. **Growth and Change**, v. 18, n. 2, p. 69-78, 1987.

HERZOG, Henry W.; OLSEN, Richard J. Shift-share analysis revisited: the allocation effect and the stability of regional structure. **Journal of Regional Science**, v. 17, n. 3, p. 441-454, 1977.

HOUSTON, David B. The shift and share analysis of regional growth: a critique. **Southern Economic Journal**, v. 33, p. 577-581, 1967.

KEIL, Stanley R. On the value of homotheticity in the shift-share framework. **Growth and Change**, v. 23, n. 4, p. 469-493, 1992.

KNUDSEN, Daniel C. Generalizing Poisson regression: including a priori information using the method of offsets. **The Professional Geographer**, v. 44, p. 202-208, 1992.

KNUDSEN, Daniel C. Shift-share analysis: further examination of models for the description of economic change. **Socio-Economic Planning Sciences**, v. 34, n. 3, p. 177-198, 2000.

KNUDSEN, Daniel C.; BARFF, Richard. Shift-share analysis as a linear model. **Environment and Planning A**, v. 23, n. 3, p. 421-431, 1991.

KULLBACK, Solomon; LEIBLER, Richard A. On information and sufficiency. **The Annals of Mathematical Statistics**, v. 22, n. 1, p. 79-86, 1951.

LOVETT, Andrew; FLOWERDEW, Robin. Analysis of count data using Poisson regression. **Professional Geographer**, v. 41, n. 2, p. 190-198, 1989.

LOVERIDGE, Scott; SELTING, Anne C. A review and comparison of shift-share identities. **International Regional Science Review**, v. 21, n. 1, p. 37-58, 1998.

MCCULLAGH, Peter; NELDER, John A. **Generalized linear models**. London: Chapman and Hall, 1983.

NAZARA, Suahasil; HEWINGS, Geoffrey J. D. Spatial structure and taxonomy of decomposition in shift-share analysis. **Growth and Change**, v. 35, n. 4, p. 476-490, 2004.

PERLOFF, Harvey S.; DUNN, Edgar S.; LAMPARD, Eric E.; MUTH, Richard F. **Regions, resources, and economic growth**. Baltimore: Johns Hopkins University Press, 1960.

ROSENFELD, Stephen S. *(referência a ser completada conforme a fonte primária)*.

SELTING, Anne C.; LOVERIDGE, Scott. **A summary of the literature on shift-share analysis**. Regional Research Institute, West Virginia University, 1992.

---

*Nota de transparência: este documento formaliza a extensão de Arcelus (1984) apenas para os componentes de crescimento nacional e composição setorial (Equação 5, Seção 7); o segundo modelo do mesmo autor (Arcelus II, com efeitos regionais endógenos) não foi verificado contra a fonte primária e é descrito apenas conceitualmente. A Seção 10 foi revisada com base no texto integral de Knudsen (2000): as equações do artigo são citadas pela numeração original, e as adaptações da implementação de referência (erros quase-Poisson, recentragem ponderada de $D_r$ e conversão em empregos) estão identificadas como tais na Seção 10.2 e na Seção 14. A referência a Rosenfeld (1959), citada na literatura secundária como um dos primeiros a apontar o defeito do efeito competitivo clássico, não pôde ser completada com periódico, volume e página exatos e é sinalizada como incompleta na lista de referências, em vez de inventada. Todos os valores numéricos das Tabelas 1 a 16 são sintéticos e devem ser validados como tal antes de qualquer circulação do documento; as medidas de ajuste citadas na Seção 10.1 são as reportadas por Knudsen (2000) para dados reais dos Estados Unidos.*
