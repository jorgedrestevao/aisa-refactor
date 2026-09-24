# Story — f8-r3-fx02

## Episódio 1 — o pedido

Sou director de sistemas de informação da Organização Exemplo. Quero digitalizar os pedidos de equipamento informático — portáteis, monitores, acessórios — porque hoje tudo corre por email e folha de cálculo, e isso já nos custou encomendas a dobrar e diferenças de cêntimos com a contabilidade. A plataforma já está decidida: Power Platform, por deliberação interna da direcção de SI (DSI-SINT-07) — isso não está em discussão. Quero o pedido, a aprovação e a passagem a compras cobertos; gestão de stock e recepção física ficam de fora. A auditoria interna tem de conseguir ver sempre quem aprovou o quê e quando.

## Episódio 2 — 2026-09-24 — ronda de Discovery (o que se descobriu, o que ficou por saber)

A primeira passagem confirmou o que eu já sabia: a chefia nunca aprova o seu próprio pedido, o limiar de aprovação da direcção financeira existe (só não sei o valor de cor), a auditoria quer rasto de quem aprovou o quê, e guardamos tudo dez anos. Mas apareceram buracos que não tinha visto assim tão claros. Não sei dizer quando é que este projecto "correu bem" — vou ter de pensar nisso antes de aprovar o desenho final. Ninguém sabe se arredondamos o cêntimo linha a linha ou só no total, e isso já gerou diferenças reais com a contabilidade. E há uma tensão que não tinha reparado: o caminho de urgência salta a aprovação da chefia, mas ninguém disse se também salta o limiar financeiro — vou ter de decidir isso. Falta-me ainda arranjar o despacho com o valor do limiar, e pensar no volume de pedidos e no tempo que cada passo demora hoje, para o esforço e o custo ficarem bem medidos.

## Episódio 3 — 2026-09-24 — segunda passagem (a mesma tensão, ainda por decidir)

Pedi uma segunda passagem antes de fechar a etapa de ouvir e perguntar, porque a tensão do caminho de urgência (X-001) toca duas regras que dei como garantidas — a separação entre quem pede e quem aprova, e o controlo da direcção financeira acima do limiar — e não queria dar isso por resolvido sem mais olhar. A conclusão, depois de reler tudo outra vez: ninguém escreveu nada, em nenhuma das notas, que resolva isto numa direcção ou noutra. Não é uma pergunta que se resolva a reler o que já temos — sou eu que tenho de decidir se o caminho de urgência também salta o controlo financeiro, ou não.

## Episódio 4 — 2026-09-24 — o problema ganhou uma frase (frame)

Decidi avançar mesmo com a tensão do caminho de urgência (X-001) por resolver — não vale a pena o projecto ficar parado à espera de uma resposta que hoje ninguém tem. Fiquei a ver a frase que resume o problema, e reconheço-me nela: os pedidos a dobrar, as diferenças de arredondamento com a contabilidade, o catálogo actualizado à mão, e o custo que ainda não sei quantificar. Gostei de ver marcado o que ainda não confirmei — não fica tudo apresentado como certeza. Sem nome de plataforma nenhuma nesta frase, como deve ser: essa conversa fica para a fase seguinte.

## Episódio 5 — 2026-09-24 — as opções na mesa

Agora sim, apareceram os nomes: duas formas de construir o pedido dentro do Power Platform que já está decidido, uma terceira mais barata mas mais frágil, e as duas alternativas de sempre — mudar só o processo, ou não fazer nada por agora. Cinco especialistas independentes revisitaram tudo antes de eu ver isto, e não pouparam nas críticas: a regra de detectar pedidos a dobrar, tal como estava descrita, não ia funcionar como eu pensava — foi corrigida. Descobri também que nunca verificámos se temos licenças suficientes para as cinco equipas envolvidas, nem se conseguimos mesmo ler os preços do outro sistema em tempo real. E uma das três formas mais baratas não consegue, por construção, impor o limiar dos 5 000 euros sem um risco que alguém tem de assinar. Não me deram uma recomendação fechada entre as duas formas principais — dizem que depende de saber se os meus colaboradores pedem também pelo telemóvel, coisa que ainda não perguntei a ninguém.

## Episódio 6 — 2026-09-24 — o obituário antes de decidir

Antes de escolher, pedi para escrever a necrológica do projecto, um ano para a frente, como se tivesse falhado. Não foi confortável de ler. Seis causas de morte, cada uma juntando coisas que já sabia mas não tinha ligado: o mecanismo de auditoria e as licenças por confirmar a acabarem em re-trabalho depois de ir ao ar; a regra de duplicados a falhar exactamente no pico que mais me custaria; a forma mais barata (registos) a deixar de fora quem pede pelo telemóvel, coisa que ainda não sei se acontece; a cópia dos preços a repetir o mesmo erro de hoje se ninguém ficar dono dela; o caso de negócio sem números nenhuns e sem critério de sucesso, ao fim de um ano sem ninguém saber dizer se valeu a pena; e o caminho de urgência a continuar a saltar o controlo financeiro que ainda não fechei. Ficaram-me claros os requisitos que têm de entrar no desenho e as condições que, se acontecerem, me obrigam a rever a escolha.

## Episódio 7 — 2026-09-24 — o desenho da aplicação (blueprint)

Escolhida a app orientada a registos, veio a primeira versão do desenho. Reconheço o pedido, as linhas, o registo de quem aprovou o quê e quando — está lá a auditoria que pedi (M-3), com um registo próprio, não só um log de sistema. O limiar dos 5000€ (M-2) e a regra de que a chefia nunca aprova o seu próprio pedido (M-1) estão desenhados nos estados do pedido. Uma coisa ficou por fechar de propósito: de onde vem o preço do catálogo — se lido em tempo real do outro sistema ou copiado — porque ainda não sei se há lá uma porta de entrada técnica para isso (U-004, U-012). O resto está pronto para eu olhar e aprovar.

## Episódio 8 — 2026-09-24 — os primeiros documentos (render)

Pedi para gerar os documentos finais e saíram três: o relatório de descoberta, o relatório executivo e o desenho da arquitectura, todos na primeira versão. Não saíram os outros três — a especificação de implementação e o guião de desenho ficam à espera de eu aprovar o desenho, e essa aprovação continua bloqueada pela mesma pergunta de sempre: de onde vem o preço do catálogo. A estimativa também não saiu — ainda não há especificação aprovada nem pedi eu uma conta por candidato. Nenhum dos três documentos que saíram se diz "completo": todos dizem, com todas as letras, o que ainda falta e onde. Prefiro isto a um documento bonito que esconda o que não sei.

## Episódio 9 — 2026-09-24 — voltámos a pôr as alternativas na mesa

Já com o desenho em mãos, chegou-me da contabilidade e de um despacho novo três mudanças ao que tínhamos combinado. A contabilidade quer arredondar linha a linha, não só no total, e de uma forma diferente da que tínhamos escrito — para bater certo com a facturação do fornecedor. Alguém corrigiu uma gralha na descrição do pedido, sem mexer no sentido. E o despacho novo baixa o limiar que obriga a passar pela direcção financeira, de 5 000 para 3 000 euros — o que significa que mais pedidos vão passar por ali a partir de agora, incluindo, se calhar, mais pedidos urgentes, e continuo sem responder se o caminho de urgência salta esse controlo ou não. Não é motivo para recomeçar do zero: a plataforma e a forma que escolhi continuam de pé, isto é só actualizar as regras. Pedi para reabrir só o que mudou, não a escolha toda outra vez.

## Episódio 10 — 2026-09-24 — a actualização, revista por cinco olhares

Voltou a app que já tinha escolhido, só que actualizada às três mudanças que trouxe. Cinco especialistas voltaram a olhar para ela, e todos bateram nos mesmos pontos, de ângulos diferentes: a condição que eu próprio aceitei para vigiar o caminho de urgência ficou escrita contra o limiar antigo — com o novo, deixa de cobrir exactamente a faixa que mais me preocupa. Ninguém confirmou ainda se a plataforma sabe arredondar da forma nova que a contabilidade pediu, ou se isso é trabalho técnico extra. E ninguém testou ainda um pedido mesmo em cima dos 3 000 euros novos, para ver se as duas mudanças juntas não me pregam uma partida ali. Não me apresentaram outra alternativa — isto continua a ser a app que escolhi, só com as regras a bater certo; só não avanço para decidir sem fechar estes três pontos primeiro.
