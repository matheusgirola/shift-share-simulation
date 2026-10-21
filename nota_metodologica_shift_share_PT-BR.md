# NOTA METODOLÓGICA: A EVOLUÇÃO DOS MÉTODOS DE ANÁLISE *SHIFT-SHARE* (SSA)

**Resumo** — Este documento descreve, formaliza e ilustra numericamente a evolução metodológica da análise *shift-share* (SSA), da decomposição clássica de Dunn (1960) às reformulações homotéticas (Esteban-Marquillas, 1972; Arcelus, 1984), à forma dinâmica (Barff-Knight, 1988), às formalizações inferenciais (Berzeg, 1978, 1984) e à extensão espacial (Nazara-Hewings, 2004). Cada etapa é apresentada segundo o ciclo justificar–formalizar–interpretar e ilustrada com um exemplo numérico único, construído com dados sintéticos para cinco regiões e três setores, de modo que o leitor acompanhe como cada fórmula se deriva da anterior e o que cada nova camada de decomposição corrige. Às seções formais segue-se uma aplicação a dados reais — o emprego formal das 27 unidades federativas brasileiras na RAIS de 2022 a 2025 —, cujo resultado central é metodológico: a discordância entre escolhas igualmente defensáveis do analista (tratamento de quebras de série, ano de ponderação, nível de agregação setorial) é de uma ordem de magnitude superior à diferença entre as variantes do método, de modo que o efeito competitivo de uma região, e sua posição em um ordenamento, são em parte decididos por quem calcula.
**Palavras-chave:** *Shift-share analysis*. Decomposição de crescimento regional. Efeito competitivo. Efeito alocação. *Shift-share* espacial. Robustez metodológica. RAIS.

## 1 INTRODUÇÃO

A análise *shift-share* (SSA) é, desde sua formulação original, uma identidade contábil que reparte a variação do emprego regional em componentes atribuíveis ao crescimento nacional, à composição setorial da região e a um resíduo dito "competitivo". Como observam Loveridge e Selting (1998), "SSA é apenas uma identidade contábil praticável: nunca pretendeu ser uma teoria" — afirmação que orienta toda a leitura deste documento. Se a SSA não é um modelo causal, o valor de cada variante está em quão bem ela isola, do resíduo, os efeitos que não deveriam nele estar: a estrutura setorial da região, o viés de ponderação temporal, a ausência de significância estatística e, mais recentemente, a dependência espacial entre regiões vizinhas.

Este documento cobre a fundamentação teórica de cada camada de reformulação, a formalização matemática associada e a tradução de cada fórmula para um exemplo numérico único e recorrente. Ele não cobre a implementação computacional das rotinas (tratada em código separado), nem pretende ser uma revisão exaustiva da literatura — para isso, ver o levantamento bibliográfico que fundamenta esta nota. O objetivo das Seções 4 a 11 é estritamente pedagógico-metodológico: mostrar, com números, *por que* cada variante surgiu e *o que* ela corrige na anterior. A Seção 12 fecha o documento com a contraprova em dados reais: aplicadas ao emprego formal das 27 unidades federativas brasileiras na RAIS de 2022 a 2025, as catorze variantes implementadas produzem para São Paulo efeitos competitivos que vão de −23,6 mil a +212,6 mil vínculos, e posições no ordenamento nacional que vão da 1ª à 24ª entre 27 — sem que nenhuma dessas estimativas seja indefensável à luz da literatura. A leitura que se pretende transmitir é, portanto, dupla: cada camada de reformulação corrige um defeito real, e nenhuma delas protege o resultado das escolhas discricionárias de quem o calcula.

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

**Tabela 8 — Arcelus I (Equação 5): totais regionais**

| Região | $EN_r$ | $DN_r$ | $EM_r$ | $DM_r$ | $CE^{*}_r$ | $AE_r$ |
|:---|---:|---:|---:|---:|---:|---:|
| PI | 101,96 | 0,00 | 0,00 | −9,62 | 22,99 | −1,33 |
| CE | 163,14 | 0,00 | 0,00 | 8,79 | 22,35 | 1,72 |
| MA | 91,77 | 0,00 | 0,00 | −16,52 | −23,80 | 0,55 |
| BA | 230,44 | 0,00 | 0,00 | 0,85 | −3,72 | −0,57 |
| PE | 191,69 | 0,00 | 0,00 | 16,49 | −8,35 | −9,83 |

Fonte: elaboração própria, Equação 5.

Em outras palavras: ao nível regional agregado (a soma sobre setores), a homotetização de $NE$ e $IM$ não produz informação nova — $EN_r$ reproduz $NE_r$ e $DM_r$ reproduz $IM_r$ da Tabela 4, célula a célula. O ganho analítico da homotetização, como Esteban-Marquillas já havia percebido, está concentrado no efeito competitivo, onde $(g_{ri}-g_{ni})$ varia célula a célula e não se anula ao somar. Esse resultado algébrico é consistente com — e ajuda a explicar — o achado empírico de Keil (1992), que, usando dados de Indiana (1977–1986), concluiu que as extensões homotéticas de Esteban-Marquillas e Arcelus "lançam pouca luz sobre o crescimento regional total" mesmo quando esclarecem taxas de indústrias individuais: o próprio arcabouço algébrico garante que dois dos quatro novos subcomponentes de Arcelus sejam nulos quando agregados por região. Arcelus (1984) propôs ainda um segundo modelo (Arcelus II), que não parte do emprego homotético, mas da taxa de crescimento *da própria região* como referência adicional; é a variante formalizada na Seção 7.4.

### 7.4 Arcelus II: deslocamento regional e deslocamento diferencial

O segundo modelo de Arcelus (1984) ataca um problema diferente do da Seção 7.2. Ali, a referência contra a qual cada célula é avaliada continua sendo nacional, e o que muda é o ponderador, substituído pelo emprego homotético. Aqui, o que muda é a própria referência: parte do desempenho de uma célula pode decorrer de a região inteira estar crescendo acima ou abaixo do país, e não de uma vantagem no setor $i$ especificamente. O modelo separa esses dois níveis, acrescentando à identidade de Dunn um **deslocamento regional** e um **deslocamento diferencial**, medido contra a taxa da própria região.

Seja $g_r = (\sum_i E_{1,ri} - \sum_i E_{0,ri})/\sum_i E_{0,ri}$ a taxa de crescimento agregada da região $r$. A identidade passa a ter quatro termos:

$$ \Delta E_{ri} = \underbrace{E_{0,ri}\,g_n}_{n_{ri}} + \underbrace{E_{0,ri}\,(g_{ni}-g_n)}_{s_{ri}} + \underbrace{E_{0,ri}\,(g_r-g_n)}_{r_{ri}} + \underbrace{E_{0,ri}\,\big[(g_{ri}-g_r)-(g_{ni}-g_n)\big]}_{d_{ri}} \tag{6} $$

em que $n_{ri}$ e $s_{ri}$ são o crescimento nacional e a composição setorial da Equação 1, inalterados; $r_{ri}$ é o **deslocamento regional**, o quanto a célula se move por a região como um todo crescer acima ou abaixo do país; e $d_{ri}$ é o **deslocamento diferencial**, o quanto o setor $i$ se destaca *dentro* da região, líquido do que esse mesmo setor se destaca dentro do país. A soma dos quatro termos recupera $E_{0,ri}\,g_{ri} = \Delta E_{ri}$: os termos $g_n$, $g_{ni}$ e $g_r$ se cancelam dois a dois, e a identidade fecha à precisão de máquina, como a de Dunn.

A relação com as Seções 4 e 7.2 é direta e vale célula a célula:

$$ r_{ri} + d_{ri} = E_{0,ri}\,(g_{ri}-g_{ni}) = CE_{ri} \tag{7} $$

Ou seja: **Arcelus II é uma partição do efeito competitivo de Dunn**, que ele reparte entre um componente de desempenho da região inteira e um componente de desempenho setorial líquido. Arcelus I, por contraste, não toca no competitivo total — ele repondera os componentes nacional e de composição pelo emprego homotético. São dois objetos distintos, e a confusão entre eles tem consequência prática, discutida na Seção 10.1: a "extensão de Arcelus" a que Knudsen (2000) recorre para construir suas formas probabilísticas é esta, a da Equação 6, não a da Equação 5.

Somando a Equação 6 sobre os setores de uma mesma região, emerge uma propriedade algébrica análoga à da Seção 7.3, e igualmente desfavorável à extensão. Como $g_r$ é, por construção, a taxa que reproduz o total da região, vale $\sum_i E_{0,ri}(g_{ri}-g_r) \equiv 0$, e portanto:

$$ d_r \equiv -\,IM_r, \qquad r_r \equiv IM_r + CE_r, \qquad \sum_r r_r \equiv 0 \tag{8} $$

para qualquer conjunto de dados. Ao nível regional agregado, portanto, o deslocamento diferencial não é informação nova: é o efeito de composição setorial da Tabela 4 com o sinal trocado. E o deslocamento regional é a soma dos efeitos de composição e competitivo, isto é, todo o desvio da região em relação ao crescimento nacional. A Tabela 9 confirma as três identidades numericamente. A consequência prática aparece na simulação de 27 unidades federativas do projeto, cujo processo gerador constrói a taxa competitiva como $c_{ri} = \bar c_r + d_{ri}$ e portanto oferece gabarito separado para os dois deslocamentos: o deslocamento regional estimado recupera a vantagem verdadeira da região com correlação de 0,84, enquanto o diferencial, somado por região, tem correlação de −0,20, nRMSE de 1,16 e sinal correto em 44% das unidades — desempenho pior que o de chutar a média, exatamente como a identidade $d_r \equiv -IM_r$ prevê.

**Tabela 9 — Arcelus II (Equação 6): totais regionais**

| Região | $n_r$ | $s_r$ | $r_r$ | $d_r$ | $r_r+d_r$ | $CE_r$ (Tab. 4) |
|:---|---:|---:|---:|---:|---:|---:|
| PI | 101,96 | −9,62 | 12,04 | 9,62 | 21,65 | 21,65 |
| CE | 163,14 | 8,79 | 32,86 | −8,79 | 24,07 | 24,07 |
| MA | 91,77 | −16,52 | −39,77 | 16,52 | −23,25 | −23,25 |
| BA | 230,44 | 0,85 | −3,44 | −0,85 | −4,29 | −4,29 |
| PE | 191,69 | 16,49 | −1,69 | −16,49 | −18,18 | −18,18 |

Fonte: elaboração própria, Equação 6 aplicada às Tabelas 1–3.

A leitura substantiva, ainda assim, difere da de Dunn. Piauí e Ceará têm efeitos competitivos quase iguais (21,65 e 24,07), mas Arcelus II mostra que eles vêm de fontes opostas: no Ceará, o deslocamento regional (32,86) mais do que explica o total, e o diferencial o puxa para baixo (−8,79) — é um estado crescendo acima do país em bloco, não por um setor; no Piauí, o deslocamento regional é modesto (12,04) e quase metade do resultado é deslocamento diferencial (9,62), concentrado em serviços. Maranhão é o inverso simétrico do Ceará: um deslocamento regional fortemente negativo (−39,77) parcialmente compensado por um diferencial positivo. Essa é exatamente a distinção que a Seção 4 apontou como ausente no $CE_r$ de Dunn — e que Esteban-Marquillas responde por outro caminho, o da especialização.

**Procedência da formalização.** O artigo original de Arcelus (1984) não foi consultado diretamente. A Equação 6 reproduz as equações 2, 2a, 2b e 2c de Knudsen (2000, p. 179), que apresenta essa identidade de quatro termos como "a extensão de Arcelus" e a credita a Arcelus (1984, *Growth and Change* 15:3–8) na referência [23] de sua lista. Trata-se, portanto, de uma fonte secundária, mas com a álgebra explícita e verificável — e verificada aqui, pelo fechamento da identidade e pelas três propriedades da Equação 8. Duas ressalvas. Primeira: as equações 1a–1c e 2a–2b aparecem impressas em Knudsen (2000) com $\acute{E}^{\,r}_i$, o emprego do **ano terminal**, como ponderador; com esses pesos a soma dos componentes dá $E_{1,ri}\,g_{ri}$, e não $\Delta E_{ri}$, de modo que a identidade não fecha. Esta nota adota $E_{0,ri}$, coerente com a Equação 1 e com a prática corrente. Segunda: Arcelus (1984) descreve seu segundo modelo em termos de efeitos de crescimento e de composição *regionais*; a correspondência desses nomes com $r_{ri}$ e $d_{ri}$ é a leitura natural da álgebra, mas não foi conferida contra a nomenclatura do original. Antes de qualquer uso formal, recomenda-se a consulta direta à fonte primária.

## 8 SHIFT-SHARE DINÂMICO: BARFF-KNIGHT (1988)

### 8.1 Justificativa

Todas as decomposições até aqui são "estáticas comparativas": comparam apenas os pontos $t_0$ e $t_1$, ignorando a trajetória entre eles. Barff e Knight (1988), retomando uma sugestão de Thirlwall (1967) de particionar o período em subperíodos, argumentaram que essa comparação de extremos é distorcida por crescimento composto e por mudanças na composição setorial *durante* o intervalo — um setor pode crescer rapidamente no início do período e desacelerar no fim (ou vice-versa) sem que a taxa ponta a ponta capture essa dinâmica.

### 8.2 Formalização

Particiona-se o intervalo $[t_0,t_1]$ em $K$ subperíodos. Para cada subperíodo $k$, calcula-se a decomposição clássica (Equação 1) usando o emprego do início do subperíodo como peso-base; o efeito competitivo dinâmico é a soma dos efeitos competitivos de cada subperíodo:

$$ CE^{\text{din}}_{ri} = \sum_{k=1}^{K} E_{k-1,ri}\left(g^{(k)}_{ri}-g^{(k)}_{ni}\right) \tag{9} $$

em que $g^{(k)}_{ri}$ e $g^{(k)}_{ni}$ são as taxas regional-setorial e nacional-setorial calculadas apenas dentro do subperíodo $k$, com peso-base $E_{k-1,ri}$ (o emprego no início daquele subperíodo, não o do início do período total). Compara-se $CE^{\text{din}}_{ri}$ ao efeito competitivo estático $CE^{\text{est}}_{ri}$ (Equação 1, aplicada diretamente a $t_0$ e $t_1$) para medir a magnitude da distorção de trajetória.

### 8.3 Aplicação

Para ilustrar, o intervalo $[t_0,t_1]$ foi dividido em dois subperíodos ($K=2$) com uma trajetória setorial deliberadamente desigual — crescimento industrial concentrado no primeiro subperíodo e crescimento de serviços concentrado no segundo, um padrão plausível de transição estrutural. A Tabela 10 compara o efeito competitivo dinâmico (soma dos dois subperíodos, Equação 9) ao estático (Equação 1).

**Tabela 10 — Efeito competitivo: decomposição dinâmica versus estática, totais regionais**

| Região | $CE^{\text{din}}_r$ (soma de 2 subperíodos) | $CE^{\text{est}}_r$ | Diferença |
|:---|---:|---:|---:|
| PI | 23,55 | 25,65 | −2,10 |
| CE | 25,08 | 25,93 | −0,84 |
| MA | −23,96 | −24,97 | 1,01 |
| BA | −4,96 | −4,86 | −0,09 |
| PE | −19,71 | −21,75 | 2,04 |

Fonte: elaboração própria, Equações 1 e 9, com trajetória hipotética de dois subperíodos.

A diferença entre as duas formas não é uniforme entre regiões — nem em magnitude, nem em sinal. Para Piauí e Ceará, a forma estática superestima o efeito competitivo em relação à forma dinâmica (diferenças negativas); para Maranhão e Pernambuco, ocorre o oposto: a forma estática *subestima* o desempenho competitivo real ao concentrar toda a comparação nos dois pontos extremos. Isso confirma, neste exemplo reduzido, a advertência de Barff e Knight (1988): a decomposição ponto a ponto pode inverter o sinal relativo da vantagem competitiva entre regiões dependendo de como a mudança estrutural se distribuiu dentro do intervalo, sobretudo quando o período é longo ou volátil.

## 9 FORMALIZAÇÃO INFERENCIAL: A ANOVA DE BERZEG (1978, 1984)

### 9.1 Justificativa

Como observam Selting e Loveridge (1992), por ser uma identidade determinística, nenhum componente da SSA clássica pode ser testado estatisticamente — não há erro-padrão, não há teste de hipótese, não há forma de dizer se um efeito competitivo de −4,29 (Bahia, Tabela 4) é "significativamente" diferente de zero ou apenas ruído amostral. Berzeg (1978, 1984) forneceu a fundamentação estatística definitiva ao recastar a identidade como um modelo linear de análise de variância (ANOVA), no qual o crescimento nacional é o intercepto, a composição setorial é um coeficiente estimado e o efeito competitivo é o **termo de erro** de uma regressão — passível, sob normalidade dos erros, de teste *t*.

### 9.2 Formalização

Considere a regressão da taxa de crescimento regional-setorial em variáveis binárias (*dummies*) de setor, sem intercepto separado (conjunto completo de *dummies*):

$$ g_{ri} = \sum_{i=1}^{N} \beta_i D_i + u_{ri} \tag{10} $$

em que $D_i$ é uma *dummy* igual a 1 se a observação pertence ao setor $i$ e $\beta_i$, estimado por mínimos quadrados ordinários, é a média amostral de $g_{ri}$ no setor $i$ — o análogo, nesta formulação, do parâmetro de composição setorial $g_{ni}$. O resíduo $u_{ri} = g_{ri}-\hat\beta_i$ é a **taxa competitiva estimada**: sob a hipótese de erros normais e homocedásticos, a razão entre a média de $u_{ri}$ em uma região e seu erro-padrão segue distribuição *t* de Student,

$$ t_r = \frac{\bar{u}_r}{s/\sqrt{n_r}} \tag{11} $$

com $s$ o desvio-padrão residual do modelo (Equação 10) e $n_r$ o número de observações setoriais na região $r$ — permitindo testar $H_0: \bar u_r = 0$, isto é, se a região tem, em média, desempenho competitivo estatisticamente distinguível de zero.

### 9.3 Aplicação

A Tabela 11 mostra a decomposição célula a célula da Equação 10 aplicada ao painel de 15 observações (5 regiões × 3 setores) das Tabelas 1–2. A Tabela 12 aplica o teste da Equação 11 por região.

**Tabela 11 — Regressão de Berzeg: taxa observada, componente de composição estimado e resíduo competitivo**

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

Fonte: elaboração própria, Equação 10, mínimos quadrados ordinários com 15 observações.

**Tabela 12 — Teste *t* do desempenho competitivo médio por região ($H_0: \bar u_r=0$; graus de liberdade = 12)**

| Região | $\bar u_r$ | $t_r$ | valor-*p* |
|:---|---:|---:|---:|
| PI | 0,0253 | 0,7659 | 0,4585 |
| CE | 0,0343 | 1,0393 | 0,3192 |
| MA | −0,0562 | −1,7022 | 0,1145 |
| BA | −0,0067 | −0,2039 | 0,8418 |
| PE | 0,0033 | 0,1008 | 0,9213 |

Fonte: elaboração própria, Equação 11.

Nenhuma região atinge significância convencional de 5% neste exemplo — o mais próximo é o Maranhão, com $t=-1,70$ e valor-*p*=0,11, sugerindo desvantagem competitiva sistemática, mas não conclusiva na amostra. Esse resultado ilustra, mais do que qualquer conclusão substantiva sobre as regiões fictícias, a própria lição metodológica da Seção 9.1: a decomposição clássica (Tabela 4) mostraria o efeito competitivo do Maranhão como um número aparentemente grande e "real" (−23,25), mas a formalização de Berzeg revela que, com apenas três observações setoriais por região, esse número não é estatisticamente distinguível de zero ao nível de 5% — exatamente o tipo de afirmação que a SSA clássica é incapaz de fazer e que o limiar de significância listado no Quadro de Parâmetros Consolidados (Seção 14) torna operacional.

## 10 KNUDSEN (2000): AS DUAS FORMAS PROBABILÍSTICAS, ANOVA E TEORIA DA INFORMAÇÃO

### 10.1 Justificativa

Knudsen (2000) classifica os métodos de SSA em três famílias: os modelos contábeis tradicionais, os modelos de análise de variância (ANOVA) e os modelos de teoria da informação. As duas últimas são as "duas formas probabilísticas" que o artigo apresenta. A primeira é a ANOVA de Berzeg (1978, 1984), que o autor reescreve nas versões simples, com a extensão de Arcelus e dinâmica (equações 4 a 6 do artigo). A segunda é o *shift-share* de teoria da informação, derivado do princípio de mínima informação discriminante (MDI) (equações 7 a 19), ao qual o artigo acrescenta um modelo misto, com variável exógena contínua, para mostrar a flexibilidade da abordagem (equações 20 a 24). A ideia de fundo é ler o problema da SSA como a partição da variação de uma tabela de contingência com três dimensões (setor, região e ano). Assim lida, a SSA é um caso particular da classe de modelos para dados tabulares agregados usada em planejamento, geografia e ciência regional, e passa a admitir testes de hipótese sobre a variação do emprego por região ou setor.

**A "extensão de Arcelus" a que Knudsen se refere, aqui e em todo o artigo, é a identidade de quatro termos da equação 2 — deslocamento regional e deslocamento diferencial —, formalizada na Seção 7.4 desta nota, e não a decomposição homotética da Seção 7.2, que o artigo não utiliza.** A distinção importa porque as duas levam a objetos diferentes: o que a extensão acrescenta às formas probabilísticas é um efeito principal de região ($G_r$ na ANOVA, $D_r$ na forma informacional), que é a contraparte estatística do deslocamento regional $r_{ri}$ — não do efeito competitivo homotético $CE^{*}_r$ da Seção 6.

O artigo também qualifica a equivalência entre a identidade contábil (Equação 1) e a forma ANOVA (Equação 10). As duas são matematicamente equivalentes, mas a regressão estimada não reproduz os componentes contábeis, por duas razões: ela é medida em taxas, e não em empregos, de modo que os termos diferem pelo fator $E_{0,ri}$; e seus erros são heterocedásticos. Segundo Knudsen (2000), Berzeg (1978, 1984) mostra que as estimativas coincidem quando se supõe $E[e_{ri}^2] = \sigma^2/w_{ri}$, com $w_{ri} = E_{0,ri}/\sum_{r,i}E_{0,ri}$, e se estima por mínimos quadrados ponderados. A regressão da Seção 9, estimada por mínimos quadrados ordinários sem ponderação, não tem essa propriedade: nela, a taxa $g_{ri}$ de uma célula de emprego-base pequeno, cuja variância tende a ser maior, pesa tanto quanto a de uma célula grande.

Na comparação empírica do artigo (emprego do Bureau of Labor Statistics agregado nas divisões setoriais do BLS e nas nove divisões censitárias dos Estados Unidos, anos de 1970 e 1980), a forma informacional teve ajuste superior e discriminou melhor os parâmetros nos modelos simples e com a extensão de Arcelus: a porcentagem da *deviance* do modelo nulo explicada (PNMD, uma medida do tipo $R^2$) foi de 0,5163 e 0,6601, contra $R^2$ de 0,1836 e 0,2284 da ANOVA correspondente. Na forma dinâmica, o ajuste foi fraco nos dois casos (0,0258 contra 0,0111). O autor conclui com cautela. Os modelos informacionais exigem pouca manipulação prévia dos dados, permitem incorporar a informação disponível sob a forma de restrições, colocam a SSA no campo da análise estatística de dados tabulares nominais e parecem úteis em dados com poucos valores extremos grandes; em contrapartida, seus parâmetros são mais difíceis de interpretar e nem sempre ajustam melhor que a ANOVA.

### 10.2 Formalização

**Forma I (ANOVA).** É a regressão da Equação 10 (Seção 9.2). Knudsen (2000) a escreve com intercepto, $g_{ri} = a + B_i + e_{ri}$ (sua equação 4), em que $a$ estima $g_n$, $B_i$ estima $g_{ni}-g_n$ e o erro $e_{ri}$ estima o termo competitivo $g_{ri}-g_{ni}$; a Equação 10 usa o conjunto completo de *dummies* de setor no lugar do intercepto, o que é apenas outra parametrização. A extensão de Arcelus acrescenta um efeito de região, $g_{ri} = a + B_i + G_r + e_{ri}$ (equação 5), com $G_r = g_r - g_n$ e $e_{ri} = (g_{ri}-g_r)-(g_{ni}-g_n)$ — isto é, exatamente o deslocamento regional e o deslocamento diferencial da Equação 6, agora em taxas e com o segundo deslocado para o termo de erro. A forma dinâmica acrescenta ainda um efeito de período $V_k$ (equação 6). Sob normalidade dos erros, a razão entre cada parâmetro e seu erro-padrão segue a distribuição *t* de Student.

**Forma II (teoria da informação).** Sejam $q_{ri} = E_{0,ri}/\sum_{r,i}E_{0,ri}$ a distribuição *a priori* (participações no ano-base) e $p_{ri} = E_{1,ri}/\sum_{r,i}E_{1,ri}$ a distribuição *a posteriori* (participações no ano terminal). O ganho de informação de Kullback e Leibler (1951), equação 7 do artigo, mede a informação obtida ao observar $P$ dado $Q$:

$$ I(P:Q) = \sum_{r,i} p_{ri}\,\ln\frac{p_{ri}}{q_{ri}} \tag{12} $$

O modelo de mínima informação discriminante escolhe $P$ minimizando $I(P:Q)$ sujeito a restrições lineares que representam o que se sabe sobre a distribuição final, além de $\sum_{r,i}p_{ri}=1$ e $p_{ri}\ge 0$ (equação 8). O problema pode ser resolvido pelo dual, um programa geométrico sem restrições (equação 9), mas, com restrições de igualdade lineares, o método de Lagrange leva diretamente a um modelo log-linear em $p_{ri}$ (equação 10), e as quantidades resultantes são estimadores assintóticos de máxima verossimilhança. Na forma básica, a restrição fixa os totais setoriais, $\sum_r p_{ri} = o_i$ (equação 11), e a solução é $p_{ri} = q_{ri}\exp(a + o_i + f_{ri})$ (equação 12 do artigo). Na extensão de Arcelus — a da Seção 7.4 —, acrescenta-se a restrição dos totais regionais, $\sum_i p_{ri} = d_r$ (equação 15), e a solução passa a ser $p_{ri} = q_{ri}\exp(a + o_i + d_r + f_{ri})$ (equação 16). Reescrita em níveis de emprego (equação 17) e linearizada, ela dá a **forma estática** (equação 18 do artigo):

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

A Tabela 13 estima a forma estática (Equações 13 e 15) sobre o mesmo painel de 15 observações das Tabelas 1 e 2, com Bahia (a região "neutra" do exemplo) e Agropecuária como categorias de referência, isto é, como os níveis *aliased* de cada dimensão. Para manter a comparação com o artigo, os erros-padrão da tabela são os de máxima verossimilhança pura, com dispersão fixada em 1.

**Tabela 13 — Forma informacional estática de Knudsen (Equações 13 e 15): coeficientes, erro-padrão e teste de Wald**

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

A razão *deviance*/g.l. de 0,49, e a dispersão de Pearson de valor semelhante ($\hat\phi \approx 0{,}50$), não indicam sobredispersão neste painel. Com os erros quase-Poisson que a implementação usa por padrão, os erros-padrão da Tabela 13 seriam multiplicados por $\hat\phi^{1/2} \approx 0{,}70$, e nenhuma conclusão mudaria: os efeitos regionais continuam não significativos a 5%, e os dois efeitos setoriais continuam significativos.

O primeiro resultado notável não está nos efeitos de região, mas nos de setor. Na Seção 9, os coeficientes setoriais da Forma I foram usados apenas como médias amostrais, sem teste; a Forma II testa formalmente a composição setorial e a rejeita como nula com folga (Indústria: $p=0,017$; Serviços: $p<0,001$). O componente de composição setorial deste exemplo não é apenas numericamente grande: é estatisticamente bem determinado, ao contrário do componente competitivo, discutido a seguir. O padrão lembra o resultado empírico de Knudsen (2000), em que a forma informacional discriminou melhor os parâmetros setoriais do que a ANOVA.

Os efeitos de região reproduzem a conclusão substantiva da Seção 9: nenhuma região diverge de forma estatisticamente significativa da região de referência ao nível de 5%, e o Maranhão tem o coeficiente mais negativo do conjunto ($-0,0426$), embora com $p=0,420$, distante do limiar. A recentragem ponderada da implementação (Seção 10.2) mudaria o nível desses efeitos, porque subtrai a mesma constante de todos os $\hat D_r$, mas não as diferenças entre regiões nem sua ordenação. A Tabela 14 compara diretamente as duas formas.

**Tabela 14 — Comparação Forma I (ANOVA) versus Forma II (teoria da informação): efeito regional e significância**

| Região | Forma I: $\bar u_r$ (Tabela 12) | Forma I: valor-*p* | Forma II: $\hat D_r$ (rel. a BA) | Forma II: valor-*p* |
|:---|---:|---:|---:|---:|
| PI | 0,0253 | 0,459 | 0,0388 | 0,427 |
| CE | 0,0343 | 0,319 | 0,0277 | 0,507 |
| MA | −0,0562 | 0,115 | −0,0426 | 0,420 |
| BA | −0,0067 | 0,842 | (referência) | — |
| PE | 0,0033 | 0,921 | −0,0126 | 0,754 |

Fonte: elaboração própria, Tabela 12 e Tabela 13.

As duas formas não são diretamente comparáveis célula a célula. A Forma I deixa a região no termo de erro e reporta o desvio médio de cada região em relação às médias setoriais não ponderadas, em unidades de taxa; a Forma II reporta um coeficiente log-multiplicativo relativo à Bahia. A comparação que o próprio Knudsen (2000) faz entre parâmetros regionais usa a ANOVA com efeito de região explícito (sua equação 5) frente à equação 18. Ainda assim, as duas formas concordam no essencial: Piauí e Ceará ficam acima da Bahia, o Maranhão é sempre o mais negativo, e nenhuma região é estatisticamente distinguível de zero, ou da referência, a 5%. Elas divergem nas posições intermediárias: o Ceará supera o Piauí na Forma I e fica atrás dele na Forma II, e Pernambuco fica acima da Bahia na Forma I e abaixo dela na Forma II.

Essa concordância parcial não deve ser generalizada. Na Poisson, a variância cresce com a média, de modo que as células com mais emprego pesam mais sem que seja preciso escolher pesos, ponderação que na Forma I precisa ser imposta por mínimos quadrados ponderados. Por isso, as duas formas tendem a divergir mais em painéis com heterogeneidade de escala pronunciada entre células região-setor (células de emprego-base muito pequeno ao lado de células muito grandes), situação em que a Forma I sem ponderação pode subestimar a incerteza nas células pequenas e superestimá-la nas grandes. Em painéis reais, a dispersão $\hat\phi$ deve ser verificada antes de reportar os testes da Forma II.

## 11 SHIFT-SHARE ESPACIAL: NAZARA-HEWINGS (2004)

### 11.1 Justificativa

Todas as reformulações anteriores tratam cada região como uma unidade isolada. Nazara e Hewings (2004) argumentaram que essa suposição é implausível quando regiões vizinhas compartilham mercados de trabalho, cadeias de fornecimento ou efeitos de transbordamento (*spillover*) — o desempenho competitivo de uma região pode estar sistematicamente correlacionado com o de suas vizinhas, positiva ou negativamente. A proposta foi incorporar uma matriz de pesos espaciais à decomposição, criando uma taxonomia de vinte estruturas de decomposição possíveis conforme o componente considerado "local" ou "vizinho".

### 11.2 Formalização

Seja $w_{rs}$ o elemento da matriz de pesos espaciais $W$ — aqui, contiguidade de fronteira terrestre entre as unidades federativas, padronizada em linha ($\sum_s w_{rs}=1$ para toda região $r$ com ao menos um vizinho). Define-se a **taxa competitiva** regional (para distinguir do efeito competitivo em nível, $CE_r$, que depende da escala de emprego da região):

$$ c_r = \frac{CE_r}{E_{0,r\bullet}} \tag{16} $$

O componente espacial central da abordagem de Nazara-Hewings é a **defasagem espacial** da taxa competitiva — a média (ponderada pela contiguidade) da taxa competitiva das regiões vizinhas:

$$ (Wc)_r = \sum_{s} w_{rs}\,c_s \tag{17} $$

A diferença $c_r - (Wc)_r$ indica se a região tem desempenho competitivo destoante de sua vizinhança imediata (positiva: melhor que os vizinhos; negativa: pior). Para testar se essa dependência espacial é sistemática — e não um artefato de amostra pequena —, calcula-se o **I de Moran global** sobre as taxas competitivas (nunca sobre o emprego em nível, cuja heterogeneidade de escala entre regiões mascara inteiramente o padrão espacial):

$$ I = \frac{n}{S_0}\cdot\frac{z'Wz}{z'z}, \qquad z_r = c_r - \bar c, \qquad S_0=\sum_r\sum_s w_{rs} \tag{18} $$

com valor esperado sob a hipótese nula de aleatoriedade espacial $E[I]=-1/(n-1)$. Valores de $I$ acima de $E[I]$ indicam autocorrelação espacial positiva (regiões vizinhas com taxas competitivas parecidas); valores abaixo indicam autocorrelação negativa (vizinhos dissimilares).

### 11.3 Aplicação

A malha de contiguidade das cinco regiões deste exemplo segue as fronteiras terrestres reais entre as unidades federativas: Piauí faz fronteira com as quatro demais (Ceará, Maranhão, Bahia e Pernambuco), Ceará e Pernambuco fazem fronteira entre si, e Bahia e Pernambuco também. Maranhão e Bahia, apesar de ambos vizinhos do Piauí, não fazem fronteira uma com a outra. A Tabela 15 apresenta a matriz padronizada em linha.

**Tabela 15 — Matriz de pesos espaciais $W$ (contiguidade de fronteira, padronizada em linha)**

| | PI | CE | MA | BA | PE |
|:---|---:|---:|---:|---:|---:|
| PI | 0,000 | 0,250 | 0,250 | 0,250 | 0,250 |
| CE | 0,500 | 0,000 | 0,000 | 0,000 | 0,500 |
| MA | 1,000 | 0,000 | 0,000 | 0,000 | 0,000 |
| BA | 0,500 | 0,000 | 0,000 | 0,000 | 0,500 |
| PE | 0,333 | 0,333 | 0,000 | 0,333 | 0,000 |

Fonte: elaboração própria a partir de fronteiras terrestres reais entre as cinco unidades federativas (subconjunto ilustrativo; ver Seção 15). A matriz completa das 27 unidades federativas é usada na aplicação empírica da Seção 12.6.

**Tabela 16 — Taxa competitiva local, defasagem espacial e hiato (Equações 16–17)**

| Região | $c_r$ (taxa competitiva local) | $(Wc)_r$ (média dos vizinhos) | Hiato $c_r-(Wc)_r$ |
|:---|---:|---:|---:|
| PI | 4,33% | −1,12% | 5,45 p.p. |
| CE | 3,01% | 1,20% | 1,81 p.p. |
| MA | −5,17% | 4,33% | −9,50 p.p. |
| BA | −0,38% | 1,20% | −1,58 p.p. |
| PE | −1,93% | 2,32% | −4,25 p.p. |

Fonte: elaboração própria, Equações 16 e 17.

O caso do Maranhão é o mais informativo: sua taxa competitiva local é a mais negativa do conjunto (−5,17%), mas seu único vizinho na malha, o Piauí, tem a taxa mais positiva (4,33%) — um hiato de −9,5 pontos percentuais em relação à própria vizinhança. Isso é o oposto do padrão que a hipótese de *spillover* positivo prediria (vizinhos com desempenho parecido) e resulta, para este pequeno conjunto de cinco regiões, em um I de Moran global de $I=-0{,}4852$, abaixo do valor esperado sob aleatoriedade $E[I]=-0{,}25$ — um sinal de dissimilaridade, e não de agrupamento espacial positivo, entre vizinhos. Como discutido na Seção 15, um I de Moran com apenas cinco unidades tem poder estatístico praticamente nulo; o valor é reportado aqui unicamente para ilustrar o cálculo da Equação 18, não como evidência substantiva de dependência espacial.

## 12 APLICAÇÃO EMPÍRICA: AS UNIDADES FEDERATIVAS BRASILEIRAS NA RAIS, 2022–2025

As Seções 4 a 11 usaram dados sintéticos porque o objetivo era didático: com uma verdade conhecida por construção, é possível mostrar o que cada variante corrige. Dados reais não têm verdade conhecida, e a pergunta muda. O que se pode ainda perguntar — e é exatamente o que a literatura aplicada discute — é **quanto as variantes discordam entre si sobre os mesmos números**. Esta seção responde a essa pergunta com o emprego formal das 27 unidades federativas brasileiras entre 2022 e 2025, e sua conclusão central é metodológica, não substantiva: no painel real, a discordância entre escolhas igualmente defensáveis do analista é maior do que os defeitos que as reformulações das Seções 5 a 11 se propõem a corrigir.

### 12.1 Base de dados, medida e recorte

A fonte é a Relação Anual de Informações Sociais (RAIS), arquivo de estabelecimentos, divulgada pelo Ministério do Trabalho e Emprego por meio do Programa de Disseminação de Estatísticas do Trabalho (BRASIL, 2026). A medida de emprego é a **quantidade de vínculos ativos em 31 de dezembro** de cada ano, agregada por unidade federativa (código de UF do IBGE) e por **seção da CNAE 2.0**, derivada dos dois primeiros dígitos da divisão econômica do estabelecimento. O painel cobre quatro anos — 2022, 2023, 2024 e 2025 —, e não apenas os dois extremos, porque as formas dinâmica (Seção 8) e inferenciais (Seções 9 e 10) degeneram em suas formas estáticas quando há apenas dois pontos no tempo; a janela de referência de todos os resultados reportados, contudo, é 2022→2025.

Das 21 seções da CNAE 2.0, três são excluídas do painel-padrão, restando $R=27$ regiões e $N=18$ setores. As seções T (serviços domésticos, 1.283 vínculos no país) e U (organismos internacionais, 2.319) são pequenas demais para sustentar uma taxa de crescimento e estão vazias em diversas células região-ano. A seção O (administração pública) é excluída por uma razão de natureza diferente, tratada na Seção 12.2 — e é o achado mais importante desta aplicação.

No painel resultante, o emprego formal passa de 44,073 milhões de vínculos em 2022 para 48,697 milhões em 2025 ($g_n = 10{,}49\%$), com trajetória anual de 44,073 → 45,651 → 47,335 → 48,697 milhões. A Tabela 17 apresenta as taxas nacionais setoriais $g_{ni}$ — a "ponta" contra a qual cada unidade federativa é comparada, no papel que as taxas da Seção 3 cumpriam no exemplo sintético.

**Tabela 17 — Taxa nacional de crescimento do emprego formal por seção da CNAE 2.0, Brasil, 2022–2025**

| Seção | Atividade | $g_{ni}$ (%) |
|:---|:---|---:|
| P | Educação | 38,98 |
| R | Artes e recreação | 30,71 |
| Q | Saúde e serviços sociais | 16,40 |
| N | Administrativas | 15,28 |
| M | Profissionais e técnicas | 14,79 |
| B | Extrativa | 13,24 |
| H | Transporte | 11,26 |
| F | Construção | 10,80 |
| I | Alojamento e alimentação | 9,57 |
| E | Água e resíduos | 8,99 |
| L | Imobiliárias | 7,91 |
| S | Outros serviços | 7,61 |
| D | Eletricidade e gás | 7,17 |
| J | Informação e comunicação | 6,00 |
| C | Transformação | 5,24 |
| G | Comércio | 4,28 |
| K | Financeiro e seguros | 4,02 |
| A | Agropecuária | 3,39 |
| — | **Agregado ($g_n$)** | **10,49** |

Fonte: elaboração própria a partir da RAIS 2022–2025 (MTE/PDET), arquivo de estabelecimentos, vínculos ativos em 31/12.

### 12.2 A quebra de série do eSocial e o custo de ignorá-la

Entre as bases 2022 e 2023 da RAIS houve migração da coleta para o eSocial, com reclassificação dos tipos de vínculo do setor público. A nota técnica da RAIS 2023 registra, no agregado nacional, queda de 907.224 vínculos estatutários (−15,4%) e aumento de 927.463 vínculos regidos por contrato de legislação municipal (+260,7%) — isto é, praticamente o mesmo contingente mudando de rótulo. O efeito sobre a seção O é incompatível com qualquer leitura econômica: entre 2022 e 2025 ela cresce 175,8% no Distrito Federal, 110,4% em Roraima e 80,0% em Mato Grosso, enquanto **cai 8,9% em São Paulo** (Tabela 18). A seção respondia por 16,5% dos vínculos do país em 2022, de modo que não se trata de um detalhe periférico do painel.

**Tabela 18 — Crescimento da seção O (administração pública): as cinco maiores e as cinco menores variações entre as unidades federativas, 2022–2025 (%)**

| UF | Variação | Posição |
|:---|---:|:---|
| DF | +175,8 | 1ª (maior) |
| RR | +110,4 | 2ª |
| MT | +80,0 | 3ª |
| AM | +70,4 | 4ª |
| CE | +63,9 | 5ª |
| PR | +14,4 | 23ª |
| RS | +13,0 | 24ª |
| RN | +11,5 | 25ª |
| RO | +8,9 | 26ª |
| **SP** | **−8,9** | **27ª (menor)** |

Fonte: elaboração própria a partir da RAIS 2022–2025 (MTE/PDET).

A SSA não distingue uma quebra de cobertura de um ganho de competitividade. Sendo uma identidade contábil, tudo o que não é crescimento nacional nem composição setorial vai para o resíduo competitivo: a mudança de rótulo contratual **aparece como vantagem competitiva**. Para medir quanto resíduo essa quebra fabrica, define-se o erro quadrático médio normalizado entre duas versões do mesmo componente, $x$ e $x^{\text{ref}}$, calculado sobre as $R$ regiões:

$$ \mathrm{nRMSE}\!\left(x, x^{\text{ref}}\right) = \frac{\sqrt{R^{-1}\sum_{r}\left(x_r - x_r^{\text{ref}}\right)^2}}{\sigma\!\left(x^{\text{ref}}\right)} \tag{19} $$

A normalização pelo desvio-padrão da própria referência torna a medida interpretável: $\mathrm{nRMSE}=0{,}30$ significa que a discordância típica equivale a um terço da dispersão que a referência reporta entre as unidades federativas; valores acima de 1 significam que a discordância excede toda a variação que se pretende explicar. A Tabela 19 aplica a Equação 19 ao painel com e sem a seção O.

**Tabela 19 — Custo de incluir a administração pública no painel (base de comparação: painel sem a seção O; maior diferença em vínculos)**

| Modelo | Pearson | Spearman | nRMSE | Maior dif. | UF |
|:---|---:|---:|---:|---:|:---|
| Dunn, pesos-base | 0,140 | 0,335 | 3,98 | 589.018 | SP |
| Barff-Knight dinâmico | 0,266 | 0,440 | 3,82 | 529.466 | SP |
| Nazara-Hewings estático | 0,140 | 0,335 | 3,98 | 589.018 | SP |

Fonte: elaboração própria, Equação 19 aplicada à RAIS 2022–2025 (MTE/PDET).

Incluir a seção O multiplica a discordância por quase quatro desvios-padrão da própria série e desmancha a ordenação das unidades federativas: a correlação de Spearman entre as duas versões cai para 0,33 (Dunn) ou 0,44 (Barff-Knight). São Paulo, a UF mais afetada, muda em mais de meio milhão de vínculos o seu efeito competitivo. Nenhuma economia estadual ganhou ou perdeu competitividade nessa escala entre 2022 e 2025 — mudou o formulário. Como a Tabela 24 mostrará, esse é o maior de todos os efeitos medidos nesta aplicação, cerca de três vezes o da escolha de pesos e dez vezes o do nível de agregação setorial.

### 12.3 A decomposição de referência (Barff-Knight, 2022–2025)

Adota-se como referência a decomposição dinâmica de Barff-Knight (Seção 8), somada sobre os três subperíodos anuais do painel, por ser a variante que não exige escolha de ano de ponderação (Seção 5) e que não impõe reponderação homotética (Seção 6) — portanto a menos dependente de decisões discricionárias entre as variantes aplicáveis. A Tabela 20 apresenta seus componentes.

**Tabela 20 — Decomposição dinâmica de Barff-Knight, unidades federativas, RAIS 2022–2025 (mil vínculos)**

| UF | $\Delta E_r$ | $NE_r$ | $IM_r$ | $CE_r$ |
|:---|---:|---:|---:|---:|
| MG | 571,7 | 498,2 | 11,5 | 62,0 |
| PI | 87,2 | 38,2 | 7,7 | 41,2 |
| PB | 87,5 | 51,8 | 3,3 | 32,4 |
| TO | 65,2 | 26,9 | 6,7 | 31,6 |
| MA | 91,0 | 62,2 | 1,1 | 27,7 |
| PA | 124,6 | 97,2 | 0,8 | 26,6 |
| PE | 161,3 | 144,3 | 1,3 | 15,7 |
| RR | 19,8 | 8,2 | 0,3 | 11,3 |
| AP | 21,3 | 9,2 | 2,1 | 10,0 |
| SE | 44,7 | 32,9 | 2,2 | 9,6 |
| RN | 61,4 | 50,5 | 2,6 | 8,3 |
| CE | 140,4 | 131,6 | 1,1 | 7,8 |
| BA | 208,2 | 202,2 | −1,6 | 7,6 |
| MT | 81,9 | 92,1 | −16,8 | 6,6 |
| RO | 29,1 | 28,7 | −4,0 | 4,4 |
| SP | 1.404,0 | 1.408,4 | −6,2 | 1,8 |
| AC | 11,5 | 10,2 | 0,2 | 1,0 |
| AL | 39,2 | 42,8 | −0,9 | −2,7 |
| GO | 159,9 | 160,1 | 5,5 | −5,7 |
| ES | 80,4 | 91,3 | −0,8 | −10,0 |
| SC | 203,7 | 248,2 | −32,4 | −12,1 |
| AM | 44,0 | 54,7 | 5,9 | −16,7 |
| PR | 289,0 | 320,7 | −11,5 | −20,2 |
| MS | 44,8 | 67,7 | −2,5 | −20,4 |
| DF | 82,9 | 97,4 | 12,5 | −27,0 |
| RJ | 348,0 | 372,0 | 38,2 | −62,1 |
| RS | 121,7 | 276,6 | −26,3 | −128,6 |

Fonte: elaboração própria, Equações 1 e 9 aplicadas à RAIS 2022–2025 (MTE/PDET). Soma nacional: $\sum_r NE_r = 4.624{,}3$; $\sum_r IM_r = \sum_r CE_r = 0$, por construção.

Três leituras se destacam, e todas valem apenas sob esta variante. Primeira: o efeito de crescimento nacional domina em toda parte — São Paulo cresce 1,404 milhão de vínculos, dos quais 1,408 milhão são a maré nacional, e seu resíduo competitivo é de apenas 1,8 mil, essencialmente nulo em termos relativos. Segunda: o efeito de composição setorial é pequeno — em nenhuma UF ele chega a um quarto do efeito nacional —, o que confirma, com dados reais, por que a literatura concentrou quatro décadas de reformulação no resíduo competitivo e não no *industry mix*. Terceira: os efeitos competitivos positivos estão fortemente concentrados no Norte e Nordeste (PI, PB, TO, MA, PA) e os negativos no Sul e Sudeste (RS, RJ, PR, SC), padrão de convergência que a Seção 12.6 testa quanto a agrupamento espacial.

### 12.4 O impacto da escolha do analista

Esta é a subseção central do documento, e seu resultado deve ser lido como uma advertência operacional: **as decisões discricionárias do analista movem o resultado da SSA mais do que os defeitos que as variantes das Seções 5 a 11 corrigem**. A Tabela 21 ilustra o problema no caso extremo. São Paulo tem, nos mesmos dados, nos mesmos anos e no mesmo nível de agregação, catorze estimativas de efeito competitivo — de −23,6 mil a +212,6 mil vínculos.

**Tabela 21 — Efeito competitivo de São Paulo e sua posição no ordenamento nacional sob cada variante, RAIS 2022–2025 (mil vínculos)**

| Variante | $CE_{\text{SP}}$ | Posição de SP no ordenamento |
|:---|---:|---:|
| Regressão análoga completa | −23,6 | 24ª |
| Knudsen MDI (dinâmico) | −21,3 | 24ª |
| Berzeg ANOVA | 1,8 | 16ª |
| Nazara-Hewings dinâmico | 1,8 | 16ª |
| **Barff-Knight dinâmico (referência)** | **1,8** | **16ª** |
| Knudsen MDI (estático) | 25,2 | 6ª |
| Dunn, pesos-base | 26,0 | 7ª |
| Nazara-Hewings estático | 26,0 | 7ª |
| Arcelus II (estático) | 26,0 | 7ª |
| Esteban-Marquillas dinâmico* | 88,9 | 1ª |
| Dunn, pesos médios (Fuchs) | 119,3 | 2ª |
| Esteban-Marquillas estático* | 127,3 | 1ª |
| Arcelus I (estático)* | 127,3 | 1ª |
| Dunn, pesos terminais | 212,6 | 1ª |
| **Amplitude** | **236,2** | **23 posições** |

Fonte: elaboração própria, RAIS 2022–2025 (MTE/PDET). Mediana: 25,2 mil vínculos entre as onze variantes de alvo comparável; 26,0 mil entre as catorze. (*) Variantes homotéticas, cujo efeito competitivo é, por construção, uma grandeza diferente (Seção 6.2) e que não são estritamente comparáveis às demais; ainda assim são reportadas pela literatura aplicada como "o efeito competitivo" da região.

O ponto não é que uma dessas estimativas esteja certa e as outras erradas. É que **o sinal do resultado é uma escolha do analista, não uma leitura dos dados**: São Paulo é competitivamente favorecido ou desfavorecido no período conforme a variante adotada, e nenhuma das catorze é indefensável à luz da literatura das Seções 4 a 11. Entre as onze variantes de alvo comparável, três das 27 unidades federativas trocam de sinal — São Paulo, Amazonas e Alagoas —, e Goiás junta-se a elas quando as três variantes homotéticas são incluídas, totalizando quatro; as demais preservam o sinal, o que confirma a estabilidade relativa de sinal observada por Fuchs (1959) para a maioria das regiões, mas não para aquelas cujo resíduo é pequeno em relação à sua escala.

A instabilidade de **ordenação** é mais severa do que a de sinal, porque é sobre o ranking que se costuma construir o argumento de política. A Tabela 22 reporta a posição mínima e máxima que cada UF ocupa no ordenamento do efeito competitivo, de 1 (maior) a 27 (menor), à medida que se troca de variante.

**Tabela 22 — Amplitude da posição no ordenamento do efeito competitivo entre as 14 variantes (UFs com oscilação de 3 ou mais posições)**

| UF | Melhor posição | Pior posição | Amplitude |
|:---|---:|---:|---:|
| SP | 1 | 24 | 23 |
| AM | 11 | 22 | 11 |
| BA | 9 | 17 | 8 |
| PA | 3 | 8 | 5 |
| SE | 9 | 14 | 5 |
| MT | 10 | 14 | 4 |
| TO | 3 | 7 | 4 |
| RN | 11 | 15 | 4 |
| AP | 9 | 13 | 4 |
| AL / AC / RO / SC / PR / GO / ES / CE / PE | — | — | 3 |

Fonte: elaboração própria, RAIS 2022–2025 (MTE/PDET). Rio de Janeiro e Rio Grande do Sul são as únicas UFs com posição invariante (26ª e 27ª em todas as variantes).

São Paulo pode ser apresentado como a unidade federativa **mais** competitiva do país (1ª posição, sob pesos terminais) ou como a 24ª entre 27 (regressão análoga completa) a partir do mesmo painel. Esse é o resultado que esta nota considera o mais importante a transmitir: um ranking de competitividade estadual derivado de SSA, reportado sem a variante, os pesos, o nível de agregação e as exclusões que o produziram, não é um resultado verificável.

A Tabela 23 ordena as variantes pela distância até a referência, separando as homotéticas, que miram grandeza distinta.

**Tabela 23 — Concordância de cada variante com a referência dinâmica de Barff-Knight, RAIS 2022–2025**

| Variante | Pearson | Spearman | nRMSE | Salto máx. | Sinal |
|:---|---:|---:|---:|---:|:---|
| Nazara-Hewings dinâmico | 1,000 | 1,000 | 0,00 | 0 | 27/27 |
| Berzeg ANOVA | 1,000 | 1,000 | 0,00 | 0 | 27/27 |
| Knudsen MDI (estático) | 0,990 | 0,963 | 0,14 | 10 | 27/27 |
| Knudsen MDI (dinâmico) | 0,990 | 0,970 | 0,15 | 8 | 26/27 |
| Regressão análoga completa | 0,989 | 0,973 | 0,15 | 8 | 26/27 |
| Dunn, pesos-base | 0,991 | 0,968 | 0,16 | 9 | 27/27 |
| Nazara-Hewings estático | 0,991 | 0,968 | 0,16 | 9 | 27/27 |
| Arcelus II (estático) | 0,991 | 0,968 | 0,16 | 9 | 27/27 |
| Dunn, pesos médios (Fuchs) | 0,864 | 0,921 | 0,75 | 14 | 27/27 |
| Dunn, pesos terminais | 0,719 | 0,861 | 1,37 | 15 | 25/27 |
| Esteban-Marquillas dinâmico* | 0,886 | 0,902 | 0,52 | 15 | 25/27 |
| Esteban-Marquillas estático* | 0,819 | 0,893 | 0,73 | 15 | 25/27 |
| Arcelus I (estático)* | 0,819 | 0,893 | 0,73 | 15 | 25/27 |

Fonte: elaboração própria, RAIS 2022–2025 (MTE/PDET). nRMSE conforme a Equação 19; "salto máx." é o maior deslocamento de posição de uma UF entre os dois ordenamentos; "sinal" é o número de UFs em que a variante e a referência concordam quanto ao sinal. (*) Variantes homotéticas, de alvo distinto.

Dois padrões merecem registro. Primeiro, a escolha da **família de modelos** importa pouco entre as variantes de alvo comparável: Berzeg e Nazara-Hewings dinâmico reproduzem a referência à precisão de máquina (como a álgebra prediz — ver Seções 9.2 e 11.2), e Knudsen, a regressão análoga e Dunn com pesos-base ficam todos entre 0,14 e 0,16 de nRMSE. Segundo, a escolha dos **pesos temporais** importa muito: pesos terminais ficam a 1,37 — a discordância excede em 37% toda a dispersão entre as 27 UFs. A título de comparação, no Monte Carlo sintético do cenário benigno do projeto, o pior nRMSE **contra a verdade conhecida** era 0,37, também dos pesos terminais. Isto é, a discordância entre duas convenções de ponderação em dados reais é quase quatro vezes maior do que o erro que qualquer variante comete em um desenho controlado.

A Tabela 24 consolida a hierarquia das decisões discricionárias, agora medindo cada uma contra sua própria linha de base.

**Tabela 24 — Hierarquia do impacto das escolhas do analista sobre o efeito competitivo (maior diferença em vínculos)**

| Decisão | Comparação | Spearman | nRMSE | Maior dif. | UF |
|:---|:---|---:|---:|---:|:---|
| Tratamento da quebra de série | com vs. sem seção O (Dunn) | 0,335 | 3,98 | 589.018 | SP |
| Tratamento da quebra de série | com vs. sem seção O (Barff-Knight) | 0,440 | 3,82 | 529.466 | SP |
| Ano de ponderação | pesos terminais vs. base | 0,932 | 1,16 | 186.538 | SP |
| Ano de ponderação | pesos médios vs. base | 0,983 | 0,58 | 93.269 | SP |
| Nível de agregação setorial | 5 setores vs. 18 seções (Dunn) | 0,879 | 0,43 | 74.246 | SP |
| Nível de agregação setorial | 5 setores vs. 18 seções (Barff-Knight) | 0,958 | 0,38 | 58.609 | SP |
| Família de modelos | variantes de alvo comparável vs. referência | 0,963–1,000 | 0,00–0,16 | — | — |

Fonte: elaboração própria, Equação 19 aplicada à RAIS 2022–2025 (MTE/PDET).

A ordenação é inequívoca e inverte a hierarquia implícita na literatura. O tratamento da quebra de série — uma decisão sobre os **dados**, raramente documentada em trabalhos aplicados — domina tudo, com nRMSE de 3,8 a 4,0. Em seguida vem a convenção de ponderação (1,16), a crítica mais antiga do campo (FUCHS, 1959; ASHBY, 1970) e, ainda hoje, a menos resolvida. Depois o nível de agregação setorial (0,38 a 0,43), exatamente o viés que Houston (1967) apontou: passar de 18 seções da CNAE a 5 setores agregados desloca o efeito competitivo em até 74 mil vínculos em São Paulo, porque o resíduo absorve a heterogeneidade intrassetorial que a agregação apaga. Só por último, e com folga, vem a escolha da **variante do método** — aquilo a que as Seções 4 a 11 dedicam toda a sua formalização.

A consequência prática é que a atenção metodológica está mal alocada. Discutir Esteban-Marquillas contra Arcelus contra Knudsen é legítimo e bem fundamentado, mas um trabalho aplicado que faça essa escolha com rigor e trate a quebra de série, os pesos e a agregação como detalhes de implementação estará reportando um número cuja incerteza é, em ordem de magnitude, dez vezes maior do que a diferença que escolheu discutir. Daí um protocolo mínimo de transparência para aplicações da SSA, que esta nota recomenda: **(i)** declarar a variante e sua equação; **(ii)** declarar o ano de ponderação e justificar a escolha teoricamente, não por conveniência; **(iii)** declarar o nível de agregação setorial e verificar a sensibilidade a um nível mais fino; **(iv)** declarar e justificar toda célula excluída, com atenção especial a quebras de cobertura administrativa; e **(v)** reportar a **amplitude** do componente competitivo entre as variantes defensáveis, e não apenas uma estimativa pontual. A Tabela 21 é um exemplo do item (v): o resultado honesto para São Paulo não é "+26 mil vínculos", mas "entre −24 mil e +213 mil, mediana +25 mil, sinal indeterminado".

### 12.5 Inferência: o que sobrevive a um teste estatístico

As Seções 9 e 10 introduziram variantes que permitem testar se um efeito competitivo difere de zero. Aplicadas ao painel da RAIS, elas convergem em um resultado desconfortável: quase nada é significativo.

**Tabela 25 — Unidades federativas com efeito competitivo significativo a 5%, RAIS 2022–2025**

| Modelo | Nº de UFs | Proporção | UFs |
|:---|---:|---:|:---|
| Berzeg ANOVA (Seção 9) | 4 | 14,8% | AP, PI, RS, TO |
| Knudsen MDI, forma estática (Seção 10) | 3 | 11,1% | PI, RS, TO |
| Knudsen MDI, forma dinâmica (Seção 10) | 2 | 7,4% | PI, RS |
| Regressão análoga completa (Seção 9.2) | 0 | 0,0% | — |

Fonte: elaboração própria, RAIS 2022–2025 (MTE/PDET), nível de significância de 5%.

Apenas Piauí e Rio Grande do Sul são sinalizados por todos os modelos que sinalizam algo, e a regressão análoga completa — a especificação mais exigente, com o conjunto completo de interações região-setor — não encontra nenhuma UF significativa. A leitura correta não é que o Brasil não tenha diferenciais regionais de competitividade, e sim que, com 18 setores por UF e três subperíodos anuais, a variação intrassetorial é grande o bastante para que a maior parte dos resíduos competitivos da Tabela 20 não seja distinguível de zero. Isso qualifica diretamente as Tabelas 20 a 22: a instabilidade de ordenação documentada na Seção 12.4 se dá, em boa medida, entre números que não são estatisticamente diferentes entre si — o que a torna ao mesmo tempo mais compreensível e mais grave, porque rankings são publicados como se fossem.

### 12.6 Dependência espacial: a ausência de agrupamento

Nazara e Hewings (2004) motivam a extensão espacial supondo que o desempenho competitivo de regiões vizinhas seja correlacionado. A matriz $W$ aqui é a contiguidade de fronteira terrestre real entre as 27 unidades federativas, padronizada em linha — a matriz completa, e não o subconjunto de cinco regiões da Seção 11.3. A Tabela 26 reporta o I de Moran (Equação 18) das taxas competitivas, com valores-*p* por permutação (999 permutações).

**Tabela 26 — I de Moran das taxas competitivas estimadas, RAIS 2022–2025 ($E[I]=-0{,}0385$)**

| Série | $I$ | Valor-*p* |
|:---|---:|---:|
| Crescimento total observado | 0,164 | 0,268 |
| Esteban-Marquillas / Arcelus I (estático) | 0,190 | 0,183 |
| Esteban-Marquillas dinâmico | 0,166 | 0,235 |
| Knudsen MDI (dinâmico) | 0,155 | 0,307 |
| Barff-Knight dinâmico (referência) | 0,142 | 0,339 |
| Dunn, pesos-base | 0,128 | 0,389 |
| Dunn, pesos médios (Fuchs) | 0,074 | 0,608 |
| Dunn, pesos terminais | 0,056 | 0,679 |
| Barff-Knight, sobre o **nível** do efeito competitivo | 0,101 | 0,427 |

Fonte: elaboração própria, Equação 18 aplicada à RAIS 2022–2025 (MTE/PDET), 999 permutações.

Todas as estimativas são positivas e todas estão acima de $E[I]$, o que é consistente com o padrão de convergência Norte-Nordeste observado na Tabela 20, mas **nenhuma é significativa**: os valores-*p* vão de 0,18 a 0,68. Para o emprego formal brasileiro agregado por UF nesta janela, portanto, a dependência espacial que motiva a extensão de Nazara-Hewings não é detectável. Convém notar que a coincidência entre as variantes espaciais e suas contrapartes não espaciais na Tabela 23 não é consequência disso: a decomposição de Nazara-Hewings reparte o efeito competitivo em uma parcela de vizinhança e uma parcela própria sem alterar seu total (Seção 11.2), de modo que o nRMSE nulo ali é algébrico. O que o teste de Moran acrescenta é que a repartição, neste recorte, não carrega sinal sistemático — a camada espacial é informativa sobre a composição do resíduo, não sobre sua magnitude. Isso não refuta a proposta: com $n=27$ unidades grandes e heterogêneas, o I de Moran tem poder modesto, e transbordamentos de mercado de trabalho operam plausivelmente em escala municipal ou microrregional, não estadual. A conclusão é de escala, não de método: a camada espacial deve ser adotada quando há motivo para esperar interação na unidade geográfica efetivamente usada, e sua adoção testada, não presumida. Note-se ainda que o I calculado sobre o **nível** do efeito competitivo (0,101) difere do calculado sobre a taxa (0,142), confirmando em dados reais a advertência da Seção 11.2 contra o uso de níveis.

### 12.7 Síntese da aplicação

**Quadro 2 — O que a aplicação à RAIS acrescenta a cada camada metodológica**

| Camada (Seção) | O que o exemplo sintético mostrava | O que a RAIS 2022–2025 mostra |
|:---|:---|:---|
| Identidade clássica (4) | A identidade fecha; o resíduo mistura estrutura e desempenho | A identidade fecha em dados reais; o componente nacional domina em todas as 27 UFs e o *industry mix* é pequeno em todas |
| Pesos temporais (5) | Magnitude muda, sinal não | Segunda maior fonte de discordância do estudo (nRMSE 1,16); Alagoas e Amazonas trocam de sinal entre pesos-base e terminais, e SP se desloca 187 mil vínculos |
| Homotetização (6, 7) | Separa competitividade de estrutura | Afasta-se mais da referência (nRMSE 0,52–0,73) do que qualquer variante de alvo comparável, e mede grandeza distinta — comparabilidade que a literatura aplicada frequentemente ignora |
| Dinâmica (8) | Corrige o viés de ponto a ponto | Adotada como referência justamente por não exigir escolha de pesos; diverge da forma estática em 0,16 |
| Inferência (9, 10) | Com $n$ pequeno, nada é significativo | Com $n=27$ e 18 setores, ainda assim 0 a 4 UFs significativas a 5% — a maior parte dos rankings publicáveis não é estatisticamente distinguível |
| Espacial (11) | Ilustra o cálculo com 5 regiões | Com a matriz completa de 27 UFs, $I$ entre 0,06 e 0,19 e nenhum valor-*p* abaixo de 0,18: a dependência espacial não é detectável nesta escala |
| Agregação (Houston, 1967) | Não exercitada | 18 seções vs. 5 setores desloca o resíduo em até 74 mil vínculos (nRMSE 0,38–0,43) |
| Qualidade do dado | Não exercitada | **Maior efeito de todos**: a quebra do eSocial na seção O produz nRMSE de 3,8 a 4,0 e derruba a correlação de ordenação a 0,33 |

Fonte: elaboração própria, síntese da Seção 12.

A lição que atravessa o Quadro 2 é a que a Seção 12.4 formula: a SSA é robusta no que tem de contábil — a identidade fecha, o componente nacional é inequívoco — e frágil exatamente onde é usada para fundamentar decisão, isto é, no resíduo competitivo e em sua ordenação entre regiões. Essa fragilidade não é um defeito de uma variante específica a ser corrigido por uma variante melhor; é uma propriedade do método, e a resposta disponível não é algébrica, mas de transparência: declarar cada escolha e reportar a amplitude que ela gera.

## 13 SÍNTESE: A LÓGICA DA EVOLUÇÃO METODOLÓGICA

O Quadro 1 resume, para cada variante tratada, qual falha da variante anterior ela ataca e o que permanece em aberto depois dela — a mesma lógica de "problema → correção → novo limite" que estruturou as Seções 4 a 11.

**Quadro 1 — Evolução dos componentes da SSA: problema atacado e limite remanescente**

| Variante | Problema que ataca | Mudança estrutural | Limite remanescente |
|:---|:---|:---|:---|
| Dunn (1960) — clássico | (linha de base) | Identidade aditiva de 3 componentes | Efeito competitivo contaminado por estrutura; sem inferência |
| Fuchs (1959) / pesos terminais | Viés do ano de ponderação | Média ou reversão de pesos | Sensibilidade permanece no efeito de alocação (Seção 6) |
| Esteban-Marquillas (1972) | Contaminação estrutural do efeito competitivo | Emprego homotético; efeito de alocação | Sinal de $AE$ sensível à escolha de pesos (Herzog-Olsen, 1977) |
| Arcelus (1984), Modelo I | Homotetização restrita ao efeito competitivo | Extensão da partição homotética a todos os componentes | Dois dos quatro novos subcomponentes são nulos por construção ao nível regional (Seção 7.3) |
| Arcelus (1984), Modelo II | Competitivo de Dunn não distingue desempenho da região do desempenho do setor | Partição de $CE_r$ em deslocamento regional e diferencial, com $g_r$ como referência | Somado por região, o diferencial é $-IM_r$ por construção (Seção 7.4); base das formas probabilísticas de Knudsen (2000) |
| Barff-Knight (1988) | Viés de ponto-a-ponto e crescimento composto | Soma de decomposições anuais/subperiódicas | Ainda determinístico; exige dados de alta frequência |
| Berzeg (1978, 1984) | Impossibilidade de teste estatístico | Identidade recastada como ANOVA/regressão | Pressupõe normalidade; erro absorve toda variação não sistemática |
| Knudsen (2000) | ANOVA heterocedástica, que depende de pesos impostos para reproduzir a identidade | *Shift-share* de mínima informação discriminante: modelo log-linear estimado por máxima verossimilhança (GLM de Poisson com *offset* pelo emprego-base) | Parâmetros em escala log, de interpretação mais difícil; erros de máxima verossimilhança pura exigem correção de dispersão (quase-Poisson) |
| Nazara-Hewings (2004) | Regiões tratadas como independentes | Matriz de pesos espaciais; defasagem espacial | Sensível à especificação da matriz; exige N grande para inferência confiável |

Fonte: elaboração própria, síntese das Seções 4 a 11.

## 14 QUADRO DE PARÂMETROS CONSOLIDADOS

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
| Erros-padrão do modelo de Knudsen (Seção 10) | Máxima verossimilhança pura na Tabela 13; quase-Poisson ($\hat\phi$ = qui-quadrado de Pearson/g.l.) por padrão na implementação |
| Diagnóstico de dispersão (Seção 10) | $\hat\phi \gg 1$ indica sobredispersão; modelo binomial negativo como alternativa |
| Critério de vizinhança espacial (Seção 11) | Contiguidade de fronteira terrestre real entre as 5 unidades federativas, padronizada em linha |
| Base de cálculo do I de Moran (Seção 11) | Taxa competitiva $c_r=CE_r/E_{0,r\bullet}$, nunca o emprego em nível |
| **Aplicação empírica (Seção 12) — fonte** | RAIS, arquivo de estabelecimentos (MTE/PDET), bases 2022 a 2025 |
| Medida de emprego (Seção 12) | Quantidade de vínculos ativos em 31 de dezembro de cada ano |
| Unidades e setores (Seção 12) | $R$ = 27 unidades federativas; $N$ = 18 seções da CNAE 2.0 |
| Seções CNAE excluídas (Seção 12.1) | O (administração pública, quebra do eSocial), T e U (escala insuficiente) |
| Janela de referência e painel (Seção 12.1) | 2022→2025; painel anual de quatro pontos para as formas dinâmica e inferenciais |
| Variante de referência (Seção 12.3) | Barff-Knight dinâmico (Equação 9), soma de três subperíodos anuais |
| Métrica de discordância (Seção 12.2) | nRMSE da Equação 19: RMSE entre regiões dividido pelo desvio-padrão da referência |
| Matriz espacial da aplicação (Seção 12.6) | Contiguidade de fronteira terrestre das 27 UFs, padronizada em linha; 999 permutações |

## 15 LIMITAÇÕES

**Escala do exemplo numérico.** Cinco regiões e três setores foram escolhidos exclusivamente por clareza expositiva — o quadro é pequeno demais para qualquer inferência estatística com poder adequado. Os testes *t* e de Wald das Seções 9 e 10, e o I de Moran da Seção 11, devem ser lidos como demonstrações do cálculo, não como evidência substantiva; com $n=5$, o I de Moran em particular tem variância amostral elevada e não deve ser interpretado como teste confiável de dependência espacial.

**Dados inteiramente sintéticos.** Nenhum valor de emprego neste documento corresponde a estatística oficial de Piauí, Ceará, Maranhão, Bahia ou Pernambuco — os nomes das unidades federativas foram usados apenas para ancorar a matriz de contiguidade espacial (Seção 11) em fronteiras reais, não para descrever essas economias.

**Trajetória do exemplo dinâmico é arbitrária.** A divisão em dois subperíodos e a distribuição de crescimento setorial entre eles (Seção 8) foram escolhidas para exibir divergência entre a forma dinâmica e a estática, não estimadas a partir de nenhum processo real; a magnitude da divergência em uma aplicação empírica dependerá inteiramente da volatilidade e do comprimento do período analisado, como já advertiam Barff e Knight (1988).

**Arcelus II formalizado por fonte secundária.** A Seção 7.4 formaliza o segundo modelo de Arcelus (1984) a partir das equações 2, 2a, 2b e 2c de Knudsen (2000, p. 179), que as apresenta como "a extensão de Arcelus" e as credita ao original. A álgebra foi verificada aqui — a identidade fecha à precisão de máquina e as três propriedades da Equação 8 valem —, mas o artigo de Arcelus (1984), *Growth and Change* 15(1), pp. 3–8, não foi consultado diretamente. Duas ressalvas, detalhadas ao fim da Seção 7.4: os ponderadores impressos em Knudsen (2000) são os do ano terminal, com os quais a identidade não fecha, e esta nota adota os do ano-base; e a correspondência entre os nomes de Arcelus (efeitos de crescimento e de composição regionais) e os termos $r_{ri}$ e $d_{ri}$ é leitura da álgebra, não verificada contra a nomenclatura do original. O modelo está implementado em `ssa_models.arcelus_ii` e entra na comparação de recuperação do caderno.

**Adaptações ao modelo de Knudsen (2000).** A Seção 10 foi conferida com o texto integral do artigo, e as equações que ela cita (4 a 6, 7 a 19 e 20 a 24) seguem a numeração do original. Três elementos não vêm do artigo, mas da implementação de referência do projeto: os erros-padrão quase-Poisson usados por padrão, a recentragem de $D_r$ para média ponderada nula e a conversão $(e^{D_r}-1)\,W_r$ em empregos. O artigo também não discute sobredispersão; a menção ao modelo binomial negativo vem de Flowerdew e Lovett (1989). A relação entre os parâmetros das Formas I e II segue a leitura $B_i = e^{O_i} - 1$, que difere da forma impressa no artigo, e o próprio autor não a encontrou com precisão nos dados (Seção 10.2). Por fim, o modelo misto com variável exógena contínua (equações 20 a 24) é apenas descrito, sem implementação nem exemplo numérico, e a forma dinâmica (equação 19) é formalizada mas não aplicada ao exemplo, cujas trajetórias de subperíodo da Seção 8 são hipotéticas.

**Matriz de contiguidade reduzida.** A malha espacial da Seção 11 usa apenas cinco das 26 unidades federativas mais o Distrito Federal — um subconjunto ilustrativo, não a matriz de contiguidade completa da federação brasileira (que integra o código computacional do projeto mais amplo do qual esta nota deriva). Padrões de dependência espacial identificados em um subconjunto de cinco regiões não são generalizáveis à matriz completa.

**A aplicação à RAIS mede discordância, não acerto.** A Seção 12 não tem verdade conhecida contra a qual avaliar as variantes: todas as suas métricas são de concordância entre modelos, tomando o Barff-Knight dinâmico como referência por convenção justificada na Seção 12.3, não por superioridade demonstrada. Que uma variante se afaste da referência não significa que erre; significa apenas que a escolha entre as duas altera a conclusão. Pela mesma razão, nenhum resultado da Seção 12 deve ser lido como diagnóstico de competitividade das economias estaduais brasileiras — e a Seção 12.5 mostra que, a 5%, de zero a quatro das 27 unidades federativas têm efeito competitivo distinguível de zero.

**Quebra de série e cobertura da RAIS.** A migração da coleta para o eSocial entre as bases 2022 e 2023 afeta a comparabilidade de toda a série, não só da seção O. A exclusão da administração pública (Seção 12.1) remove o caso extremo e mensurável, mas as seções P (educação) e Q (saúde e serviços sociais) carregam versão atenuada do mesmo problema e foram mantidas por terem emprego privado grande demais para ser descartado — suas taxas nacionais de 38,98% e 16,40% na Tabela 17 devem, por isso, ser lidas com reserva. Além disso, a RAIS cobre apenas o emprego formal declarado: a informalidade, heterogênea entre unidades federativas, fica inteiramente fora do painel, e o efeito competitivo estimado é o do mercado formal, não o da economia estadual.

**Escala geográfica da aplicação espacial.** O resultado da Seção 12.6 — ausência de autocorrelação espacial significativa — é condicional à unidade geográfica. Com 27 unidades grandes e internamente heterogêneas, o I de Moran tem poder modesto, e transbordamentos de mercado de trabalho operam plausivelmente em escala municipal ou microrregional. O achado não deve ser lido como evidência contra a proposta de Nazara e Hewings (2004), e sim como demonstração de que sua adoção deve ser testada na escala efetivamente usada.

**Sensibilidade a escolha não neutra de pesos.** Como demonstrado na Seção 5 e na Seção 6.3, tanto o efeito competitivo clássico quanto — de forma mais acentuada, e inclusive com inversão de sinal — o efeito de alocação de Esteban-Marquillas são sensíveis à escolha do ano de ponderação. Essa sensibilidade é uma propriedade do método, não um artefato deste exemplo específico, e já havia sido documentada empiricamente por Herzog e Olsen (1977) em dados reais das regiões do U.S. Bureau of Economic Analysis — e é confirmada, em escala muito maior do que a deste exemplo, pela Tabela 24: na RAIS, a troca de pesos-base por pesos terminais desloca o efeito competitivo de São Paulo em 187 mil vínculos.

## REFERÊNCIAS

ARCELUS, Francisco J. An extension of shift-share analysis. **Growth and Change**, v. 15, n. 1, p. 3-8, 1984.

BARFF, Richard A.; KNIGHT, Prentice L. Dynamic shift-share analysis. **Growth and Change**, v. 19, n. 2, p. 1-10, 1988.

BERZEG, Korkut. The empirical content of shift-share analysis. **Journal of Regional Science**, v. 18, n. 3, p. 463-469, 1978.

BRASIL. Ministério do Trabalho e Emprego. **Nota técnica: RAIS 2023**. Brasília: MTE, 2024. Disponível em: https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/estatisticas-trabalho/rais. Acesso em: 21 out. 2026.

BRASIL. Ministério do Trabalho e Emprego. **Relação Anual de Informações Sociais (RAIS): microdados de estabelecimentos, bases 2022 a 2025**. Brasília: Programa de Disseminação das Estatísticas do Trabalho (PDET), 2026. Disponível em: https://acesso.trabalho.gov.br/portal-pdet/o-pdet/portifolio-de-produtos/bases-de-dados.htm. Acesso em: 21 out. 2026.

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

*Nota de transparência: este documento formaliza os dois modelos de Arcelus (1984) — o Modelo I, homotético (Equação 5, Seção 7.2), e o Modelo II, de deslocamento regional (Equação 6, Seção 7.4) —, mas o Modelo II foi reconstruído a partir de Knudsen (2000, equações 2 a 2c), fonte secundária, sem consulta ao artigo original de Arcelus; a álgebra foi verificada, a nomenclatura não. A Seção 10 foi revisada com base no texto integral de Knudsen (2000): as equações do artigo são citadas pela numeração original, e as adaptações da implementação de referência (erros quase-Poisson, recentragem ponderada de $D_r$ e conversão em empregos) estão identificadas como tais na Seção 10.2 e na Seção 15. A referência a Rosenfeld (1959), citada na literatura secundária como um dos primeiros a apontar o defeito do efeito competitivo clássico, não pôde ser completada com periódico, volume e página exatos e é sinalizada como incompleta na lista de referências, em vez de inventada. Todos os valores numéricos das Tabelas 1 a 16 são sintéticos e devem ser validados como tal antes de qualquer circulação do documento; os das Tabelas 17 a 26 e do Quadro 2, ao contrário, são calculados a partir dos microdados reais da RAIS 2022-2025 (MTE/PDET) e são reproduzíveis pelos scripts `rais_data.py` e `run_rais.py` do projeto, cujas saídas em `results_rais_*.csv` são a fonte de cada número reportado na Seção 12; a seção não foi revisada contra publicação oficial de resultados de SSA para o Brasil, e sua contribuição é de robustez metodológica, não de diagnóstico econômico estadual; as medidas de ajuste citadas na Seção 10.1 são as reportadas por Knudsen (2000) para dados reais dos Estados Unidos.*
