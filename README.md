# DX Invest

Acesse aqui: http://daniloxaxa.pythonanywhere.com

DX Invest é uma aplicação web que simula compra e venda de ações da bolsa de valores norte-americana.

Ao acessar o site, o usuário pode criar uma conta clicando em "Cadastrar" na parte superior direita. Ao se cadastrar, chegará um e-mail avisando que o cadastro foi realizado com sucesso, mas não há necessidade de confirmar cadastro via e-mail.

Na página inicial, o usuário tem acesso à sua carteira de ações (portfólio). Inicialmente há 10.000 dólares em caixa e nenhuma ação, mas depois de comprar e vender ações, você poderá ver quanto você perdeu ou ganhou com os seus investimentos.

---

* Em "Cotações", o usuário pode fazer cotação de preço usando o código de alguma ação listada na bolsa dos EUA. Exemplos: GOOGL, AMZN, AAPL, TSLA, NFLX...

* Em "Comprar", o usuário pode comprar qualquer ação desejada, desde que ela exista e o usuário tenha dinheiro suficiente em caixa para comprar a quantidade de ações desejada.

* Em "Vender", o usuário pode vender quantas ações ele tiver de qualquer empresa que ele tenha comprado.

* Em "Histórico", o usuário pode ver qualquer transação feita e todos os seus detalhes, até mesmo as transações de adicionar e remover dinheiro.

* Em "Adicionar Dinheiro", o usuário pode adicionar em caixa qualquer quantia de dinheiro desejada.

* Em "Remover Dinheiro", o usuário pode remover em caixa qualquer quantia de dinheiro desejada.

* Em "Sair", o usuário desloga e é redirecionado para a página de login, mas vale constar que o site usa cookies/sessions para evitar que o usuário tenha que entrar repetitivamente diversas vezes.

---

OBS: Não use nenhuma senha importante que você usa em outros lugares, pois ela pode acabar vazando. Já que o medidor de força de senha está desabilitado, o usuário pode usar qualquer senha simples que desejar, como "123" ou "abc".

OBS 2: A aplicação ainda não suporta lidar com e-mails inexistentes ou navegação diretamente pela barra de URL.

OBS 3: Embora a página inicial redirecione para "/login" se o usuário não está cadastrado ou não entrou, ele deve se cadastrar antes de qualquer outra coisa.

---

O projeto foi desenvolvido com Python e seu framework Flask no back-end, sem nenhum uso de JavaScript (front-end estático). O banco de dados utilizado é o SQLite. Para alguns detalhes visuais, o Bootstrap foi utilizado.

Todos os dados das ações são fornecidos gratuitamente e em tempo real via IEX Cloud.
A hospedagem foi realizada via PythonAnywhere.

O projeto é inspirado no desafio Finance do curso CS50 de Harvard e tem fins apenas educacionais.
